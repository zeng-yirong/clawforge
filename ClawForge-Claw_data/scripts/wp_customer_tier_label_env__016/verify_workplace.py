import os
import sys
import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify(workspace):
    results = []
    total_score = 0

    # --- 1. Directory structure (10 points) ---
    dir_exists = os.path.isdir(os.path.join(workspace, "results"))
    if dir_exists:
        results.append({"item": "results directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory 'results/' found"})
        total_score += 10
    else:
        results.append({"item": "results directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'results/' not found"})

    # --- 2. File exists (10 points) ---
    result_path = os.path.join(workspace, "results", "updated_labels.json")
    file_exists = os.path.isfile(result_path)
    if file_exists:
        results.append({"item": "results/updated_labels.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10
    else:
        results.append({"item": "results/updated_labels.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # cannot proceed further
        final_score = total_score
        write_score(workspace, final_score, results)
        return final_score

    # --- 3. JSON validity (10 points) ---
    try:
        data = load_json(result_path)
        results.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        total_score += 10
    except Exception as e:
        results.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
        write_score(workspace, total_score, results)
        return total_score

    # --- 4. Correct keys (all 5 customer IDs present) (20 points) ---
    expected_keys = {"C001", "C002", "C003", "C004", "C005"}
    actual_keys = set(data.keys())
    missing_keys = expected_keys - actual_keys
    extra_keys = actual_keys - expected_keys
    if missing_keys or extra_keys:
        reason_parts = []
        if missing_keys:
            reason_parts.append(f"Missing keys: {missing_keys}")
        if extra_keys:
            reason_parts.append(f"Extra keys: {extra_keys}")
        results.append({"item": "All 5 customer IDs present", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(reason_parts)})
    else:
        results.append({"item": "All 5 customer IDs present", "score": 20, "max_score": 20, "passed": True, "reason": "All expected keys found"})
        total_score += 20

    # --- 5. Label correctness per customer (60 points, 12 each) ---
    # Expected labels (order insensitive, using sets for comparison)
    expected_labels = {
        "C001": {"active", "high_value"},
        "C002": {"vip", "low_value"},
        "C003": {"new"},
        "C004": {"inactive", "low_value"},
        "C005": {"startup"}
    }
    per_customer_score = 12  # 5 * 12 = 60
    for cust_id in expected_keys:
        if cust_id not in data:
            results.append({"item": f"Labels for {cust_id}", "score": 0, "max_score": per_customer_score, "passed": False, "reason": "Customer missing"})
            continue
        actual_labels = set(data[cust_id])
        expected_set = expected_labels[cust_id]
        if actual_labels == expected_set:
            results.append({"item": f"Labels for {cust_id}", "score": per_customer_score, "max_score": per_customer_score, "passed": True, "reason": f"Got {sorted(actual_labels)}"})
            total_score += per_customer_score
        else:
            # Partial credit possible? For simplicity, 0 if not exact match
            results.append({"item": f"Labels for {cust_id}", "score": 0, "max_score": per_customer_score, "passed": False, "reason": f"Expected {sorted(expected_set)}, got {sorted(actual_labels)}"})

    final_score = min(total_score, 100)
    write_score(workspace, final_score, results)
    return final_score

def write_score(workspace, score, details):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, 'w') as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    print(f"Total score: {result}")
