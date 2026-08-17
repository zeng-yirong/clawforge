"""
Verify that the agent produced the correct blocked requests file.
Expected: ops/blocked_requests.json containing exactly these three request IDs:
    "req_fin_001", "req_arch_002", "req_fin_003"
Order does not matter.
"""
import sys
import json
import os
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check ops directory exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory missing"
        })

    # 2. Check blocked_requests.json exists (10 points)
    target_file = os.path.join(ops_dir, "blocked_requests.json")
    if os.path.isfile(target_file):
        score_details.append({
            "item": "blocked_requests.json file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found at ops/blocked_requests.json"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "blocked_requests.json file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # If file doesn't exist, we can't continue further checks
        final_score = total_score
        _write_score(final_score, score_details, workspace)
        return

    # 3. Validate JSON format (10 points)
    try:
        with open(target_file, "r") as f:
            content = json.load(f)
        # Must be a list
        if isinstance(content, list):
            score_details.append({
                "item": "JSON is a valid list",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Content is a JSON array"
            })
            total_score += 10
        else:
            score_details.append({
                "item": "JSON is a valid list",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Expected a list, got {type(content).__name__}"
            })
    except json.JSONDecodeError as e:
        score_details.append({
            "item": "JSON is a valid list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        final_score = total_score
        _write_score(final_score, score_details, workspace)
        return

    # 4. Check that all items are strings (10 points)
    if all(isinstance(x, str) for x in content):
        score_details.append({
            "item": "All elements are strings",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Each entry is a string request ID"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "All elements are strings",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Some entries are not strings"
        })

    # 5. Content exact match (60 points) — expect specific set
    expected_ids = {"req_fin_001", "req_arch_002", "req_fin_003"}
    actual_ids = set(content)
    if actual_ids == expected_ids:
        score_details.append({
            "item": "Blocked request IDs match expected set",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": "All three correct IDs present; no extra, no missing"
        })
        total_score += 60
    else:
        # Partial scoring: count correct matches
        correct = actual_ids & expected_ids
        false_positive = actual_ids - expected_ids
        false_negative = expected_ids - actual_ids
        points = len(correct) * 20  # each correct ID gives 20 points, max 60
        reason_parts = []
        if correct:
            reason_parts.append(f"Correct IDs found: {sorted(correct)}")
        if false_positive:
            reason_parts.append(f"Unexpected extra IDs: {sorted(false_positive)}")
        if false_negative:
            reason_parts.append(f"Missing IDs: {sorted(false_negative)}")
        score_details.append({
            "item": "Blocked request IDs match expected set",
            "score": points,
            "max_score": 60,
            "passed": points == 60,
            "reason": "; ".join(reason_parts) if reason_parts else "No match"
        })
        total_score += points

    # 6. Bonus: No extra files in ops/ (no points, but keep clean)
    # Not scored, but noted if present
    final_score = min(total_score, 100)
    _write_score(final_score, score_details, workspace)

def _write_score(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {out_path}")

if __name__ == "__main__":
    main()
