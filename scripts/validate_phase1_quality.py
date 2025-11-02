#!/usr/bin/env python3
"""
Quality validation script for Phase 1 data generation.
Checks for:
- Response validity (non-empty, no errors)
- Expected counts per model
- Sample response quality
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# Handle imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from scripts.run_local_ollama import get_models


def validate_jsonl_file(file_path: Path) -> Tuple[int, int, int, List[str]]:
    """
    Validate a JSONL file and return stats.
    Returns: (total_lines, valid_responses, errors, error_messages)
    """
    total = 0
    valid = 0
    errors = 0
    error_messages = []
    
    if not file_path.exists():
        return 0, 0, 0, [f"File does not exist: {file_path}"]
    
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                total += 1
                
                try:
                    data = json.loads(line)
                    
                    # Check for required fields
                    if "id" not in data:
                        errors += 1
                        error_messages.append(f"Line {line_num}: Missing 'id' field")
                        continue
                    
                    # Check for response
                    response = data.get("response", "")
                    if not response or len(response.strip()) == 0:
                        errors += 1
                        error_messages.append(f"Line {line_num} [{data.get('id')}]: Empty response")
                        continue
                    
                    # Check for error field
                    if "error" in data:
                        errors += 1
                        error_messages.append(f"Line {line_num} [{data.get('id')}]: Has error field: {data.get('error')[:100]}")
                        continue
                    
                    # Check response length (should be reasonable)
                    if len(response) < 10:
                        errors += 1
                        error_messages.append(f"Line {line_num} [{data.get('id')}]: Response too short ({len(response)} chars)")
                        continue
                    
                    # Check for thinking field usage (deepseek-r1)
                    if data.get("model") == "deepseek-r1:7b" and "thinking" in str(data).lower():
                        # This is OK - it's a thinking model
                        pass
                    
                    valid += 1
                    
                except json.JSONDecodeError as e:
                    errors += 1
                    error_messages.append(f"Line {line_num}: Invalid JSON - {str(e)[:100]}")
                    continue
                    
    except Exception as e:
        error_messages.append(f"Error reading file: {str(e)}")
    
    return total, valid, errors, error_messages


def check_sample_responses(file_path: Path, n_samples: int = 3) -> List[Dict]:
    """Extract sample responses for quality inspection."""
    samples = []
    
    if not file_path.exists():
        return samples
    
    try:
        with file_path.open("r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            # Get first, middle, and last responses
            indices = [0, len(lines) // 2, len(lines) - 1] if len(lines) > 2 else list(range(len(lines)))
            
            for idx in indices[:n_samples]:
                if idx < len(lines):
                    try:
                        data = json.loads(lines[idx])
                        response = data.get("response", "")
                        samples.append({
                            "id": data.get("id"),
                            "iteration": data.get("iteration"),
                            "response_length": len(response),
                            "response_preview": response[:200] + "..." if len(response) > 200 else response,
                            "temperature": data.get("temperature"),
                            "has_error": "error" in data
                        })
                    except:
                        pass
    except:
        pass
    
    return samples


def main():
    input_dir = Path("results/local_runs_expanded")
    models = get_models()
    
    print("=" * 80)
    print("Phase 1 Data Quality Validation")
    print("=" * 80)
    print()
    
    all_errors = []
    all_samples = {}
    summary = []
    
    for model in models:
        model_slug = model.replace("/", "_").replace(":", "_")
        file_path = input_dir / f"{model_slug}.jsonl"
        
        print(f"Validating {model}...")
        print(f"  File: {file_path.name}")
        
        total, valid, errors, error_messages = validate_jsonl_file(file_path)
        samples = check_sample_responses(file_path, n_samples=3)
        
        all_errors.extend(error_messages[:5])  # Limit error messages
        all_samples[model] = samples
        summary.append({
            "model": model,
            "file_exists": file_path.exists(),
            "total": total,
            "valid": valid,
            "errors": errors,
            "expected": 150,  # 30 scenarios × 5 iterations
            "status": "✓ Complete" if valid == 150 else "⏳ In Progress" if valid > 0 else "✗ Not Started"
        })
        
        print(f"  Total lines: {total}")
        print(f"  Valid responses: {valid}")
        print(f"  Errors: {errors}")
        print(f"  Expected: 150 (30 scenarios × 5 iterations)")
        
        if samples:
            print(f"  Sample response lengths: {[s['response_length'] for s in samples]}")
        
        print()
    
    # Print summary table
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"{'Model':<30} {'Status':<15} {'Valid':<8} {'Errors':<8} {'Progress':<10}")
    print("-" * 80)
    for s in summary:
        progress = f"{s['valid']}/{s['expected']}" if s['file_exists'] else "N/A"
        print(f"{s['model']:<30} {s['status']:<15} {s['valid']:<8} {s['errors']:<8} {progress:<10}")
    print("=" * 80)
    print()
    
    # Print errors if any
    if all_errors:
        print(f"⚠️  Found {len(all_errors)} errors (showing first 5):")
        for err in all_errors[:5]:
            print(f"  - {err}")
        print()
    
    # Print sample responses
    print("Sample Responses:")
    print("-" * 80)
    for model, samples in all_samples.items():
        if samples:
            print(f"\n{model}:")
            for i, sample in enumerate(samples, 1):
                print(f"  Sample {i} [ID: {sample['id']}, Iter: {sample['iteration']}, Temp: {sample['temperature']}]")
                print(f"    Length: {sample['response_length']} chars")
                print(f"    Preview: {sample['response_preview']}")
    
    # Overall status
    total_valid = sum(s['valid'] for s in summary)
    total_expected = sum(s['expected'] for s in summary)
    total_errors = sum(s['errors'] for s in summary)
    
    print()
    print("=" * 80)
    print(f"Overall: {total_valid}/{total_expected} valid responses, {total_errors} errors")
    
    if total_valid == total_expected and total_errors == 0:
        print("✓ All data looks good!")
        sys.exit(0)
    elif total_valid > 0:
        print("⏳ Data generation in progress...")
        sys.exit(0)
    else:
        print("✗ No valid data found")
        sys.exit(1)


if __name__ == "__main__":
    main()

