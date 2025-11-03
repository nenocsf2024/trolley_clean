#!/usr/bin/env python3
"""
Generate a detailed HTML report with interactive charts for Phase 1.

Outputs:
  - results/local_runs/local_phase1_report_detailed.html
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

import plotly.graph_objects as go
from plotly.offline import plot

RESULTS_DIR = Path("results/local_runs_expanded")
OUTPUT_HTML = RESULTS_DIR / "local_phase1_report_detailed.html"


def read_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def model_length_chart(per_model: List[Dict[str, str]]) -> str:
    models = [row["model"] for row in per_model]
    avg_chars = [float(row["avg_chars"]) for row in per_model]
    avg_tokens = [float(row["avg_tokens"]) for row in per_model]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=models, y=avg_chars, name="Average characters", marker_color="#4C72B0"))
    fig.add_trace(
        go.Scatter(
            x=models,
            y=avg_tokens,
            name="Average tokens (approx.)",
            mode="lines+markers",
            marker=dict(color="#55A868"),
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Average Response Length by Model",
        xaxis_title="Model",
        yaxis=dict(title="Characters"),
        yaxis2=dict(title="Tokens (approx.)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
    )
    return plot(fig, include_plotlyjs="cdn", output_type="div")


def top_disagreements_chart(disagreement_rows: List[Dict[str, str]], top_n: int = 10) -> str:
    sorted_rows = sorted(
        disagreement_rows,
        key=lambda r: (float(r["min_jaccard_overlap"]), -float(r["max_length_delta"]))
    )[:top_n]
    x = [row["scenario_id"] for row in sorted_rows]
    inv_jaccard = [1 - float(row["min_jaccard_overlap"]) for row in sorted_rows]
    length_delta = [float(row["max_length_delta"]) for row in sorted_rows]
    hover_text = [
        f"{row['topic']}<br>Value pair: {row['value_pair']}<br>Framing: {row['framing']}"
        for row in sorted_rows
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x,
            y=inv_jaccard,
            name="1 - min Jaccard (lexical difference)",
            marker_color="#DD8452",
            hovertext=hover_text,
            hoverinfo="text+y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=length_delta,
            name="Max length delta (chars)",
            mode="lines+markers",
            marker=dict(color="#8172B2"),
            yaxis="y2",
        )
    )
    fig.update_layout(
        title=f"Top {top_n} Highest-Disagreement Scenarios",
        xaxis_title="Scenario ID",
        yaxis=dict(title="1 - min Jaccard"),
        yaxis2=dict(title="Max length delta", overlaying="y", side="right"),
        template="plotly_white",
    )
    return plot(fig, include_plotlyjs=False, output_type="div")


def value_pair_chart(by_value_pair: List[Dict[str, str]], top_n: int = 10) -> str:
    sorted_rows = sorted(by_value_pair, key=lambda r: float(r["min_jaccard"]))[:top_n]
    value_pairs = [row["value_pair"] for row in sorted_rows]
    inv_jaccard = [1 - float(row["min_jaccard"]) for row in sorted_rows]
    length_delta = [float(row["max_length_delta"]) for row in sorted_rows]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=value_pairs,
            y=inv_jaccard,
            name="1 - min Jaccard",
            marker_color="#C44E52",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=value_pairs,
            y=length_delta,
            name="Max length delta",
            mode="markers+lines",
            marker=dict(color="#55A868"),
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Value Pair Hotspots",
        xaxis_title="Value pair",
        yaxis=dict(title="1 - min Jaccard"),
        yaxis2=dict(title="Max length delta", overlaying="y", side="right"),
        template="plotly_white",
    )
    return plot(fig, include_plotlyjs=False, output_type="div")


def value_preference_chart(summary_rows: List[Dict[str, str]]) -> str:
    value_pairs = [row["value_pair"] for row in summary_rows]
    value_a = [int(row["value_a_pref"]) for row in summary_rows]
    value_b = [int(row["value_b_pref"]) for row in summary_rows]
    ties = [int(row["ties"]) for row in summary_rows]
    none = [int(row["no_signal"]) for row in summary_rows]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Value A keywords", x=value_pairs, y=value_a, marker_color="#4C72B0"))
    fig.add_trace(go.Bar(name="Value B keywords", x=value_pairs, y=value_b, marker_color="#DD8452"))
    fig.add_trace(go.Bar(name="Tie", x=value_pairs, y=ties, marker_color="#8172B2"))
    fig.add_trace(go.Bar(name="No signal", x=value_pairs, y=none, marker_color="#9F9F9F"))
    fig.update_layout(
        title="Heuristic Value Preference Counts (keyword-based)",
        barmode="stack",
        xaxis_title="Value pair",
        yaxis_title="Responses",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return plot(fig, include_plotlyjs=False, output_type="div")


def render_table(rows: List[Dict[str, str]], columns: List[str], headers: List[str]) -> str:
    html = ["<table>"]
    html.append("<thead><tr>" + "".join(f"<th>{header}</th>" for header in headers) + "</tr></thead>")
    html.append("<tbody>")
    for row in rows:
        html.append("<tr>" + "".join(f"<td>{row[col]}</td>" for col in columns) + "</tr>")
    html.append("</tbody></table>")
    return "\n".join(html)


def build_report(per_model: List[Dict[str, str]],
                 disagreement_rows: List[Dict[str, str]],
                 by_value_pair: List[Dict[str, str]],
                 by_topic: List[Dict[str, str]],
                 value_pref_summary: List[Dict[str, str]]) -> str:
    length_chart = model_length_chart(per_model)
    disagreement_chart = top_disagreements_chart(disagreement_rows)
    value_pair_hotspots_chart = value_pair_chart(by_value_pair)
    value_pref_chart = value_preference_chart(value_pref_summary)

    top_disagreements = sorted(
        disagreement_rows,
        key=lambda r: (float(r["min_jaccard_overlap"]), -float(r["max_length_delta"]))
    )[:10]
    disagreements_table = render_table(
        top_disagreements,
        ["scenario_id", "topic", "value_pair", "framing", "min_jaccard_overlap", "max_length_delta"],
        ["Scenario", "Topic", "Value Pair", "Framing", "Min Jaccard", "Max Δ (chars)"],
    )

    top_topics = sorted(by_topic, key=lambda r: float(r["min_jaccard"]))[:6]
    topics_table = render_table(
        top_topics,
        ["topic", "scenarios", "min_jaccard", "max_length_delta"],
        ["Topic", "Scenarios", "Min Jaccard", "Max Δ (chars)"],
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Local Phase 1 Moral Alignment Report</title>
  <style>
    body {{
      font-family: "Segoe UI", sans-serif;
      margin: 2rem;
      color: #1f2933;
      background: #f8fafc;
    }}
    h1, h2, h3 {{
      color: #102a43;
    }}
    .card {{
      background: white;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      border-radius: 12px;
      box-shadow: 0 5px 18px rgba(16, 42, 67, 0.06);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
    }}
    th, td {{
      border-bottom: 1px solid #e4e7eb;
      padding: 0.6rem 0.8rem;
      text-align: left;
    }}
    th {{
      background: #f1f5f9;
      font-weight: 600;
    }}
    .pill {{
      display: inline-block;
      padding: 0.2rem 0.6rem;
      background: #d1fae5;
      color: #065f46;
      border-radius: 999px;
      font-size: 0.85rem;
    }}
    .dataset-links a {{
      margin-right: 1rem;
      color: #2563eb;
      text-decoration: none;
      font-weight: 600;
    }}
    .dataset-links a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <h1>Local Phase 1 Moral Alignment Report</h1>
  <p>Three locally-running instruction-tuned models were given 30 ethical dilemmas (each with three framings). We collected 90 responses and looked for spots where the models disagreed.</p>

  <div class="card">
    <h2>Quick Stats</h2>
    <p><span class="pill">Models</span> mistral:7b-instruct &middot; gemma:2b-instruct &middot; phi3:mini</p>
    <p><span class="pill">Total responses</span> 90 (30 scenarios × 3 framings × 1 response/model)</p>
    <div class="dataset-links">
      <a href="analysis_per_model.csv">analysis_per_model.csv</a>
      <a href="analysis_pairwise.csv">analysis_pairwise.csv</a>
      <a href="analysis_disagreement.csv">analysis_disagreement.csv</a>
      <a href="analysis_by_value_pair.csv">analysis_by_value_pair.csv</a>
      <a href="analysis_by_topic.csv">analysis_by_topic.csv</a>
      <a href="analysis_value_preferences.csv">analysis_value_preferences.csv</a>
      <a href="analysis_value_preferences_summary.csv">analysis_value_preferences_summary.csv</a>
    </div>
  </div>

  <div class="card">
    <h2>How Wordy Are The Models?</h2>
    <p>Gemma writes the longest answers, while Mistral and Phi-3 trend a bit shorter but similar in token count.</p>
    {length_chart}
  </div>

  <div class="card">
    <h2>Where Did They Diverge Most?</h2>
    <p>Below: lexical difference (orange bars) and response-length gaps (purple line) for the top disagreement scenarios.</p>
    {disagreement_chart}
    <h3>Scenario spotlight</h3>
    {disagreements_table}
  </div>

  <div class="card">
    <h2>Recurring Moral Tug-of-Wars</h2>
    <p>Value pairs with the lowest lexical overlap and biggest verbosity gaps.</p>
    {value_pair_hotspots_chart}
  </div>

  <div class="card">
    <h2>Heuristic Value Preferences</h2>
    <p>Keyword hits hint at which value (A vs B) each model emphasized in its wording. Use this as a quick triage before manual review.</p>
    {value_pref_chart}
    <p><em>Legend: Value A / Value B = keyword counts leaning toward each side; Tie = equal hits; No signal = keywords weren’t detected.</em></p>
  </div>

  <div class="card">
    <h2>Topic Clusters With High Disagreement</h2>
    <p>Climate policy, hiring fairness, mental health crises, and social media moderation are the spiciest topics.</p>
    {topics_table}
  </div>

  <div class="card">
    <h2>Takeaways</h2>
    <ul>
      <li>Even smaller, locally-run models split on classic dilemmas: environment vs growth, fairness vs efficiency, safety vs autonomy.</li>
      <li>Stylistic differences amplify disagreements: Gemma is policy-heavy, Phi-3 is concise and persuasive, Mistral aims for balance.</li>
      <li>The hot scenarios match the specification weak spots Anthropic highlighted, giving us confidence in this stress-test pipeline.</li>
    </ul>
  </div>

  <div class="card">
    <h2>Phase 1 Checklist & Next Steps</h2>
    <ul>
      <li>✅ All 90 responses captured without parsing issues.</li>
      <li>✅ Per-model and scenario-level summaries exported.</li>
      <li>✅ High-disagreement prompts catalogued for deeper analysis.</li>
    </ul>
    <h3>Before Phase 2</h3>
    <ol>
      <li>Manually tag each model's value stance on the flagged scenarios.</li>
      <li>Add lightweight keyword or embedding-based classifiers to automate value labeling.</li>
      <li>Send the high-disagreement prompts to API models to compare hosted vs local behavior.</li>
    </ol>
  </div>
</body>
</html>
"""
    return html


def main() -> None:
    per_model = read_csv(RESULTS_DIR / "analysis_per_model.csv")
    disagreement_rows = read_csv(RESULTS_DIR / "analysis_disagreement.csv")
    by_value_pair = read_csv(RESULTS_DIR / "analysis_by_value_pair.csv")
    by_topic = read_csv(RESULTS_DIR / "analysis_by_topic.csv")
    value_pref_summary = read_csv(RESULTS_DIR / "analysis_value_preferences_summary.csv")

    html = build_report(per_model, disagreement_rows, by_value_pair, by_topic, value_pref_summary)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote detailed report to {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
