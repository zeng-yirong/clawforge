import os
import sys
import json

def verify(workspace):
    score_details = []
    total_score = 100

    # Helper to add detail
    def add_detail(item, score, max_score, passed, reason):
        score_details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # 1. Check that ops directory exists (10 pts)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        add_detail("ops directory exists", 10, 10, True, "Directory 'ops' found.")
    else:
        add_detail("ops directory exists", 0, 10, False, "Directory 'ops' not found.")
        # If ops doesn't exist, we can't proceed, but still score other items as 0
        # We'll continue checks but all file-related will fail

    # 2. Check that blocked_attempts.json exists and is valid JSON (10 pts)
    result_file = os.path.join(workspace, "ops", "blocked_attempts.json")
    json_valid = False
    data = None
    if os.path.isfile(result_file):
        try:
            with open(result_file, "r") as f:
                data = json.load(f)
            json_valid = True
            add_detail("blocked_attempts.json is valid JSON", 10, 10, True, "JSON parsed successfully.")
        except (json.JSONDecodeError, Exception) as e:
            add_detail("blocked_attempts.json is valid JSON", 0, 10, False, f"JSON parse error: {e}")
    else:
        add_detail("blocked_attempts.json exists", 0, 10, False, "File not found.")

    # 3. Check structure: should contain a list under key "blocked_requests" or be a list directly (10 pts)
    # Allow flexible structure: either a dict with key "blocked_requests" or a list.
    blocked_list = None
    if json_valid and data is not None:
        if isinstance(data, list):
            blocked_list = data
            add_detail("Structure: top-level list", 10, 10, True, "Data is a list of blocked requests.")
        elif isinstance(data, dict) and "blocked_requests" in data:
            blocked_list = data["blocked_requests"]
            add_detail("Structure: dict with 'blocked_requests' key", 10, 10, True, "Found 'blocked_requests' key.")
        else:
            add_detail("Structure: valid format", 0, 10, False, "Data is neither a list nor a dict with 'blocked_requests' key.")
    else:
        add_detail("Structure: valid format", 0, 10, False, "No data available.")

    # 4. Check that exactly one request is blocked (30 pts)
    if blocked_list is None:
        add_detail("Blocked requests count = 1", 0, 30, False, "No blocked_requests data.")
    else:
        count = len(blocked_list)
        if count == 1:
            add_detail("Blocked requests count = 1", 30, 30, True, f"Exactly 1 request blocked: {count}.")
        else:
            add_detail("Blocked requests count = 1", 0, 30, False, f"Expected 1, found {count}.")

    # 5. Check that the blocked request has correct request_id, reason, and action (40 pts)
    # Expected: request_id = "req_vault_001", action = "deny", reason contains "External Contractor" or "violation"
    if blocked_list is not None and len(blocked_list) == 1:
        entry = blocked_list[0]
        score_item = 0
        reason_parts = []
        # 5a. request_id correct (15 pts)
        if entry.get("request_id") == "req_vault_001":
            score_item += 15
            reason_parts.append("request_id correct")
        else:
            reason_parts.append(f"request_id expected 'req_vault_001', got '{entry.get('request_id')}'")
        # 5b. action is "deny" (10 pts)
        if entry.get("action") == "deny":
            score_item += 10
            reason_parts.append("action is 'deny'")
        else:
            reason_parts.append(f"action expected 'deny', got '{entry.get('action')}'")
        # 5c. reason mentions violation (15 pts)
        reason = entry.get("reason", "")
        # Check for key phrases indicating the violation reason
        keywords = ["external", "contractor", "unauthorized", "violation", "policy"]
        if any(kw.lower() in reason.lower() for kw in keywords):
            score_item += 15
            reason_parts.append("reason contains violation context")
        else:
            reason_parts.append(f"reason lacks violation keywords; got: {reason}")
        add_detail("Blocked request fields correct", score_item, 40, score_item == 40, "; ".join(reason_parts))
    else:
        # If count not 1, score 0 for this section
        add_detail("Blocked request fields correct", 0, 40, False, "Cannot evaluate because blocked_requests count is not 1.")

    # Calculate total score (sum of all scores)
    total = sum(item["score"] for item in score_details)
    # Ensure total <= 100
    total = min(total, 100)

    # Write results
    result = {
        "total_score": total,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Total score: {total}/100")
    return total

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
