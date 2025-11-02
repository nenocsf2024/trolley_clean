#!/usr/bin/env python3
"""
Local Phase 1 runner using Ollama.

Reads moral_core_21_sample.jsonl, queries local Ollama models, and writes
raw outputs to results/local_runs/{model}.jsonl plus a minimal summary CSV.

Supports multiple iterations per scenario with configurable temperatures and seeds
for richer sampling (matching Phase 2's approach).

Prereqs:
  - Ollama installed and running:  ollama serve
  - Models pulled, e.g.:          ollama pull mistral:7b-instruct-v0.2
                                   ollama pull microsoft/phi:4-mini-instruct

Configure models via env OLLAMA_MODELS (comma-separated) or edit DEFAULT_MODELS.
"""

import argparse
import hashlib
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
import csv

SAMPLE_PATH = Path("moral_core_21_sample.jsonl")
DEFAULT_OUTPUT_DIR = Path("results/local_runs")

# Reasonable defaults; override with OLLAMA_MODELS env var if desired
DEFAULT_MODELS = [
    "mistral:7b-instruct",
    "gemma:2b-instruct",
    "phi3:mini",
    "llama3:8b",
    "orca-mini:7b"  # Added as 5th model - tested and working
]

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


def load_sample(sample_path: Optional[Path] = None) -> List[Dict]:
    path = sample_path or SAMPLE_PATH
    if not path.exists():
        raise FileNotFoundError(f"Sample file not found: {path}")
    items: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def get_models() -> List[str]:
    env = os.getenv("OLLAMA_MODELS", "").strip()
    if env:
        return [m.strip() for m in env.split(",") if m.strip()]
    return DEFAULT_MODELS


def _coalesce_ollama_response(text: str) -> Dict[str, Any]:
    """Parse Ollama response JSON while tolerating newline-delimited streaming chunks."""
    text = text.strip()
    if not text:
        raise ValueError("Empty response from Ollama")

    # Prefer a single JSON object if available
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # Fall back to NDJSON-style streaming payload
    chunks: List[Dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            chunk = json.loads(line)
        except json.JSONDecodeError as err:
            raise ValueError(f"Failed to parse Ollama chunk: {line[:120]}") from err
        if isinstance(chunk, dict):
            chunks.append(chunk)

    if not chunks:
        raise ValueError("Received unparseable response from Ollama")

    merged = chunks[-1].copy()
    merged["response"] = "".join(chunk.get("response", "") for chunk in chunks)
    return merged


def generate(
    model: str,
    prompt: str,
    max_tokens: int = 300,
    temperature: float = 0.7,
    seed: Optional[int] = None,
    dry_run: bool = False,
) -> Dict:
    """
    Generate a response from Ollama model.
    
    Args:
        model: Model name
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        seed: Optional seed for reproducibility
        dry_run: If True, skip actual API call and return mock response
    
    Returns:
        Dict with 'response' and 'eval_time_s' keys
    """
    if dry_run:
        return {
            "response": f"[DRY RUN] Mock response for {model}",
            "eval_time_s": 0.0
        }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature
        }
    }
    
    if seed is not None:
        payload["options"]["seed"] = seed
    
    t0 = time.time()
    r = requests.post(OLLAMA_URL, json=payload, timeout=300)
    r.raise_for_status()
    try:
        data = r.json()
    except (json.JSONDecodeError, ValueError):
        data = _coalesce_ollama_response(r.text)
    dt = time.time() - t0
    return {"response": data.get("response", ""), "eval_time_s": dt}


def generate_deterministic_seed(model: str, scenario_id: str, iteration: int) -> int:
    """
    Generate a deterministic seed from model name, scenario ID, and iteration.
    Ensures reproducibility when seeds are not explicitly provided.
    """
    seed_str = f"{model}:{scenario_id}:{iteration}"
    seed_hash = hashlib.md5(seed_str.encode()).hexdigest()
    # Use first 8 hex digits as int (max value ~4.3 billion, fits in int32)
    return int(seed_hash[:8], 16)


