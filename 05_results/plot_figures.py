from __future__ import annotations

import argparse
import os
from collections.abc import Iterable
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]

COLUMN_ALIASES = {
    "case_id": ("case_id", "Case ID", "case", "Case"),
    "l_sp_s_nm": ("l_sp_s_nm", "L_sp_S", "L_sp_S_nm", "l_sp_s"),
    "l_sp_d_nm": ("l_sp_d_nm", "L_sp_D", "L_sp_D_nm", "l_sp_d"),
    "w_low_k_nm": ("w_low_k_nm", "W_low_k", "W_low_k_nm", "w_low_k"),
    "ion_A": ("ion_A", "Ion", "Ion_A", "ion"),
    "ioff_A": ("ioff_A", "Ioff", "Ioff_A", "ioff"),
    "ss_mV_dec": ("ss_mV_dec", "SS", "SS_mV_dec", "ss"),
    "dibl_mV_V": ("dibl_mV_V", "DIBL", "DIBL_mV_V", "dibl"),
    "cgd_F": ("cgd_F", "Cgd", "Cgd_F", "cgd"),
    "delay_s": ("delay_s", "Delay", "delay", "fo4_delay_s", "FO4_delay"),
    "power_W": ("power_W", "Power", "power", "average_power_W", "avg_power_W"),
    "energy_J": ("energy_J", "Energy", "energy", "energy_per_transition_J"),
    "edp_Js": ("edp_Js", "EDP", "edp"),
}

LABELS = {
    "l_sp_s_nm": "L_sp_S (nm)",
    "l_sp_d_nm": "L_sp_D (nm)",
    "w_low_k_nm": "W_low_k (nm)",
    "ion_A": "Ion (A)",
    "ioff_A": "Ioff (A)",
    "ss_mV_dec": "SS (mV/dec)",
    "dibl_mV_V": "DIBL (mV/V)",
    "cgd_F": "Cgd (F)",
    "delay_s": "Delay (s)",
    "power_W": "Power (W)",
    "energy_J": "Energy (J)",
    "edp_Js": "EDP (J*s)",
    "ion_retention_min_pct": "Worst Ion retention (%)",
    "cgd_reduction_retention_min_pct": "Worst Cgd improvement retained (%)",
    "compensation_min_pct": "Worst compensation (%)",
    "edp_degradation_max_pct": "Worst EDP degradation (%)",
    "robust_score": "Robust score",
    "predicted_utility": "Predicted utility (GP-UCB mean)",
    "actual_utility": "Actual utility (TCAD)",
    "surrogate_uncertainty": "GP predicted std",
}

DEFAULT_HEATMAP_METRICS = (
    "ion_A",
    "cgd_F",
    "edp_Js",
    "delay_s",
    "power_W",
    "ss_mV_dec",
    "dibl_mV_V",
)


def load_config() -> dict:
    path = ROOT / "project.yaml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_column(df: pd.DataFrame, canonical: str, required: bool = False) -> str | None:
    names = COLUMN_ALIASES.get(canonical, (canonical,))
    for name in names:
        if name in df.columns:
            return name
    if required:
        raise ValueError(f"missing required column for {canonical}: tried {list(names)}")
    return None


def resolve_metric(df: pd.DataFrame, name: str) -> str | None:
    if name in df.columns:
        return name
    canonical = name if name in COLUMN_ALIASES else None
    if canonical is not None:
        return resolve_column(df, canonical)
    for key in COLUMN_ALIASES:
        column = resolve_column(df, key)
        if column is not None and name.lower() in {key.lower(), column.lower()}:
            return column
    return None


def label_for(column: str) -> str:
    for canonical, aliases in COLUMN_ALIASES.items():
        if column == canonical or column in aliases:
            return LABELS.get(canonical, column)
    return LABELS.get(column, column)


def output_path(output_dir: Path, stem: str, file_format: str) -> Path:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in stem).strip("_")
    return output_dir / f"{safe}.{file_format}"


def save(fig: plt.Figure, output_dir: Path, stem: str, file_format: str, dpi: int) -> Path:
    path = output_path(output_dir, stem, file_format)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    return path


def numeric_frame(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    result = df.copy()
    for column in columns:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    return result.dropna(subset=list(columns))


def auto_heatmap_metrics(df: pd.DataFrame) -> list[str]:
    metrics = []
    for metric in DEFAULT_HEATMAP_METRICS:
        column = resolve_column(df, metric)
        if column is not None:
            metrics.append(column)
    return metrics


def setup_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#333333",
            "axes.grid": True,
            "grid.color": "#d8d8d8",
            "grid.linewidth": 0.6,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "legend.frameon": False,
        }
    )


