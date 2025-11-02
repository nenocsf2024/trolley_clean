#!/usr/bin/env python3
"""
Generate a Phase 2 report in the same style as the Phase 1 detailed HTML.

Reads the analysis CSV files from results/phase2/ and produces
  results/phase2/phase2_report_detailed.html
with ASCII-style tables, key takeaways, and links to the raw CSVs.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import List

import argparse
import pandas as pd

BASE_DIR = Path("results/phase2")
REPORT_PATH = BASE_DIR / "phase2_report_detailed.html"


def load_csv(name: str) -> pd.DataFrame:
    path = BASE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing expected file: {path}")
    return pd.read_csv(path)


def ascii_bar(value: float, max_value: float, width: int = 30) -> str:
    if max_value <= 0:
        return " " * width
    filled = int(round(value / max_value * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def build_lengths_section(df: pd.DataFrame) -> str:
    max_chars = df["avg_chars"].max()
    rows: List[str] = []
    rows.append("<table>")
    rows.append("<thead><tr><th>Model</th><th>Responses</th><th>Avg chars</th>"
                "<th>Avg tokens</th><th>Visual</th></tr></thead>")
    rows.append("<tbody>")
    for _, row in df.sort_values("avg_chars", ascending=False).iterrows():
        bar = ascii_bar(row["avg_chars"], max_chars)
        rows.append(
            "<tr>"
            f"<td>{html.escape(row['model'])}</td>"
            f"<td>{int(row['responses'])}</td>"
            f"<td>{row['avg_chars']:.1f}</td>"
            f"<td>{row['avg_tokens']:.1f}</td>"
            f"<td><code>{bar}</code></td>"
            "</tr>"
        )
    rows.append("</tbody></table>")
    return "\n".join(rows)


def build_disagreement_section(df: pd.DataFrame) -> str:
    rows: List[str] = []
    rows.append("<table>")
    rows.append("<thead><tr><th>Scenario</th><th>Topic</th><th>Value pair</th>"
                "<th>Framing</th><th>Max length Δ</th><th>Min Jaccard</th></tr></thead>")
    rows.append("<tbody>")
    for _, row in df.iterrows():
        rows.append(
            "<tr>"
            f"<td>{row['scenario_id']}</td>"
            f"<td>{html.escape(row['topic'])}</td>"
            f"<td>{row['value_pair']}</td>"
            f"<td>{row['framing']}</td>"
            f"<td>{int(row['max_length_delta'])}</td>"
            f"<td>{row['min_jaccard_overlap']:.3f}</td>"
            "</tr>"
        )
    rows.append("</tbody></table>")
    return "\n".join(rows)


def build_value_preferences_section(df: pd.DataFrame) -> str:
    label_map = {
        "autonomy_vs_safety": ("Autonomy / user choice", "Safety / intervention"),
        "efficiency_vs_fairness": ("Efficiency / throughput", "Fairness / equity safeguards"),
        "environment_vs_growth": ("Environment / sustainability", "Economic growth / flexibility"),
        "fairness_vs_efficiency": ("Fairness / equity", "Efficiency / throughput"),
        "safety_vs_freedom": ("Safety / protection", "Freedom / expression"),
    }
    rows: List[str] = []
    rows.append("<table>")
    rows.append("<thead><tr><th>Value pair</th><th>Value A</th><th>Value B</th>"
                "<th>Ties</th><th>No signal</th><th>Total</th></tr></thead>")
    rows.append("<tbody>")
    for _, row in df.iterrows():
        label_a, label_b = label_map.get(row["value_pair"], ("Value A", "Value B"))
        rows.append(
            "<tr>"
            f"<td>{row['value_pair']}</td>"
            f"<td>{int(row['value_a_pref'])}</td>"
            f"<td>{int(row['value_b_pref'])}</td>"
            f"<td>{int(row['ties'])}</td>"
            f"<td>{int(row['no_signal'])}</td>"
            f"<td>{int(row['total'])}</td>"
            "</tr>"
        )
    rows.append("</tbody></table>")
    mapping_list = []
    for vp, (a_label, b_label) in label_map.items():
        mapping_list.append(f"<li><code>{vp}</code>: Value A = {html.escape(a_label)}; "
                            f"Value B = {html.escape(b_label)}</li>")
    mapping_html = "<ul>" + "".join(mapping_list) + "</ul>"
    return "\n".join(rows) + "<p><strong>Legend:</strong></p>" + mapping_html


def build_pairwise_summary(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p>No pairwise data available.</p>"
    df = df.copy()
    df["jaccard_overlap"] = df["jaccard_overlap"].astype(float)
    df["pair"] = df.apply(lambda row: f"{row['model_a']} vs {row['model_b']}", axis=1)
    agg = (df.groupby(["scenario_id", "pair"], as_index=False)
             ["jaccard_overlap"].mean()
             .sort_values(["scenario_id", "pair"]))

    rows: List[str] = []
    rows.append("<table>")
    rows.append("<thead><tr><th>Scenario</th><th>Model pair</th><th>Jaccard overlap</th></tr></thead>")
    rows.append("<tbody>")
    for _, row in agg.iterrows():
        rows.append(
            "<tr>"
            f"<td>{row['scenario_id']}</td>"
            f"<td>{html.escape(row['pair'])}</td>"
            f"<td>{row['jaccard_overlap']:.3f}</td>"
            "</tr>"
        )
    rows.append("</tbody></table>")
    return "\n".join(rows)


def gather_highlights(per_model: pd.DataFrame,
                      disagreement: pd.DataFrame,
                      prefs: pd.DataFrame) -> List[str]:
    highlights: List[str] = []

    longest = per_model.sort_values("avg_chars", ascending=False).iloc[0]
    highlights.append(
        f"- **Longest answers:** `{longest['model']}` averaged {longest['avg_chars']:.0f} characters; "
        f"`{per_model.sort_values('avg_chars').iloc[0]['model']}` stayed around "
        f"{per_model.sort_values('avg_chars').iloc[0]['avg_chars']:.0f}."
    )

    fairness_row = prefs[prefs["value_pair"] == "efficiency_vs_fairness"].iloc[0]
    highlights.append(
        f"- **Fairness consensus:** Hosted models chose fairness safeguards "
        f"{int(fairness_row['value_b_pref'])}× versus {int(fairness_row['value_a_pref'])} efficiency votes."
    )

    autonomy_row = prefs[prefs["value_pair"] == "autonomy_vs_safety"].iloc[0]
    highlights.append(
        f"- **Autonomy first:** {int(autonomy_row['value_a_pref'])} responses backed autonomy with only "
        f"{int(autonomy_row['value_b_pref'])} safety-leaning answer."
    )

    climate = disagreement[disagreement["scenario_id"].str.contains("MC21-005")]
    if not climate.empty:
        highlights.append(
            f"- **Climate trade-off:** Climate prompts still show the largest disagreements "
            f"(max length Δ up to {climate['max_length_delta'].max():.0f}, min Jaccard {climate['min_jaccard_overlap'].min():.3f})."
        )

    moderation = disagreement[disagreement["scenario_id"] == "MC21-003-N"]
    if not moderation.empty:
        highlights.append(
            f"- **Moderation tension:** Social media moderation retains low lexical overlap "
            f"(min Jaccard {moderation['min_jaccard_overlap'].iloc[0]:.3f}) despite freedom-leaning conclusions."
        )

    return highlights


def build_html(per_model: pd.DataFrame,
               disagreement: pd.DataFrame,
               prefs: pd.DataFrame,
               pairwise: pd.DataFrame) -> str:
    highlights = gather_highlights(per_model, disagreement, prefs)
    highlight_html = "<br/>".join(highlights)

    css = """
    <style>
    body { font-family: "Segoe UI", Arial, sans-serif; background: #f8fafc; color: #1f2933; margin: 2rem; }
    h1, h2, h3 { color: #102a43; }
    table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
    th, td { border-bottom: 1px solid #e4e7eb; padding: 0.6rem 0.8rem; text-align: left; font-size: 0.95rem; }
    th { background: #f1f5f9; font-weight: 600; }
    code { font-family: "Fira Code", monospace; font-size: 0.9rem; }
    .card { background: white; padding: 1.5rem; margin-bottom: 1.5rem; border-radius: 12px;
            box-shadow: 0 6px 18px rgba(16, 42, 67, 0.08); }
    .dataset-links a { margin-right: 1rem; color: #2563eb; text-decoration: none; font-weight: 600; }
    .dataset-links a:hover { text-decoration: underline; }
    </style>
    """

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Phase 2 Moral Alignment Report</title>
  {css}
</head>
<body>
  <h1>Phase 2 Moral Alignment Report (Hosted Models)</h1>
  <div class="card">
    <h2>Highlights</h2>
    <p>{highlight_html}</p>
    <div class="dataset-links">
      <a href="analysis_per_model.csv">analysis_per_model.csv</a>
      <a href="analysis_disagreement.csv">analysis_disagreement.csv</a>
      <a href="analysis_value_preferences_summary.csv">analysis_value_preferences_summary.csv</a>
      <a href="analysis_pairwise.csv">analysis_pairwise.csv</a>
    </div>
  </div>

  <div class="card">
    <h2>Model Response Lengths</h2>
    <p>Bars show average characters per answer; values are based on 5 samples for each of the 6 scenarios.</p>
    {build_lengths_section(per_model)}
  </div>

  <div class="card">
    <h2>Value Preferences</h2>
    <p>Counts summarize the heuristic keyword tags across all responses (Value A vs Value B, ties, and no-signal cases).</p>
    {build_value_preferences_section(prefs)}
  </div>

  <div class="card">
    <h2>Scenario Disagreement Metrics</h2>
    <p>Higher max length deltas and lower Jaccard overlaps indicate stronger divergence across the five hosted models.</p>
    {build_disagreement_section(disagreement)}
  </div>

  <div class="card">
    <h2>Lexical Overlap by Model Pair</h2>
    <p>Average Jaccard overlap (higher is closer) for each model pair and scenario.</p>
    {build_pairwise_summary(pairwise)}
  </div>

  <div class="card">
    <h2>How to Use This</h2>
    <ul>
      <li>Compare these tables to <code>results/local_runs/local_phase1_report_detailed.html</code> to spot hosted vs local shifts.</li>
      <li>Follow the CSV links above for deeper analysis or to import into your own notebooks.</li>
      <li>Sample raw responses from <code>results/phase2/*.jsonl</code> for qualitative write-ups.</li>
      <li>Re-run this script after future Phase 2 experiments (e.g., once GPT-4.1 access is available).</li>
    </ul>
  </div>
</body>
</html>
"""
    return html_body


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate detailed moral alignment report")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("results/phase2"),
        help="Directory containing analysis CSVs",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="phase2_report_detailed.html",
        help="Output HTML file name (relative to input dir)",
    )
    args = parser.parse_args()

    global BASE_DIR, REPORT_PATH
    BASE_DIR = args.input_dir.resolve()
    REPORT_PATH = BASE_DIR / args.output

    per_model = load_csv("analysis_per_model.csv")
    disagreement = load_csv("analysis_disagreement.csv")
    prefs = load_csv("analysis_value_preferences_summary.csv")
    pairwise = load_csv("analysis_pairwise.csv")

    html_doc = build_html(per_model, disagreement, prefs, pairwise)
    REPORT_PATH.write_text(html_doc, encoding="utf-8")
    print(f"Wrote detailed report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
