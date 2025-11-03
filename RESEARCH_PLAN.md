# Research Plan: Two-Paper Strategy

**Last Updated:** 2025-01-XX  
**Status:** Planning Phase

---

## Strategy Overview

**Priority 1:** Complete Phase 1 fully  
**Priority 2:** Design Phase 2 expansion for comparative analysis  
**Outcome:** Two separate research papers

---

## Paper 1: Phase 1 Standalone Analysis

### Scope
**Phase 1 only** - Complete local model analysis

### Data Requirements
- ✅ 5 local Ollama models
- ✅ 30 scenarios (full set)
- ✅ 10 iterations per scenario
- ✅ Full temperature range: 0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0
- ✅ Total responses: 1,500 (5 models × 30 scenarios × 10 iterations)

### Current Status
- ✅ 5 models complete
- ✅ 30 scenarios complete
- ✅ 5 iterations complete (1-5)
- ✅ Temperatures 0.6-1.0 complete
- ❌ 5 iterations missing (6-10)
- ❌ Temperatures 0.0-0.5 missing
- **Completion:** 50% (750/1,500 responses)

### Action Items
1. **Generate iterations 6-10** with temperatures 0.0, 0.2, 0.3, 0.4, 0.5
   - Script: `scripts/add_low_temp_iterations.sh`
   - Cost: FREE (local compute)
   - Time: ~6-12 hours
   - Adds: 750 responses

2. **Verify completion**
   - Check all models have 150 responses each (30 scenarios × 10 iterations)
   - Verify temperature coverage: 0.0-1.0 (10 distinct temperatures)
   - Validate data quality

3. **Run analysis**
   - Generate comprehensive Phase 1 analysis
   - Temperature effect analysis (0.0-1.0)
   - Model comparison across scenarios
   - Framing effect analysis
   - Value preference patterns

### Research Questions (Paper 1)
1. How do local 7B models handle moral dilemmas across different scenarios?
2. What is the effect of temperature on moral reasoning consistency?
3. Do different framings (neutral, safety_first, freedom_first) affect model responses?
4. Which scenarios show the most disagreement between models?
5. How consistent are model responses across temperature ranges?
6. What are the patterns in value preference alignment?

---

## Paper 2: Comparative Analysis (Phase 1 + Phase 2)

### Scope
**Shared scenarios only** - Compare local vs API models

### Data Requirements

#### Phase 1 (Subset)
- 5 local Ollama models
- **6 scenarios** (shared with Phase 2)
- 10 iterations per scenario
- Full temperature range: 0.0-1.0 (10 temperatures)
- Total: 300 responses (5 models × 6 scenarios × 10 iterations)

#### Phase 2 (Expanded)
- 5 API models
- **6 scenarios** (same as Phase 1 subset)
- 10 iterations per scenario
- **Full temperature range: 0.0-1.0** (mirror Phase 1)
  - Must match Phase 1's 10 distinct temperatures
- Total: 300 responses (5 models × 6 scenarios × 10 iterations)

### Shared Scenarios (6)
1. MC21-005-F - Climate Policy (environment_vs_growth, freedom_first)
2. MC21-005-N - Climate Policy (environment_vs_growth, neutral)
3. MC21-002-S - Algorithmic Hiring (efficiency_vs_fairness, safety_first)
4. MC21-006-F - Mental Health Crisis (autonomy_vs_safety, freedom_first)
5. MC21-003-N - Social Media Moderation (safety_vs_freedom, neutral)
6. MC21-007-N - Autonomous Vehicles (fairness_vs_efficiency, neutral)

### Current Phase 2 Status
- ✅ 5 API models
- ✅ 6 scenarios (correct subset)
- ✅ 5 iterations
- ✅ Temperature ~0.7 (±0.05 jitter)
- **Completion:** ~50% (150/300 responses needed)

### Phase 2 Expansion Required

**Current:** 150 responses (5 models × 6 scenarios × 5 iterations)  
**Needed:** 300 responses (5 models × 6 scenarios × 10 iterations)  
**Missing:** 150 additional responses

**Temperature Expansion:**
- Current: ~0.7 ± 0.05 (narrow range)
- Needed: 0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 (10 distinct temperatures)
- **Approach:** Use explicit temperatures per iteration (like Phase 1), not jitter

**Cost Estimate:**
- Current Phase 2: ~$0.69 (150 responses)
- Expansion needed: ~$0.69 (additional 150 responses)
- **Total for Paper 2 Phase 2: ~$1.38**

### Action Items (Phase 2 Expansion)

