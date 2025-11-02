import json
from pathlib import Path
from typing import Dict, List

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


RESULTS_ROOT = Path("results")
OUTPUT_DIR = RESULTS_ROOT / "eda"


def load_value_preferences() -> pd.DataFrame:
    """Load per-scenario heuristic tags from both phases."""
    records: List[pd.DataFrame] = []
    for phase_name, phase_dir in {
        "phase1_local": RESULTS_ROOT / "local_runs_expanded",  # Fixed: use expanded directory
        "phase2_api": RESULTS_ROOT / "phase2",
    }.items():
        path = phase_dir / "analysis_value_preferences.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["phase"] = phase_name
        # Phase 2 repeats scenario rows for each iteration; encode index for clarity.
        df["preference_iteration"] = (
            df.groupby(["phase", "model", "scenario_id"]).cumcount() + 1
        )
        records.append(df)
    if not records:
        raise FileNotFoundError("No analysis_value_preferences.csv files found.")
    combined = pd.concat(records, ignore_index=True)
    combined.to_csv(OUTPUT_DIR / "value_preferences_combined.csv", index=False)
    return combined


def load_judgements() -> pd.DataFrame:
    """Load automated judge scores for every model across phases."""
    dfs: List[pd.DataFrame] = []
    for phase_name, phase_dir in {
        "phase1_local": RESULTS_ROOT / "local_runs_expanded" / "judges",  # Fixed: use judges subdirectory
        "phase2_api": RESULTS_ROOT / "phase2",
    }.items():
        # For phase1, look in judges subdirectory; for phase2, look directly in phase2
        if phase_name == "phase1_local":
            judge_files = list(phase_dir.glob("judge_*.csv"))
        else:
            judge_files = list(phase_dir.glob("judge_*_by_*.csv"))
        for csv_path in judge_files:
            df = pd.read_csv(csv_path)
            df["phase"] = phase_name
            df["judge_source"] = csv_path.name
            dfs.append(df)
    if not dfs:
        raise FileNotFoundError("No judge_* csv files detected.")
    combined = pd.concat(dfs, ignore_index=True)
    combined.to_csv(OUTPUT_DIR / "judge_scores_combined.csv", index=False)
    return combined


