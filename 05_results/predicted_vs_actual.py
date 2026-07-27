from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict:
    with (ROOT / "project.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalized_utility(df: pd.DataFrame, maximize: list[str], minimize: list[str]) -> np.ndarray:
    """Same scalarization as 03_doe/suggest_active_cases.py, applied to the
    matched actual-result subset so the actual utility is comparable to the
    predicted utility that GP-UCB scored."""
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


def pearson_r(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def spearman_r(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2:
        return float("nan")
    return pearson_r(pd.Series(a).rank().to_numpy(), pd.Series(b).rank().to_numpy())


def main() -> None:
    cfg = load_config()
    active_cfg = cfg.get("active_doe", {})
    validation_cfg = cfg.get("surrogate_validation", {})

    parser = argparse.ArgumentParser(
        description=(
            "Compare GP-UCB active DOE predicted_utility against the actual TCAD result "
            "once suggested cases are run, as a surrogate-model calibration check."
        )
    )
    parser.add_argument(
        "--suggested",
        type=Path,
        default=ROOT / active_cfg.get("output", "03_doe/cases/active_suggested_cases.csv"),
        help="active_suggested_cases.csv containing predicted_utility/surrogate_uncertainty",
    )
    parser.add_argument(
        "--actual",
        type=Path,
        default=ROOT / "05_results/summary/all_results.csv",
        help="accumulated TCAD result CSV; must contain rows for the same case_id values",
    )
    parser.add_argument(
        "--mode",
        choices=["device_screening", "circuit_dtco"],
        default=None,
        help="objective set to recompute actual utility with; default inferred from --suggested's active_doe_mode column",
    )
    parser.add_argument(
        "--min-matched-cases",
        type=int,
        default=int(validation_cfg.get("min_matched_cases", 3)),
    )
    parser.add_argument("--ci-z-score", type=float, default=float(validation_cfg.get("ci_z_score", 1.96)))
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / validation_cfg.get("output", "05_results/summary/predicted_vs_actual.csv"),
    )
    args = parser.parse_args()

    suggested = pd.read_csv(args.suggested)
    needed_suggested = {"case_id", "predicted_utility", "surrogate_uncertainty"}
    missing = needed_suggested - set(suggested.columns)
    if missing:
        raise ValueError(f"--suggested input is missing columns: {sorted(missing)}")

    mode = args.mode
    if mode is None:
        if "active_doe_mode" in suggested.columns and suggested["active_doe_mode"].notna().any():
            modes_present = suggested["active_doe_mode"].dropna().unique().tolist()
            if len(modes_present) > 1:
                raise ValueError(
                    f"--suggested mixes active_doe_mode values {modes_present}; pass --mode explicitly"
                )
            mode = str(modes_present[0])
        else:
            mode = active_cfg.get("default_mode", "device_screening")

    mode_cfg = active_cfg.get("modes", {}).get(mode, {})
    objective_cfg = mode_cfg.get("objectives", {})
    maximize = list(objective_cfg.get("maximize", []))
    minimize = list(objective_cfg.get("minimize", []))
    if not maximize and not minimize:
        raise ValueError(f"no active_doe objectives configured for mode={mode}")

    actual = pd.read_csv(args.actual)
    needed_actual = {"case_id", *maximize, *minimize}
    missing = needed_actual - set(actual.columns)
    if missing:
        raise ValueError(f"--actual input is missing columns: {sorted(missing)}")

    merged = suggested.merge(actual[list(needed_actual)], on="case_id", how="inner")
    merged = merged.dropna(subset=[*maximize, *minimize])
    if len(merged) < args.min_matched_cases:
        raise ValueError(
            f"only {len(merged)} suggested case_id(s) have a matching row in {args.actual} "
            f"(need >= {args.min_matched_cases}); run the active-DOE-suggested cases in TCAD "
            "and log them into all_results.csv before validating the surrogate"
        )

    merged["actual_utility"] = normalized_utility(merged, maximize, minimize)
    merged["prediction_error"] = merged["actual_utility"] - merged["predicted_utility"]
    ci_half_width = args.ci_z_score * merged["surrogate_uncertainty"]
    merged["within_predicted_ci"] = merged["prediction_error"].abs() <= ci_half_width

    residual = merged["prediction_error"].to_numpy()
    rmse = float(np.sqrt(np.mean(residual**2)))
    mae = float(np.mean(np.abs(residual)))
    r_pearson = pearson_r(merged["predicted_utility"].to_numpy(), merged["actual_utility"].to_numpy())
    r_spearman = spearman_r(merged["predicted_utility"].to_numpy(), merged["actual_utility"].to_numpy())
    ci_coverage_pct = float(merged["within_predicted_ci"].mean() * 100.0)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.output, index=False)

    print(f"saved: {args.output} ({len(merged)} matched cases, mode={mode})")
    print(
        f"pearson_r={r_pearson:.3f} spearman_r={r_spearman:.3f} "
        f"rmse={rmse:.4f} mae={mae:.4f} "
        f"predicted_ci_coverage={ci_coverage_pct:.1f}% (target ~95% at z={args.ci_z_score})"
    )


if __name__ == "__main__":
    main()
