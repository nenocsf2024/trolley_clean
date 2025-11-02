#!/bin/bash
# Quick monitoring script for Phase 1 data generation

OUTPUT_DIR="${1:-results/local_runs_expanded}"
EXPECTED_TOTAL=750  # 5 models × 30 scenarios × 5 iterations

echo "=== Phase 1 Generation Monitor ==="
echo "Output directory: $OUTPUT_DIR"
echo "Expected total responses: $EXPECTED_TOTAL"
echo ""

# Check if process is running
if pgrep -f "run_phase1_expanded.py" > /dev/null; then
    echo "✓ Phase 1 process is running"
else
    echo "✗ Phase 1 process is NOT running"
fi
echo ""

# Count current responses
echo "Current progress:"
echo "Model                          Responses    Status"
echo "--------------------------------------------------------------------"

models=("mistral:7b-instruct" "gemma:2b-instruct" "phi3:mini" "deepseek-r1:7b" "llama3:8b")
total=0

for model in "${models[@]}"; do
    model_slug=$(echo "$model" | sed 's/\//_/g' | sed 's/:/_/g')
    jsonl_file="$OUTPUT_DIR/${model_slug}.jsonl"
    
    if [ -f "$jsonl_file" ]; then
        count=$(wc -l < "$jsonl_file" 2>/dev/null || echo "0")
        expected=150  # 30 scenarios × 5 iterations
        if [ "$count" -ge "$expected" ]; then
            status="✓ Complete"
        elif [ "$count" -gt 0 ]; then
            pct=$((count * 100 / expected))
            status="⏳ ${pct}%"
        else
            status="✗ Empty"
        fi
    else
        count=0
        status="✗ Missing"
    fi
    
    printf "%-30s %8s    %s\n" "$model" "$count" "$status"
    total=$((total + count))
done

echo "--------------------------------------------------------------------"
printf "%-30s %8s\n" "TOTAL" "$total"

pct_total=$((total * 100 / EXPECTED_TOTAL))
echo ""
echo "Overall progress: ${pct_total}% ($total / $EXPECTED_TOTAL)"
echo ""

# Show recent activity (last modified files)
echo "Most recently updated files:"
find "$OUTPUT_DIR" -name "*.jsonl" -type f -printf "%T@ %p\n" 2>/dev/null | \
    sort -rn | head -3 | \
    while read timestamp file; do
        model_name=$(basename "$file" .jsonl)
        time_ago=$(date -d "@${timestamp%.*}" -u +"%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "recent")
        echo "  $model_name - updated $time_ago"
    done

echo ""
echo "To see detailed validation: python scripts/check_phase1_iterations.py --input-dir $OUTPUT_DIR"
echo "To watch live updates: watch -n 5 '$0 $OUTPUT_DIR'"



