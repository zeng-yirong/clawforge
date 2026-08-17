import json
import os
import sys

def verify(workspace):
    # Ensure workspace path ends with / for consistent joins
    if not workspace.endswith('/'):
        workspace += '/'

    score = 0
    details = []

    # --- 1. Directory structure (max 10) ---
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory missing"
        })

    # --- 2. deny_list.json exists (max 10) ---
    deny_path = os.path.join(workspace, "ops", "deny_list.json")
    if os.path.isfile(deny_path):
        details.append({
            "item": "deny_list.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/deny_list.json found"
        })
        score += 10
    else:
        details.append({
            "item": "deny_list.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/deny_list.json not found"
        })
        # If file missing, we cannot check further – return partial score
        total = sum(d.get("score",0) for d in details)
        result = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # --- 3. JSON format valid (max 10) ---
    try:
        with open(deny_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "deny_list.json is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully"
        })
        score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "deny_list.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {str(e)}"
        })
        total = sum(d.get("score",0) for d in details)
        result = {"total_score": total, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # --- 4. Content type is list (max 10) ---
    if isinstance(data, list):
        details.append({
            "item": "content is a JSON array",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "deny_list.json contains a list"
        })
        score += 10
    else:
        details.append({
            "item": "content is a JSON array",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected list, got {type(data).__name__}"
        })

    # --- 5. Correct request IDs (max 60) ---
    expected_ids = {"req-001", "req-003", "req-007"}
    actual_ids = set(data) if isinstance(data, list) else set()

    # Check for any unexpected IDs
    extra = actual_ids - expected_ids
    missing = expected_ids - actual_ids

    # Score: each correct ID 20, if extra present -10 per extra, if missing -20 per missing (capped at 0)
    correct_score = 0
    max_correct = 60
    correct_count = len(actual_ids & expected_ids)
    correct_score = correct_count * 20
    # Penalty for extra
    penalty_extra = len(extra) * 10
    # No extra penalty for missing (already penalized in correct_count)
    final_correct = max(0, correct_score - penalty_extra)
    final_correct = min(final_correct, max_correct)

    passed_correct = (final_correct == max_correct)
    reason_parts = []
    if missing:
        reason_parts.append(f"missing: {missing}")
    if extra:
        reason_parts.append(f"unexpected: {extra}")
    if not reason_parts:
        reason_parts.append("all expected IDs present")

    details.append({
        "item": "deny_list contains exactly req-001, req-003, req-007",
        "score": final_correct,
        "max_score": max_correct,
        "passed": passed_correct,
        "reason": "; ".join(reason_parts)
    })
    score += final_correct

    # --- Write final score ---
    result = {"total_score": score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
