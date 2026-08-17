import json
import os
import sys
import re

def verify(workspace: str) -> dict:
    details = []
    total = 0

    # 1) postmortems directory exists (10)
    postmortems_dir = os.path.join(workspace, "postmortems")
    if os.path.isdir(postmortems_dir):
        details.append({"item": "postmortems directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory found"})
        total += 10
    else:
        details.append({"item": "postmortems directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'postmortems' not found"})

    # 2) expected report file exists (10)
    report_path = os.path.join(postmortems_dir, "fault_014_postmortem.json")
    if os.path.isfile(report_path):
        details.append({"item": "report file exists", "score": 10, "max_score": 10, "passed": True, "reason": "fault_014_postmortem.json found"})
        total += 10
    else:
        details.append({"item": "report file exists", "score": 0, "max_score": 10, "passed": False, "reason": "fault_014_postmortem.json not found in postmortems/"})

    # 3) JSON is valid (10)
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON valid", "score": 10, "max_score": 10, "passed": True, "reason": "File parses as valid JSON"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        return {"total_score": total, "details": details}

    # 4) fault_id correct (20)
    if isinstance(data, dict) and data.get("fault_id") == "fault_014":
        details.append({"item": "fault_id correct", "score": 20, "max_score": 20, "passed": True, "reason": "fault_id is 'fault_014'"})
        total += 20
    else:
        details.append({"item": "fault_id correct", "score": 0, "max_score": 20, "passed": False, "reason": f"fault_id is {data.get('fault_id')}, expected 'fault_014'"})

    # 5) transaction_id correct (30)
    expected_tx = "TX-2024-03-15-001"
    actual_tx = data.get("transaction_id")
    if actual_tx == expected_tx:
        details.append({"item": "transaction_id correct", "score": 30, "max_score": 30, "passed": True, "reason": f"transaction_id is '{expected_tx}'"})
        total += 30
    else:
        details.append({"item": "transaction_id correct", "score": 0, "max_score": 30, "passed": False, "reason": f"Got '{actual_tx}', expected '{expected_tx}'"})

    # 6) root_cause correct (20)
    expected_cause = "Deadlock due to long-running transaction"
    actual_cause = data.get("root_cause")
    if actual_cause == expected_cause:
        details.append({"item": "root_cause correct", "score": 20, "max_score": 20, "passed": True, "reason": f"root_cause matches expected"})
        total += 20
    else:
        details.append({"item": "root_cause correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Got '{actual_cause}', expected '{expected_cause}'"})

    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