def plot_response_map(
    df: pd.DataFrame,
    metric: str,
    output_dir: Path,
    file_format: str,
    dpi: int,
) -> Path | None:
    x_col = resolve_column(df, "l_sp_s_nm", required=True)
    y_col = resolve_column(df, "l_sp_d_nm", required=True)
    w_col = resolve_column(df, "w_low_k_nm")
    data = numeric_frame(df, [x_col, y_col, metric])
    if len(data) < 3:
        return None

    fig, ax = plt.subplots(figsize=(6.4, 5.2), constrained_layout=True)
    x = data[x_col].to_numpy(float)
    y = data[y_col].to_numpy(float)
    z = data[metric].to_numpy(float)

    unique_xy = np.unique(np.column_stack([x, y]), axis=0)
    can_triangulate = len(unique_xy) >= 3 and np.ptp(x) > 0 and np.ptp(y) > 0
    if can_triangulate:
        try:
            triangulation = mtri.Triangulation(x, y)
            contour = ax.tricontourf(triangulation, z, levels=14, cmap="viridis")
            fig.colorbar(contour, ax=ax, label=label_for(metric))
        except RuntimeError:
            can_triangulate = False

    if not can_triangulate:
        scatter = ax.scatter(x, y, c=z, cmap="viridis", s=56, edgecolor="white", linewidth=0.6)
        fig.colorbar(scatter, ax=ax, label=label_for(metric))
    else:
        ax.scatter(x, y, s=24, c="white", edgecolor="#222222", linewidth=0.6)

    if w_col is not None and w_col in data.columns:
        w = pd.to_numeric(data[w_col], errors="coerce")
        if w.notna().any():
            for _, row in data.dropna(subset=[w_col]).iterrows():
                ax.annotate(
                    f"{float(row[w_col]):.1f}",
                    (float(row[x_col]), float(row[y_col])),
                    textcoords="offset points",
                    xytext=(4, 4),
                    fontsize=7,
                    color="#333333",
                )

    ax.set_title(f"{label_for(metric)} response map")
    ax.set_xlabel(label_for(x_col))
    ax.set_ylabel(label_for(y_col))
    return save(fig, output_dir, f"heatmap_{metric}", file_format, dpi)


def plot_tradeoffs(
    df: pd.DataFrame,
    output_dir: Path,
    file_format: str,
    dpi: int,
) -> list[Path]:
    paths = []
    ion = resolve_column(df, "ion_A")
    cgd = resolve_column(df, "cgd_F")
    edp = resolve_column(df, "edp_Js")
    wlk = resolve_column(df, "w_low_k_nm")

    pairs = []
    if cgd is not None and ion is not None:
        pairs.append((cgd, ion, "tradeoff_cgd_vs_ion"))
    if cgd is not None and edp is not None:
        pairs.append((cgd, edp, "tradeoff_cgd_vs_edp"))
    if ion is not None and edp is not None:
        pairs.append((ion, edp, "tradeoff_ion_vs_edp"))

    for x_col, y_col, stem in pairs:
        color_col = wlk if wlk is not None else None
        columns = [x_col, y_col] + ([color_col] if color_col else [])
        data = numeric_frame(df, columns)
        if data.empty:
            continue

        fig, ax = plt.subplots(figsize=(6.2, 4.8), constrained_layout=True)
        if color_col:
            scatter = ax.scatter(
                data[x_col],
                data[y_col],
                c=data[color_col],
                cmap="plasma",
                s=58,
                edgecolor="white",
                linewidth=0.7,
            )
            fig.colorbar(scatter, ax=ax, label=label_for(color_col))
        else:
            ax.scatter(data[x_col], data[y_col], s=58, color="#2f80ed", edgecolor="white", linewidth=0.7)

        ax.set_title(f"{label_for(y_col)} vs {label_for(x_col)}")
        ax.set_xlabel(label_for(x_col))
        ax.set_ylabel(label_for(y_col))
        paths.append(save(fig, output_dir, stem, file_format, dpi))
    return paths


