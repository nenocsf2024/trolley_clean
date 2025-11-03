# Phase 1 Expansion: Real-Time Monitoring Guide

**Status:** Expansion Started

---

## Quick Start

### Monitor Progress (Choose One)

**Option 1: Python Monitor (Recommended)**
```bash
python scripts/monitor_phase1_expansion.py
```
- Most detailed view
- Shows per-model, per-iteration, per-temperature progress
- Updates every 3 seconds
- Color-coded status (✓ COMPLETE, ● IN PROGRESS, ○ READY)

**Option 2: Bash Monitor (Simple)**
```bash
./scripts/monitor_phase1_expansion.sh
```
- Basic progress view
- Updates every 5 seconds

**Option 3: Log File**
```bash
# Find the latest log file
ls -lth /tmp/phase1_expansion_*.log | head -1

# Watch it in real-time
tail -f /tmp/phase1_expansion_*.log
```

---

## What to Expect

### Expansion Process
- **Generating:** 750 new responses (5 models × 30 scenarios × 5 iterations)
- **Temperatures:** 0.0, 0.2, 0.3, 0.4, 0.5 (iterations 6-10)
- **Time:** ~6-12 hours (depending on model speeds)
- **Output:** Appends to existing JSONL files

### Progress Indicators

**Per Model:**
- Starting: 150 responses (iterations 1-5 only)
- During: 150-300 responses (iterations 6-10 being added)
- Complete: 300 responses (all 10 iterations)

**Temperature Coverage:**
- Before: [0.6, 0.7, 0.8, 0.9, 1.0]
- After: [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

---

## Manual Status Check

```bash
# Quick check: Count responses per model
wc -l results/local_runs_expanded/*.jsonl | grep -v judge | grep -v summary

# Detailed check: Verify iterations
python scripts/check_phase1_iterations.py \
    --input-dir results/local_runs_expanded \
    --verbose
```

---

## Troubleshooting

### Process Stopped?
```bash
# Check if process is running
pgrep -f "run_phase1_expanded"

# If not, restart (resume mode will skip completed work)
./scripts/add_low_temp_iterations.sh
```

### Check for Errors
```bash
# Look for error messages in log
grep -i error /tmp/phase1_expansion_*.log

# Or in the JSONL files
grep -l '"error"' results/local_runs_expanded/*.jsonl
```

### Verify Resume Mode
- Resume mode checks for existing (scenario_id, iteration) pairs
- If iteration exists with response → skips
- If iteration missing → generates
- Safe to restart if process stops

---

## Completion Verification

When expansion is complete, verify:

```bash
# 1. Check all models have 300 responses
python scripts/check_phase1_iterations.py \
    --input-dir results/local_runs_expanded

# 2. Verify temperature coverage
python3 << 'EOF'
import json
from pathlib import Path

expected_temps = {0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}

for f in Path("results/local_runs_expanded").glob("*.jsonl"):
    if "judge" in f.stem or "summary" in f.stem:
        continue
    
    temps = set()
    with open(f) as file:
        for line in file:
            if line.strip():
                data = json.loads(line)
                if data.get("temperature") is not None:
                    temps.add(data.get("temperature"))
    
    missing = expected_temps - temps
    if missing:
        print(f"{f.stem}: Missing temps {sorted(missing)}")
    else:
        print(f"{f.stem}: ✓ All temperatures present")
EOF

# 3. Final summary
echo "Expected: 5 models × 30 scenarios × 10 iterations = 1,500 responses"
find results/local_runs_expanded -name "*.jsonl" ! -name "*judge*" ! -name "*summary*" -exec wc -l {} + | tail -1
```

---

**Next Steps After Completion:**
1. Verify all 1,500 responses are complete
2. Judge new iterations: `./scripts/judge_all_phase1.sh`
3. Generate comprehensive analysis

