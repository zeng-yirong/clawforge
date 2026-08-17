"""
Verify the agent's output for wp_privilege_export_guard_env__006.
Checks that `ops/deny_target.json` contains exactly the request IDs that should be denied:
    - Only pending requests (status == "pending")
    - Target asset's asset_type must NOT be in the current account's permissions list
Account: acc_001, permissions: ["customer_data"]
"""
import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    max_total = 100

    # ---------- 1. Directory structure (10 pts) ----------
    required_dirs = ["ops"]
    dir_score = 0
    for d in required_dirs:
        path = os.path.join(workspace, d)
        if os.path.isdir(path):
            dir_score += 5
        else:
            dir_score += 0
    score_details.append({
        "item": "ops directory exists",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": "Missing ops directory" if dir_score < 10 else "OK"
    })
    total_score += dir_score

    # ---------- 2. Output file existence (10 pts) ----------
    output_file = os.path.join(workspace, "ops", "deny_target.json")
    file_exists = os.path.isfile(output_file)
    file_score = 10 if file_exists else 0
    score_details.append({
        "item": "ops/deny_target.json exists",
        "score": file_score,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File not found" if not file_exists else "OK"
    })
    total_score += file_score

    if not file_exists:
        # early exit if file missing
        finalize(workspace, total_score, score_details)
        return

    # ---------- 3. File content validity (10 pts) ----------
    try:
        with open(output_file, "r") as f:
            deny_list = json.load(f)
        content_valid = isinstance(deny_list, list)
        content_score = 10 if content_valid else 0
        reason = "Valid JSON list" if content_valid else "Not a valid JSON list"
    except (json.JSONDecodeError, IOError):
        content_valid = False
        content_score = 0
        reason = "JSON decode error"
    score_details.append({
        "item": "Output is a valid JSON list",
        "score": content_score,
        "max_score": 10,
        "passed": content_valid,
        "reason": reason
    })
    total_score += content_score

    if not content_valid:
        finalize(workspace, total_score, score_details)
        return

    # ---------- 4. Correct denied IDs (70 pts) ----------
    # Ground truth: pending requests whose target asset type is NOT in acc_001 permissions.
    # Load reference data from workspace
    try:
        with open(os.path.join(workspace, "data/accounts.json")) as f:
            accounts = json.load(f)["accounts"]
        current_account = next(acct for acct in accounts if acct["account_id"] == "acc_001")
        permissions = current_account["permissions"]  # ["customer_data"]

        with open(os.path.join(workspace, "data/assets/assets.json")) as f:
            assets_data = json.load(f)["assets"]
        asset_map = {a["asset_id"]: a["asset_type"] for a in assets_data}

        with open(os.path.join(workspace, "data/requests/requests.json")) as f:
            requests_data = json.load(f)["requests"]
    except (FileNotFoundError, KeyError, StopIteration) as e:
        score_details.append({
            "item": "Ground truth computation",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": f"Cannot load reference data: {str(e)}"
        })
        finalize(workspace, total_score, score_details)
        return

    expected_denied = []
    for req in requests_data:
        if req["status"] != "pending":
            continue
        asset_id = req["target_asset_id"]
        asset_type = asset_map.get(asset_id, None)
        if asset_type is None:
            # asset not found – treat as should be denied (safety)
            expected_denied.append(req["request_id"])
        elif asset_type not in permissions:
            expected_denied.append(req["request_id"])

    # Expected: pending requests with architecture_data -> req_002, req_007
    # (asset_002 -> architecture_data, asset_004 -> architecture_data)
    expected_set = set(expected_denied)
    actual_set = set(deny_list)

    # Scoring: exact match gets full marks; partial matching with penalty
    correct_only = expected_set.intersection(actual_set)
    false_positives = actual_set - expected_set
    false_negatives = expected_set - actual_set

    total_correct = len(correct_only)
    total_expected = len(expected_set)
    total_actual = len(deny_list)

    if total_expected == 0 and total_actual == 0:
        correctness_score = 70
    elif total_expected == 0:
        correctness_score = 0
    else:
        # Precision/Recall based scoring
        recall = total_correct / total_expected if total_expected > 0 else 0
        precision = total_correct / total_actual if total_actual > 0 else 0
        # F1 score but scaled to 70
        if precision + recall == 0:
            f1 = 0
        else:
            f1 = 2 * precision * recall / (precision + recall)
        correctness_score = round(f1 * 70)

    # Additional penalty for extra entries beyond expected (>=1)
    if false_positives:
        correctness_score = max(0, correctness_score - 10 * len(false_positives))
    if false_negatives:
        correctness_score = max(0, correctness_score - 10 * len(false_negatives))

    correctness_score = min(correctness_score, 70)

    # Build reason string
    reason_parts = []
    if correct_only:
        reason_parts.append(f"Correctly denied: {sorted(correct_only)}")
    if false_positives:
        reason_parts.append(f"False positives (should not deny): {sorted(false_positives)}")
    if false_negatives:
        reason_parts.append(f"False negatives (should deny): {sorted(false_negatives)}")

    score_details.append({
        "item": "Denied request IDs match expected set",
        "score": correctness_score,
        "max_score": 70,
        "passed": correctness_score == 70,
        "reason": "; ".join(reason_parts) if reason_parts else "Perfect match"
    })
    total_score += correctness_score

    # ---------- Finalize ----------
    finalize(workspace, total_score, score_details)

def finalize(workspace, total_score, details):
    # Clamp score to 0-100
    total_score = max(0, min(100, total_score))
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[verify_workplace] Score: {total_score}/100 written to {score_path}")

if __name__ == "__main__":
    main()
