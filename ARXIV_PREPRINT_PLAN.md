# The Balance Penalty: ArXiv Preprint Blueprint  
*Inspired by Anthropic’s “Stress-Testing Model Specs Reveals Character Differences Among Language Models”*

---

## 1 Project Synopsis

Large language models increasingly double as evaluators in alignment workflows (RLHF, constitutional AI, automated red-teaming). Anthropic’s stress-test study showed that frontier-model judges agree only ~70 % of the time (Fleiss’ κ≈0.42), attributing the gap to specification ambiguity. Our Phase 1 dataset—5 local LLMs, 30 moral dilemmas, 10 temperatures, dual LLM judges—captures the mechanics of this disagreement. The central insight: judges systematically penalize balanced moral reasoning (mean alignment 3.60) relative to single-value commitments (mean 4.42), producing a “balance penalty” that explains elevated evaluator disagreement (38–46 % agreement overall, 1.7× higher disagreement on balanced responses).

Goal: ship an arXiv preprint within 2–3 weeks that (1) documents the balance penalty, (2) quantifies framing/temperature interactions, and (3) connects these results back to Anthropic’s evaluator findings while supplying reproducible assets and next-step roadmaps (Phase 2 APIs, human validation, meta-judging).

---

## 2 Dataset & Asset Inventory

| Component | Description | Location |
| --- | --- | --- |
| Scenario corpus | 30 dilemmas × 3 framings (neutral / safety_first / freedom_first), value-pair metadata, prompt text | `moral_core_21_sample.jsonl` |
| Phase 1 responses | 1,500 JSONL rows (5 models × 30 scenarios × 10 iterations) across temps `[0.6,0.7,0.8,0.9,1.0,0.0,0.2,0.3,0.4,0.5]`, deterministic seeds | `results/local_runs_expanded/*.jsonl`, summary in `README.txt` |
| Judges | GPT‑4o-mini & Claude 3.5 Haiku CSVs (preferred value, alignment score, confidence, rationale); raw 3,149 rows deduped to 3,000 in analysis | `results/local_runs_expanded/judges/` |
| Derived metrics | Temperature curves, framing spreads, judge agreement tables, scenario difficulty stats, model summaries | `results/local_runs_expanded/analysis_*.csv`, `tables/` |
| Qualitative notes | Scenario-level disagreement narratives, judge rationales | `results/local_runs_expanded/qualitative_interpretation.md` |
| QA documentation | Verified counts, corrected metrics, duplicate handling | `results/local_runs_expanded/QA_SUMMARY.md` |
| Supporting scripts | Data collection, judging, analysis, reporting, plot export | `scripts/` (`run_phase1_expanded.py`, `judge_all_phase1.sh`, `analyze_local_results.py`, etc.) |
| Visual assets | Plot PNG/HTML exports, Word report with figures | `figures/word_report/`, `Phase1_Report_with_figures.docx` |
| Planning docs | Completion plan, gap analysis, expansion roadmaps, P1 vs P2 comparison | `PHASE1_COMPLETION_PLAN.md`, `PHASE1_GAPS.md`, `TEMP_EXPANSION_PLAN.md`, `PHASE1_VS_PHASE2_COMPARISON.md` |
| Phase 2 seeds | API responses for 5 frontier models × 6 shared scenarios × 5 iterations | `results/phase2/` |

---

## 3 Document Structure (ArXiv Draft Outline)

### Abstract (≈250 words)
Condense balance penalty finding, framing/temperature contrasts, judge disagreement, and implications for evaluator design; highlight Anthropic inspiration and dataset scale.

### 1 Introduction (2–3 pp)
1. LLM-based evaluation (RLHF, constitutional AI) and the reliability challenge.  
2. Anthropic stress-test findings (12 models, 300k dilemmas, κ≈0.42 agreement) → open question: *why* evaluators disagree.  
3. Research Questions:  
   - **RQ1:** Do LLM judges penalize balanced moral reasoning?  
   - **RQ2:** How do framing and temperature modulate this bias?  
   - **RQ3:** What patterns explain judge disagreement?  
4. Contributions: quantify balance penalty (Δ=0.82), show framing hierarchy (0.4–0.8 spread), dissect disagreement (38–46 % agreement; 1.7× higher on balanced responses), provide reproducible pipeline and expansion roadmap.  
5. Preview dataset (1,500 responses × 2 judges) and forthcoming analyses.