1. **Modify Phase 2 script** to support explicit temperatures
   - Update `scripts/run_phase2_api.py`
   - Add `--temperatures` parameter (like Phase 1)
   - Use explicit temperature per iteration (0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
   - Remove random jitter approach

2. **Generate additional iterations**
   - Add iterations 6-10 to existing Phase 2 data
   - Use explicit temperatures to match Phase 1
   - Preserve existing work (iterations 1-5)

3. **Verify completion**
   - Check all models have 60 responses each (6 scenarios × 10 iterations)
   - Verify temperature coverage matches Phase 1 (0.0-1.0)
   - Validate alignment with Phase 1 subset

### Research Questions (Paper 2)
1. How do local 7B models compare to API models on shared scenarios?
2. Do temperature effects differ between local and API models?
3. Which models show more consistency across temperature ranges?
4. Are value preferences consistent between local and API models?
5. How does model scale/architecture affect moral reasoning?
6. What are the patterns of agreement/disagreement between local and API models?

---

## Implementation Timeline

### Phase 1 Completion (Priority 1)

**Step 1: Generate Missing Iterations**
```bash
# Generate iterations 6-10 with temperatures 0.0-0.5
./scripts/add_low_temp_iterations.sh
```

**Step 2: Verify Completion**
```bash
# Check all models have 150 responses each
python scripts/check_phase1_iterations.py \
    --input-dir results/local_runs_expanded \
    --verbose
```

**Step 3: Judge Responses (if not already done)**
```bash
# Judge all Phase 1 responses with both judges
./scripts/judge_all_phase1.sh
```

**Step 4: Generate Paper 1 Analysis**
```bash
# Comprehensive Phase 1 analysis
python scripts/analyze_local_results.py \
    --input-dir results/local_runs_expanded

# Temperature-specific analysis
# (may need new script for temperature effect analysis)
```

### Phase 2 Expansion (Priority 2 - After Paper 1)

**Step 1: Modify Phase 2 Script**
- Update to support explicit temperatures
- Match Phase 1's temperature approach

**Step 2: Generate Expanded Phase 2**
- Add iterations 6-10 with explicit temperatures
- Match Phase 1's 10-temperature approach

**Step 3: Generate Paper 2 Analysis**
- Extract Phase 1 subset (6 scenarios)
- Compare with Phase 2 (6 scenarios)
- Analyze temperature effects across both phases

---

## Key Design Decisions

### Temperature Matching Strategy

**Paper 2 Requirement:** Phase 1 and Phase 2 must use identical temperature settings

**Approach:**
- Phase 1: Explicit temperatures [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
- Phase 2: **Must match** - use same explicit temperatures
- **Do NOT use:** Random jitter (current Phase 2 approach)
- **Use:** Explicit temperature per iteration (like Phase 1)

### Scenario Selection Strategy

**Paper 2:** Use only the 6 scenarios that Phase 2 currently has

**Rationale:**
- Phase 2 already has these 6 scenarios
- Represents diverse topics, value pairs, and framings
- Minimizes Phase 2 expansion cost
- Provides sufficient data for comparison

---

## Cost Summary

### Paper 1 (Phase 1)
- **Cost:** FREE (local compute)
- **Time:** ~6-12 hours for missing iterations

### Paper 2 (Phase 1 + Phase 2)
- **Phase 1 subset:** FREE (already generated, just extract)
- **Phase 2 expansion:** ~$1.38 total
  - Current: ~$0.69
  - Additional: ~$0.69
- **Time:** ~2-4 hours for Phase 2 expansion

---

## Deliverables

### Paper 1 Deliverables
1. Complete Phase 1 dataset (1,500 responses)
2. Comprehensive Phase 1 analysis
3. Temperature effect analysis (0.0-1.0)
4. Model comparison across 30 scenarios
5. Framing effect analysis

### Paper 2 Deliverables
1. Phase 1 subset (300 responses from 6 scenarios)
2. Expanded Phase 2 dataset (300 responses from 6 scenarios)
3. Comparative analysis (local vs API models)
4. Temperature effect comparison
5. Alignment analysis across model types

---

## Next Steps

1. ✅ **Complete Phase 1** (Priority 1)
   - Run `scripts/add_low_temp_iterations.sh`
   - Verify completion
   - Generate Paper 1 analysis

2. ⏸️ **Phase 2 expansion** (Priority 2 - after Paper 1)
   - Modify Phase 2 script for explicit temperatures
   - Generate expanded Phase 2 data
   - Prepare Paper 2 comparative analysis

---

**Related Documents:**
- `PHASE1_GAPS.md` - What's missing from Phase 1
- `PHASE1_VS_PHASE2_COMPARISON.md` - Detailed comparison
- `PHASE2_COST_SUMMARY.md` - Phase 2 expansion costs
- `SCENARIOS_LIST.md` - Complete scenario listing

