Phase 1 Expanded Data Collection Summary
==================================================

Generated: 2025-11-02T03:27:19.584450

Iterations per scenario: 5
Temperatures: [0.6, 0.8, 1.0, 0.7, 0.9]
Seeds: auto-generated (deterministic)

Models run: mistral:7b-instruct, gemma:2b-instruct, phi3:mini, llama3:8b, orca-mini:7b

Generation counts:
  mistral:7b-instruct: 150 responses
  gemma:2b-instruct: 150 responses
  phi3:mini: 150 responses
  llama3:8b: 299 responses
  orca-mini:7b: 150 responses

Total generations: 899

File format: Each JSONL line contains:
  - model, id, iteration, seed, temperature
  - topic, value_pair, framing, sensitivity
  - response, eval_time_s
