from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
EPS = 1e-9


def load_config() -> dict:
    with (ROOT / "project.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def require_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def optional_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None
    return float(value)


def nominal_row(group: pd.DataFrame, variation_col: str) -> pd.Series:
    nominal = group[group[variation_col].astype(str).str.lower() == "nominal"]
    if nominal.empty:
        raise ValueError(f"base_case_id={group.iloc[0]['base_case_id']} has no nominal row")
    return nominal.iloc[0]


def pct_change(values: pd.Series, nominal: float) -> pd.Series:
    if nominal == 0:
        return pd.Series(np.nan, index=values.index)
    return (values.astype(float) / nominal - 1.0) * 100.0


def pct_retention(values: pd.Series, nominal: float) -> pd.Series:
    if nominal == 0:
        return pd.Series(np.nan, index=values.index)
    return values.astype(float) / nominal * 100.0


def add_limit_check(
    checks: dict[str, pd.Series],
    name: str,
    values: pd.Series,
    limit: float | None,
    direction: str,
) -> None:
    if limit is None:
        return
    if direction == "max":
        checks[name] = values <= limit + EPS
    elif direction == "min":
        checks[name] = values + EPS >= limit
    else:
        raise ValueError(f"unknown direction: {direction}")


def main() -> None:
    cfg = load_config()
    robust_metrics = cfg.get("robust_validation", {}).get("metrics", {})
    yield_cfg = cfg.get("yield_like", {})
    specs = yield_cfg.get("specs", {})

    parser = argparse.ArgumentParser(
        description="Compute spec pass-rate metrics from robust variation samples."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / yield_cfg.get("output", "05_results/summary/yield_like.csv"))
    parser.add_argument("--base-col", default="base_case_id")
    parser.add_argument("--variation-col", default="variation_kind")
    parser.add_argument("--ion-col", default=robust_metrics.get("ion", "ion_A"))
    parser.add_argument("--cgd-col", default=robust_metrics.get("cgd", "cgd_F"))
    parser.add_argument("--edp-col", default=robust_metrics.get("edp", "edp_Js"))
    parser.add_argument("--delay-col", default=robust_metrics.get("delay", "fo4_delay_s"))
    parser.add_argument("--average-power-col", default=robust_metrics.get("average_power", "average_power_W"))
    parser.add_argument("--energy-col", default=robust_metrics.get("energy", "energy_per_transition_J"))
    parser.add_argument("--max-edp-degradation-pct", type=float, default=optional_float(specs.get("max_edp_degradation_pct")))
    parser.add_argument(
        "--max-fo4-delay-degradation-pct",
        type=float,
        default=optional_float(specs.get("max_fo4_delay_degradation_pct")),
    )
    parser.add_argument(
        "--max-average-power-degradation-pct",
        type=float,
        default=optional_float(specs.get("max_average_power_degradation_pct")),
    )
    parser.add_argument(
        "--max-energy-degradation-pct",
        type=float,
        default=optional_float(specs.get("max_energy_degradation_pct")),
    )
    parser.add_argument("--min-ion-retention-pct", type=float, default=optional_float(specs.get("min_ion_retention_pct")))
    parser.add_argument("--max-cgd-variation-pct", type=float, default=optional_float(specs.get("max_cgd_variation_pct")))
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    required = [args.base_col, args.variation_col, args.ion_col, args.cgd_col, args.edp_col]
    require_columns(df, required, "yield-like input")

    df = df.rename(columns={args.base_col: "base_case_id", args.variation_col: "variation_kind"})
    rows = []

    for base_case_id, group in df.groupby("base_case_id", sort=False):
        nominal = nominal_row(group, "variation_kind")
        samples = group[group["variation_kind"].astype(str).str.lower() != "nominal"].copy()
        if samples.empty:
            continue

        checks: dict[str, pd.Series] = {}
        ion_retention = pct_retention(samples[args.ion_col], float(nominal[args.ion_col]))
        cgd_variation = pct_change(samples[args.cgd_col], float(nominal[args.cgd_col])).abs()
        edp_degradation = pct_change(samples[args.edp_col], float(nominal[args.edp_col]))

        add_limit_check(checks, "ion_retention", ion_retention, args.min_ion_retention_pct, "min")
        add_limit_check(checks, "cgd_variation", cgd_variation, args.max_cgd_variation_pct, "max")
        add_limit_check(checks, "edp_degradation", edp_degradation, args.max_edp_degradation_pct, "max")

        summary = {
            "base_case_id": base_case_id,
            "sample_count": len(samples),
            "nominal_ion": float(nominal[args.ion_col]),
            "nominal_cgd": float(nominal[args.cgd_col]),
            "nominal_edp": float(nominal[args.edp_col]),
            "ion_retention_min_pct": ion_retention.min(),
            "cgd_variation_max_pct": cgd_variation.max(),
            "edp_degradation_max_pct": max(0.0, edp_degradation.max()),
        }

        optional_specs = [
            (args.delay_col, args.max_fo4_delay_degradation_pct, "fo4_delay_degradation"),
            (args.average_power_col, args.max_average_power_degradation_pct, "average_power_degradation"),
            (args.energy_col, args.max_energy_degradation_pct, "energy_degradation"),
        ]
        for col, limit, label in optional_specs:
            if col in samples.columns and pd.notna(nominal.get(col, np.nan)):
                degradation = pct_change(samples[col], float(nominal[col]))
                add_limit_check(checks, label, degradation, limit, "max")
                summary[f"{label}_max_pct"] = max(0.0, degradation.max())
                summary[f"nominal_{col}"] = float(nominal[col])

        if not checks:
            raise ValueError("no yield-like specs are enabled")

        pass_matrix = pd.DataFrame(checks)
        sample_pass = pass_matrix.all(axis=1)
        summary["pass_count"] = int(sample_pass.sum())
        summary["fail_count"] = int((~sample_pass).sum())
        summary["spec_pass_rate_pct"] = float(sample_pass.mean() * 100.0)
        summary["failed_variations"] = ";".join(samples.loc[~sample_pass, "variation_kind"].astype(str))

        for check_name, check_values in checks.items():
            summary[f"{check_name}_pass_rate_pct"] = float(check_values.mean() * 100.0)

        rows.append(summary)

    result = pd.DataFrame(rows)
    if result.empty:
        raise ValueError("no yield-like summaries could be computed")

    result = result.sort_values(
        ["spec_pass_rate_pct", "edp_degradation_max_pct", "ion_retention_min_pct"],
        ascending=[False, True, False],
    ).reset_index(drop=True)
    result.insert(0, "yield_like_rank", np.arange(1, len(result) + 1))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"saved: {args.output}")
    print(f"best yield-like candidate: {result.iloc[0]['base_case_id']} ({result.iloc[0]['spec_pass_rate_pct']:.1f}%)")


if __name__ == "__main__":
    main()
