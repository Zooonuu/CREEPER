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


def pct_ratio(numerator: float, denominator: float) -> float:
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return np.nan
    return numerator / denominator * 100.0


def clipped_pct(value: float) -> float:
    if pd.isna(value):
        return np.nan
    return float(np.clip(value, 0.0, 100.0))


def require_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def reference_row(path: Path | None, case_id: str | None) -> pd.Series | None:
    if path is None:
        return None
    df = pd.read_csv(path)
    if case_id is not None:
        require_columns(df, ["case_id"], "baseline input")
        df = df[df["case_id"].astype(str) == str(case_id)]
    if df.empty:
        raise ValueError("baseline input does not contain a usable reference row")
    return df.iloc[0]


def nominal_row(group: pd.DataFrame, variation_col: str) -> pd.Series:
    nominal = group[group[variation_col].astype(str).str.lower() == "nominal"]
    if nominal.empty:
        raise ValueError(f"base_case_id={group.iloc[0]['base_case_id']} has no nominal row")
    return nominal.iloc[0]


def robust_score(row: pd.Series, guardrails: dict) -> float:
    weighted = []

    min_ion = float(guardrails.get("min_ion_retention_pct", 95.0))
    ion_retention = row.get("ion_retention_min_pct", np.nan)
    if pd.notna(ion_retention) and min_ion > 0:
        weighted.append((30.0, clipped_pct(ion_retention / min_ion * 100.0)))

    max_edp = float(guardrails.get("max_edp_degradation_pct", 10.0))
    edp_degradation = row.get("edp_degradation_max_pct", np.nan)
    if pd.notna(edp_degradation) and max_edp > 0:
        weighted.append((40.0, clipped_pct((1.0 - edp_degradation / max_edp) * 100.0)))

    min_cgd = float(guardrails.get("min_cgd_reduction_retention_pct", 80.0))
    cgd_retention = row.get("cgd_reduction_retention_min_pct", np.nan)
    if pd.notna(cgd_retention) and min_cgd > 0:
        weighted.append((15.0, clipped_pct(cgd_retention / min_cgd * 100.0)))

    min_comp = float(guardrails.get("min_compensation_pct", 70.0))
    compensation = row.get("compensation_min_pct", np.nan)
    if pd.notna(compensation) and min_comp > 0:
        weighted.append((15.0, clipped_pct(compensation / min_comp * 100.0)))

    if not weighted:
        return np.nan
    weight_sum = sum(weight for weight, _ in weighted)
    return sum(weight * score for weight, score in weighted) / weight_sum


def passes_guardrails(row: pd.Series, guardrails: dict) -> bool:
    checks = [
        row.get("ion_retention_min_pct", np.nan)
        + EPS >= float(guardrails.get("min_ion_retention_pct", 95.0)),
        row.get("edp_degradation_max_pct", np.nan)
        <= float(guardrails.get("max_edp_degradation_pct", 10.0)) + EPS,
    ]

    if pd.notna(row.get("cgd_reduction_retention_min_pct", np.nan)):
        checks.append(
            row["cgd_reduction_retention_min_pct"]
            + EPS >= float(guardrails.get("min_cgd_reduction_retention_pct", 80.0))
        )
    if pd.notna(row.get("compensation_min_pct", np.nan)):
        checks.append(row["compensation_min_pct"] + EPS >= float(guardrails.get("min_compensation_pct", 70.0)))

    return bool(all(checks))


