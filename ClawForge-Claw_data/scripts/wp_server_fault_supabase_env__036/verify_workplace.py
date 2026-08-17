import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # --- check ops directory exists (10 pts) ---
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Directory ops/ present" if dir_exists else "ops/ not found"
    })
    if dir_exists:
        total_score += 10

    # --- check remediation report exists and valid JSON (10 pts) ---
    report_path = os.path.join(ops_dir, "remediation_report.json")
    if not os.path.isfile(report_path):
        details.append({
            "item": "remediation_report.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File ops/remediation_report.json not found"
        })
        # can't proceed further, but still calculate rest as 0
    else:
        details.append({
            "item": "remediation_report.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File ops/remediation_report.json found"
        })
        total_score += 10

        # --- parse JSON ---
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            json_valid = True
        except (json.JSONDecodeError, Exception):
            json_valid = False
            data = None

        details.append({
            "item": "JSON format valid",
            "score": 10 if json_valid else 0,
            "max_score": 10,
            "passed": json_valid,
            "reason": "Valid JSON" if json_valid else "Invalid JSON content"
        })
        if json_valid:
            total_score += 10

        # --- must be a list (10 pts) ---
        is_list = isinstance(data, list)
        details.append({
            "item": "Top-level is a list",
            "score": 10 if is_list else 0,
            "max_score": 10,
            "passed": is_list,
            "reason": "Root element is list" if is_list else "Root element is not a list"
        })
        if is_list:
            total_score += 10

        if is_list and json_valid:
            # --- each item must have required keys (20 pts) ---
            required_keys = {"incident_id", "action", "status"}
            keys_ok = all(isinstance(item, dict) and required_keys.issubset(item.keys()) for item in data)
            details.append({
                "item": "All entries have incident_id, action, status",
                "score": 20 if keys_ok else 0,
                "max_score": 20,
                "passed": keys_ok,
                "reason": "All entries complete" if keys_ok else "Missing keys in one or more entries"
            })
            if keys_ok:
                total_score += 20

            # --- expected incidents: INC-001, INC-002 (30 pts) ---
            actual_ids = [item["incident_id"] for item in data]
            expected_ids = {"INC-001", "INC-002"}
            if set(actual_ids) == expected_ids and len(actual_ids) == 2:
                id_correct = True
            else:
                id_correct = False
            details.append({
                "item": "Incident IDs match expected open service-down tickets",
                "score": 30 if id_correct else 0,
                "max_score": 30,
                "passed": id_correct,
                "reason": f"IDs {actual_ids} match expected {expected_ids}" if id_correct else f"IDs {actual_ids} != expected {expected_ids}"
            })
            if id_correct:
                total_score += 30

            # --- action must be "restart-service" for each (10 pts) ---
            actions_correct = all(item["action"] == "restart-service" for item in data)
            details.append({
                "item": "Action is 'restart-service' for all entries",
                "score": 10 if actions_correct else 0,
                "max_score": 10,
                "passed": actions_correct,
                "reason": "All actions correct" if actions_correct else "Some actions are not 'restart-service'"
            })
            if actions_correct:
                total_score += 10

            # --- status must be "completed" (10 pts) ---
            status_correct = all(item["status"] == "completed" for item in data)
            details.append({
                "item": "Status is 'completed' for all entries",
                "score": 10 if status_correct else 0,
                "max_score": 10,
                "passed": status_correct,
                "reason": "All status correct" if status_correct else "Some status are not 'completed'"
            })
            if status_correct:
                total_score += 10

    # write score file
    score_file = os.path.join(workspace, "workplace_score.json")
    report = {
        "total_score": total_score,
        "details": details
    }
    with open(score_file, "w") as f:
        json.dump(report, f, indent=2)

    # Also print to stderr for debugging
    print(f"Total score: {total_score}/100", file=sys.stderr)

if __name__ == "__main__":
    main()
