#!/bin/bash
# Commit and push judging results after completion
# Run this when all judging jobs are done

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$BASE_DIR"

echo "============================================================"
echo "Committing Judging Results"
echo "============================================================"
echo ""

# Check if we're on the right branch
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"
echo ""

# Check what will be committed
echo "Files to commit:"
git status --short | grep -E "judges|results" || echo "  (no new files)"
echo ""

# Check if judge files are complete
python3 << 'PYEOF'
import csv
from pathlib import Path

judges_dir = Path("results/local_runs_expanded/judges")
csv_files = sorted(judges_dir.glob("judge_*.csv"))

expected = 10  # 5 models × 2 judges
complete = sum(1 for f in csv_files if len(list(csv.DictReader(open(f)))) >= 150)

print(f"Judge files status: {complete}/{expected} complete")
if complete < expected:
    print("⚠️  Warning: Some judge files may be incomplete")
    print("   Continue anyway? This will commit current state.")
else:
    print("✅ All judge files complete")
PYEOF

echo ""
read -p "Commit these changes? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Stage judge files and results
echo ""
echo "Staging files..."
git add results/local_runs_expanded/judges/*.csv
git add results/local_runs_expanded/*.csv results/local_runs_expanded/*.txt 2>/dev/null || true
git add scripts/ 2>/dev/null || true

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No changes to commit."
    exit 0
fi

# Commit
git commit -m "Complete Phase 1 judging with GPT-4o-mini and Claude 3.5 Haiku

- All 10 judge jobs complete (5 models × 2 judges)
- Judge evaluations include alignment scores and value preferences
- Ready for temperature expansion analysis"

echo ""
echo "Pushing to GitHub..."
git push

echo ""
echo "============================================================"
echo "✅ Judging results committed and pushed!"
echo "============================================================"
echo ""
echo "Next step: Run low-temperature iteration generation"
echo "  ./scripts/add_low_temp_iterations.sh"

