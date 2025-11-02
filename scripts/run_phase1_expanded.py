#!/usr/bin/env python3
"""
Expanded Phase 1 runner - multi-iteration collection for local Ollama models.

This script wraps run_local_ollama.py to run multiple iterations per scenario,
matching Phase 2's richer sampling approach. Defaults to 5 iterations.

Example:
    python scripts/run_phase1_expanded.py --iterations 5 --temperatures 0.7,0.8,0.9,1.0,0.6
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import the main runner function
# Handle imports whether running as script or module
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.run_local_ollama import (
    run_local_ollama,
    parse_temperatures,
    parse_seeds,
    get_models,
    DEFAULT_OUTPUT_DIR,
)


EXPANDED_OUTPUT_DIR = Path("results/local_runs_expanded")


def count_generations(output_dir: Path, models: list) -> dict:
    """Count total generations per model from JSONL files."""
    counts = {}
    for model in models:
        model_slug = model.replace("/", "_").replace(":", "_")
        jsonl_path = output_dir / f"{model_slug}.jsonl"
        
        count = 0
        if jsonl_path.exists():
            with jsonl_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            import json
                            data = json.loads(line)
                            if data.get("response"):
                                count += 1
                        except (json.JSONDecodeError, KeyError):
                            continue
        counts[model] = count
    return counts


def write_readme(
    output_dir: Path,
    iterations: int,
    temperatures: list,
    seeds: Optional[list],
    models: list,
    generation_counts: dict,
) -> None:
    """Write a README.txt summarizing the run configuration."""
    readme_path = output_dir / "README.txt"
    
    total_generations = sum(generation_counts.values())
    
    with readme_path.open("w", encoding="utf-8") as f:
        f.write("Phase 1 Expanded Data Collection Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(f"Iterations per scenario: {iterations}\n")
        f.write(f"Temperatures: {temperatures}\n")
        f.write(f"Seeds: {'provided' if seeds else 'auto-generated (deterministic)'}\n")
        if seeds:
            f.write(f"  Seed values: {seeds}\n")
        f.write(f"\nModels run: {', '.join(models)}\n\n")
        f.write("Generation counts:\n")
        for model, count in generation_counts.items():
            f.write(f"  {model}: {count} responses\n")
        f.write(f"\nTotal generations: {total_generations}\n")
        f.write("\n")
        f.write("File format: Each JSONL line contains:\n")
        f.write("  - model, id, iteration, seed, temperature\n")
        f.write("  - topic, value_pair, framing, sensitivity\n")
        f.write("  - response, eval_time_s\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Expanded Phase 1 runner with multi-iteration support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: 5 iterations, single temperature 0.7
  python scripts/run_phase1_expanded.py

  # Custom iterations and temperatures
  python scripts/run_phase1_expanded.py --iterations 5 --temperatures 0.7,0.8,0.9,1.0,0.6

  # With explicit seeds
  python scripts/run_phase1_expanded.py --iterations 3 --seeds 42,123,456

  # Dry run to test configuration
  python scripts/run_phase1_expanded.py --iterations 2 --dry-run
        """
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=EXPANDED_OUTPUT_DIR,
        help=f"Output directory (default: {EXPANDED_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of iterations per scenario per model (default: 5)",
    )
    parser.add_argument(
        "--temperatures",
        type=str,
        default=None,
        help="Comma-separated list of temperatures. If not provided, defaults to 0.7 for all iterations. "
             "If single value, applies to all; if multiple, cycles per iteration.",
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default=None,
        help="Optional comma-separated list of seeds (one per iteration). If not provided, auto-generates deterministic seeds.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Truncate output files instead of appending (default: False)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip actual API calls (for testing)",
    )
    
    args = parser.parse_args()
    
    # Parse temperatures (default to 0.7 if not provided)
    if args.temperatures:
        temperatures = parse_temperatures(args.temperatures)
    else:
        temperatures = [0.7]
    
    seeds = parse_seeds(args.seeds)
    
    if seeds and len(seeds) != args.iterations:
        parser.error(f"Number of seeds ({len(seeds)}) must match iterations ({args.iterations})")
    
    models = get_models()
    
    print(f"\n{'='*60}")
    print(f"Phase 1 Expanded Run")
    print(f"{'='*60}")
    print(f"Output directory: {args.output_dir}")
    print(f"Iterations: {args.iterations}")
    print(f"Temperatures: {temperatures}")
    print(f"Seeds: {'provided' if seeds else 'auto-generated'}")
    print(f"Models: {models}")
    print(f"Overwrite: {args.overwrite}")
    print(f"Dry run: {args.dry_run}")
    print(f"{'='*60}\n")
    
    # Run the actual collection
    run_local_ollama(
        output_dir=args.output_dir,
        iterations=args.iterations,
        temperatures=temperatures,
        seeds=seeds,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )
    
    # Count generations and log summary table
    generation_counts = count_generations(args.output_dir, models)
    
    print(f"\n{'='*60}")
    print("Generation Summary")
    print(f"{'='*60}")
    print(f"{'Model':<30} {'Generations':<15}")
    print("-" * 60)
    for model, count in generation_counts.items():
        print(f"{model:<30} {count:<15}")
    print("-" * 60)
    total = sum(generation_counts.values())
    print(f"{'TOTAL':<30} {total:<15}")
    print(f"{'='*60}\n")
    
    # Write README
    write_readme(
        output_dir=args.output_dir,
        iterations=args.iterations,
        temperatures=temperatures,
        seeds=seeds,
        models=models,
        generation_counts=generation_counts,
    )
    print(f"Wrote README: {args.output_dir / 'README.txt'}")


if __name__ == "__main__":
    main()