### 2 Related Work (2–3 pp)
* Moral reasoning benchmarks (Moral Machine, AIRisk, Daily Dilemmas).  
* Constitutional AI, rule-based rewards, deliberative alignment.  
* RLHF/reward modeling biases, Goodhart effects.  
* Evaluator reliability (Anthropic stress test, SpecEval).  
Position balance penalty as mechanistic extension of prior evaluator disagreement reports.

### 3 Methods (3–4 pp)
1. **Dataset:** scenario design, framing taxonomy, value pairs, sensitivity categories (table with examples).  
2. **Models:** five local 2B–8B instruct models, iteration & temperature scheduling, deterministic seed generation.  
3. **Judges:** GPT‑4o-mini / Claude 3.5 Haiku prompts, scoring rubric, rate limiting, deduping.  
4. **Quality Control:** duplicate detection, on-topic check (98–100 %), logging, scripts used.  
5. **Analysis Pipeline:** temperature curves, framing contrasts, judge agreement computation, mixed-effects regression specification.  
Include diagrams (data pipeline), tables (model specs, scenario stats).

### 4 Results (4–5 pp)
1. **Balance Penalty:**  
   - Boxplots of alignment by response type (balanced vs commitment).  
   - Mixed-effects regression (scenario random intercept) → report β, CI, p-value, effect size.  
   - Judge-specific penalties, response-type disagreement rates.  
2. **Framing Effects:**  
   - Alignment means by framing; spreads per model and temperature.  
   - Compare magnitude vs temperature effects (framing dominates).  
3. **Judge Disagreement:**  
   - Heatmap by scenario, statistics by response type/value pair/framing.  
   - Qualitative examples (from `qualitative_interpretation.md`).  
4. **Temperature Effects:**  
   - Alignment curves per model (0.15–0.24 variation).  
   - Note stability across low vs high temps.  
5. **Model Rankings:** descriptive metrics (orca-mini, phi3 lead; gemma/mistral lag).  

### 5 Discussion (3–4 pp)
* Hypotheses for balance penalty (RLHF simplicity bias, constitutional deontological lean, rubric design).  
* Implications for model developers (train/adjust prompts to reward nuance), evaluator designers (explicitly score balance), researchers (meta-judge ensembles, human calibration).  
* Connect back to Anthropic’s evaluator disagreement, arguing balance penalty as partial explanation.

### 6 Limitations & Future Work (1–2 pp)
* Local-model scope; Phase 2 API expansion plan (explicit temperature scheduling).  
* LLM-only judges; proposed human validation (50–100 annotated cases).  
* Scenario coverage; plan to broaden to >100 dilemmas.  
* Meta-judge enhancement (Claude Sonnet 4) to audit disagreements.  

### 7 Conclusion (≈1 pp)
Restate balance penalty insight, stress need for nuanced evaluation rubrics, outline upcoming validation and cross-tier studies.

### Appendices (5–10 pp)
* Scenario examples (all framings).  
* Response excerpts w/ judge rationales (balanced vs commitment).  
* Comprehensive quantitative tables (framing spreads, temperature stats, scenario difficulty).  
* Qualitative deep dives.  
* Reproduction instructions (environment setup, commands).  

---

## 4 Analysis & Figure Checklist

| Analysis | Status | Actions |
| --- | --- | --- |
| Balance penalty mixed-effects regression | Pending | Feature engineering (`response_type`), run `statsmodels` mixed model, report β/CI/p-value, compute effect size |
| Judge-specific penalty comparison | Pending | Aggregate alignment by judge × response type; test Δ, run conditional disagreement ratios |
| Framing spread quantification | Partial (CSV exists) | Visualize means & spreads; highlight safety_first dominance |
| Temperature stability | Partial | Plot per-model curves, calculate max range (≤0.24) |
| Judge disagreement heatmap | Pending | Use `analysis_judge_agreement_by_temp.csv` & scenario aggregation to build heatmaps |
| Model ranking summary | Complete (CSV) | Convert to table/figure |

**Figures (target 8–10):**
1. Pipeline diagram (existing).  
2. Balance penalty boxplot.  
3. Regression coefficient plot.  
4. Framing effect bar chart.  
5. Judge disagreement heatmap.  
6. Temperature curves by model.  
7. Model ranking bar chart.  
8. Scenario difficulty scatter (optional).  

**Tables (target 6–8):**
1. Model specifications.  
2. Scenario/value pair overview.  
3. Regression summary.  
4. Framing spreads per model.  
5. Judge disagreement by response type.  
6. Temperature effect summary.  
7. Scenario difficulty top cases.  

