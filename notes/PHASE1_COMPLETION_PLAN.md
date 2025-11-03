# Phase 1 Completion Plan

**Status:** Analysis Complete - Ready to Execute  
**Date:** 2025-01-XX

---

## Current State Analysis

### ✅ What's Working

1. **Data Integrity (4 of 5 models):**
   - ✅ `gemma_2b-instruct`: 150 responses, clean
   - ✅ `mistral_7b-instruct`: 150 responses, clean
   - ✅ `orca-mini_7b`: 150 responses, clean
   - ✅ `phi3_mini`: 150 responses, clean
   - ⚠️ `llama3_8b`: 300 responses, **has duplicates** (needs cleanup)

2. **Coverage:**
   - ✅ All 5 models have 30/30 scenarios
   - ✅ All models have iterations 1-5 complete
   - ✅ All models have temperatures 0.6-1.0

3. **Resume Logic:**
   - ✅ Script correctly implements resume mode
   - ✅ Checks for (scenario_id, iteration) pairs
   - ✅ Skips existing iterations if they have responses
   - ✅ Uses append mode by default (preserves existing data)

### ⚠️ Issue Found

**llama3_8b.jsonl has duplicate records:**
- Has 300 responses instead of expected 150
- Every (scenario_id, iteration) pair appears twice
- Likely caused by accidental double-write or append

**Impact:** Resume mode will skip duplicates, but file is bloated

**Solution:** Remove duplicates before expansion

---

## Completion Strategy

### Step 1: Clean llama3_8b.jsonl

**Action:** Remove duplicate records, keep first occurrence

**Script:**
```python
# Keep first occurrence of each (scenario_id, iteration) pair
```

**Verification:** Ensure file has exactly 150 unique responses

### Step 2: Verify All Models

**Action:** Confirm all models have:
- 30 scenarios
- 5 iterations per scenario (1-5)
- 150 total responses
- Temperatures: [0.6, 0.7, 0.8, 0.9, 1.0]

### Step 3: Run Expansion

**Action:** Execute `scripts/add_low_temp_iterations.sh`

**What it does:**
- Sets `OLLAMA_RESUME=1` (enables resume mode)
- Runs with `--iterations 10`
- Provides temperatures: `0.6,0.7,0.8,0.9,1.0,0.0,0.2,0.3,0.4,0.5`
- Resume mode skips iterations 1-5 (already exist)
- Generates only iterations 6-10 (temperatures 0.0-0.5)
- Uses append mode (adds to existing files)

**Expected Result:**
- Each model gets 150 additional responses
- Total per model: 300 responses (30 scenarios × 10 iterations)
- Temperature coverage: 0.0-1.0 (all 10 temperatures)

### Step 4: Verify Completion

**Action:** Check final state

**Verification:**
- All models have 300 responses
- All models have iterations 1-10
- All models have temperatures 0.0-1.0
- Total: 1,500 responses (5 models × 300)

---

## Detailed Execution Plan

### Pre-Expansion: Cleanup

1. **Fix llama3_8b.jsonl duplicates**
   ```bash
   # Create backup first
   cp results/local_runs_expanded/llama3_8b.jsonl results/local_runs_expanded/llama3_8b.jsonl.backup
   
   # Remove duplicates (keep first occurrence)
   python scripts/fix_duplicates.py results/local_runs_expanded/llama3_8b.jsonl
   ```

2. **Verify cleanup**
   ```bash
   python scripts/check_phase1_iterations.py \
       --input-dir results/local_runs_expanded \
       --verbose
   ```

### Expansion Execution

1. **Dry-run test** (optional but recommended)
   ```bash
   ./scripts/add_low_temp_iterations.sh --dry-run
   ```
   - Verifies configuration without generating data
   - Checks that resume mode will work correctly

2. **Actual expansion**
   ```bash
   ./scripts/add_low_temp_iterations.sh
   ```
   - Runs in background (recommended)
   - Takes ~6-12 hours depending on model speeds
   - Can monitor progress by checking file sizes

3. **Monitor progress** (during execution)
   ```bash
   # Watch file sizes grow
   watch -n 60 'wc -l results/local_runs_expanded/*.jsonl | tail -1'
   
   # Or check iteration counts
   python scripts/check_phase1_iterations.py --input-dir results/local_runs_expanded
   ```