def plot_pareto_front(
    all_df: pd.DataFrame,
    pareto_df: pd.DataFrame,
    objectives: list[str] | None,
    output_dir: Path,
    file_format: str,
    dpi: int,
) -> Path | None:
    if objectives is None:
        candidates = [("cgd_F", "edp_Js"), ("cgd_F", "ion_A"), ("delay_s", "power_W")]
        for left, right in candidates:
            x_col = resolve_column(all_df, left)
            y_col = resolve_column(all_df, right)
            if x_col is not None and y_col is not None:
                objectives = [x_col, y_col]
                break
    else:
        objectives = [resolve_metric(all_df, item) for item in objectives]

    if objectives is None or any(item is None for item in objectives):
        return None

    x_col, y_col = objectives
    all_data = numeric_frame(all_df, [x_col, y_col])
    pareto_data = numeric_frame(pareto_df, [x_col, y_col])
    if all_data.empty or pareto_data.empty:
        return None

    fig, ax = plt.subplots(figsize=(6.2, 4.8), constrained_layout=True)
    ax.scatter(all_data[x_col], all_data[y_col], s=42, color="#b8b8b8", label="All cases")
    ax.scatter(
        pareto_data[x_col],
        pareto_data[y_col],
        s=70,
        color="#d94f45",
        edgecolor="white",
        linewidth=0.8,
        label="Pareto candidates",
    )
    ax.set_title("Pareto front")
    ax.set_xlabel(label_for(x_col))
    ax.set_ylabel(label_for(y_col))
    ax.legend()
    return save(fig, output_dir, f"pareto_{x_col}_vs_{y_col}", file_format, dpi)


def plot_robust_summary(
    df: pd.DataFrame,
    output_dir: Path,
    file_format: str,
    dpi: int,
    guardrails: dict,
) -> list[Path]:
    case_col = "base_case_id" if "base_case_id" in df.columns else df.columns[0]
    score_cols = [
        col
        for col in (
            "ion_retention_min_pct",
            "cgd_reduction_retention_min_pct",
            "compensation_min_pct",
            "robust_score",
        )
        if col in df.columns
    ]
    degradation_col = "edp_degradation_max_pct" if "edp_degradation_max_pct" in df.columns else None
    paths = []

    if score_cols:
        data = df[[case_col, *score_cols]].copy()
        for column in score_cols:
            data[column] = pd.to_numeric(data[column], errors="coerce")
        data = data.dropna(how="all", subset=score_cols)
        if not data.empty:
            fig, ax = plt.subplots(figsize=(8.6, 4.8), constrained_layout=True)
            x = np.arange(len(data))
            width = 0.78 / len(score_cols)
            for index, column in enumerate(score_cols):
                offset = (index - (len(score_cols) - 1) / 2) * width
                ax.bar(x + offset, data[column], width=width, label=label_for(column))

            min_ion = guardrails.get("min_ion_retention_pct")
            min_cgd = guardrails.get("min_cgd_reduction_retention_pct")
            min_comp = guardrails.get("min_compensation_pct")
            for value, color, name in (
                (min_ion, "#2e7d32", "Ion guardrail"),
                (min_cgd, "#1565c0", "Cgd guardrail"),
                (min_comp, "#6a1b9a", "Comp. guardrail"),
            ):
                if value is not None:
                    ax.axhline(float(value), color=color, linestyle="--", linewidth=1.0, alpha=0.6)
                    ax.text(len(data) - 0.5, float(value), name, color=color, fontsize=8, va="bottom")

            ax.set_title("Robust defense and compensation")
            ax.set_xlabel("Base case")
            ax.set_ylabel("Percent or score")
            ax.set_xticks(x)
            ax.set_xticklabels(data[case_col].astype(str), rotation=35, ha="right")
            ax.set_ylim(bottom=0)
            ax.legend(ncols=2)
            paths.append(save(fig, output_dir, "robust_defense_compensation", file_format, dpi))

    if degradation_col is not None:
        data = df[[case_col, degradation_col]].copy()
        data[degradation_col] = pd.to_numeric(data[degradation_col], errors="coerce")
        data = data.dropna(subset=[degradation_col])
        if not data.empty:
            fig, ax = plt.subplots(figsize=(7.2, 4.4), constrained_layout=True)
            colors = np.where(data[degradation_col] <= float(guardrails.get("max_edp_degradation_pct", np.inf)), "#3f8f6b", "#d94f45")
            ax.bar(data[case_col].astype(str), data[degradation_col], color=colors)
            max_edp = guardrails.get("max_edp_degradation_pct")
            if max_edp is not None:
                ax.axhline(float(max_edp), color="#333333", linestyle="--", linewidth=1.0, label="EDP guardrail")
                ax.legend()
            ax.set_title("Worst-case EDP degradation")
            ax.set_xlabel("Base case")
            ax.set_ylabel(label_for(degradation_col))
            ax.tick_params(axis="x", rotation=35)
            ax.set_ylim(bottom=0)
            paths.append(save(fig, output_dir, "robust_edp_degradation", file_format, dpi))

    return paths


