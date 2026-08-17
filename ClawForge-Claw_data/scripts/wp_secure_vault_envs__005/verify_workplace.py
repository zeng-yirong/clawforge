import sys
import json
import os
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = pathlib.Path(workspace)

    score_details = []
    total_score = 0

    # 1. Check file existence and parseability (10 points)
    file_path = workspace / "ops" / "weak_creds.json"
    if not file_path.exists():
        score_details.append({
            "item": "ops/weak_creds.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        total_score = 0
        # Can't proceed further
        write_score(total_score, score_details)
        return

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "ops/weak_creds.json exists and is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists and parsed successfully"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "ops/weak_creds.json exists and is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        write_score(total_score, score_details)
        return

    # 2. Check structure: must be a list of objects with 'id' and 'reason' (20 points)
    structure_score = 0
    if not isinstance(data, list):
        score_details.append({
            "item": "Result is a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Root is not a list"
        })
        structure_score += 0
    else:
        score_details.append({
            "item": "Result is a list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Root is a list with {len(data)} items"
        })
        structure_score += 10

    # Check each item
    all_items_valid = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            all_items_valid = False
            break
        if "id" not in item or "reason" not in item:
            all_items_valid = False
            break
        if not isinstance(item["id"], str) or not isinstance(item["reason"], str):
            all_items_valid = False
            break
        if len(item["id"]) == 0 or len(item["reason"]) == 0:
            all_items_valid = False
            break

    if all_items_valid:
        score_details.append({
            "item": "Each item has non-empty 'id' and 'reason' strings",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"All {len(data)} items valid"
        })
        structure_score += 10
    else:
        score_details.append({
            "item": "Each item has non-empty 'id' and 'reason' strings",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Some items missing fields or wrong type"
        })
        structure_score += 0

    total_score += structure_score

    # 3. Check correctness of identified weak credentials (70 points)
    expected_ids = {"cred_001", "cred_002", "cred_005", "cred_006"}
    actual_ids = set(item["id"] for item in data if isinstance(item, dict) and "id" in item)

    # Compute match percentage
    intersection = expected_ids & actual_ids
    union = expected_ids | actual_ids
    if len(union) == 0:
        match_ratio = 0.0
    else:
        match_ratio = len(intersection) / len(union)

    # Penalty for extra ids or missing ids
    correct_score = int(70 * match_ratio)

    detail_reason_parts = []
    if len(actual_ids - expected_ids) > 0:
        detail_reason_parts.append(f"extra ids: {actual_ids - expected_ids}")
    if len(expected_ids - actual_ids) > 0:
        detail_reason_parts.append(f"missing ids: {expected_ids - actual_ids}")
    if detail_reason_parts:
        reason = "Mismatches: " + "; ".join(detail_reason_parts)
    else:
        reason = "All expected weak credentials found, no extras"

    score_details.append({
        "item": "Correct weak credential IDs identified",
        "score": correct_score,
        "max_score": 70,
        "passed": correct_score == 70,
        "reason": reason
    })
    total_score += correct_score

    write_score(total_score, score_details)

def write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
