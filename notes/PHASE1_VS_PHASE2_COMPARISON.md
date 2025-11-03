# Phase 1 vs Phase 2: Complete Comparison

**Last Updated:** 2025-01-XX

---

## Side-by-Side Comparison

| Aspect | Phase 1 (Local Models) | Phase 2 (API Models) |
|--------|------------------------|----------------------|
| **Models** | 5 local Ollama models | 5 API-based models |
| | • `mistral:7b-instruct` | • `claude-sonnet-4-20250514` |
| | • `gemma:2b-instruct` | • `gpt-4o-mini` |
| | • `phi3:mini` | • `mistral-large-latest` |
| | • `llama3:8b` | • `gemini-2.5-flash-lite` |
| | • `orca-mini:7b` | • `grok-3-latest` |
| **Scenarios** | **30 scenarios** (full set) | **6 scenarios** (selected shortlist) |
| | All scenarios from `moral_core_21_sample.jsonl` | Selected subset: |
| | | • MC21-005-F (Climate Policy - freedom_first) |
| | | • MC21-005-N (Climate Policy - neutral) |
| | | • MC21-002-S (Algorithmic Hiring - safety_first) |
| | | • MC21-006-F (Mental Health - freedom_first) |
| | | • MC21-003-N (Social Media Moderation - neutral) |
| | | • MC21-007-N (Autonomous Vehicles - neutral) |
| **Iterations** | **10 total** (planned) | **5 per scenario** |
| | • 5 completed (iterations 1-5) | |
| | • 5 planned (iterations 6-10) | |
| **Temperature Range** | **0.0 - 1.0** (full range) | **~0.7** (with jitter) |
| | • Iterations 1-5: `0.6, 0.7, 0.8, 0.9, 1.0` | • Base: `0.7` |
| | • Iterations 6-10: `0.0, 0.2, 0.3, 0.4, 0.5` (planned) | • Jitter: `±0.05` random |
| | | • Actual range: `0.65 - 0.75` |
| **Temperature Method** | Explicit per iteration | Random jitter around base |
| | Each iteration has fixed temperature | `temp = 0.7 + random.uniform(-0.05, 0.05)` |
| **Seeds** | Deterministic (auto-generated) | Not specified (random) |
| | Based on model name + scenario ID + iteration | |
| **Cost** | **FREE** (local compute) | **~$0.69** total |
| | No API costs | Per model: |
| | | • GPT-4o-mini: $0.009 |
| | | • Gemini 2.5 Flash Lite: $0.029 |
| | | • Mistral Large: $0.17 |
| | | • Grok 3: $0.21 |
| | | • Claude Sonnet 4: $0.27 |
| **Total Responses** | **1,500** (30 × 5 × 10) | **150** (6 × 5 × 5) |
| | 30 scenarios × 5 models × 10 iterations | 6 scenarios × 5 models × 5 iterations |
| **Response Format** | JSONL with metadata | JSONL with metadata |
| | Includes: model, id, iteration, seed, temperature | Includes: scenario_id, iteration, model, |
| | topic, value_pair, framing, sensitivity | temperature_used, latency_s, response |
| | response, eval_time_s | topic, value_pair, framing |
| **Output Directory** | `results/local_runs_expanded/` | `results/phase2/` |
| **Execution Speed** | Slower (local inference) | Faster (API responses) |
| | ~30-60s per response | ~1-10s per response |

---

## Temperature Comparison Details

### Phase 1 Temperature Strategy

**Current (Iterations 1-5):**
- Fixed temperatures: `[0.6, 0.7, 0.8, 0.9, 1.0]`
- One temperature per iteration
- Systematic coverage of mid-to-high range

**Planned (Iterations 6-10):**
- Fixed temperatures: `[0.0, 0.2, 0.3, 0.4, 0.5]`
- One temperature per iteration
- Systematic coverage of low range
- **Total coverage: 0.0 to 1.0 (10 distinct temperatures)**

### Phase 2 Temperature Strategy

**Current:**
- Base temperature: `0.7`
- Random jitter: `±0.05`
- Actual range: `0.65 - 0.75` per call
- No systematic coverage of low temperatures
- Focused on mid-range stochasticity

---

## Design Rationale

### Why Different Approaches?

| Phase | Design Goal | Rationale |
|-------|------------|-----------|
| **Phase 1** | Comprehensive, systematic | Local models = FREE → Why not test everything? |
| | • All 30 scenarios | • Full scenario coverage at zero cost |
| | • Full temperature range (0.0-1.0) | • Complete temperature analysis |
| | • 10 iterations for stability | • Sufficient samples for variance analysis |
| **Phase 2** | Cost-efficient, representative | API models = EXPENSIVE → Control costs |
| | • 6 selected scenarios | • Representative subset to validate patterns |
| | • Narrow temperature range (~0.7) | • Focus on typical use case |
| | • 5 iterations | • Balance between coverage and cost |

### The Mismatch

**Current State:**
- Phase 1: Designed for completeness (cost-free)
- Phase 2: Designed for cost efficiency (representative sample)
- **Result:** Can't fully compare local vs API models across all scenarios

**Implications:**
- 24 scenarios missing API data
- Temperature analysis incomplete for API models
- Scenario-specific patterns unclear
- Limited cross-phase comparison

---

## Expansion Options

### Option 1: Add Low Temperatures to Phase 2 (6 scenarios)
**Cost:** ~$3.42  
**What it adds:** 150 additional responses with temperatures 0.0-0.5  
**Coverage:** Temperature range expanded, but still only 6 scenarios

### Option 2: Full Expansion (30 scenarios × 10 iterations)
**Cost:** ~$34.40  
**What it adds:** Complete parity with Phase 1  
**Coverage:** All scenarios + full temperature range (0.0-1.0)

---

## Key Differences Summary

1. **Scenario Coverage:**
   - Phase 1: 30 scenarios (100%)
   - Phase 2: 6 scenarios (20%)

2. **Temperature Coverage:**
   - Phase 1: 10 distinct temperatures (0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
   - Phase 2: Continuous range ~0.65-0.75 (narrow band)

3. **Iteration Count:**
   - Phase 1: 10 iterations per scenario (planned)
   - Phase 2: 5 iterations per scenario

4. **Model Type:**
   - Phase 1: 7B parameter local models
   - Phase 2: Various sizes, hosted APIs

5. **Cost:**
   - Phase 1: $0 (local compute)
   - Phase 2: ~$0.69 current, ~$34.40 for full expansion

---

## Notes

- Phase 1 low-temperature iterations (6-10) are **in progress** or **planned**
- Phase 2 currently uses randomized temperature jitter rather than systematic coverage
- Both phases use the same prompt format and system instructions
- Phase 1 scenarios include all framings (neutral, safety_first, freedom_first)
- Phase 2 scenarios are a mix of framings selected from Phase 1 analysis

---

**Related Documents:**
- `PHASE2_API_PRICING.md` - Detailed API pricing information
- `PHASE2_COST_SUMMARY.md` - Cost summary and expansion estimates
- `RESEARCH_CONTEXT.md` - Research background and methodology