def main() -> None:
    cfg = load_config()
    robust_cfg = cfg.get("robust_validation", {})
    metric_cfg = robust_cfg.get("metrics", {})

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--baseline-input", type=Path)
    parser.add_argument("--baseline-case-id")
    parser.add_argument("--output", type=Path, default=ROOT / "05_results/summary/robust_optimum.csv")
    parser.add_argument("--base-col", default="base_case_id")
    parser.add_argument("--variation-col", default="variation_kind")
    parser.add_argument("--ion-col", default=metric_cfg.get("ion", "ion_A"))
    parser.add_argument("--cgd-col", default=metric_cfg.get("cgd", "cgd_F"))
    parser.add_argument("--edp-col", default=metric_cfg.get("edp", "edp_Js"))
    parser.add_argument(
        "--delay-col",
        default=metric_cfg.get("delay", "fo4_delay_s"),
    )
    parser.add_argument("--average-power-col", default=metric_cfg.get("average_power", "average_power_W"))
    parser.add_argument("--energy-col", default=metric_cfg.get("energy", "energy_per_transition_J"))
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    optional_circuit_cols = [
        args.delay_col,
        args.average_power_col,
        args.energy_col,
    ]
    require_columns(
        df,
        [args.base_col, args.variation_col, args.ion_col, args.cgd_col, args.edp_col],
        "robust result input",
    )

    df = df.rename(columns={args.base_col: "base_case_id", args.variation_col: "variation_kind"})
    baseline = reference_row(args.baseline_input, args.baseline_case_id)
    if baseline is not None:
        require_columns(pd.DataFrame([baseline]), [args.ion_col, args.cgd_col], "baseline input")

    summaries = []
    for base_case_id, group in df.groupby("base_case_id", sort=False):
        nominal = nominal_row(group, "variation_kind")
        variations = group[group["variation_kind"].astype(str).str.lower() != "nominal"]
        if variations.empty:
            continue

        ion_nom = float(nominal[args.ion_col])
        cgd_nom = float(nominal[args.cgd_col])
        edp_nom = float(nominal[args.edp_col])

        ion_retention = variations[args.ion_col].astype(float) / ion_nom * 100.0
        cgd_variation = (variations[args.cgd_col].astype(float) / cgd_nom - 1.0).abs() * 100.0
        edp_degradation = (variations[args.edp_col].astype(float) / edp_nom - 1.0) * 100.0

        row = {
            "base_case_id": base_case_id,
            "variation_count": len(variations),
            "ion_retention_min_pct": ion_retention.min(),
            "cgd_variation_max_pct": cgd_variation.max(),
            "edp_degradation_max_pct": max(0.0, edp_degradation.max()),
            "nominal_ion": ion_nom,
            "nominal_cgd": cgd_nom,
            "nominal_edp": edp_nom,
        }

        for col in optional_circuit_cols:
            if col in group.columns and pd.notna(nominal[col]):
                nominal_value = float(nominal[col])
                degradation = (variations[col].astype(float) / nominal_value - 1.0) * 100.0
                row[f"{col}_degradation_max_pct"] = max(0.0, degradation.max())
                row[f"nominal_{col}"] = nominal_value

        if baseline is not None:
            ion_base = float(baseline[args.ion_col])
            cgd_base = float(baseline[args.cgd_col])
            ion_loss_nom = max(0.0, pct_ratio(ion_base - ion_nom, ion_base))
            cgd_reduction_nom = pct_ratio(cgd_base - cgd_nom, cgd_base)

            cgd_gain_nom_abs = cgd_base - cgd_nom
            if cgd_gain_nom_abs > 0:
                cgd_retention = (cgd_base - variations[args.cgd_col].astype(float)) / cgd_gain_nom_abs * 100.0
                row["cgd_reduction_retention_min_pct"] = cgd_retention.min()
            else:
                row["cgd_reduction_retention_min_pct"] = np.nan

            if cgd_reduction_nom > 0:
                row["compensation_nominal_pct"] = clipped_pct(
                    (1.0 - ion_loss_nom / cgd_reduction_nom) * 100.0
                )
                ion_loss_worst = max(0.0, pct_ratio(ion_base - variations[args.ion_col].astype(float).min(), ion_base))
                cgd_reduction_worst = pct_ratio(cgd_base - variations[args.cgd_col].astype(float).max(), cgd_base)
                row["compensation_min_pct"] = clipped_pct(
                    (1.0 - ion_loss_worst / cgd_reduction_worst) * 100.0
                    if cgd_reduction_worst > 0
                    else np.nan
                )
            else:
                row["compensation_nominal_pct"] = np.nan
                row["compensation_min_pct"] = np.nan

            row["ion_loss_nominal_pct"] = ion_loss_nom
            row["cgd_reduction_nominal_pct"] = cgd_reduction_nom
        else:
            row["cgd_reduction_retention_min_pct"] = np.nan
            row["compensation_nominal_pct"] = np.nan
            row["compensation_min_pct"] = np.nan
            row["ion_loss_nominal_pct"] = np.nan
            row["cgd_reduction_nominal_pct"] = np.nan

        summaries.append(row)

    result = pd.DataFrame(summaries)
    if result.empty:
        raise ValueError("no robust summaries could be computed")

    guardrails = robust_cfg.get("guardrails", {})
    result["passes_guardrails"] = result.apply(lambda row: passes_guardrails(row, guardrails), axis=1)
    result["robust_score"] = result.apply(lambda row: robust_score(row, guardrails), axis=1)
    result = result.sort_values(
        ["passes_guardrails", "robust_score", "edp_degradation_max_pct", "ion_retention_min_pct"],
        ascending=[False, False, True, False],
    ).reset_index(drop=True)
    result.insert(0, "robust_rank", np.arange(1, len(result) + 1))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"saved: {args.output}")
    print(f"robust optimum candidate: {result.iloc[0]['base_case_id']}")


if __name__ == "__main__":
    main()
