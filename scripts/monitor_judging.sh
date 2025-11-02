#!/bin/bash
# Monitor Phase 1 judging progress

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$BASE_DIR"

JUDGES_DIR="results/local_runs_expanded/judges"
LOG_FILE="judging.log"

# Models and judges
MODELS=(
    "mistral:7b-instruct"
    "gemma:2b-instruct"
    "phi3:mini"
    "llama3:8b"
    "orca-mini:7b"
)

JUDGES=(
    "openai::gpt-4o-mini"
    "anthropic::claude-3-5-haiku-20241022"
)

# Convert model names to file slugs
model_to_slug() {
    echo "$1" | sed 's/\//_/g' | sed 's/:/_/g'
}

# Convert judge model to slug
judge_to_slug() {
    local judge="$1"
    judge_parts=(${judge//::/ })
    judge_model="${judge_parts[1]}"
    echo "$judge_model" | sed 's/-/_/g' | tr '[:upper:]' '[:lower:]'
}

echo "============================================================"
echo "Judging Progress Monitor"
echo "============================================================"
echo ""

# Check if process is running
if pgrep -f "judge_responses.py" > /dev/null; then
    PID=$(pgrep -f "judge_responses.py" | head -1)
    echo "✓ Process running (PID: $PID)"
    
    # Show process stats
    PS_OUTPUT=$(ps -p "$PID" -o etime,pcpu,rss,cmd --no-headers 2>/dev/null)
    if [ -n "$PS_OUTPUT" ]; then
        ETIME=$(echo "$PS_OUTPUT" | awk '{print $1}')
        CPU=$(echo "$PS_OUTPUT" | awk '{print $2}')
        RSS=$(echo "$PS_OUTPUT" | awk '{print $3}')
        echo "  Runtime: $ETIME | CPU: $CPU% | Memory: ${RSS}KB"
    fi
else
    echo "✗ No judging process found"
    echo ""
    echo "Start judging with:"
    echo "  nohup bash ./scripts/judge_all_phase1.sh > judging.log 2>&1 &"
    exit 1
fi

echo ""

# Check CSV files
if [ ! -d "$JUDGES_DIR" ]; then
    echo "✗ Judges directory doesn't exist"
    exit 1
fi

TOTAL_JOBS=$((${#MODELS[@]} * ${#JUDGES[@]}))
COMPLETED=0
IN_PROGRESS=0

echo "File Status:"
echo "----------------------------------------"

for model in "${MODELS[@]}"; do
    model_slug=$(model_to_slug "$model")
    
    for judge in "${JUDGES[@]}"; do
        judge_slug=$(judge_to_slug "$judge")
        csv_file="$JUDGES_DIR/judge_${model_slug}_by_${judge_slug}.csv"
        
        if [ -f "$csv_file" ]; then
            # Count rows (excluding header)
            row_count=$(tail -n +2 "$csv_file" 2>/dev/null | wc -l | tr -d ' ')
            file_size=$(ls -lh "$csv_file" | awk '{print $5}')
            
            # Check if file has 150 rows (complete) or less (in progress)
            if [ "$row_count" -ge 150 ]; then
                echo "✓ $model_slug × $judge_slug: COMPLETE ($row_count rows, $file_size)"
                COMPLETED=$((COMPLETED + 1))
            else
                echo "⏳ $model_slug × $judge_slug: $row_count/150 rows ($file_size)"
                IN_PROGRESS=$((IN_PROGRESS + 1))
            fi
        else
            echo "○ $model_slug × $judge_slug: Not started"
        fi
    done
done

echo "----------------------------------------"
echo "Progress: $COMPLETED/$TOTAL_JOBS complete, $IN_PROGRESS in progress"
echo ""

# Show recent log activity
if [ -f "$LOG_FILE" ]; then
    echo "Recent Log Activity (last 5 lines):"
    echo "----------------------------------------"
    tail -5 "$LOG_FILE" 2>/dev/null | sed 's/^/  /'
    echo ""
    
    # Check for errors
    ERROR_COUNT=$(grep -i "error\|failed\|exception" "$LOG_FILE" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "⚠️  Warning: Found $ERROR_COUNT error(s) in log"
        echo "   Recent errors:"
        grep -i "error\|failed\|exception" "$LOG_FILE" | tail -3 | sed 's/^/     /'
        echo ""
    fi
else
    echo "⚠️  Log file not found: $LOG_FILE"
    echo ""
fi

# Estimate time remaining (rough)
if [ "$IN_PROGRESS" -gt 0 ] && pgrep -f "judge_responses.py" > /dev/null; then
    echo "Note: Each model×judge pair takes ~2.5-5 minutes for 150 responses"
    echo "      Monitor with: tail -f $LOG_FILE"
fi

echo ""
echo "============================================================"