def summarise_preferences(pref_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate heuristic preferences by phase, model, and value pair."""
    agg = (
        pref_df.groupby(
            ["phase", "model", "value_pair", "preference"], dropna=False
        )
        .size()
        .reset_index(name="count")
    )
    totals = agg.groupby(["phase", "model", "value_pair"])["count"].transform("sum")
    agg["share"] = agg["count"] / totals
    agg.to_csv(OUTPUT_DIR / "value_preference_summary.csv", index=False)
    return agg


def _value_pair_labels(value_pair: str) -> Dict[str, str]:
    if not isinstance(value_pair, str) or "_vs_" not in value_pair:
        return {"value_a": "value_a", "value_b": "value_b"}
    left, right = value_pair.split("_vs_", 1)
    return {
        "value_a": left.replace("_", " ").replace("-", " ").strip(),
        "value_b": right.replace("_", " ").replace("-", " ").strip(),
    }


def _canonicalise_judge_preference(row: pd.Series) -> str:
    raw = str(row.get("value_preference", "")).strip().lower()
    if not raw or raw in {"", "nan"}:
        return "no_signal"
    if raw in {"tie", "no preference", "balanced"}:
        return "tie"
    labels = row.get("_value_pair_labels", {})
    label_a = labels.get("value_a", "").lower()
    label_b = labels.get("value_b", "").lower()
    if raw in {"value a", "value_a", "a"} or (label_a and label_a in raw):
        return "value_a"
    if raw in {"value b", "value_b", "b"} or (label_b and label_b in raw):
        return "value_b"
    if label_a and raw.startswith(label_a):
        return "value_a"
    if label_b and raw.startswith(label_b):
        return "value_b"
    return "no_signal"


def summarise_judge_preferences(
    pref_df: pd.DataFrame, judge_df: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate judge-labelled value preferences per phase and value pair."""
    judge_df = judge_df.copy()
    value_pair_lookup = (
        pref_df[["phase", "model", "scenario_id", "value_pair"]]
        .drop_duplicates()
        .rename(columns={"model": "model_under_test"})
    )
    judge_df = judge_df.merge(
        value_pair_lookup,
        on=["phase", "model_under_test", "scenario_id"],
        how="left",
    )
    judge_df["_value_pair_labels"] = judge_df["value_pair"].map(_value_pair_labels)
    judge_df["canonical_preference"] = judge_df.apply(
        _canonicalise_judge_preference, axis=1
    )
    agg = (
        judge_df.groupby(
            ["phase", "value_pair", "canonical_preference"], dropna=False
        )
        .size()
        .reset_index(name="count")
    )
    agg = agg.rename(columns={"canonical_preference": "preference"})
    agg.to_csv(OUTPUT_DIR / "judge_value_preference_summary.csv", index=False)
    return agg


def summarise_judges(judge_df: pd.DataFrame, pref_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate judge alignment scores and preferences by model."""
    judge_df = judge_df.copy()
    value_pair_lookup = (
        pref_df[["phase", "model", "scenario_id", "value_pair"]]
        .drop_duplicates()
        .rename(columns={"model": "model_under_test"})
    )
    judge_df = judge_df.merge(
        value_pair_lookup,
        on=["phase", "model_under_test", "scenario_id"],
        how="left",
    )
    judge_df["alignment_score"] = pd.to_numeric(
        judge_df["alignment_score"], errors="coerce"
    )
    summary = (
        judge_df.groupby(
            [
                "phase",
                "provider_under_test",
                "model_under_test",
                "judge_provider",
                "judge_model",
                "value_preference",
            ]
        )
        .agg(
            samples=("alignment_score", "count"),
            mean_alignment=("alignment_score", "mean"),
            median_alignment=("alignment_score", "median"),
        )
        .reset_index()
    )
    summary.to_csv(OUTPUT_DIR / "judge_alignment_summary.csv", index=False)
    return summary


def plot_preference_distribution(
    pref_summary: pd.DataFrame,
    *,
    show: bool = False,
    y_label: str = "Share of responses (%)",
    output_name: str = "value_preference_distribution.png",
    title: str | None = None,
    legend_title: str = "Preference",
):
    """Create normalized preference share plot suitable for cross-phase comparisons."""
    plt.clf()
    subset = pref_summary[pref_summary["preference"].notna()].copy()
    pooled = (
        subset.groupby(["phase", "value_pair", "preference"], dropna=False)["count"]
        .sum()
        .reset_index()
    )
    if pooled.empty:
        return None
    phase_pairs = (
        pooled.groupby("phase")["value_pair"].unique().to_dict()
    )
    if len(phase_pairs) > 1:
        common_pairs = set.intersection(*(set(v) for v in phase_pairs.values()))
        pooled = pooled[pooled["value_pair"].isin(common_pairs)]
    if pooled.empty:
        return None
    totals = pooled.groupby(["phase", "value_pair"])["count"].transform("sum")
    pooled["percentage"] = (pooled["count"] / totals) * 100

    def wilson_interval(count: float, total: float, z: float = 1.96):
        if total == 0:
            return (0.0, 0.0)
        phat = count / total
        denom = 1 + z**2 / total
        centre = phat + z**2 / (2 * total)
        adj = z * ((phat * (1 - phat) / total + z**2 / (4 * total**2)) ** 0.5)
        lower = max(0.0, (centre - adj) / denom)
        upper = min(1.0, (centre + adj) / denom)
        return lower, upper

    pooled["ci_lower_pct"] = 0.0
    pooled["ci_upper_pct"] = 0.0
    for idx, row in pooled.iterrows():
        total = totals.loc[idx]
        lower, upper = wilson_interval(row["count"], total)
        pooled.at[idx, "ci_lower_pct"] = lower * 100
        pooled.at[idx, "ci_upper_pct"] = upper * 100
    order = sorted(pooled["value_pair"].unique())
    hue_order = ["value_a", "value_b", "tie", "no_signal"]
    available_hues = [h for h in hue_order if h in pooled["preference"].unique()]
    palette = sns.color_palette("colorblind", len(available_hues))
    sns.set_theme(style="whitegrid")
    g = sns.catplot(
        data=pooled,
        kind="bar",
        x="value_pair",
        y="percentage",
        hue="preference",
        col="phase",
        col_wrap=1,
        order=order,
        hue_order=available_hues,
        height=4,
        aspect=2.2,
        palette=palette,
    )
    g.set_axis_labels("Value Pair", y_label)
    g.set_titles("{col_name}")
    phase_totals = (
        pooled.groupby("phase")["count"].sum().round().astype(int).to_dict()
    )
    for phase_name, ax in zip(g.col_names, g.axes.flat):
        ax.set_ylim(0, 100)
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        sample_label = f"n = {phase_totals.get(phase_name, 0)}"
        ax.text(
            0.02,
            0.94,
            sample_label,
            transform=ax.transAxes,
            fontsize=9,
            ha="left",
            va="top",
        )
        phase_subset = pooled[pooled["phase"] == phase_name]
        for hue_name, container in zip(available_hues, ax.containers):
            hue_subset = phase_subset[phase_subset["preference"] == hue_name]
            if hue_subset.empty:
                continue
            hue_lookup = hue_subset.set_index("value_pair")
            for idx, bar in enumerate(container):
                if idx >= len(order):
                    continue
                value_pair = order[idx]
                if value_pair not in hue_lookup.index:
                    continue
                row = hue_lookup.loc[value_pair]
                height = bar.get_height()
                lower = row["ci_lower_pct"]
                upper = row["ci_upper_pct"]
                err_low = max(0.0, height - lower)
                err_high = max(0.0, upper - height)
                if err_low == 0 and err_high == 0:
                    continue
                ax.errorbar(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    yerr=[[err_low], [err_high]],
                    fmt="none",
                    ecolor=bar.get_facecolor(),
                    elinewidth=1.0,
                    capsize=3,
                )
    legend = g._legend
    if legend is not None:
        legend.set_title(legend_title)
        legend.set_bbox_to_anchor((0.5, 1.02))
        legend.set_loc("lower center")
    if title:
        g.fig.suptitle(title)
        g.fig.tight_layout()
    else:
        g.fig.tight_layout()
    g.fig.savefig(OUTPUT_DIR / output_name, dpi=200)
    if show:
        plt.show()
    else:
        plt.close(g.fig)
    return g


def plot_alignment_boxplots(judge_df: pd.DataFrame) -> None:
    """Create boxplots of alignment scores per model and judge provider."""
    plt.clf()
    box_data = judge_df.dropna(subset=["alignment_score"]).copy()
    order = (
        box_data.groupby("model_under_test")["alignment_score"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(
        data=box_data,
        x="alignment_score",
        y="model_under_test",
        hue="judge_provider",
        ax=ax,
        order=order,
        whis=[5, 95],
    )
    ax.set_title("Alignment score distribution by model and judge provider")
    ax.set_xlabel("Alignment score")
    ax.set_ylabel("Model under test")
    ax.legend(title="Judge provider")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "alignment_scores_by_model.png", dpi=200)
    plt.close(fig)


def plot_preference_alignment_heatmap(
    pref_df: pd.DataFrame, judge_df: pd.DataFrame
) -> None:
    """Plot heatmap relating heuristic preferences to average alignment scores."""
    merged = pref_df.merge(
        judge_df[
            [
                "phase",
                "scenario_id",
                "model_under_test",
                "alignment_score",
                "value_preference",
            ]
        ],
        left_on=["phase", "scenario_id", "model"],
        right_on=["phase", "scenario_id", "model_under_test"],
        how="inner",
    )
    if merged.empty:
        return
    merged = merged.rename(columns={"preference": "heuristic_preference"})
    pivot = (
        merged.groupby(
            ["phase", "model_under_test", "heuristic_preference", "value_preference"]
        )["alignment_score"]
        .mean()
        .reset_index()
    )
    for phase_name, phase_data in pivot.groupby("phase"):
        grid = phase_data.pivot_table(
            index=["model_under_test", "heuristic_preference"],
            columns="value_preference",
            values="alignment_score",
        )
        plt.clf()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            grid,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            cbar_kws={"label": "Mean alignment score"},
            ax=ax,
        )
        ax.set_title(
            f"Alignment scores by heuristic vs judge preference ({phase_name})"
        )
        fig.tight_layout()
        fig.savefig(
            OUTPUT_DIR
            / f"alignment_heatmap_{phase_name.replace(' ', '_')}.png",
            dpi=200,
        )
        plt.close(fig)


def save_snapshot(metadata: Dict) -> None:
    """Persist a run summary for reproducibility."""
    snapshot_path = OUTPUT_DIR / "eda_snapshot.json"
    snapshot_path.write_text(json.dumps(metadata, indent=2))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pref_df = load_value_preferences()
    judge_df = load_judgements()
    pref_summary = summarise_preferences(pref_df)
    judge_pref_summary = summarise_judge_preferences(pref_df, judge_df)
    judge_summary = summarise_judges(judge_df, pref_df)
    plot_preference_distribution(
        judge_pref_summary,
        y_label="Share of judge decisions (%)",
        output_name="value_preference_distribution_judges.png",
        title="Judge-labelled value preferences",
        legend_title="Judge preference",
    )
    plot_preference_distribution(
        pref_summary,
        y_label="Share of heuristic tags (%)",
        output_name="value_preference_distribution_heuristic.png",
        title="Model heuristic value tags",
        legend_title="Heuristic tag",
    )
    plot_alignment_boxplots(judge_df)
    plot_preference_alignment_heatmap(pref_df, judge_df)
    save_snapshot(
        {
            "preference_rows": len(pref_df),
            "judgement_rows": len(judge_df),
            "preference_summary_rows": len(pref_summary),
            "judge_summary_rows": len(judge_summary),
            "judge_preference_summary_rows": len(judge_pref_summary),
        }
    )


if __name__ == "__main__":
    main()
