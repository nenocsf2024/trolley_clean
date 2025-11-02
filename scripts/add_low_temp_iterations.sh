#!/bin/bash
# Add low-temperature iterations (6-10) to existing Phase 1 data
# This adds temperatures: 0.0, 0.2, 0.3, 0.4, 0.5
# Preserves all existing work (iterations 1-5)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$BASE_DIR"

# Auto-activate venv if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "$BASE_DIR/.venv/bin/activate" ]; then
        echo "Activating virtual environment..."
        source "$BASE_DIR/.venv/bin/activate"
    else
        echo "ERROR: Virtual environment not found at $BASE_DIR/.venv"
        exit 1
    fi
fi

echo "============================================================"
echo "Adding Low-Temperature Iterations (6-10)"
echo "============================================================"
echo ""
echo "This will add 750 new responses:"
echo "  • 5 models × 30 scenarios × 5 iterations (6-10)"
echo "  • Temperatures: 0.0, 0.2, 0.3, 0.4, 0.5"
echo ""
echo "Safety checks:"
echo "  ✓ Resume mode enabled - will skip existing iterations 1-5"
echo "  ✓ Append mode - will add to files, not overwrite"
echo "  ✓ All existing work preserved"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Check if dry-run flag provided
DRY_RUN=""
if [ "$1" = "--dry-run" ] || [ "$1" = "-n" ]; then
    DRY_RUN="--dry-run"
    echo "⚠️  DRY RUN MODE - No actual API calls will be made"
    echo ""
fi

# Enable resume mode to skip existing iterations
export OLLAMA_RESUME=1

# Run with 10 iterations total, providing all 10 temperatures
# Resume mode will skip 1-5, generate only 6-10
python scripts/run_phase1_expanded.py \
    --iterations 10 \
    --temperatures 0.6,0.7,0.8,0.9,1.0,0.0,0.2,0.3,0.4,0.5 \
    --output-dir results/local_runs_expanded \
    $DRY_RUN

echo ""
echo "============================================================"
echo "Generation Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Verify new data was added:"
echo "     wc -l results/local_runs_expanded/*.jsonl"
echo ""
echo "  2. Run judging for new iterations:"
echo "     ./scripts/judge_all_phase1.sh"
echo "     (This will judge ALL responses, including new ones)"
echo ""

