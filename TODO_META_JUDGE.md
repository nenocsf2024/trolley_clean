# TODO: Meta-Judge Evaluation Layer

## Status: ⏸️ Deferred - To implement after initial judging completes

## Idea
Add a third judge (Claude Sonnet 4) to evaluate the evaluations made by GPT-4o-mini and Claude 3.5 Haiku.

## When to implement
✅ After all initial judging is complete (10/10 jobs done)
✅ After EDA is complete and we have baseline analysis
✅ As an enhancement/extension

## Approach
- **Selective meta-judging**: Only cases where judges disagree significantly
  - Criteria: Alignment score difference ≥2 OR different value preferences
  - Estimated: ~30-40% of cases (~450-600 API calls)
- **Meta-judge**: Claude Sonnet 4 (or Claude 3.5 Sonnet)

## Implementation notes
- Script: `scripts/meta_judge_evaluations.py`
- Input: Combined judge CSVs from both judges
- Output: `results/local_runs_expanded/meta_judges/meta_judge_[scenario_id]_[model].csv`
- Filter: Only meta-judge cases where judges disagree

## Research value
- Follows Anthropic paper's finding about evaluator disagreement
- Novel contribution: Systematic analysis of which judge is "right"
- Quality control for evaluation reliability
- Identifies systematic judge biases

## Reference
See `META_JUDGE_ANALYSIS.md` for full analysis.