---

## 5 Writing & Submission Timeline (Day-Level Tasks)

| Day | Focus | Deliverables |
| --- | --- | --- |
| 1–2 | Introduction draft | Anthropic context, RQs, contributions |
| 3–4 | Run regression & disagreement analyses | Notebook cells, intermediate tables/figures |
| 5–6 | Methods section | Detailed narrative, tables, pipeline figure |
| 7 | Results section skeleton | Insert key figures/tables, write captions |
| 8–9 | Discussion | Mechanisms, implications, Anthropic tie-back |
| 10–11 | Limitations/Future work | Include Phase 2, human validation, meta-judge plans |
| 12–13 | Abstract + Related Work + Conclusion | Finalize literature links |
| 14–15 | Generate final figures/tables | Ensure consistent styling/resolution |
| 16–17 | Appendices | Scenario examples, qualitative notes, reproduction steps |
| 18–19 | LaTeX conversion & copyedit | `arxiv` class, references, captions |
| 20–21 | Final review & submission | Peer feedback, arXiv upload, social rollout plan |

Post-submission: social media threads, Reddit posts, optional blog summary emphasizing Anthropic inspiration and balance penalty discovery.

---

## 6 Action Items & Owners

| Task | Owner | Due |
| --- | --- | --- |
| Engineer `response_type` feature & run mixed-effects regression | — | Day 3 |
| Generate balance penalty & regression coefficient figures | — | Day 4 |
| Build judge disagreement heatmap & response-type analysis | — | Day 4 |
| Draft Intro/Methods (with Anthropic framing) | — | Day 6 |
| Prepare scenario/model tables (LaTeX-ready) | — | Day 6 |
| Write Discussion with hypotheses & implications | — | Day 9 |
| Draft Limitations/Future plan (Phase 2, human validation, meta-judge) | — | Day 11 |
| Assemble appendices (scenario examples, response excerpts, reproduction guide) | — | Day 17 |
| Convert to LaTeX, manage references, compile PDF | — | Day 19 |
| Final review, arXiv submission, outreach assets | — | Day 21 |

*(Replace “—” with specific assignees as team solidifies.)*

---

## 7 Resources & Reproducibility

```bash
# Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Data generation (already completed; rerun if needed)
python scripts/run_phase1_expanded.py --iterations 10 --temperatures 0.6,0.7,0.8,0.9,1.0,0.0,0.2,0.3,0.4,0.5

# Judge evaluation
bash scripts/judge_all_phase1.sh

# Analysis notebooks & scripts
python scripts/analyze_local_results.py --input-dir results/local_runs_expanded
jupyter notebook phase1_analysis.ipynb
```

Document all preprocessing (duplicate removal, on-topic filtering) in Methods Appendix; include pointers to QA notes and qualitative interpretations.

---

## 8 Future Extensions Beyond ArXiv Snapshot

1. **Phase 2 Expansion:** adapt `run_phase2_api.py` for explicit temperature lists, generate iterations 6–10 for 6 shared scenarios on frontier APIs, mirror analyses to test balance penalty generalization.  
2. **Human Validation:** collect 50–100 human ratings on high-disagreement responses to benchmark judge bias; analyze correlation vs LLM judges.  
3. **Meta-Judge Layer:** implement `meta_judge_evaluations.py` using Claude Sonnet 4 to assess disagreement cases, providing tie-breaking and quality calibration.  
4. **Rubric Intervention Study:** experiment with modified judge prompts that reward acknowledgment of trade-offs; measure impact on balance penalty.  
5. **Scenario Expansion:** grow moral core set to ≥100 dilemmas covering broader ethical axes and cultural contexts.

---

## 9 Communication Plan

* **ArXiv Summary:** emphasize Anthropic inspiration, balance penalty insight, public availability of scripts and data.  
* **Social Posts:** Twitter/X thread, r/MachineLearning, r/AIAlignment, r/LanguageModels.  
* **Blog / Medium:** 1,000-word accessible write-up linking to preprint, focusing on practical takeaways for alignment practitioners.  
* **Follow-up Talks:** propose workshop lightning talk or reading-group session showcasing methodology and findings.

---

By executing this blueprint we translate the existing clean dataset and analyses into a clear, mechanistically grounded arXiv preprint that advances the community’s understanding of evaluator bias—directly inspired by Anthropic’s foundational stress-testing study.
