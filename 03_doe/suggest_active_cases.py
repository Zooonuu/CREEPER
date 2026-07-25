from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import qmc

ROOT = Path(__file__).resolve().parents[1]
PARAM_NAMES = ("l_sp_s_nm", "l_sp_d_nm", "w_low_k_nm")


def load_config() -> dict:
    with (ROOT / "project.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def feasible_array(values: np.ndarray) -> np.ndarray:
    return (values[:, 1] >= values[:, 0]) & (values[:, 2] <= values[:, 1])


def snap_array(values: np.ndarray, step: float) -> np.ndarray:
    return np.round(np.round(values / step) * step, 6)


def rbf_kernel(a: np.ndarray, b: np.ndarray, length_scale: float, sigma_f: float) -> np.ndarray:
    sq_dist = ((a[:, None, :] - b[None, :, :]) / length_scale) ** 2
    return sigma_f**2 * np.exp(-0.5 * sq_dist.sum(axis=2))


def gp_log_marginal_likelihood(
    x: np.ndarray, y: np.ndarray, length_scale: float, sigma_f: float, sigma_n: float
) -> float:
    n = len(x)
    k = rbf_kernel(x, x, length_scale, sigma_f) + (sigma_n**2) * np.eye(n)
    try:
        chol = np.linalg.cholesky(k)
    except np.linalg.LinAlgError:
        return -np.inf
    alpha = np.linalg.solve(chol.T, np.linalg.solve(chol, y))
    log_det = 2.0 * np.sum(np.log(np.diag(chol)))
    return float(-0.5 * y @ alpha - 0.5 * log_det - 0.5 * n * np.log(2 * np.pi))


def fit_gp(x: np.ndarray, y: np.ndarray, length_scale_grid: np.ndarray, sigma_n: float) -> dict:
    """Lightweight Gaussian-process surrogate (RBF kernel) with a small
    grid search over length scale by marginal likelihood. Deliberately
    dependency-free (numpy/scipy only) so it runs on the TCAD PC without
    needing scikit-learn installed."""
    sigma_f = max(float(y.std()), 1e-3)
    best_ll, best_ls = -np.inf, length_scale_grid[0]
    for ls in length_scale_grid:
        ll = gp_log_marginal_likelihood(x, y, ls, sigma_f, sigma_n)
        if ll > best_ll:
            best_ll, best_ls = ll, ls
    k = rbf_kernel(x, x, best_ls, sigma_f) + (sigma_n**2) * np.eye(len(x))
    chol = np.linalg.cholesky(k)
    alpha = np.linalg.solve(chol.T, np.linalg.solve(chol, y))
    return {"x": x, "alpha": alpha, "chol": chol, "length_scale": best_ls, "sigma_f": sigma_f}


def gp_predict(model: dict, x_star: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    k_star = rbf_kernel(x_star, model["x"], model["length_scale"], model["sigma_f"])
    mean = k_star @ model["alpha"]
    v = np.linalg.solve(model["chol"], k_star.T)
    var = model["sigma_f"] ** 2 - np.sum(v**2, axis=0)
    std = np.sqrt(np.maximum(var, 1e-12))
    return mean, std


def normalized_utility(df: pd.DataFrame, maximize: list[str], minimize: list[str]) -> np.ndarray:
    terms = []
    for col in maximize:
        values = df[col].astype(float).to_numpy()
        span = values.max() - values.min()
        terms.append(np.zeros_like(values) if span == 0 else (values - values.min()) / span)
    for col in minimize:
        values = df[col].astype(float).to_numpy()
        span = values.max() - values.min()
        terms.append(np.zeros_like(values) if span == 0 else (values.max() - values) / span)
    if not terms:
        raise ValueError("active_doe objectives are empty")
    return np.mean(np.column_stack(terms), axis=1)


def main() -> None:
    cfg = load_config()
    space = cfg["design_space"]
    active_cfg = cfg.get("active_doe", {})
    grid_cfg = cfg.get("fabrication_grid", {})

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=["device_screening", "circuit_dtco"],
        default=active_cfg.get("default_mode", "device_screening"),
    )
    parser.add_argument("--batch-size", type=int, default=int(active_cfg.get("suggestion_batch_size", 8)))
    parser.add_argument("--pool-size", type=int, default=int(active_cfg.get("candidate_pool_size", 4096)))
    parser.add_argument("--seed", type=int, default=int(cfg.get("doe", {}).get("seed", 20260723)))
    parser.add_argument("--exploration-weight", type=float, default=float(active_cfg.get("exploration_weight", 0.35)))
    parser.add_argument("--gp-noise-std", type=float, default=float(active_cfg.get("gp_noise_std", 0.05)))
    parser.add_argument("--min-distance-nm", type=float, default=float(active_cfg.get("min_distance_nm", 0.25)))
    parser.add_argument("--grid-step-nm", type=float, default=float(grid_cfg.get("step_nm", 0.5)))
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / active_cfg.get("output", "03_doe/cases/active_suggested_cases.csv"),
    )
    args = parser.parse_args()

    mode_cfg = active_cfg.get("modes", {}).get(args.mode, {})
    objective_cfg = mode_cfg.get("objectives", {})
    maximize = list(objective_cfg.get("maximize", ["ion_A"]))
    minimize = list(objective_cfg.get("minimize", ["cgd_F"]))
    needed = {"case_id", *PARAM_NAMES, *maximize, *minimize}

    raw = pd.read_csv(args.input)
    missing = needed - set(raw.columns)
    if missing:
        raise ValueError(f"result input is missing columns: {sorted(missing)}")
    df = raw.dropna(subset=list(needed - {"case_id"}))
    if len(df) < 6:
        raise ValueError("at least 6 completed cases are needed for active DOE suggestion")

    lower = np.array([space[name][0] for name in PARAM_NAMES], dtype=float)
    upper = np.array([space[name][1] for name in PARAM_NAMES], dtype=float)
    x = df[list(PARAM_NAMES)].astype(float).to_numpy()
    x_norm = (x - lower) / (upper - lower)
    y = normalized_utility(df, maximize, minimize)

    length_scale_grid = np.array([0.15, 0.25, 0.35, 0.5, 0.75, 1.0])
    gp = fit_gp(x_norm, y, length_scale_grid, sigma_n=args.gp_noise_std)

    sampler = qmc.Sobol(d=len(PARAM_NAMES), scramble=True, seed=args.seed)
    unit = sampler.random_base2(m=int(np.ceil(np.log2(args.pool_size))))
    pool = qmc.scale(unit, lower, upper)[: args.pool_size]
    pool = pool[feasible_array(pool)]
    pool = snap_array(pool, args.grid_step_nm)
    pool = np.unique(pool, axis=0)
    pool = pool[feasible_array(pool)]

    existing = snap_array(x, args.grid_step_nm)
    keep = []
    for point in pool:
        distance = np.sqrt(((existing - point) ** 2).sum(axis=1)).min()
        keep.append(distance >= args.min_distance_nm)
    pool = pool[np.array(keep, dtype=bool)]
    if len(pool) == 0:
        raise ValueError("no feasible active DOE candidates remain after filtering")

    pool_norm = (pool - lower) / (upper - lower)
    pred_mean, pred_std = gp_predict(gp, pool_norm)
    std_scale = pred_std.max() if pred_std.max() > 0 else 1.0
    score = pred_mean + args.exploration_weight * pred_std / std_scale  # GP-UCB acquisition

    order = np.argsort(score)[::-1][: args.batch_size]
    selected = pool[order]
    result = pd.DataFrame(selected, columns=PARAM_NAMES)
    result.insert(0, "case_id", [f"AC{i:03d}" for i in range(1, len(result) + 1)])
    result.insert(1, "case_group", "active_doe")
    result.insert(2, "structure", "proposed")
    result.insert(3, "active_doe_mode", args.mode)
    result["acquisition_score"] = score[order]
    result["predicted_utility"] = pred_mean[order]
    result["surrogate_uncertainty"] = pred_std[order]
    result["grid_step_nm"] = args.grid_step_nm
    result["grid_snapped"] = True
    result["status"] = "not_started"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(
        f"saved: {args.output} ({len(result)} active DOE suggestions, "
        f"GP length_scale={gp['length_scale']:.3f}, sigma_f={gp['sigma_f']:.3f})"
    )


if __name__ == "__main__":
    main()
