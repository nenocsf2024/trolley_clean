#!/bin/bash
# Quick script to check if Phase 1 process is actively running

PID=$(pgrep -f "run_phase1_expanded.py" | head -1)

if [ -z "$PID" ]; then
    echo "❌ Phase 1 process is NOT running"
    exit 1
fi

echo "✓ Phase 1 process is running (PID: $PID)"
ps -p $PID -o pid,pcpu,pmem,etime,stat

# Check if process is in uninterruptible sleep (D state) which might indicate I/O wait
STAT=$(ps -p $PID -o stat --no-headers)
if [[ "$STAT" == *"D"* ]]; then
    echo "⚠️  Process may be waiting on I/O (deepseek-r1:7b can be slow)"
fi

# Check recent file activity
echo ""
echo "Recent file activity:"
find results/local_runs_expanded -name "*.jsonl" -mmin -5 -ls 2>/dev/null | head -5 || echo "No files modified in last 5 minutes"



