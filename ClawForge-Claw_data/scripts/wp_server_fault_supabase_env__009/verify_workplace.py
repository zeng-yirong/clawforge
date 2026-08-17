import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # Expected output file
    expected_path = os.path.join(workspace, "ops", "remediation_plan.json")
    if not os.path.exists(expected_path):
        details.append({
            "item": "ops/remediation_plan.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        total_score = 0
        write_score(workspace, total_score, details)
        return

    details.append({
        "item": "ops/remediation_plan.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File found"
    })

    # Validate JSON
    try:
        with open(expected_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        total_score = sum(d["score"] for d in details)
        write_score(workspace, total_score, details)
        return

    details.append({
        "item": "Valid JSON",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON parsed successfully"
    })

    # Check structure: must be a dict with key 'incidents' which is a list
    if not isinstance(data, dict) or "incidents" not in data:
        details.append({
            "item": "Structure: top-level object with 'incidents' key",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected dict with 'incidents' key, got {type(data).__name__}"
        })
        total_score = sum(d["score"] for d in details)
        write_score(workspace, total_score, details)
        return

    incidents = data["incidents"]
    if not isinstance(incidents, list):
        details.append({
            "item": "Structure: incidents is a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected list, got {type(incidents).__name__}"
        })
        total_score = sum(d["score"] for d in details)
        write_score(workspace, total_score, details)
        return

    details.append({
        "item": "Structure: incidents key with list",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Correct structure"
    })

    # Check no extra keys at top level
    if set(data.keys()) != {"incidents"}:
        details.append({
            "item": "No extra top-level keys",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Found extra keys: {set(data.keys()) - {'incidents'}}"
        })
    else:
        details.append({
            "item": "No extra top-level keys",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only 'incidents' key present"
        })

    # Define expected incidents and actions
    # Ground truth from env_builder: target incidents are INC-001 and INC-003
    # INC-001: ups_outage -> action: power_cycle
    # INC-003: service_down -> action: restart_service
    expected = {
        "INC-001": "power_cycle",
        "INC-003": "restart_service"
    }

    # Check that each incident entry has required fields and no extra fields
    required_fields = {"incident_id", "action"}
    passed_ids = set()
    errors = []
    for entry in incidents:
        if not isinstance(entry, dict):
            errors.append(f"Non-dict entry: {entry}")
            continue
        keys = set(entry.keys())
        if keys != required_fields:
            errors.append(f"Entry with keys {keys} has extra or missing fields")
            continue
        if "incident_id" not in entry or "action" not in entry:
            errors.append(f"Missing incident_id or action in {entry}")
            continue
        passed_ids.add(entry["incident_id"])

    if errors:
        details.append({
            "item": "Each incident entry has exactly incident_id and action",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "; ".join(errors)
        })
    else:
        details.append({
            "item": "Each incident entry has exactly incident_id and action",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"All {len(incidents)} entries have correct fields"
        })

    # Check no duplicates
    if len(passed_ids) != len(incidents):
        details.append({
            "item": "No duplicate incident IDs",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Found {len(incidents)} entries but only {len(passed_ids)} unique IDs"
        })
    else:
        details.append({
            "item": "No duplicate incident IDs",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "All IDs unique"
        })

    # Check that all expected IDs are present
    expected_ids = set(expected.keys())
    missing = expected_ids - passed_ids
    extra = passed_ids - expected_ids
    if missing:
        details.append({
            "item": "All required incident IDs present",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Missing incident IDs: {missing}"
        })
    elif extra:
        details.append({
            "item": "No extra incident IDs",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Extra incident IDs: {extra}"
        })
        # Still check actions for expected ones
        action_score = 0
        for inc in incidents:
            iid = inc["incident_id"]
            if iid in expected:
                if inc["action"] == expected[iid]:
                    action_score += 10
                else:
                    action_score += 0
        details.append({
            "item": "Actions match runbook for expected incidents",
            "score": action_score,
            "max_score": 20,
            "passed": action_score == 20,
            "reason": f"Scored {action_score}/20"
        })
        total_score = sum(d["score"] for d in details)
        write_score(workspace, total_score, details)
        return

    details.append({
        "item": "All required incident IDs present, no extra",
        "score": 20,
        "max_score": 20,
        "passed": True,
        "reason": "Exactly INC-001 and INC-003"
    })

    # Check actions
    action_errors = []
    for inc in incidents:
        iid = inc["incident_id"]
        if iid in expected:
            if inc["action"] != expected[iid]:
                action_errors.append(f"{iid}: expected {expected[iid]}, got {inc['action']}")
    if action_errors:
        details.append({
            "item": "Actions match runbook for all incidents",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "; ".join(action_errors)
        })
    else:
        details.append({
            "item": "Actions match runbook for all incidents",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "All actions correct: INC-001 -> power_cycle, INC-003 -> restart_service"
        })

    total_score = sum(d["score"] for d in details)
    write_score(workspace, total_score, details)

def write_score(workspace, total_score, details):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    main()
