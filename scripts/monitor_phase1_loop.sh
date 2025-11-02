#!/bin/bash
# Regular monitoring loop for Phase 1 generation

INTERVAL=${1:-30}  # Check every 30 seconds by default
MAX_CHECKS=${2:-20}  # Stop after 20 checks (~10 minutes)

echo "Phase 1 Monitoring Loop"
echo "======================"
echo "Checking every ${INTERVAL} seconds (max ${MAX_CHECKS} checks)"
echo ""

CHECK_COUNT=0

while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    CHECK_COUNT=$((CHECK_COUNT + 1))
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo ""
    echo "[$TIMESTAMP] Check #$CHECK_COUNT"
    echo "----------------------------------------"
    
    # Check if process is running
    PID=$(pgrep -f "run_phase1_expanded.py" | head -1)
    if [ -z "$PID" ]; then
        echo "❌ Process is NOT running!"
        break
    fi
    
    # Check process stats
    PS_INFO=$(ps -p $PID -o pid,pcpu,pmem,etime,stat --no-headers 2>/dev/null)
    if [ -z "$PS_INFO" ]; then
        echo "❌ Process not found!"
        break
    fi
    
    echo "✓ Process running: $PS_INFO"
    
    # Check for new files
    NEW_FILES=$(find results/local_runs_expanded -name "deepseek-r1_7b.jsonl" -o -name "llama3_8b.jsonl" -mmin -2 2>/dev/null | wc -l)
    if [ "$NEW_FILES" -gt 0 ]; then
        echo "✓ NEW FILES CREATED!"
    fi
    
    # Check for updated files
    RECENT=$(find results/local_runs_expanded -name "*.jsonl" -mmin -5 2>/dev/null | wc -l)
    if [ "$RECENT" -gt 0 ]; then
        echo "✓ Files updated in last 5 minutes"
    fi
    
    # Count valid (non-DRY-RUN) responses
    echo ""
    echo "Current counts (excluding DRY RUN):"
    for file in results/local_runs_expanded/*.jsonl; do
        model=$(basename "$file" .jsonl)
        total=$(grep -c "model" "$file" 2>/dev/null || echo "0")
        dry=$(grep -c "DRY RUN" "$file" 2>/dev/null || echo "0")
        valid=$((total - dry))
        echo "  $model: $valid valid ($total total, $dry dry-run)"
    done
    
    # Check Ollama activity
    OLLAMA_ACTIVE=$(ps aux | grep -E "ollama|deepseek|llama3" | grep -v grep | wc -l)
    if [ "$OLLAMA_ACTIVE" -gt 0 ]; then
        echo "✓ Ollama/model activity detected"
    fi
    
    if [ $CHECK_COUNT -lt $MAX_CHECKS ]; then
        echo ""
        echo "Waiting ${INTERVAL} seconds..."
        sleep $INTERVAL
    fi
done

echo ""
echo "Monitoring loop complete. Final check:"
./scripts/validate_phase1_quality.py 2>&1 | tail -30



