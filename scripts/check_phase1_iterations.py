#!/usr/bin/env python3
"""
Validation helper to check per-model/per-scenario iteration counts.

Reports how many iterations each model has for each scenario, helping verify
that data collection completed successfully.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.run_local_ollama import get_models


def check_iterations(input_dir: Path) -> Dict[str, Dict[str, int]]:
    """
    Check iteration counts per model per scenario.
    
    Returns:
        Dict mapping model -> scenario_id -> iteration_count
    """
    models = get_models()
    results: Dict[str, Dict[str, int]] = {}
    
    for model in models:
        model_slug = model.replace("/", "_").replace(":", "_")
        jsonl_path = input_dir / f"{model_slug}.jsonl"
        
        scenario_counts: Dict[str, Set[int]] = defaultdict(set)
        
        if not jsonl_path.exists():
            results[model] = {}
            continue
        
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    scenario_id = data.get("id")
                    iteration = data.get("iteration", 1)
                    
                    if scenario_id and data.get("response"):
                        scenario_counts[scenario_id].add(iteration)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        results[model] = {
            scenario_id: len(iterations)
            for scenario_id, iterations in scenario_counts.items()
        }
    
    return results


def print_summary(results: Dict[str, Dict[str, int]], verbose: bool = False) -> None:
    """Print a summary table of iteration counts."""
    all_models = list(results.keys())
    all_scenarios: Set[str] = set()
    for model_data in results.values():
        all_scenarios.update(model_data.keys())
    
    all_scenarios = sorted(all_scenarios)
    
    if not all_scenarios:
        print("No data found in input directory.")
        return
    
    print("\n" + "=" * 80)
    print("Iteration Count Summary")
    print("=" * 80)
    
    # Per-model summary
    print(f"\n{'Model':<30} {'Total Responses':<20} {'Unique Scenarios':<20}")
    print("-" * 80)
    for model in all_models:
        model_data = results[model]
        total = sum(model_data.values())
        unique = len(model_data)
        print(f"{model:<30} {total:<20} {unique:<20}")
    
    # Per-scenario details (if verbose)
    if verbose and all_scenarios:
        print(f"\n{'=' * 80}")
        print("Detailed Per-Scenario Counts")
        print("=" * 80)
        print(f"\n{'Scenario ID':<20} " + " ".join(f"{m[:10]:<10}" for m in all_models))
        print("-" * 80)
        
        for scenario_id in all_scenarios[:20]:  # Limit to first 20 for readability
            counts = [str(results[m].get(scenario_id, 0)) for m in all_models]
            print(f"{scenario_id:<20} " + " ".join(f"{c:<10}" for c in counts))
        
        if len(all_scenarios) > 20:
            print(f"\n... and {len(all_scenarios) - 20} more scenarios (use --verbose for full output)")
    
    # Validation warnings
    print(f"\n{'=' * 80}")
    print("Validation")
    print("=" * 80)
    
    warnings = []
    expected_iterations: Dict[str, int] = {}
    
    # Detect expected iteration count from most common value per model
    for model in all_models:
        model_data = results[model]
        if not model_data:
            warnings.append(f"⚠️  {model}: No data found")
            continue
        
        # Find most common iteration count
        from collections import Counter
        counts = Counter(model_data.values())
        if counts:
            most_common = counts.most_common(1)[0][0]
            expected_iterations[model] = most_common
    
    # Check for scenarios with inconsistent iteration counts
    for scenario_id in all_scenarios:
        model_counts = [results[m].get(scenario_id, 0) for m in all_models]
        if model_counts:
            min_count = min(model_counts)
            max_count = max(model_counts)
            if min_count != max_count:
                warnings.append(
                    f"⚠️  Scenario {scenario_id}: inconsistent counts "
                    f"(range: {min_count}-{max_count})"
                )
        
        # Check against expected for each model
        for model in all_models:
            expected = expected_iterations.get(model, 0)
            actual = results[model].get(scenario_id, 0)
            if expected > 0 and actual > 0 and actual != expected:
                warnings.append(
                    f"⚠️  {model} [{scenario_id}]: expected {expected}, got {actual}"
                )
    
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("✓ All scenarios have consistent iteration counts")
    
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check iteration counts per model per scenario",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("results/local_runs_expanded"),
        help="Input directory containing JSONL files (default: results/local_runs_expanded)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed per-scenario counts",
    )
    
    args = parser.parse_args()
    
    if not args.input_dir.exists():
        print(f"Error: Input directory not found: {args.input_dir}")
        return
    
    results = check_iterations(args.input_dir)
    print_summary(results, verbose=args.verbose)


if __name__ == "__main__":
    main()
