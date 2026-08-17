import json
import os
import sys

def main(workspace):
    # Expected denied request IDs (derived from env_builder.py)
    expected_ids = {"req-001", "req-002", "req-007", "req-008", "req-009"}
    details = []
    total_score = 0
    max_total = 100

    # 1. Check ops/ directory exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ present"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ missing"})

    # 2. Check deny_list.json exists (10 points)
    deny_path = os.path.join(workspace, "ops/deny_list.json")
    if os.path.isfile(deny_path):
        details.append({"item": "deny_list.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file present"})
        total_score += 10
    else:
        details.append({"item": "deny_list.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # Skip further checks if file missing
        output_result(total_score, details, workspace)
        return

    # 3. Parse JSON and validate structure (10 points)
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {str(e)}"})
        output_result(total_score, details, workspace)
        return

    if isinstance(data, dict) and "denied_request_ids" in data:
        details.append({"item": "valid JSON structure", "score": 10, "max_score": 10, "passed": True, "reason": "object with 'denied_request_ids' field"})
        total_score += 10
    else:
        details.append({"item": "valid JSON structure", "score": 0, "max_score": 10, "passed": False, "reason": "missing 'denied_request_ids' or not a dict"})
        output_result(total_score, details, workspace)
        return

    # 4. Check that the list is a list of strings (10 points)
    ids = data["denied_request_ids"]
    if isinstance(ids, list) and all(isinstance(x, str) for x in ids):
        details.append({"item": "denied_request_ids is list of strings", "score": 10, "max_score": 10, "passed": True, "reason": "format correct"})
        total_score += 10
    else:
        details.append({"item": "denied_request_ids is list of strings", "score": 0, "max_score": 10, "passed": False, "reason": "not a list or contains non-string elements"})
        output_result(total_score, details, workspace)
        return

    # 5. Exact set match (60 points) – compare sets
    actual_set = set(ids)
    if len(ids) != len(actual_set):
        # duplicates present – penalize
        details.append({"item": "denied IDs set equality", "score": 0, "max_score": 60, "passed": False, "reason": "duplicate IDs found"})
        output_result(total_score, details, workspace)
        return

    if actual_set == expected_ids:
        details.append({"item": "denied IDs set equality", "score": 60, "max_score": 60, "passed": True, "reason": "exactly matches expected set"})
        total_score += 60
    else:
        # Partial scoring based on Jaccard similarity
        intersection = actual_set & expected_ids
        union = actual_set | expected_ids
        jaccard = len(intersection) / len(union) if union else 0
        partial_score = round(jaccard * 60)
        missing = expected_ids - actual_set
        extra = actual_set - expected_ids
        reason = f"partial match; intersection={intersection}, missing={missing}, extra={extra}"
        details.append({"item": "denied IDs set equality", "score": partial_score, "max_score": 60, "passed": partial_score == 60, "reason": reason})
        total_score += partial_score

    output_result(total_score, details, workspace)

def output_result(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {out_path}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    main(workspace)