def write_summaries(models: List[str], output_dir: Path) -> None:
    """
    Write summary CSVs including iteration, seed, and temperature columns.
    """
    summary_rows = []
    model_stats = []

    for model in models:
        out_path = output_dir / f"{model.replace('/', '_').replace(':', '_')}.jsonl"
        n_ok = 0
        n_err = 0
        total_len = 0
        if not out_path.exists():
            continue
        with out_path.open("r", encoding="utf-8") as in_f:
            for line in in_f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if data.get("response"):
                    n_ok += 1
                    resp = data.get("response") or ""
                    total_len += len(resp)
                    summary_rows.append({
                        "model": model,
                        "id": data.get("id"),
                        "iteration": str(data.get("iteration", "")),
                        "seed": str(data.get("seed", "")),
                        "temperature": f"{data.get('temperature', ''):.3f}" if data.get('temperature') is not None else "",
                        "topic": data.get("topic", ""),
                        "framing": data.get("framing", ""),
                        "len_response": len(resp),
                        "eval_time_s": f"{data.get('eval_time_s', 0.0):.3f}"
                    })
                else:
                    n_err += 1
        avg_len = (total_len / n_ok) if n_ok else 0.0
        model_stats.append({
            "model": model,
            "ok": n_ok,
            "errors": n_err,
            "avg_len": f"{avg_len:.1f}"
        })

    csv_path = output_dir / "summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as cf:
        fieldnames = ["model", "id", "iteration", "seed", "temperature", "topic", "framing", "len_response", "eval_time_s"]
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Wrote summary: {csv_path}")

    stats_path = output_dir / "summary_models.csv"
    with stats_path.open("w", newline="", encoding="utf-8") as sf:
        writer = csv.DictWriter(sf, fieldnames=["model", "ok", "errors", "avg_len"])
        writer.writeheader()
        writer.writerows(model_stats)
    print(f"Wrote per-model stats: {stats_path}")


def _parse_int_env(name: str) -> Optional[int]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
        return value
    except ValueError:
        print(f"Ignoring invalid {name} value: {raw}")
        return None


def parse_temperatures(temp_str: str) -> List[float]:
    """Parse comma-separated temperature string into list of floats."""
    temps = []
    for t in temp_str.split(","):
        t = t.strip()
        if not t:
            continue
        try:
            temps.append(float(t))
        except ValueError:
            raise ValueError(f"Invalid temperature value: {t}")
    if not temps:
        raise ValueError("At least one temperature must be provided")
    return temps


def parse_seeds(seed_str: Optional[str]) -> Optional[List[int]]:
    """Parse comma-separated seed string into list of ints."""
    if not seed_str:
        return None
    seeds = []
    for s in seed_str.split(","):
        s = s.strip()
        if not s:
            continue
        try:
            seeds.append(int(s))
        except ValueError:
            raise ValueError(f"Invalid seed value: {s}")
    return seeds if seeds else None


