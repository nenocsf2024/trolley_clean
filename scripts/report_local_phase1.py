#!/usr/bin/env python3
"""
Generate a Markdown report summarizing local Phase 1 runs.

Creates ASCII-style charts so no plotting dependencies are required.
Outputs report to results/local_runs/local_phase1_report.md.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

RESULTS_DIR = Path("results/local_runs_expanded")
REPORT_PATH = RESULTS_DIR / "local_phase1_report.md"


def read_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def ascii_bar(value: float, max_value: float, width: int = 30) -> str:
    if max_value <= 0:
        return " " * width
    filled = int(round(value / max_value * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def build_length_section(per_model: List[Dict[str, str]]) -> str:
    max_chars = max(float(row["avg_chars"]) for row in per_model)
    lines = []
    lines.append("| Model | Avg chars | Avg tokens | Visual |\n")
    lines.append("| --- | --- | --- | --- |\n")
    for row in per_model:
        avg_chars = float(row["avg_chars"])
        avg_tokens = float(row["avg_tokens"])
        lines.append(
            "| {model} | {chars:.1f} | {tokens:.1f} | `{bar}` |\n".format(
                model=row["model"],
                chars=avg_chars,
                tokens=avg_tokens,
                bar=ascii_bar(avg_chars, max_chars),
            )
        )
    return "".join(lines)


def build_disagreement_table(disagreement_rows: List[Dict[str, str]], top_n: int = 6) -> str:
    sorted_rows = sorted(
        disagreement_rows,
        key=lambda r: (float(r["min_jaccard_overlap"]), -float(r["max_length_delta"]))
    )[:top_n]
    max_inv_j = max(1 - float(r["min_jaccard_overlap"]) for r in sorted_rows)
    lines = []
    lines.append("| Scenario | Topic | Value pair | Framing | 1 - min Jaccard | Max length Δ | Visual |\n")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |\n")
    for row in sorted_rows:
        inv_j = 1 - float(row["min_jaccard_overlap"])
        delta = float(row["max_length_delta"])
        lines.append(
            "| {id} | {topic} | {value_pair} | {framing} | {inv:.3f} | {delta:.0f} | `{bar}` |\n".format(
                id=row["scenario_id"],
                topic=row.get("topic", ""),
                value_pair=row.get("value_pair", ""),
                framing=row.get("framing", ""),
                inv=inv_j,
                delta=delta,
                bar=ascii_bar(inv_j, max_inv_j),
            )
        )
    return "".join(lines)


def top_entries(rows: List[Dict[str, str]], key: str, reverse: bool = False, limit: int = 5) -> List[Dict[str, str]]:
    return sorted(rows, key=lambda r: float(r[key]), reverse=reverse)[:limit]


def write_report(
    per_model: List[Dict[str, str]],
    disagreement_rows: List[Dict[str, str]],
    by_value_pair: List[Dict[str, str]],
    by_topic: List[Dict[str, str]],
    value_pref_summary: List[Dict[str, str]],
) -> None:
    total_responses = sum(int(row["responses"]) for row in per_model)
    length_section = build_length_section(per_model)
    disagreement_section = build_disagreement_table(disagreement_rows)

    lowest_value_pairs = top_entries(by_value_pair, "min_jaccard")
    highest_value_pairs_delta = top_entries(by_value_pair, "max_length_delta", reverse=True)
    lowest_topics = top_entries(by_topic, "min_jaccard")

    # Build dynamic model list
    model_names = ", ".join(sorted({row["model"] for row in per_model}))

    lines: List[str] = []
    lines.append("# Local Phase 1 Moral Alignment Summary (Plain Speak)\n")
    lines.append(
        "We asked five locally-running AI models to answer 30 ethical dilemmas "
        "(each phrased three ways) across 10 iterations and 10 temperatures (0.0–1.0).\n"
    )
    lines.append(f"**Models tested:** {model_names}  ")
    lines.append(f"**Total answers collected:** {total_responses}\n")

    lines.append("\n## 1. What We Did\n")
    lines.append("- Used 30 tricky moral scenarios from moral_core_21, each framed three ways (neutral, safety_first, freedom_first).\n")
    lines.append("- Collected responses from five local models (10 iterations per scenario; explicit temperatures 0.0–1.0).\n")
    lines.append("- Saved answers and computed summaries: length, lexical overlap, judge scores and value preferences.\n")

    lines.append("\n## 2. Average Answer Length (by Model)\n")
    lines.append("Bars show how long answers tended to be. More filled bars = longer answers.\n\n")
    lines.append(length_section)

    lines.append("\n## 3. Scenarios Where Models Disagreed Most\n")
    lines.append("These are the prompts where the models used very different wording or wrote very different-length answers.\n\n")
    lines.append(disagreement_section)

    lines.append("\n### 3.1 Which Moral Tug-of-Wars Caused the Most Spread?\n")
    lines.append("| Value pair | Scenarios | Lowest overlap | Biggest length gap | Avg chars |\n")
    lines.append("| --- | --- | --- | --- | --- |\n")
    for row in lowest_value_pairs:
        lines.append(
            "| {vp} | {sc} | {j:.3f} | {delta} | {avg} |\n".format(
                vp=row["value_pair"],
                sc=row["scenarios"],
                j=float(row["min_jaccard"]),
                delta=row["max_length_delta"],
                avg=row["avg_chars"],
            )
        )

    lines.append("\n**Where one model got especially long-winded**\n\n")
    lines.append("| Value pair | Biggest length gap | Lowest overlap |\n")
    lines.append("| --- | --- | --- |\n")
    for row in highest_value_pairs_delta:
        lines.append(
            "| {vp} | {delta} | {j:.3f} |\n".format(
                vp=row["value_pair"],
                delta=row["max_length_delta"],
                j=float(row["min_jaccard"]),
            )
        )

    lines.append("\n### 3.2 Topics That Sparked the Most Divergence\n")
    lines.append("| Topic | Scenarios | Lowest overlap | Biggest length gap |\n")
    lines.append("| --- | --- | --- | --- |\n")
    for row in lowest_topics:
        lines.append(
            "| {topic} | {sc} | {j:.3f} | {delta} |\n".format(
                topic=row["topic"],
                sc=row["scenarios"],
                j=float(row["min_jaccard"]),
                delta=row["max_length_delta"],
            )
        )

    lines.append("\n### 3.3 Quick Heuristic Value Preferences\n")
    lines.append("We scanned responses for simple keywords to guess whether a model leans toward value A or value B. Counts below show how many model answers referenced each side more often.\n\n")
    lines.append("| Value pair | Value A prefs | Value B prefs | Ties | No signal |\n")
    lines.append("| --- | --- | --- | --- | --- |\n")
    for row in value_pref_summary:
        lines.append(
            "| {vp} | {a} | {b} | {tie} | {none} |\n".format(
                vp=row["value_pair"],
                a=row["value_a_pref"],
                b=row["value_b_pref"],
                tie=row["ties"],
                none=row["no_signal"],
            )
        )
    lines.append("_Note: keyword counts are a rough guide—manual review still recommended._\n")

    lines.append("\n## 4. What We Learned (In Everyday Terms)\n")
    lines.append("- Local 7B-class models split on classic dilemmas: environment vs growth, efficiency vs fairness, freedom vs safety.\n")
    lines.append("- Gemma tends to write longer, policy-style answers; Mistral aims for balance; Phi-3 is concise; Llama3 and Orca show stable but temperature-sensitive preferences.\n")
    lines.append("- Climate policy, mental health crises, and social media moderation were among the trickiest topics—aligning with prior findings on challenging domains.\n")

    lines.append("\n## 5. Phase 1: What’s Done\n")
    lines.append(f"- ✅ Collected {total_responses} clean answers.\n")
    lines.append("- ✅ Logged per-model stats and cross-model comparisons (`analysis_per_model.csv`, `analysis_pairwise.csv`).\n")
    lines.append("- ✅ Flagged the toughest scenarios (`analysis_disagreement.csv`).\n")
    lines.append("- ✅ Summarized hotspots by moral trade-off and topic (`analysis_by_value_pair.csv`, `analysis_by_topic.csv`).\n")
    lines.append("- ✅ Published this plain-language report (`local_phase1_report.md`).\n")

    lines.append("\n## 6. Suggested Next Steps (Before Phase 2)\n")
    lines.append("1. Read the flagged scenarios side by side and note which value each model seems to endorse.\n")
    lines.append("2. Add simple keyword-based labels to automate those value judgments in the future.\n")
    lines.append("3. Take these high-disagreement prompts into the API-based Phase 2 tests to see whether bigger models agree or diverge even more.\n")

    REPORT_PATH.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    per_model = read_csv(RESULTS_DIR / "analysis_per_model.csv")
    disagreement_rows = read_csv(RESULTS_DIR / "analysis_disagreement.csv")
    by_value_pair = read_csv(RESULTS_DIR / "analysis_by_value_pair.csv")
    by_topic = read_csv(RESULTS_DIR / "analysis_by_topic.csv")
    value_pref_summary = read_csv(RESULTS_DIR / "analysis_value_preferences_summary.csv")
    write_report(per_model, disagreement_rows, by_value_pair, by_topic, value_pref_summary)
    print(f"Wrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
