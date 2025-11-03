# How Phase 1 Expansion Preserves Data & Manages Temperatures

## Summary

The script **preserves all existing iterations 1-5** and **generates only new iterations 6-10** with correct temperatures (0.0-0.5).

---

## 1. Preserving Existing Data (Iterations 1-5)

### Mechanism:
1. **Resume mode loads existing records**:
   ```python
   existing_keys: Dict[tuple, Dict[str, Any]] = {}
   # Loads all (scenario_id, iteration) pairs from file
   # Example: (MC21-001-N, 1), (MC21-001-N, 2), ..., (MC21-001-N, 5)
   ```

2. **File opened in APPEND mode** (not overwrite):
   ```python
   out_f = out_path.open("a", encoding="utf-8")  # 'a' = append, preserves existing
   ```

3. **Skip check for existing iterations**:
   ```python
   for iteration in range(1, iterations + 1):
       if resume and (rec_id, iteration) in existing_keys:
           existing = existing_keys[(rec_id, iteration)]
           if existing.get("response"):
               continue  # SKIP - preserves existing data
   ```

### Result:
- ✅ Iterations 1-5: **Never touched** (preserved exactly as-is)
- ✅ Existing temperature values: **Maintained** (0.6, 0.7, 0.8, 0.9, 1.0)
- ✅ File grows by appending, never overwrites

---

## 2. Managing New Temperatures (Iterations 6-10)

### Temperature Mapping:
The script receives temperatures in order:
```python
temperatures = [0.6, 0.7, 0.8, 0.9, 1.0, 0.0, 0.2, 0.3, 0.4, 0.5]
#                ↑    ↑    ↑    ↑    ↑    ↑    ↑    ↑    ↑    ↑
#              iter1 iter2 iter3 iter4 iter5 iter6 iter7 iter8 iter9 iter10
```

### Logic:
```python
temp = temp_per_iteration[iteration - 1]
# Iteration 6 → temp_per_iteration[5] = 0.0
# Iteration 7 → temp_per_iteration[6] = 0.2
# Iteration 8 → temp_per_iteration[7] = 0.3
# Iteration 9 → temp_per_iteration[8] = 0.4
# Iteration 10 → temp_per_iteration[9] = 0.5
```

### Generation:
- For iterations 6-10: `(rec_id, iteration)` **doesn't exist** in `existing_keys`
- Script **generates** with correct temperature from `temp_per_iteration`
- **Writes immediately** after each generation:
  ```python
  out_f.write(json.dumps(record) + "\n")
  out_f.flush()  # Immediate disk write
  ```

### Result:
- ✅ Iterations 6-10: **Generated** with temperatures 0.0, 0.2, 0.3, 0.4, 0.5
- ✅ Progress visible in real-time (incremental writing)
- ✅ Final file: 300 responses per model (150 existing + 150 new)

---

## 3. Complete Temperature Coverage

### Before Expansion:
- Iterations: 1-5
- Temperatures: 0.6, 0.7, 0.8, 0.9, 1.0
- Coverage: **High range only** (0.6-1.0)

### After Expansion:
- Iterations: 1-10
- Temperatures: 0.6, 0.7, 0.8, 0.9, 1.0, **0.0, 0.2, 0.3, 0.4, 0.5**
- Coverage: **Full range** (0.0-1.0)

---

## 4. Verification

You can verify the logic works:

```python
# For scenario MC21-001-N:
Iter 1 (temp 0.6): SKIP (already exists)      ← Preserved
Iter 2 (temp 0.7): SKIP (already exists)      ← Preserved
Iter 3 (temp 0.8): SKIP (already exists)      ← Preserved
Iter 4 (temp 0.9): SKIP (already exists)      ← Preserved
Iter 5 (temp 1.0): SKIP (already exists)      ← Preserved
Iter 6 (temp 0.0): GENERATE (not in file)     ← New
Iter 7 (temp 0.2): GENERATE (not in file)     ← New
Iter 8 (temp 0.3): GENERATE (not in file)     ← New
Iter 9 (temp 0.4): GENERATE (not in file)     ← New
Iter 10 (temp 0.5): GENERATE (not in file)    ← New
```

---

## Key Code Sections

### Resume Mode (Lines 343-359):
```python
existing_keys: Dict[tuple, Dict[str, Any]] = {}
if resume and out_path.exists():
    # Load all existing records
    for line in in_f:
        data = json.loads(line)
        rec_id = data.get("id")
        iter_num = data.get("iteration", 1)
        if rec_id:
            existing_keys[(rec_id, iter_num)] = data
```

### Skip Logic (Lines 377-380):
```python
if resume and (rec_id, iteration) in existing_keys:
    existing = existing_keys[(rec_id, iteration)]
    if existing.get("response"):
        continue  # Skip existing iterations
```

### Temperature Assignment (Line 383):
```python
temp = temp_per_iteration[iteration - 1]
# Uses correct temperature for each iteration
```

### Incremental Writing (Lines 411-413):
```python
out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
out_f.flush()  # Immediate disk write for real-time progress
```

---

## Conclusion

✅ **Existing data is 100% safe** - never modified or overwritten
✅ **New temperatures correctly assigned** - 0.0-0.5 for iterations 6-10
✅ **Progress visible in real-time** - incremental writing with flush
✅ **Complete coverage** - full temperature range 0.0-1.0 after expansion

