#!/bin/bash
# Real-time monitoring for Phase 1 expansion progress
# Monitors temperature-related files and shows progress per model

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PHASE1_DIR="$BASE_DIR/results/local_runs_expanded"

if [ ! -d "$PHASE1_DIR" ]; then
    echo "ERROR: Phase 1 directory not found: $PHASE1_DIR"
    exit 1
fi

echo "============================================================"
echo "Phase 1 Expansion Monitor"
echo "============================================================"
echo ""
echo "Monitoring directory: $PHASE1_DIR"
echo "Press Ctrl+C to stop monitoring"
echo ""
echo "Expected final state:"
echo "  • 5 models × 30 scenarios × 10 iterations = 300 responses per model"
echo "  • Temperatures: 0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0"
echo ""
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

while true; do
    clear
    echo "============================================================"
    echo "Phase 1 Expansion Progress - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================================"
    echo ""
    
    # Get all model files (excluding judges and summaries)
    files=("$PHASE1_DIR"/*.jsonl)
    
    for file in "${files[@]}"; do
        if [[ "$file" == *"judge"* ]] || [[ "$file" == *"summary"* ]]; then
            continue
        fi
        
        model=$(basename "$file" .jsonl)
        
        # Count responses
        total=$(wc -l < "$file" 2>/dev/null || echo "0")
        
        # Count by iteration
        iters_1_5=$(grep -c '"iteration":[1-5]' "$file" 2>/dev/null || echo "0")
        iters_6_10=$(grep -c '"iteration":[6-9]\|"iteration":10' "$file" 2>/dev/null || echo "0")
        
        # Count by temperature (for iterations 6-10, which should have 0.0-0.5)
        temp_low=$(grep -E '"temperature":(0\.0|0\.2|0\.3|0\.4|0\.5)' "$file" 2>/dev/null | wc -l || echo "0")
        temp_high=$(grep -E '"temperature":(0\.6|0\.7|0\.8|0\.9|1\.0)' "$file" 2>/dev/null | wc -l || echo "0")
        
        # Calculate progress
        expected_total=300
        progress=$((total * 100 / expected_total))
        
        # Status indicators
        if [ "$total" -eq 300 ]; then
            status="${GREEN}✓ COMPLETE${NC}"
        elif [ "$total" -ge 150 ] && [ "$iters_6_10" -gt 0 ]; then
            status="${YELLOW}● IN PROGRESS${NC}"
        elif [ "$total" -eq 150 ]; then
            status="${BLUE}○ READY${NC}"
        else
            status="${BLUE}○ INITIAL${NC}"
        fi
        
        printf "%-25s | %4s responses | Iter 1-5: %3s | Iter 6-10: %3s | %s\n" \
            "$model" "$total" "$iters_1_5" "$iters_6_10" "$status"
        printf "  %-23s | Low temp (0.0-0.5): %3s | High temp (0.6-1.0): %3s | Progress: %3d%%\n" \
            "" "$temp_low" "$temp_high" "$progress"
    done
    
    echo ""
    echo "============================================================"
    echo "Summary:"
    
    total_files=$(find "$PHASE1_DIR" -name "*.jsonl" ! -name "*judge*" ! -name "*summary*" | wc -l)
    complete_models=$(for f in "$PHASE1_DIR"/*.jsonl; do 
        [[ "$f" == *"judge"* ]] || [[ "$f" == *"summary"* ]] && continue
        [ $(wc -l < "$f") -eq 300 ] && echo "$f"
    done | wc -l)
    
    echo "  Models complete: $complete_models / $total_files"
    echo "  Total responses: $(find "$PHASE1_DIR" -name "*.jsonl" ! -name "*judge*" ! -name "*summary*" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')"
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo "Refresh every 5 seconds..."
    
    sleep 5
done

