#!/usr/bin/env python3
"""
Real-time monitor for Phase 1 expansion progress.
Shows detailed progress per model, iteration, and temperature.
"""

import json
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PHASE1_DIR = Path("results/local_runs_expanded")

def analyze_file(file_path: Path):
    """Analyze a model file and return statistics."""
    stats = {
        "total": 0,
        "by_iteration": defaultdict(int),
        "by_temperature": defaultdict(int),
        "by_scenario": defaultdict(set),
        "errors": 0,
    }
    
    if not file_path.exists():
        return stats
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                stats["total"] += 1
                
                iteration = data.get("iteration")
                temperature = data.get("temperature")
                scenario_id = data.get("id")
                
                if iteration:
                    stats["by_iteration"][iteration] += 1
                if temperature is not None:
                    stats["by_temperature"][temperature] += 1
                if scenario_id:
                    stats["by_scenario"][scenario_id].add(iteration)
                
                if not data.get("response") and data.get("error"):
                    stats["errors"] += 1
            except:
                stats["errors"] += 1
    
    return stats

def get_status_color(total, expected=300):
    """Get status color based on completion."""
    if total == expected:
        return "✓ COMPLETE", 32  # Green
    elif total >= expected * 0.8:
        return "● NEARLY DONE", 33  # Yellow
    elif total >= expected * 0.5:
        return "● IN PROGRESS", 33  # Yellow
    else:
        return "○ READY", 34  # Blue

def main():
    print("=" * 100)
    print("Phase 1 Expansion Real-Time Monitor")
    print("=" * 100)
    print()
    print("Expected final state:")
    print("  • 5 models × 30 scenarios × 10 iterations = 300 responses per model")
    print("  • Temperatures: 0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0")
    print()
    print("Press Ctrl+C to stop monitoring")
    print("=" * 100)
    print()
    
    try:
        while True:
            # Clear screen (works on most terminals)
            print("\033[2J\033[H", end="")
            
            print("=" * 100)
            print(f"Phase 1 Expansion Progress - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 100)
            print()
            
            all_files = sorted(PHASE1_DIR.glob("*.jsonl"))
            model_files = [f for f in all_files if "judge" not in f.stem and "summary" not in f.stem]
            
            total_responses = 0
            complete_models = 0
            
            for file_path in model_files:
                model_name = file_path.stem
                stats = analyze_file(file_path)
                
                total_responses += stats["total"]
                
                # Status
                status, color_code = get_status_color(stats["total"])
                if stats["total"] == 300:
                    complete_models += 1
                
                # Iterations breakdown
                iter_1_5 = sum(stats["by_iteration"].get(i, 0) for i in range(1, 6))
                iter_6_10 = sum(stats["by_iteration"].get(i, 0) for i in range(6, 11))
                
                # Temperature breakdown
                temp_low = sum(count for temp, count in stats["by_temperature"].items() if 0.0 <= temp <= 0.5)
                temp_high = sum(count for temp, count in stats["by_temperature"].items() if 0.6 <= temp <= 1.0)
                
                # Progress
                progress = (stats["total"] / 300) * 100 if stats["total"] <= 300 else 100
                
                # Print model status
                print(f"\033[{color_code}m{status}\033[0m {model_name}")
                print(f"  Total: {stats['total']}/300 ({progress:.1f}%) | "
                      f"Iter 1-5: {iter_1_5:3d} | Iter 6-10: {iter_6_10:3d} | "
                      f"Low temp: {temp_low:3d} | High temp: {temp_high:3d}")
                
                if stats["errors"] > 0:
                    print(f"  \033[31m⚠ Errors: {stats['errors']}\033[0m")
                
                # Show temperature coverage for iterations 6-10
                if iter_6_10 > 0:
                    expected_temps = {0.0, 0.2, 0.3, 0.4, 0.5}
                    actual_temps = {float(t) for t in stats["by_temperature"].keys() if 0.0 <= float(t) <= 0.5}
                    missing = expected_temps - actual_temps
                    if missing:
                        print(f"  Missing temps (0.0-0.5): {sorted(missing)}")
                
                print()
            
            print("=" * 100)
            print(f"Summary: {complete_models}/{len(model_files)} models complete | "
                  f"Total responses: {total_responses}/1500")
            print("=" * 100)
            print()
            print("Refreshing every 3 seconds... (Press Ctrl+C to stop)")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print()
        print("Monitoring stopped.")
        print()

if __name__ == "__main__":
    main()