### Post-Expansion: Verification

1. **Verify completion**
   ```bash
   python scripts/check_phase1_iterations.py \
       --input-dir results/local_runs_expanded \
       --verbose
   ```
   
   **Expected output:**
   - Each model: 300 responses total
   - Each scenario: 10 iterations (1-10)
   - Temperature coverage: All models have [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

2. **Verify data quality**
   ```bash
   # Check for errors, missing responses
   python scripts/validate_phase1_quality.py \
       --input-dir results/local_runs_expanded
   ```

3. **Generate final summary**
   ```bash
   # Update README.txt with final counts
   python scripts/run_phase1_expanded.py \
       --output-dir results/local_runs_expanded \
       --iterations 10
   # (This will just regenerate the README, not re-run generation)
   ```

---

## Resume Mode Details

### How Resume Mode Works

1. **Environment variable:** `OLLAMA_RESUME=1` enables resume mode
2. **File reading:** Script reads existing file and builds lookup table
3. **Lookup key:** `(scenario_id, iteration)` tuple
4. **Skip condition:** If key exists AND has `response` field → skip
5. **Write mode:** Append (adds new records, doesn't overwrite)

### Temperature Assignment

**Command:**
```bash
--iterations 10 --temperatures 0.6,0.7,0.8,0.9,1.0,0.0,0.2,0.3,0.4,0.5
```

**Mapping:**
- Iteration 1 → 0.6 (exists, skip)
- Iteration 2 → 0.7 (exists, skip)
- Iteration 3 → 0.8 (exists, skip)
- Iteration 4 → 0.9 (exists, skip)
- Iteration 5 → 1.0 (exists, skip)
- Iteration 6 → 0.0 (**generate**)
- Iteration 7 → 0.2 (**generate**)
- Iteration 8 → 0.3 (**generate**)
- Iteration 9 → 0.4 (**generate**)
- Iteration 10 → 0.5 (**generate**)

**Result:** Only iterations 6-10 are generated, with temperatures 0.0-0.5

---

## Risk Assessment

### Low Risk ✅
- Resume logic is well-tested and correct
- Append mode preserves existing data
- Temperature assignment is verified
- 4 of 5 models are clean and ready

### Medium Risk ⚠️
- **llama3_8b duplicates:** Needs cleanup before expansion
  - **Mitigation:** Remove duplicates first
  - **Impact if skipped:** File will have 300 duplicates + 150 new = 450 total (wrong)

### Execution Risks
- **Process interruption:** If script stops mid-run
  - **Mitigation:** Resume mode will skip completed iterations on restart
  - **Recovery:** Re-run the same command, it will continue where it left off

- **Ollama crashes:** Model failures during generation
  - **Mitigation:** Script handles errors gracefully, records error in JSON
  - **Recovery:** Re-run to retry failed generations

---

## Success Criteria

Phase 1 is complete when:

1. ✅ All 5 models have 300 responses each
2. ✅ All 30 scenarios have 10 iterations each
3. ✅ All models have all 10 temperatures (0.0-1.0)
4. ✅ Total: 1,500 responses (5 × 30 × 10)
5. ✅ No duplicate records
6. ✅ All responses have valid data (no errors)

---

## Next Steps After Completion

1. **Judge new iterations:**
   ```bash
   ./scripts/judge_all_phase1.sh
   ```
   - Judges all responses (including new iterations 6-10)
   - Uses GPT-4o-mini and Claude 3.5 Haiku

2. **Generate comprehensive analysis:**
   ```bash
   python scripts/analyze_local_results.py \
       --input-dir results/local_runs_expanded
   ```

3. **Temperature effect analysis:**
   - Analyze how temperature affects value preferences
   - Compare low-temp (0.0-0.5) vs high-temp (0.6-1.0) behavior
   - Generate temperature-response curves

4. **Prepare for Paper 1:**
   - Complete Phase 1 dataset ready
   - Full temperature range coverage
   - All 30 scenarios analyzed

---

**Related Documents:**
- `PHASE1_GAPS.md` - What was missing
- `RESEARCH_PLAN.md` - Two-paper strategy
- `scripts/add_low_temp_iterations.sh` - Expansion script