def plot_predicted_vs_actual(
    df: pd.DataFrame,
    output_dir: Path,
    file_format: str,
    dpi: int,
) -> Path | None:
    if "predicted_utility" not in df.columns or "actual_utility" not in df.columns:
        return None
    has_uncertainty = "surrogate_uncertainty" in df.columns
    columns = ["predicted_utility", "actual_utility"] + (["surrogate_uncertainty"] if has_uncertainty else [])
    data = numeric_frame(df, columns)
    if data.empty:
        return None

    fig, ax = plt.subplots(figsize=(5.6, 5.6), constrained_layout=True)
    if has_uncertainty:
        ax.errorbar(
            data["predicted_utility"],
            data["actual_utility"],
            xerr=1.96 * data["surrogate_uncertainty"],
            fmt="o",
            color="#2f80ed",
            ecolor="#9fc1f5",
            elinewidth=1.2,
            capsize=3,
            markersize=6,
            markeredgecolor="white",
            label="Active DOE case (95% CI)",
        )
    else:
        ax.scatter(
            data["predicted_utility"],
            data["actual_utility"],
            s=58,
            color="#2f80ed",
            edgecolor="white",
            linewidth=0.7,
            label="Active DOE case",
        )

    lo = float(min(data["predicted_utility"].min(), data["actual_utility"].min()))
    hi = float(max(data["predicted_utility"].max(), data["actual_utility"].max()))
    pad = (hi - lo) * 0.08 if hi > lo else 0.05
    ax.plot(
        [lo - pad, hi + pad],
        [lo - pad, hi + pad],
        color="#d94f45",
        linestyle="--",
        linewidth=1.2,
        label="Predicted = Actual",
    )
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_title("GP-UCB surrogate: predicted vs actual TCAD utility")
    ax.set_xlabel(label_for("predicted_utility"))
    ax.set_ylabel(label_for("actual_utility"))
    ax.legend()
    return save(fig, output_dir, "predicted_vs_actual_utility", file_format, dpi)


def read_optional_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate publication-ready figures from DOE and robust validation CSV files."
    )
    parser.add_argument("--all-metrics", type=Path, default=ROOT / "05_results/summary/all_metrics.csv")
    parser.add_argument("--pareto", type=Path, default=ROOT / "05_results/summary/pareto.csv")
    parser.add_argument("--robust-optimum", type=Path, default=ROOT / "05_results/summary/robust_optimum.csv")
    parser.add_argument(
        "--predicted-vs-actual", type=Path, default=ROOT / "05_results/summary/predicted_vs_actual.csv"
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "05_results/figures")
    parser.add_argument("--heatmap-metrics", nargs="*", help="Metric columns to draw as response maps.")
    parser.add_argument("--pareto-objectives", nargs=2, help="Two objective columns to use for the Pareto plot.")
    parser.add_argument("--format", choices=("png", "pdf", "svg"), default="png")
    parser.add_argument("--dpi", type=int, default=220)
    args = parser.parse_args()

    setup_style()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_config()
    guardrails = cfg.get("robust_validation", {}).get("guardrails", {})

    written: list[Path] = []
    all_df = read_optional_csv(args.all_metrics)
    pareto_df = read_optional_csv(args.pareto)
    robust_df = read_optional_csv(args.robust_optimum)
    pva_df = read_optional_csv(args.predicted_vs_actual)

    if all_df is not None:
        requested_metrics = args.heatmap_metrics or auto_heatmap_metrics(all_df)
        for metric_name in requested_metrics:
            metric = resolve_metric(all_df, metric_name)
            if metric is None:
                print(f"skip heatmap metric: {metric_name} (missing column)")
                continue
            path = plot_response_map(all_df, metric, args.output_dir, args.format, args.dpi)
            if path is not None:
                written.append(path)
        written.extend(plot_tradeoffs(all_df, args.output_dir, args.format, args.dpi))

    if all_df is not None and pareto_df is not None:
        path = plot_pareto_front(
            all_df,
            pareto_df,
            args.pareto_objectives,
            args.output_dir,
            args.format,
            args.dpi,
        )
        if path is not None:
            written.append(path)

    if robust_df is not None:
        written.extend(plot_robust_summary(robust_df, args.output_dir, args.format, args.dpi, guardrails))

    if pva_df is not None:
        path = plot_predicted_vs_actual(pva_df, args.output_dir, args.format, args.dpi)
        if path is not None:
            written.append(path)

    if not written:
        print(
            "no figures generated; provide all_metrics.csv, pareto.csv, robust_optimum.csv, "
            "or predicted_vs_actual.csv"
        )
        return

    print("generated figures:")
    for path in written:
        print(f" - {path}")


if __name__ == "__main__":
    main()
