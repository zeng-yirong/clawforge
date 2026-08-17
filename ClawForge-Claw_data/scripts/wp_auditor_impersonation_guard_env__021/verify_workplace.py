import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. File existence (10 points)
    result_file = os.path.join(workspace, "ops/denied_requests.json")
    if os.path.isfile(result_file):
        score_details.append({
            "item": "Result file ops/denied_requests.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found at expected path."
        })
        total_score += 10
    else:
        score_details.append({
            "item": "Result file ops/denied_requests.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # If file missing, no point checking further
        write_score(score_details, total_score, workspace)
        return

    # 2. JSON validity and type (10 points)
    try:
        with open(result_file, "r") as f:
            agent_list = json.load(f)
        if isinstance(agent_list, list):
            score_details.append({
                "item": "Result is a valid JSON list",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Parsed successfully and type is list."
            })
            total_score += 10
        else:
            score_details.append({
                "item": "Result is a valid JSON list",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Expected list, got {type(agent_list).__name__}."
            })
            write_score(score_details, total_score, workspace)
            return
    except Exception as e:
        score_details.append({
            "item": "Result is a valid JSON list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}."
        })
        write_score(score_details, total_score, workspace)
        return

    # 3. Content accuracy (80 points)
    # Compute expected denied request IDs from ground truth data
    accounts_path = os.path.join(workspace, "data/accounts.json")
    requests_path = os.path.join(workspace, "data/requests/requests.json")
    try:
        with open(accounts_path, "r") as f:
            accounts_data = json.load(f)
        with open(requests_path, "r") as f:
            requests_data = json.load(f)
    except Exception as e:
        score_details.append({
            "item": "Content accuracy (ground truth loading)",
            "score": 0,
            "max_score": 80,
            "passed": False,
            "reason": f"Could not read ground truth data: {e}."
        })
        write_score(score_details, total_score, workspace)
        return

    # Build account permission map: account_id -> set of permissions (lowercase for comparison)
    accounts = {}
    for acc in accounts_data.get("accounts", []):
        aid = acc["account_id"]
        perms = [p.lower() for p in acc.get("permissions", [])]
        accounts[aid] = perms

    expected_ids = []
    for req in requests_data.get("requests", []):
        # Check if claimed role mentions "auditor" (case-insensitive)
        role = req.get("claimed_role", "").lower()
        if "auditor" in role:
            actor = req.get("actor_name", "")
            # Check if actor exists and has any permission starting with "audit"
            has_audit = False
            if actor in accounts:
                for perm in accounts[actor]:
                    if perm.startswith("audit"):
                        has_audit = True
                        break
            if not has_audit:
                expected_ids.append(req["request_id"])
    expected_set = set(expected_ids)
    agent_set = set(agent_list)

    # Scoring: each correct ID gives 20 points (total 60 for 3), extra IDs penalty -10 each, missing penalty -10 each
    correct = len(expected_set & agent_set)
    extra = len(agent_set - expected_set)
    missing = len(expected_set - agent_set)
    content_score = correct * 20 + max(0, (extra * 0))  # start with correct points
    # Penalties: extra and missing each cost 20 points? But we have only 80 max, so better:
    # Base 80, subtract 20 per error (missing or extra)
    # But if all 3 correct and no extra, 80; if 2 correct, 1 missing, 0 extra -> 80 - 20 = 60; etc.
    # To be precise:
    content_score = 80 - (missing * 20) - (extra * 20)
    content_score = max(0, min(80, content_score))
    passed = (missing == 0 and extra == 0)
    reason_parts = []
    if correct > 0:
        reason_parts.append(f"Correctly identified {correct} impersonators")
    if missing > 0:
        reason_parts.append(f"Missed {missing} expected ID(s): {sorted(expected_set - agent_set)}")
    if extra > 0:
        reason_parts.append(f"Falsely flagged {extra} extra ID(s): {sorted(agent_set - expected_set)}")
    reason = "; ".join(reason_parts) if reason_parts else "All impersonators correctly identified, no false positives."

    score_details.append({
        "item": "Content accuracy (denied request IDs match ground truth)",
        "score": content_score,
        "max_score": 80,
        "passed": passed,
        "reason": reason
    })
    total_score += content_score

    write_score(score_details, total_score, workspace)

def write_score(details, total, workspace):
    output = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
