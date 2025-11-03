# Low-Temperature Expansion Plan (Option A)

## Overview
Add iterations 6-10 with low temperatures (0.0, 0.2, 0.3, 0.4, 0.5) to complete temperature coverage (0.0 - 1.0).

## What Will Be Added
- **750 new responses**: 5 models × 30 scenarios × 5 iterations (6-10)
- **Temperatures**: 0.0 (deterministic), 0.2, 0.3, 0.4, 0.5
- **Total after expansion**: 1,500 responses (750 existing + 750 new)

## Safety Guarantees
✅ **All existing work preserved**:
- Existing iterations 1-5 remain untouched
- All judge evaluations remain intact
- All analysis files unchanged
- Uses append mode (no overwrites)
- Resume mode skips existing iterations

## Execution

### Option 1: Using the prepared script (Recommended)
```bash
./scripts/add_low_temp_iterations.sh
```

### Option 2: Manual command
```bash
export OLLAMA_RESUME=1
python scripts/run_phase1_expanded.py \
    --iterations 10 \
    --temperatures 0.6,0.7,0.8,0.9,1.0,0.0,0.2,0.3,0.4,0.5 \
    --output-dir results/local_runs_expanded
```

## Timeline
- **Generation**: ~8-10 hours (can run overnight)
- **Judging**: ~20-25 hours after generation completes
- **Total**: ~30 hours (mostly automated, can pause/resume)

## Verification

Before running:
```bash
wc -l results/local_runs_expanded/*.jsonl
```

After running:
```bash
wc -l results/local_runs_expanded/*.jsonl  # Should show doubled counts
python3 -c "
import json
f = open('results/local_runs_expanded/mistral_7b-instruct.jsonl')
data = [json.loads(l) for l in f if l.strip()]
print(f'Total: {len(data)}')
iters = sorted(set(d['iteration'] for d in data))
print(f'Iterations: {iters}')
temps = sorted(set(d['temperature'] for d in data))
print(f'Temperatures: {temps}')
"
```

## What This Enables
1. **Deterministic baseline** (temp=0) for every model+scenario
2. **Complete temperature sensitivity curves** (0.0 → 1.0)
3. **Full model comparisons** at all temperatures
4. **Complete scenario-level analysis**
5. **Answers all research questions** definitively

## After Generation Completes
Run judging for all responses (old + new):
```bash
./scripts/judge_all_phase1.sh
```

This will judge ALL responses including the new iterations 6-10.

