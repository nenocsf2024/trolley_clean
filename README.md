# Moral Wind Tunnel: Phase 1 + Phase 2 Analysis Workspace

A clean, reproducible workspace for analyzing moral reasoning across local and API-based language models.

## Overview

This workspace contains:
- **Phase 1**: Local model responses collected via Ollama (5 models × 5 iterations per scenario)
- **Phase 2**: API-based model responses and judge evaluations
- **EDA**: Exploratory data analysis comparing heuristic vs. judge-based value preferences

## Quick Start

### 1. Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify dependencies are installed
pip list | grep -E "(pandas|matplotlib|openai|anthropic)"
```

### 2. Verify Models

Ensure all required Ollama models are available:

```bash
ollama list
```

Required models:
- `mistral:7b-instruct`
- `gemma:2b-instruct`
- `phi3:mini`
- `deepseek-r1:7b`
- `llama3:8b`

If models are missing, pull them:

```bash
ollama pull deepseek-r1:7b
ollama pull llama3:8b
```

### 3. Regenerate Phase 1 Data

Run expanded Phase 1 collection with all 5 models:

```bash
# Dry run to test configuration
python scripts/run_phase1_expanded.py \
    --iterations 5 \
    --temperatures 0.6,0.8,1.0,0.7,0.9 \
    --dry-run

# Actual run (writes to results/local_runs_expanded/)
python scripts/run_phase1_expanded.py \
    --iterations 5 \
    --temperatures 0.6,0.8,1.0,0.7,0.9
```

### 4. Validate Coverage

Check that each model × scenario has 5 iterations:

```bash
python scripts/check_phase1_iterations.py \
    --input-dir results/local_runs_expanded \
    --verbose
```

### 5. Judge Responses

Run judge evaluations on Phase 1 responses:

```bash
python scripts/judge_responses.py \
    --input-dir results/local_runs_expanded \
    --providers openai::gpt-4o-mini,mistral::mistral-medium-latest
```

### 6. Analyze Results

Generate Phase 1 analysis:

```bash
python scripts/analyze_local_results.py \
    --input-dir results/local_runs_expanded
```

### 7. Run EDA

Generate exploratory data analysis comparing Phase 1 and Phase 2:

```bash
python scripts/eda_phase_comparison.py
```

Outputs appear in `results/eda/`:
- `value_preference_distribution_judges.png` - Main judge-based plot
- `heuristic_vs_judge_value_preference_summary.csv` - Comparison table
- Alignment heatmaps and other diagnostics

## Project Structure

```
trolley_clean/
├── scripts/                    # Analysis and data collection scripts
│   ├── run_local_ollama.py     # Core Phase 1 runner
│   ├── run_phase1_expanded.py  # Multi-iteration Phase 1 wrapper
│   ├── judge_responses.py      # Judge evaluation script
│   ├── analyze_local_results.py # Phase 1 analysis
│   ├── check_phase1_iterations.py # Validation script
│   └── eda_phase_comparison.py # Phase 1 vs Phase 2 EDA
├── results/
│   ├── phase2/                  # Phase 2 API responses and judge CSVs
│   ├── local_runs_expanded/     # Phase 1 multi-iteration outputs
│   └── eda/                     # EDA plots and tables
├── moral_core_21_sample.jsonl   # Scenario dataset
├── requirements.txt             # Python dependencies
└── local_llm_licences.md        # License information for local models
```

## Models in Use

### Phase 1 (Local via Ollama)
1. **Mistral 7B Instruct** (`mistral:7b-instruct`)
2. **Gemma 2B Instruct** (`gemma:2b-instruct`)
3. **Phi-3 Mini** (`phi3:mini`)
4. **Llama 3 8B** (`llama3:8b`) ⭐ New

Note: DeepSeek R1 7B was removed due to thinking model compatibility issues.

### Phase 2 (API-based)
- Claude Sonnet 4
- GPT-4o-mini
- Gemini 2.5 Flash Lite
- Grok 3
- Mistral Large

### Judges
- OpenAI GPT-4o-mini
- Mistral Medium Latest

## Configuration

Default models are configured in `scripts/run_local_ollama.py`:

```python
DEFAULT_MODELS = [
    "mistral:7b-instruct",
    "gemma:2b-instruct",
    "phi3:mini",
    "deepseek-r1:7b",
    "llama3:8b"
]
```

Override via environment variable:
```bash
export OLLAMA_MODELS="mistral:7b-instruct,phi3:mini"
```

## Output Format

### Phase 1 JSONL Format
Each line in `results/local_runs_expanded/*.jsonl`:
```json
{
  "model": "mistral:7b-instruct",
  "id": "MC21-001-N",
  "iteration": 1,
  "seed": 12345678,
  "temperature": 0.7,
  "topic": "Medical AI Diagnosis Disclosure",
  "value_pair": "honesty_vs_empathy",
  "framing": "neutral",
  "sensitivity": "medium",
  "response": "...",
  "eval_time_s": 2.3
}
```

### Judge CSV Format
Each `judge_*.csv` contains:
- `model`, `id`, `iteration`
- `judge_provider`, `judge_model`
- `preferred_value`, `confidence`, `reasoning`

## Troubleshooting

### Models Not Found
```bash
# List available models
ollama list

# Pull missing models
ollama pull deepseek-r1:7b
ollama pull llama3:8b
```

### Ollama Connection Issues
```bash
# Ensure Ollama is running
ollama serve

# Check Ollama status
curl http://localhost:11434/api/tags
```

### Missing Judge API Keys
Set environment variables:
```bash
export OPENAI_API_KEY="your-key"
export MISTRAL_API_KEY="your-key"
```

## License

See `local_llm_licences.md` for license information for each local model.

All scripts and analysis code are open source and available for research use.

---

**Last Updated:** Clean workspace setup for Phase 1 + Phase 2 analysis with 5 local models (including Llama 3 and DeepSeek).




