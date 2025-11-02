#!/bin/bash
# Judge all Phase 1 model responses using GPT-4o-mini and Claude 3.5 Haiku
# Requires: OPENAI_API_KEY and ANTHROPIC_API_KEY environment variables

set -e

# Auto-activate venv if not already activated
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "$BASE_DIR/.venv/bin/activate" ]; then
        echo "Activating virtual environment..."
        source "$BASE_DIR/.venv/bin/activate"
    else
        echo "ERROR: Virtual environment not found at $BASE_DIR/.venv"
        echo "  Create it with: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
fi

INPUT_DIR="results/local_runs_expanded"
SCENARIO_FILE="moral_core_21_sample.jsonl"
OUTPUT_DIR="results/local_runs_expanded/judges"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Models to judge
MODELS=(
    "mistral:7b-instruct"
    "gemma:2b-instruct"
    "phi3:mini"
    "llama3:8b"
    "orca-mini:7b"
)

# Judges
JUDGES=(
    "openai::gpt-4o-mini"
    "anthropic::claude-3-5-haiku-20241022"
)

# Load .env file if it exists (judge_responses.py also loads it, but check here too)
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✓ Loaded API keys from .env file"
fi

# Check API keys
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY not set"
    echo "  Set it via: export OPENAI_API_KEY='...'"
    echo "  Or add to .env file: OPENAI_API_KEY=your-key"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set"
    echo "  Set it via: export ANTHROPIC_API_KEY='...'"
    echo "  Or add to .env file: ANTHROPIC_API_KEY=your-key"
    exit 1
fi

echo "============================================================"
echo "Judging Phase 1 Responses"
echo "============================================================"
echo "Input: $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo "Judges: ${JUDGES[@]}"
echo ""

TOTAL_JOBS=$((${#MODELS[@]} * ${#JUDGES[@]}))
CURRENT=0

for model in "${MODELS[@]}"; do
    # Convert model name to filename
    model_file=$(echo "$model" | sed 's/\//_/g' | sed 's/:/_/g')
    input_file="$INPUT_DIR/${model_file}.jsonl"
    
    if [ ! -f "$input_file" ]; then
        echo "⚠️  Skipping $model: file not found ($input_file)"
        continue
    fi
    
    echo "Processing model: $model"
    
    for judge in "${JUDGES[@]}"; do
        CURRENT=$((CURRENT + 1))
        
        # Parse judge provider and model
        # Format: "provider::model" (e.g., "openai::gpt-4o-mini")
        judge_parts=(${judge//::/ })
        provider="${judge_parts[0]}"
        judge_model="${judge_parts[1]}"
        
        # Create output filename
        model_slug=$(echo "$model" | sed 's/\//_/g' | sed 's/:/_/g')
        judge_slug=$(echo "$judge_model" | sed 's/-/_/g' | tr '[:upper:]' '[:lower:]')
        output_file="$OUTPUT_DIR/judge_${model_slug}_by_${judge_slug}.csv"
        
        echo "  [$CURRENT/$TOTAL_JOBS] Judging with $judge_model ($provider)..."
        
        # Use different delays based on provider to respect rate limits
        if [ "$provider" = "anthropic" ]; then
            # Anthropic: moderate delay (5 requests/min = safe)
            SLEEP_DELAY=12.0
        else
            # OpenAI: more lenient (60 requests/min)
            SLEEP_DELAY=1.0
        fi
        
        python scripts/judge_responses.py \
            --input "$input_file" \
            --scenario-file "$SCENARIO_FILE" \
            --provider "$provider" \
            --model "$judge_model" \
            --output "$output_file" \
            --sleep "$SLEEP_DELAY"
        
        if [ $? -eq 0 ]; then
            echo "    ✓ Saved: $output_file"
        else
            echo "    ✗ Failed: $output_file"
            exit 1
        fi
        
        echo ""
    done
done

echo "============================================================"
echo "Judging Complete"
echo "============================================================"
echo "Generated $TOTAL_JOBS judge CSV files in $OUTPUT_DIR"

