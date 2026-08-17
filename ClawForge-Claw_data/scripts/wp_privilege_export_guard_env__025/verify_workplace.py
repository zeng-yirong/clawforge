import os
import sys
import json
import math

def verify(workspace):
    details = []
    score = 0

    # Define expected result path
    result_path = os.path.join(workspace, "ops", "deny_result.json")

    # 1. Check file exists (10 points)
    item = {"item": "ops/deny_result.json exists", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if os.path.isfile(result_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "File found."
    else:
        item["reason"] = "File not found."
    details.append(item)
    score += item["score"]

    # 2. Check JSON format (10 points)
    item = {"item": "JSON format valid", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if item["passed"]:  # only if file exists
        try:
            with open(result_path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict):
                item["score"] = 10
                item["passed"] = True
                item["reason"] = "Valid JSON object."
            else:
                item["reason"] = "JSON is not a dict."
        except (json.JSONDecodeError, Exception) as e:
            item["reason"] = f"JSON parse error: {str(e)}"
    else:
        item["reason"] = "File missing, cannot check format."
        item["score"] = 0
    details.append(item)
    score += item["score"]

    # 3. Check request_id field exists (10 points)
    item = {"item": "Field 'request_id' present", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if item["passed"]:  # only if JSON valid
        if "request_id" in data:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = f"request_id = {data['request_id']}"
        else:
            item["reason"] = "Missing request_id field."
    else:
        item["reason"] = "JSON not available."
    details.append(item)
    score += item["score"]

    # 4. Check request_id value is correct "REQ-001" (30 points)
    item = {"item": "request_id value correct", "max_score": 30, "score": 0, "passed": False, "reason": ""}
    if item["passed"]:
        if data.get("request_id") == "REQ-001":
            item["score"] = 30
            item["passed"] = True
            item["reason"] = "Correct request ID."
        else:
            item["reason"] = f"Got '{data.get('request_id')}', expected 'REQ-001'."
    else:
        item["reason"] = "Field missing, cannot check value."
    details.append(item)
    score += item["score"]

    # 5. Check reason field exists (10 points)
    item = {"item": "Field 'reason' present", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if item["passed"]:
        if "reason" in data:
            item["score"] = 10
            item["passed"] = True
            item["reason"] = f"reason = {data['reason']}"
        else:
            item["reason"] = "Missing reason field."
    else:
        item["reason"] = "JSON not available."
    details.append(item)
    score += item["score"]

    # 6. reason contains "permission" or "permissions" (10 points)
    item = {"item": "Reason mentions 'permission'", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if item["passed"]:
        reason = data.get("reason", "")
        if "permission" in reason.lower():
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "Contains 'permission'."
        else:
            item["reason"] = "Reason does not mention permission."
    else:
        item["reason"] = "Field missing."
    details.append(item)
    score += item["score"]

    # 7. reason contains "denied" (10 points)
    item = {"item": "Reason mentions 'denied'", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if item["passed"]:
        reason = data.get("reason", "")
        if "denied" in reason.lower():
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "Contains 'denied'."
        else:
            item["reason"] = "Reason does not mention denied."
    else:
        item["reason"] = "Field missing."
    details.append(item)
    score += item["score"]

    # Additional: check no extra keys? Not required.

    # Write score
    total_score = min(100, score)  # cap at 100
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
