# The Balance Penalty

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17517864.svg)](https://doi.org/10.5281/zenodo.17517864)

Code and data for the paper **“The Balance Penalty: How LLM Judges Systematically Penalize Nuanced Moral Reasoning”** by Nenad Bago (2025).

> **TL;DR** – Automated evaluators such as GPT-4o-mini and Claude 3.5 Haiku award decisively framed answers substantially higher alignment scores than balanced trade-off reasoning (Δ ≈ 0.74). This repository contains the complete Phase 1 dataset (1,500 responses, 3,000 judge evaluations), generation and judging scripts, statistical analysis, and publication figures.

---

## Quick Start

```bash
# 1. Clone the repository and enter it
git clone https://github.com/nenocsf2024/trolley_clean.git
cd trolley_clean

# 2. Create environment and install dependencies (Python 3.12 recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Re-run the analysis (recreates CSV/JSON summaries and figures)
python scripts/analyze_balance_penalty.py

# 4. Compile the manuscript (optional)
cd manuscript
latexmk -pdf main.tex
```

The regenerated artifacts will appear under `results/local_runs_expanded/analysis/` and `manuscript/figures/`.

---

## Repository Structure

```
trolley_clean/
├── moral_core_21_sample.jsonl         # Scenario corpus (30 dilemmas × 3 framings)
├── scripts/                           # Data generation, judging, and analysis scripts
│   ├── run_phase1_expanded.py
│   ├── judge_responses.py
│   ├── judge_all_phase1.sh
│   └── analyze_balance_penalty.py
├── results/local_runs_expanded/       # Phase 1 dataset (JSONL responses + judge CSV/analysis)
│   └── analysis/                      # Derived tables (alignment by framing, disagreement, etc.)
├── manuscript/                        # LaTeX source and publication figures
│   ├── main.tex
│   └── figures/
├── notebooks/
│   └── phase1_analysis.ipynb          # Supplementary exploration (plots, QA)
├── README.md
├── LICENSE
└── requirements.txt
```

---

## Reproducing Phase 1 (Local Models)

1. **Generate responses** (five local Ollama models × 30 scenarios × 10 iterations):
   ```bash
   python scripts/run_phase1_expanded.py \
       --iterations 10 \
       --temperatures 0.6,0.7,0.8,0.9,1.0,0.0,0.2,0.3,0.4,0.5
   ```

2. **Judge all responses** with GPT-4o-mini and Claude 3.5 Haiku:
   ```bash
   bash scripts/judge_all_phase1.sh
   ```
   Configure `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` in your environment or a local `.env` file before running.

3. **Run the statistical analysis and generate tables/figures**:
   ```bash
   python scripts/analyze_balance_penalty.py
   ```

All generated outputs are stored under `results/local_runs_expanded/analysis/`.

---

## Key Artifacts

- `results/local_runs_expanded/*.jsonl` – Raw Phase 1 responses (1,500 total)
- `results/local_runs_expanded/judges/*.csv` – GPT-4o-mini / Claude 3.5 Haiku judgments (3,000 rows)
- `results/local_runs_expanded/analysis/analysis_balance_penalty_overall.json` – Summary stats (effect sizes, R², Fleiss’ κ)
- `results/local_runs_expanded/analysis/analysis_response_characteristics.csv` – Length and lexical diagnostics
- `manuscript/` – LaTeX paper, including all publication figures

---

## Requirements

- Python 3.12+
- Ollama with the following models pulled locally:
  - `mistral:7b-instruct`
  - `gemma:2b-instruct`
  - `phi3:mini`
  - `llama3:8b`
  - `orca-mini:7b`
- API access to GPT-4o-mini (OpenAI) and Claude 3.5 Haiku (Anthropic) for judging

The `requirements.txt` file pins the exact Python packages used to reproduce the results.

---

## Citation

If you use this repository, please cite:

```bibtex
@misc{bago2025balance,
  title        = {The Balance Penalty: How {LLM} Judges Systematically Penalize Nuanced Moral Reasoning},
  author       = {Bago, Nenad},
  year         = {2025},
  howpublished = {Zenodo},
  doi          = {10.5281/zenodo.17517864},
  url          = {https://doi.org/10.5281/zenodo.17517864}
}
```

---

## License

This project is released under the [MIT License](LICENSE).

---

## Disclaimer

This research code is provided "as is" for academic reproducibility purposes. The findings document observed behaviors in specific LLM evaluation systems and are not intended as production-ready solutions or definitive guidance for deployment decisions.

**Not intended for:**
- Production deployment without extensive additional validation
- Safety-critical systems without independent verification
- Direct implementation without adaptation to specific contexts

**Users should:**
- Conduct their own testing and validation
- Assess applicability to their specific use cases
- Consult with domain experts before production use
- Comply with all applicable terms of service for API providers

The author disclaims all warranties and liability for any consequences arising from use of this code or implementation of findings.

## Responsible Use

This repository enables auditing of LLM judge behavior. While we encourage responsible testing and mitigation of evaluation biases, users should be aware of potential dual-use concerns. Do **not** use these findings to:
- Manipulate evaluation systems for malicious purposes
- Circumvent safety measures in production systems
- Generate misleading content that exploits documented biases

---

## Contact

Nenad Bago  
nenad@airis-med.eu  
GitHub: [@nenocsf2024](https://github.com/nenocsf2024)
