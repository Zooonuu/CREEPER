from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from scipy.stats import qmc

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with (ROOT / "project.yaml").open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    doe_cfg = cfg.get("doe", {})
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=doe_cfg.get("initial_samples", 24))
    parser.add_argument("--method", choices=["lhs", "sobol"], default=doe_cfg.get("method", "lhs"))
    parser.add_argument("--seed", type=int, default=doe_cfg.get("seed", 20260723))
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / doe_cfg.get("output", "03_doe/cases/initial_doe_cases.csv"),
    )
    args = parser.parse_args()

    space = cfg["design_space"]
    names = ["l_sp_s_nm", "l_sp_d_nm", "w_low_k_nm"]
    lower = np.array([space[n][0] for n in names], dtype=float)
    upper = np.array([space[n][1] for n in names], dtype=float)

    accepted = []
    attempt = 0
    while len(accepted) < args.samples and attempt < 20:
        attempt += 1
        if args.method == "lhs":
            sampler = qmc.LatinHypercube(d=3, seed=args.seed + attempt)
            unit = sampler.random(max(64, args.samples * 4))
        else:
            sampler = qmc.Sobol(d=3, scramble=True, seed=args.seed + attempt)
            unit = sampler.random(max(64, args.samples * 4))

        for row in qmc.scale(unit, lower, upper):
            lss, lsd, wlk = row
            if lsd < lss or wlk > lsd:
                continue
            accepted.append(row)
            if len(accepted) == args.samples:
                break

    if len(accepted) < args.samples:
        raise RuntimeError("Feasible cases could not be generated.")

    df = pd.DataFrame(accepted, columns=names)
    df.insert(0, "case_id", [f"C{i:03d}" for i in range(1, len(df) + 1)])
    df.insert(1, "case_group", "initial_doe")
    df.insert(2, "structure", "proposed")
    df["grid_snapped"] = False
    df["status"] = "not_started"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"saved: {args.output} ({len(df)} cases)")


if __name__ == "__main__":
    main()