def run_local_ollama(
    output_dir: Path,
    iterations: int = 1,
    temperatures: List[float] = None,
    seeds: Optional[List[int]] = None,
    overwrite: bool = False,
    dry_run: bool = False,
    sample_path: Optional[Path] = None,
) -> None:
    """
    Main function to run local Ollama models on scenarios with multi-iteration support.
    
    Args:
        output_dir: Directory to write output JSONL and CSV files
        iterations: Number of iterations per scenario per model
        temperatures: List of temperatures to cycle through
        seeds: Optional list of seeds (one per iteration), or None for deterministic seeds
        overwrite: If True, truncate output files; if False, append
        dry_run: If True, skip actual API calls
        sample_path: Optional path to scenario JSONL file
    """
    if temperatures is None:
        temperatures = [0.7]
    
    # Normalize temperatures: if single value, apply to all iterations; otherwise cycle
    if len(temperatures) == 1:
        temp_per_iteration = temperatures * iterations
    else:
        # Cycle through provided temperatures
        temp_per_iteration = [temperatures[i % len(temperatures)] for i in range(iterations)]
    
    # Handle seeds
    if seeds is not None and len(seeds) != iterations:
        raise ValueError(f"Number of seeds ({len(seeds)}) must match iterations ({iterations})")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_items = load_sample(sample_path)
    order_map = {ex.get("id"): idx for idx, ex in enumerate(all_items)}

    limit = _parse_int_env("OLLAMA_LIMIT")
    offset = _parse_int_env("OLLAMA_OFFSET") or 0

    if offset < 0:
        print(f"Resetting negative OLLAMA_OFFSET={offset} to 0")
        offset = 0

    if limit is not None and limit <= 0:
        print(f"Ignoring non-positive OLLAMA_LIMIT={limit}")
        limit = None

    end_idx = offset + limit if limit is not None else len(all_items)
    items = all_items[offset:end_idx]

    if offset or limit is not None:
        slice_info = f"offset {offset}"
        if limit is not None:
            slice_info += f", limit {limit}"
        print(f"Applying {slice_info}; running on {len(items)} items (from {len(all_items)} total)")

    models = get_models()
    print(f"Loaded {len(items)} sample items; running models: {models}")
    print(f"Configuration: {iterations} iterations, temperatures={temperatures}, seeds={'provided' if seeds else 'auto-generated'}")
    if dry_run:
        print("*** DRY RUN MODE: No actual API calls will be made ***")

    resume = os.getenv("OLLAMA_RESUME", "").strip().lower() in {"1", "true", "yes", "on"} and not overwrite

    for model in models:
        out_path = output_dir / f"{model.replace('/', '_').replace(':', '_')}.jsonl"
        
        # Track existing records by (id, iteration) key for resume mode
        existing_keys: Dict[tuple, Dict[str, Any]] = {}
        
        if resume and out_path.exists():
            with out_path.open("r", encoding="utf-8") as in_f:
                for line in in_f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    rec_id = data.get("id")
                    iter_num = data.get("iteration", 1)
                    if rec_id:
                        existing_keys[(rec_id, iter_num)] = data
        
        records_to_write = []

        for ex in items:
            rec_id = ex.get("id")
            if not rec_id:
                continue
            
            prompt = ex.get("prompt_text") or ex.get("prompt") or ""
            
            for iteration in range(1, iterations + 1):
                # Check if we should skip this iteration (resume mode)
                if resume and (rec_id, iteration) in existing_keys:
                    existing = existing_keys[(rec_id, iteration)]
                    if existing.get("response"):
                        continue
                
                # Get temperature and seed for this iteration
                temp = temp_per_iteration[iteration - 1]
                seed = seeds[iteration - 1] if seeds else generate_deterministic_seed(model, rec_id, iteration)
                
                try:
                    res = generate(model, prompt, temperature=temp, seed=seed, dry_run=dry_run)
                    record = {
                        "model": model,
                        "id": rec_id,
                        "iteration": iteration,
                        "seed": seed,
                        "temperature": temp,
                        "topic": ex.get("topic"),
                        "value_pair": ex.get("value_pair"),
                        "framing": ex.get("framing"),
                        "sensitivity": ex.get("sensitivity"),
                        "response": res["response"],
                        "eval_time_s": res["eval_time_s"]
                    }
                except Exception as e:
                    record = {
                        "model": model,
                        "id": rec_id,
                        "iteration": iteration,
                        "seed": seed,
                        "temperature": temp,
                        "error": str(e)
                    }
                
                records_to_write.append(record)
                
                if not dry_run:
                    print(f"{model} [{rec_id}] iter {iteration} temp={temp:.2f} seed={seed}")

        # Write records: overwrite mode truncates, otherwise append
        if overwrite:
            # Truncate file and write only new records
            with out_path.open("w", encoding="utf-8") as out_f:
                for record in records_to_write:
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
        else:
            # Append mode: just add new records
            with out_path.open("a", encoding="utf-8") as out_f:
                for record in records_to_write:
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        # Read back all records to get accurate stats
        all_records = []
        if out_path.exists():
            with out_path.open("r", encoding="utf-8") as in_f:
                for line in in_f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        all_records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        n_ok = sum(1 for rec in all_records if rec.get("response"))
        n_err = sum(1 for rec in all_records if not rec.get("response"))
        avg_len = (
            sum(len(rec.get("response") or "") for rec in all_records if rec.get("response")) / n_ok
            if n_ok else 0.0
        )
        print(f"{model}: OK={n_ok} ERR={n_err} AVG_LEN={avg_len:.1f} -> {out_path} (mode={'overwrite' if overwrite else 'append' if not resume else 'resume'})")

    write_summaries(models, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local Phase 1 runner using Ollama with multi-iteration support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single iteration (backward compatible)
  python scripts/run_local_ollama.py

  # 5 iterations with single temperature
  python scripts/run_local_ollama.py --iterations 5

  # Multiple temperatures cycling per iteration
  python scripts/run_local_ollama.py --iterations 5 --temperatures 0.6,0.7,0.8,0.9,1.0

  # Custom output directory
  python scripts/run_local_ollama.py --output-dir results/custom --iterations 3

  # Dry run to test without API calls
  python scripts/run_local_ollama.py --iterations 2 --temperatures 0.6,0.9 --dry-run
        """
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for JSONL and CSV files (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of iterations per scenario per model (default: 1)",
    )
    parser.add_argument(
        "--temperatures",
        type=str,
        default="0.7",
        help="Comma-separated list of temperatures. If single value, applies to all iterations; otherwise cycles (default: 0.7)",
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default=None,
        help="Optional comma-separated list of seeds (one per iteration). If not provided, generates deterministic seeds.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="If set, truncate output files instead of appending (default: False)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip actual API calls and return mock responses (for testing)",
    )
    parser.add_argument(
        "--sample-path",
        type=Path,
        default=None,
        help=f"Path to scenario JSONL file (default: {SAMPLE_PATH})",
    )
    
    args = parser.parse_args()
    
    temperatures = parse_temperatures(args.temperatures)
    seeds = parse_seeds(args.seeds)
    
    if seeds and len(seeds) != args.iterations:
        parser.error(f"Number of seeds ({len(seeds)}) must match iterations ({args.iterations})")
    
    run_local_ollama(
        output_dir=args.output_dir,
        iterations=args.iterations,
        temperatures=temperatures,
        seeds=seeds,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        sample_path=args.sample_path,
    )


if __name__ == "__main__":
    main()
