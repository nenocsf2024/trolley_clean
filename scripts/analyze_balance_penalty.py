#!/usr/bin/env python3
"""
Balance penalty analysis.

Loads Phase 1 response metadata and judge evaluations, labels each
evaluation as a balanced response (tie) or value commitment, runs
mixed-effects regressions, and writes summary statistics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.inter_rater import fleiss_kappa

BASE_DIR = Path(__file__).resolve().parent.parent
RESPONSES_DIR = BASE_DIR / "results" / "local_runs_expanded"
JUDGES_DIR = RESPONSES_DIR / "judges"
OUTPUT_DIR = RESPONSES_DIR / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_responses() -> pd.DataFrame:
    records: List[dict] = []
    for path in RESPONSES_DIR.glob("*.jsonl"):
        if not path.is_file():
            continue
        if path.name.startswith("Phase1_Report"):
            continue
        if path.name in {"QA_SUMMARY.md", "README.txt"}:
            continue
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                records.append(
                    {
                        "model_under_test": data["model"],
                        "scenario_id": data["id"],
                        "iteration": int(data["iteration"]),
                        "temperature": float(data["temperature"]),
                        "framing": data["framing"],
                        "topic": data.get("topic", ""),
                        "value_pair": data.get("value_pair", ""),
                        "response": data.get("response", ""),
                        "eval_time_s": data.get("eval_time_s", np.nan),
                    }
                )
    return pd.DataFrame.from_records(records)


def load_judges() -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for path in JUDGES_DIR.glob("*.csv"):
        df = pd.read_csv(path)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    key_cols = ["model_under_test", "scenario_id", "iteration", "judge_model"]
    before = len(out)
    out = out.drop_duplicates(subset=key_cols, keep="first")
    after = len(out)
    if after < before:
        print(f"Deduplicated judge rows: {before} -> {after}")
    out["value_preference"] = out["value_preference"].astype(str).str.strip()
    out["response_type"] = out["value_preference"].str.lower().apply(
        lambda x: "balance" if x == "tie" else "commitment"
    )
    return out


def run_mixedlm(df: pd.DataFrame, formula: str, groups: str):
    model = smf.mixedlm(formula, data=df, groups=df[groups])
    result = model.fit(reml=False)
    return result


def compute_r_squared(result, design_matrix: np.ndarray) -> dict:
    """Compute marginal and conditional R^2 for random-intercept models."""
    fe_params = result.fe_params.values
    fitted_fixed = design_matrix @ fe_params
    var_fixed = float(np.var(fitted_fixed, ddof=1))
    var_random = float(result.cov_re.iloc[0, 0])
    var_resid = float(result.scale)
    denom = var_fixed + var_random + var_resid
    if denom == 0:
        return {"marginal_r2": float("nan"), "conditional_r2": float("nan")}
    return {
        "marginal_r2": float(var_fixed / denom),
        "conditional_r2": float((var_fixed + var_random) / denom),
    }


def compute_length_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["response"] = df["response"].fillna("")
    df["char_len"] = df["response"].str.len()
    df["word_len"] = df["response"].str.split().str.len()

    hedging_words = {
        "may",
        "might",
        "could",
        "perhaps",
        "possibly",
        "maybe",
        "suggest",
        "consider",
        "potentially",
        "uncertain",
        "uncertainty",
        "appears",
        "seems",
    }
    certainty_words = {
        "must",
        "definitely",
        "certainly",
        "always",
        "clearly",
        "will",
        "ensure",
        "commit",
        "guarantee",
        "undeniably",
        "absolutely",
    }

    def count_terms(text: str, vocab: set[str]) -> int:
        tokens = [token.strip(".,!?;:\"'()[]{}") for token in text.lower().split()]
        return sum(token in vocab for token in tokens if token)

    df["hedge_count"] = df["response"].apply(lambda x: count_terms(x, hedging_words))
    df["certainty_count"] = df["response"].apply(
        lambda x: count_terms(x, certainty_words)
    )
    df["hedge_rate"] = df["hedge_count"] / df["word_len"].replace(0, np.nan)
    df["certainty_rate"] = df["certainty_count"] / df["word_len"].replace(0, np.nan)
    return df


def main() -> None:
    responses = load_responses()
    judges = load_judges()

    df = judges.merge(
        responses,
        on=["model_under_test", "scenario_id", "iteration"],
        how="left",
        validate="many_to_one",
    )

    if df["temperature"].isna().any():
        missing = df[df["temperature"].isna()][
            ["model_under_test", "scenario_id", "iteration"]
        ].drop_duplicates()
        raise RuntimeError(f"Missing response metadata for records:\n{missing}")

    df["alignment_score"] = df["alignment_score"].astype(float)
    df["temperature"] = df["temperature"].astype(float)
    df = compute_length_features(df)

    pair_records = []
    for (model, scenario, iteration), group in df.groupby(
        ["model_under_test", "scenario_id", "iteration"], sort=False
    ):
        prefs = group["value_preference"].str.lower().tolist()
        scores = group["alignment_score"].tolist()
        judge_models = group["judge_model"].tolist()
        response_type = "balance" if "tie" in prefs else "commitment"
        value_agree = len(set(prefs)) == 1
        score_agree = len(set(scores)) == 1
        pair_records.append(
            {
                "model_under_test": model,
                "scenario_id": scenario,
                "iteration": iteration,
                "framing": group["framing"].iloc[0],
                "temperature": group["temperature"].iloc[0],
                "response_type_pair": response_type,
                "value_preferences": prefs,
                "alignment_scores": scores,
                "judge_models": judge_models,
                "value_agree": value_agree,
                "score_agree": score_agree,
                "alignment_score_gap": max(scores) - min(scores),
            }
        )

    pair_df = pd.DataFrame(pair_records)
    pair_df.to_csv(OUTPUT_DIR / "analysis_balance_penalty_pairs.csv", index=False)

    categories = sorted(df["alignment_score"].dropna().astype(int).unique())
    matrix = []
    for _, group in df.groupby(["model_under_test", "scenario_id", "iteration"]):
        counts = [(group["alignment_score"] == cat).sum() for cat in categories]
        matrix.append(counts)
    matrix = np.array(matrix)
    fleiss = float(fleiss_kappa(matrix))

    overall_model = run_mixedlm(
        df,
        "alignment_score ~ C(response_type) + C(framing) + temperature + C(model_under_test)",
        "scenario_id",
    )
    r2_overall = compute_r_squared(overall_model, overall_model.model.exog)

    def cohens_d(subset: pd.DataFrame) -> float:
        balance = subset.loc[subset["response_type"] == "balance", "alignment_score"]
        commit = subset.loc[subset["response_type"] == "commitment", "alignment_score"]
        n1, n2 = len(balance), len(commit)
        if n1 < 2 or n2 < 2:
            return float("nan")
        var1, var2 = balance.var(ddof=1), commit.var(ddof=1)
        pooled = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
        if pooled <= 0:
            return float("nan")
        return (commit.mean() - balance.mean()) / np.sqrt(pooled)

    summaries = {
        "overall": {
            "n_rows": int(len(df)),
            "balanced_count": int((df["response_type"] == "balance").sum()),
            "commitment_count": int((df["response_type"] == "commitment").sum()),
            "mean_alignment_balance": df.loc[
                df["response_type"] == "balance", "alignment_score"
            ].mean(),
            "mean_alignment_commitment": df.loc[
                df["response_type"] == "commitment", "alignment_score"
            ].mean(),
            "cohens_d": cohens_d(df),
            "fleiss_kappa": fleiss,
            "marginal_r2": r2_overall["marginal_r2"],
            "conditional_r2": r2_overall["conditional_r2"],
            "model_summary": overall_model.summary().as_text(),
        }
    }

    pair_agg = pair_df.groupby("response_type_pair").agg(
        n_pairs=("response_type_pair", "size"),
        value_agreement_rate=("value_agree", "mean"),
        score_agreement_rate=("score_agree", "mean"),
        mean_alignment_gap=("alignment_score_gap", "mean"),
    )
    pair_agg.to_csv(OUTPUT_DIR / "analysis_balance_penalty_disagreement.csv")

    length_summary = (
        df.groupby("response_type")
        .agg(
            mean_char_len=("char_len", "mean"),
            mean_word_len=("word_len", "mean"),
            mean_hedge_rate=("hedge_rate", "mean"),
            mean_certainty_rate=("certainty_rate", "mean"),
        )
        .reset_index()
    )
    length_summary.to_csv(
        OUTPUT_DIR / "analysis_response_characteristics.csv", index=False
    )

    length_correlation = float(df["char_len"].corr(df["alignment_score"]))

    judge_summaries = []
    for judge_model, sub_df in df.groupby("judge_model"):
        model = run_mixedlm(
            sub_df,
            "alignment_score ~ C(response_type) + C(framing) + temperature + C(model_under_test)",
            "scenario_id",
        )
        r2_judge = compute_r_squared(model, model.model.exog)
        judge_summaries.append(
            {
                "judge_model": judge_model,
                "n_rows": int(len(sub_df)),
                "balanced_count": int((sub_df["response_type"] == "balance").sum()),
                "commitment_count": int((sub_df["response_type"] == "commitment").sum()),
                "mean_alignment_balance": sub_df.loc[
                    sub_df["response_type"] == "balance", "alignment_score"
                ].mean(),
                "mean_alignment_commitment": sub_df.loc[
                    sub_df["response_type"] == "commitment", "alignment_score"
                ].mean(),
                "cohens_d": cohens_d(sub_df),
                "marginal_r2": r2_judge["marginal_r2"],
                "conditional_r2": r2_judge["conditional_r2"],
                "model_summary": model.summary().as_text(),
            }
        )

    df.to_csv(OUTPUT_DIR / "analysis_balance_penalty_dataset.csv", index=False)

    pd.DataFrame(judge_summaries).to_json(
        OUTPUT_DIR / "analysis_balance_penalty_judges.json", orient="records", indent=2
    )

    import json as _json

    with (OUTPUT_DIR / "analysis_balance_penalty_overall.json").open("w", encoding="utf-8") as f:
        _json.dump(
            {
                **summaries,
                "length_correlation": length_correlation,
            },
            f,
            indent=2,
        )

    print(overall_model.summary())


if __name__ == "__main__":
    main()
