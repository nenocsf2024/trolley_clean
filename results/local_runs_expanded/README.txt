Phase 1 Expanded Data Collection Summary
==================================================

Generated: 2025-11-03T07:11:12.667520

Iterations per scenario: 10
Temperatures: [0.6, 0.7, 0.8, 0.9, 1.0, 0.0, 0.2, 0.3, 0.4, 0.5]
Seeds: auto-generated (deterministic)

Models run: mistral:7b-instruct, gemma:2b-instruct, phi3:mini, llama3:8b, orca-mini:7b

Generation counts:
  mistral:7b-instruct: 300 responses
  gemma:2b-instruct: 300 responses
  phi3:mini: 300 responses
  llama3:8b: 300 responses
  orca-mini:7b: 300 responses

Total generations: 1500

File format: Each JSONL line contains:
  - model, id, iteration, seed, temperature
  - topic, value_pair, framing, sensitivity
  - response, eval_time_s
