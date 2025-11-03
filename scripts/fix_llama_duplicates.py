#!/usr/bin/env python3
"""
Fix duplicate records in llama3_8b.jsonl.

Keeps first occurrence of each (scenario_id, iteration) pair.
Creates backup before modifying.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Tuple

def fix_duplicates(jsonl_path: Path) -> None:
    """Remove duplicate records, keeping first occurrence."""
    backup_path = jsonl_path.with_suffix('.jsonl.backup')
    
    # Create backup
    print(f"Creating backup: {backup_path}")
    shutil.copy2(jsonl_path, backup_path)
    
    # Read all records
    records = []
    seen_keys: Dict[Tuple[str, int], int] = {}  # key -> line number of first occurrence
    duplicates_removed = 0
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                scenario_id = data.get("id")
                iteration = data.get("iteration")
                key = (scenario_id, iteration) if scenario_id else None
                
                if key:
                    if key in seen_keys:
                        duplicates_removed += 1
                        print(f"  Removing duplicate at line {line_num}: {key} (first at line {seen_keys[key]})")
                    else:
                        seen_keys[key] = line_num
                        records.append(line)
            except json.JSONDecodeError as e:
                print(f"  Skipping invalid JSON at line {line_num}: {e}")
    
    # Write deduplicated records
    print(f"\nWriting {len(records)} unique records...")
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(record + '\n')
    
    print(f"\n✓ Fixed!")
    print(f"  Removed {duplicates_removed} duplicate records")
    print(f"  Kept {len(records)} unique records")
    print(f"  Backup saved at: {backup_path}")

if __name__ == '__main__':
    import sys
    jsonl_path = Path("results/local_runs_expanded/llama3_8b.jsonl")
    
    if len(sys.argv) > 1:
        jsonl_path = Path(sys.argv[1])
    
    if not jsonl_path.exists():
        print(f"ERROR: File not found: {jsonl_path}")
        sys.exit(1)
    
    fix_duplicates(jsonl_path)

