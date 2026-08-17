import sys
import os
import json

def verify(workspace):
    details = []
    total_score = 0

    # Check ops directory exists
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops directory found"})
        total_score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops directory not found"})

    # Check target file exists
    file_path = os.path.join(workspace, "ops", "remediation_actions.json")
    if os.path.isfile(file_path):
        details.append({"item": "remediation_actions.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "remediation_actions.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # No point continuing if file missing
        write_score(details, total_score)
        return

    # Parse JSON
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON is valid", "score": 15, "max_score": 15, "passed": True, "reason": "JSON parsed successfully"})
        total_score += 15
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 15, "passed": False, "reason": f"Invalid JSON: {e}"})
        write_score(details, total_score)
        return

    # Check root key 'actions'
    if isinstance(data, dict) and "actions" in data:
        details.append({"item": "root object contains 'actions' key", "score": 10, "max_score": 10, "passed": True, "reason": "actions key present"})
        total_score += 10
    else:
        details.append({"item": "root object contains 'actions' key", "score": 0, "max_score": 10, "passed": False, "reason": "missing 'actions' key"})
        write_score(details, total_score)
        return

    actions = data["actions"]
    if not isinstance(actions, list):
        details.append({"item": "'actions' is a list", "score": 0, "max_score": 10, "passed": False, "reason": "actions is not a list"})
        write_score(details, total_score)
        return

    expected_ids = {"INC-2025-001", "INC-2025-003", "INC-2025-005"}
    expected_actions = {
        "INC-2025-001": "notify_facilities_and_activate_generator",
        "INC-2025-003": "restart_service_and_notify_team",
        "INC-2025-005": "notify_facilities_and_activate_generator"
    }
    found_ids = set()
    field_errors = 0
    action_errors = 0

    # Check each element
    for idx, entry in enumerate(actions):
        if not isinstance(entry, dict):
            details.append({"item": f"actions[{idx}] is a dict", "score": 0, "max_score": 5, "passed": False, "reason": "element is not a dict"})
            field_errors = 5  # max penalty for this sub-check
            continue
        if "incident_id" not in entry or "action" not in entry:
            details.append({"item": f"actions[{idx}] has required keys", "score": 0, "max_score": 5, "passed": False, "reason": "missing incident_id or action"})
            field_errors = 5
            continue
        iid = entry["incident_id"]
        act = entry["action"]
        found_ids.add(iid)
        if iid in expected_ids:
            if act != expected_actions[iid]:
                action_errors += 1
        else:
            # unexpected ID
            pass

    # Field presence scoring (each element had keys? if all ok give 15)
    if field_errors == 0:
        details.append({"item": "all action entries have incident_id and action", "score": 15, "max_score": 15, "passed": True, "reason": "all entries have required keys"})
        total_score += 15
    else:
        details.append({"item": "all action entries have incident_id and action", "score": 0, "max_score": 15, "passed": False, "reason": "some entries missing required keys"})

    # Correct ID set scoring
    if found_ids == expected_ids:
        details.append({"item": "incident_id set matches expected", "score": 20, "max_score": 20, "passed": True, "reason": "IDs exactly match"})
        total_score += 20
    else:
        missing = expected_ids - found_ids
        extra = found_ids - expected_ids
        reason = f"missing: {missing}, unexpected: {extra}" if (missing or extra) else "set mismatch"
        details.append({"item": "incident_id set matches expected", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # Action correctness scoring (max 25)
    action_score = max(0, 25 - action_errors * 10)  # each wrong action loses 10, cap at 0
    if action_errors == 0:
        details.append({"item": "each action matches runbook for its category", "score": 25, "max_score": 25, "passed": True, "reason": "all actions correct"})
    else:
        details.append({"item": "each action matches runbook for its category", "score": action_score, "max_score": 25, "passed": False, "reason": f"{action_errors} action(s) incorrect"})
    total_score += action_score

    # Clamp total
    total_score = max(0, min(100, total_score))
    write_score(details, total_score)

def write_score(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
