import sys
import os
import json
import csv

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path) as f:
        return json.load(f)

def load_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)

def verify():
    score_details = []

    # 1. ops directory exists (10 points)
    ops_dir = os.path.join(workspace, "ops")
    dir_ok = os.path.isdir(ops_dir)
    score_details.append({
        "item": "ops directory exists",
        "score": 10 if dir_ok else 0,
        "max_score": 10,
        "passed": dir_ok,
        "reason": "ops directory present" if dir_ok else "ops directory missing"
    })
    if not dir_ok:
        _write_score(score_details)
        return

    # 2. active_critical.json exists (10 points)
    target = os.path.join(ops_dir, "active_critical.json")
    file_ok = os.path.isfile(target)
    score_details.append({
        "item": "active_critical.json exists",
        "score": 10 if file_ok else 0,
        "max_score": 10,
        "passed": file_ok,
        "reason": "file present" if file_ok else "file missing"
    })
    if not file_ok:
        _write_score(score_details)
        return

    # 3. valid JSON (10 points)
    try:
        with open(target) as f:
            agent_output = json.load(f)
        score_details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed correctly"
        })
    except Exception as e:
        score_details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        _write_score(score_details)
        return

    # 4. Read initial files to compute ground truth
    try:
        accounts_data = load_json(os.path.join(workspace, "data", "accounts.json"))["accounts"]
        sensors_data = load_json(os.path.join(workspace, "data", "sensors", "sensors.json"))["sensors"]
        incidents_data = load_csv(os.path.join(workspace, "raw_logs", "incidents.csv"))
    except Exception as e:
        score_details.append({
            "item": "Initial files readable",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Error reading initial files: {e}"
        })
        _write_score(score_details)
        return

    # Build sensor status map
    sensor_status = {s["sensor_id"]: s["status"] for s in sensors_data}
    # Build set of resolved sensor IDs
    resolved = set()
    for row in incidents_data:
        if row["status"].strip().lower() == "resolved":
            resolved.add(row["sensor_id"].strip())
    # Build account -> sensors mapping
    account_sensors = {a["account_id"]: a["sensors"] for a in accounts_data}

    # Compute expected output
    expected = {}
    for acc_id, sids in account_sensors.items():
        crit_unresolved = []
        for sid in sids:
            if sid in sensor_status and sensor_status[sid] == "critical" and sid not in resolved:
                crit_unresolved.append(sid)
        if crit_unresolved:
            expected[acc_id] = sorted(crit_unresolved)

    # 5. Check that output is a dict (10 points)
    if not isinstance(agent_output, dict):
        score_details.append({
            "item": "Output is a dictionary",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Output is not a JSON object"
        })
        _write_score(score_details)
        return
    score_details.append({
        "item": "Output is a dictionary",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Output is a JSON object"
    })

    # 6. Keys match exactly (10 points)
    expected_keys = set(expected.keys())
    agent_keys = set(agent_output.keys())
    if expected_keys != agent_keys:
        missing = expected_keys - agent_keys
        extra = agent_keys - expected_keys
        score_details.append({
            "item": "Keys match expected accounts",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Keys mismatch, missing {missing}, extra {extra}"
        })
    else:
        score_details.append({
            "item": "Keys match expected accounts",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All account keys match"
        })

    # 7. Per-account sensor lists (30 points, 10 per account)
    account_items = {}
    for acc_id in expected:
        exp_list = sorted(expected[acc_id])
        agent_list = sorted(agent_output.get(acc_id, []))
        if exp_list == agent_list:
            account_items[acc_id] = {"score": 10, "passed": True, "reason": f"Sensors correct: {exp_list}"}
        else:
            account_items[acc_id] = {"score": 0, "passed": False, "reason": f"Expected {exp_list}, got {agent_list}"}
    for acc_id, detail in account_items.items():
        score_details.append({
            "item": f"Account '{acc_id}' sensors",
            "score": detail["score"],
            "max_score": 10,
            "passed": detail["passed"],
            "reason": detail["reason"]
        })

    # 8. Overall correctness (20 points) — all previous checks must be perfect
    all_correct = all(d["score"] == d["max_score"] for d in score_details if "Account '" in d["item"] or "Keys match" in d["item"] or "Output is a dict" in d["item"])
    if all_correct and expected_keys == agent_keys:
        score_details.append({
            "item": "Overall correctness",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "All sensors and accounts match exactly"
        })
    else:
        score_details.append({
            "item": "Overall correctness",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": "One or more mismatches found"
        })

    _write_score(score_details)

def _write_score(score_details):
    total = sum(d["score"] for d in score_details)
    result = {"total_score": total, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
