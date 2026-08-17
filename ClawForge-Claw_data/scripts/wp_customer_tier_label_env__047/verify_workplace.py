import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def verify():
    results = []
    total_score = 0

    # ---- 1. File existence (10 points) ----
    result_path = os.path.join(workspace, "ops/customer_tier_update.json")
    exists = os.path.isfile(result_path)
    results.append({
        "item": "ops/customer_tier_update.json exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "File found" if exists else "File not found"
    })
    if not exists:
        # cannot proceed
        finalize(results)
        return

    # ---- 2. Valid JSON (10 points) ----
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        valid_json = True
    except (json.JSONDecodeError, Exception):
        valid_json = False
    results.append({
        "item": "File is valid JSON",
        "score": 10 if valid_json else 0,
        "max_score": 10,
        "passed": valid_json,
        "reason": "Valid JSON" if valid_json else "Invalid JSON"
    })
    if not valid_json:
        finalize(results)
        return

    # ---- 3. Must be a list of objects (5 bonus, but part of schema) ----
    if not isinstance(data, list):
        results.append({"item": "Result must be a list", "score": 0, "max_score": 5, "passed": False, "reason": "Not a list"})
        finalize(results)
        return
    else:
        results.append({"item": "Result is a list", "score": 5, "max_score": 5, "passed": True, "reason": "OK"})

    # ---- 4. Expected customer IDs present (3 points each, total 12) ----
    expected_ids = {"C001", "C002", "C003", "C004"}
    found_ids = set()
    for entry in data:
        if isinstance(entry, dict) and "customer_id" in entry:
            found_ids.add(entry["customer_id"])
    missing = expected_ids - found_ids
    extra = found_ids - expected_ids
    id_score = 3 * (4 - len(missing))
    results.append({
        "item": "All 4 expected customer IDs present",
        "score": id_score,
        "max_score": 12,
        "passed": len(missing) == 0,
        "reason": f"Missing: {missing}" if missing else "All present"
    })

    # ---- 5. No extra customer IDs (8 points) ----
    extra_score = 8 if len(extra) == 0 else 0
    results.append({
        "item": "No unexpected customer IDs",
        "score": extra_score,
        "max_score": 8,
        "passed": len(extra) == 0,
        "reason": f"Extra: {extra}" if extra else "No extras"
    })

    # ---- 6. Correct new_tier for each customer (15 points each, total 60) ----
    expected_tiers = {
        "C001": "gold",
        "C002": "gold",
        "C003": "bronze",
        "C004": "bronze"
    }
    correct_count = 0
    tier_errors = []
    for entry in data:
        if isinstance(entry, dict) and entry.get("customer_id") in expected_tiers:
            cid = entry["customer_id"]
            actual = entry.get("new_tier")
            expected = expected_tiers[cid]
            if actual == expected:
                correct_count += 1
            else:
                tier_errors.append(f"{cid}: expected {expected}, got {actual}")
    tier_score = (correct_count * 15)
    results.append({
        "item": "Correct new_tier for all customers",
        "score": tier_score,
        "max_score": 60,
        "passed": correct_count == 4,
        "reason": f"Errors: {', '.join(tier_errors)}" if tier_errors else "All correct"
    })

    # ---- 7. Each entry contains only customer_id and new_tier (5 points) ----
    additional_fields = []
    for entry in data:
        if isinstance(entry, dict):
            keys = set(entry.keys())
            allowed = {"customer_id", "new_tier"}
            extra_keys = keys - allowed
            if extra_keys:
                additional_fields.append((entry.get("customer_id", "unknown"), extra_keys))
    clean_score = 5 if len(additional_fields) == 0 else 0
    results.append({
        "item": "No extra fields in entries",
        "score": clean_score,
        "max_score": 5,
        "passed": len(additional_fields) == 0,
        "reason": f"Extra fields: {additional_fields}" if additional_fields else "Clean"
    })

    # ---- Compute total ----
    total_score = sum(r["score"] for r in results)
    # Ensure 0-100
    total_score = max(0, min(100, total_score))

    output = {
        "total_score": total_score,
        "details": results
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Total score: {total_score}")

def finalize(results):
    total_score = sum(r["score"] for r in results)
    total_score = max(0, min(100, total_score))
    output = {
        "total_score": total_score,
        "details": results
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Total score: {total_score}")

if __name__ == "__main__":
    verify()
