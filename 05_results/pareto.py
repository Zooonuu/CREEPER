from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def pareto_mask(values: np.ndarray) -> np.ndarray:
    mask = np.ones(len(values), dtype=bool)
    for i in range(len(values)):
        if np.any(
            np.all(values <= values[i], axis=1)
            & np.any(values < values[i], axis=1)
        ):
            mask[i] = False
    return mask


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--objectives", nargs="+", help="Backward-compatible minimization objectives.")
    parser.add_argument("--minimize", nargs="*", default=[])
    parser.add_argument("--maximize", nargs="*", default=[])
    parser.add_argument("--output", type=Path, default=Path("05_results/summary/pareto.csv"))
    args = parser.parse_args()

    minimize = list(args.minimize)
    maximize = list(args.maximize)
    if args.objectives:
        minimize.extend(args.objectives)
    if not minimize and not maximize:
        raise ValueError("provide --minimize/--maximize or backward-compatible --objectives")

    columns = minimize + maximize
    df = pd.read_csv(args.input).dropna(subset=columns)
    values = []
    if minimize:
        values.append(df[minimize].to_numpy(float))
    if maximize:
        values.append(-df[maximize].to_numpy(float))
    objective_values = np.column_stack(values)

    result = df.loc[pareto_mask(objective_values)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"saved: {args.output}")


if __name__ == "__main__":
    main()
