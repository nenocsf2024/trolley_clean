# Monitoring Phase 1 Judging

## Quick Status Check

```bash
./scripts/monitor_judging.sh
```

This shows:
- ✓ Process status (running/stopped)
- ✓ CSV file progress (rows completed per file)
- ✓ Overall progress (X/10 jobs complete)
- ✓ Recent log activity
- ⚠️ Any errors

## Continuous Monitoring

### Option 1: Watch the monitor script (updates every 10 seconds)
```bash
watch -n 10 ./scripts/monitor_judging.sh
```

### Option 2: Watch the log file (real-time progress)
```bash
tail -f judging.log
```

### Option 3: Watch CSV files being updated
```bash
watch -n 5 'ls -lht results/local_runs_expanded/judges/*.csv 2>/dev/null | head -5'
```

## Expected Output

### File Structure
Each judge generates a CSV file:
```
results/local_runs_expanded/judges/judge_{model}_by_{judge}.csv
```

Examples:
- `judge_mistral_7b_instruct_by_gpt_4o_mini.csv`
- `judge_gemma_2b_instruct_by_claude_3_5_haiku_20241022.csv`

### Progress Indicators

**✓ Complete:** File has 150 rows
```
✓ mistral_7b_instruct × gpt_4o_mini: COMPLETE (150 rows, 45K)
```

**⏳ In Progress:** File has <150 rows
```
⏳ gemma_2b_instruct × gpt_4o_mini: 73/150 rows (22K)
```

**○ Not Started:** File doesn't exist yet
```
○ phi3_mini × claude_3_5_haiku_20241022: Not started
```

## Expected Timeline

- **Total jobs:** 10 (5 models × 2 judges)
- **Per job:** ~2.5-5 minutes (150 responses × 1-10s delay + API time)
- **Total time:** ~25-50 minutes for all jobs

### Rate Limits
- **OpenAI (gpt-4o-mini):** 1.0s delay (60 requests/min) - Safe
- **Anthropic (claude-3-5-haiku):** 12.0s delay (5 requests/min) - Conservative

## Troubleshooting

### Process Not Running
```bash
# Check if it died
ps aux | grep judge_responses.py

# Restart if needed
nohup bash ./scripts/judge_all_phase1.sh > judging.log 2>&1 &
```

### Files Not Updating
```bash
# Check recent log activity
tail -20 judging.log

# Check for errors
grep -i error judging.log | tail -10

# Verify CSV files exist and have rows
wc -l results/local_runs_expanded/judges/*.csv
```

### Verify Data Quality
```bash
# Check a completed file
head -5 results/local_runs_expanded/judges/judge_mistral_7b_instruct_by_gpt_4o_mini.csv

# Count valid vs error rows
python3 << 'EOF'
import csv
from pathlib import Path

f = Path("results/local_runs_expanded/judges/judge_mistral_7b_instruct_by_gpt_4o_mini.csv")
if f.exists():
    with open(f) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    
    errors = [r for r in rows if r.get('error')]
    valid = [r for r in rows if r.get('alignment_score') and not r.get('error')]
    
    print(f"Total: {len(rows)}")
    print(f"Valid (with scores): {len(valid)}")
    print(f"Errors: {len(errors)}")
EOF
```

### Check API Token Usage
- **OpenAI:** Check usage dashboard at https://platform.openai.com/usage
- **Mistral:** Check your Mistral account dashboard

Token consumption should be visible within a few minutes of starting.

## Completion

When all 10 jobs complete:
```
Progress: 10/10 complete, 0 in progress
```

All files will show:
```
✓ {model} × {judge}: COMPLETE (150 rows, ...)
```

You can then proceed to analysis!

