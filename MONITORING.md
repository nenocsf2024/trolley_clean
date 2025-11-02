# Phase 1 Data Generation Monitoring Guide

## Quick Status Check

Run the monitoring script:
```bash
./scripts/monitor_phase1.sh
```

Or watch it update every 5 seconds:
```bash
watch -n 5 ./scripts/monitor_phase1.sh
```

## Manual Monitoring Commands

### 1. Check if Process is Running
```bash
ps aux | grep run_phase1_expanded | grep -v grep
```

### 2. Count Current Responses Per Model
```bash
# Quick count
wc -l results/local_runs_expanded/*.jsonl

# Detailed breakdown
for file in results/local_runs_expanded/*.jsonl; do
    model=$(basename "$file" .jsonl)
    count=$(wc -l < "$file" 2>/dev/null || echo "0")
    echo "$model: $count responses"
done
```

### 3. Watch File Sizes (Note: Only Updates When Model Completes)
```bash
# Files use batch writes - only update at model completion
watch -n 10 'ls -lh results/local_runs_expanded/*.jsonl 2>/dev/null | awk "{print \$9, \$5}"'

# For real-time progress, monitor the log instead:
watch -n 5 'tail -10 /tmp/phase1_generation.log'
```

### 4. Check Most Recent Activity
```bash
ls -lt results/local_runs_expanded/*.jsonl | head -3
```

### 5. Validate Current Coverage
```bash
python scripts/check_phase1_iterations.py --input-dir results/local_runs_expanded
```

### 6. Monitor Process Log (Real-Time Progress)
```bash
# Watch the generation log for real-time progress
tail -f /tmp/phase1_generation.log

# This shows each response as it's being generated:
# mistral:7b-instruct [MC21-001-N] iter 1 temp=0.60 seed=123456789
```

**Note:** JSONL files use batch writes - they only update when a model finishes all 150 responses. For real-time progress, monitor the log file instead.

## Expected Progress

- **Total responses needed**: 750 (5 models × 30 scenarios × 5 iterations)
- **Per model**: 150 responses (30 scenarios × 5 iterations)
- **Per scenario**: 5 responses (5 iterations)

## Important: Batch Writing Behavior

⚠️ **JSONL files use batch writes:**
- Files only update when a model completes ALL 150 responses
- Files won't show incremental progress during generation
- Monitor progress via the log file: `tail -f /tmp/phase1_generation.log`
- Each response takes ~100-200 seconds, so progress appears slowly

## Completion Indicators

✅ Each JSONL file should have exactly 150 lines (one per response)
✅ All 5 model files should exist when complete
✅ Summary CSV should show 750 total entries
✅ Validation script should show no warnings
✅ Log file should show completion messages for all models

## Troubleshooting

If progress stalls:
1. **Check the log for errors**: `tail -50 /tmp/phase1_generation.log`
2. **Check if process is running**: `ps aux | grep run_phase1_expanded | grep python`
3. **Check Ollama is responding**: `curl http://localhost:11434/api/tags`
4. **Note**: Files won't update until model completes - check log for activity
5. **Restart if needed**: Kill the process and re-run (no `--overwrite` needed if files were cleaned)

## Quick Validation

After completion, run:
```bash
python scripts/check_phase1_iterations.py \
    --input-dir results/local_runs_expanded \
    --verbose
```

This should show:
- All 5 models with 150 responses each
- All 30 scenarios with 5 iterations each
- No warnings

