import sys
import json
import os

def verify(workspace):
    workspace = workspace.rstrip('/')
    score_details = []
    total = 0

    # Helper to add score
    def add_item(name, score, max_score, passed, reason=""):
        score_details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. Check ops/ directory exists (10 pts)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        total += add_item("ops/ directory exists", 10, 10, True)
    else:
        total += add_item("ops/ directory exists", 0, 10, False, "Directory not found")

    # 2. Check fix_schedule.json exists (10 pts)
    fix_path = os.path.join(workspace, "ops/fix_schedule.json")
    if os.path.isfile(fix_path):
        total += add_item("ops/fix_schedule.json exists", 10, 10, True)
    else:
        total += add_item("ops/fix_schedule.json exists", 0, 10, False, "File not found")
        # If file missing, we can still continue but all other checks will fail
        # We'll return early with score
        result = {"total_score": total, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. File is valid JSON (10 pts)
    try:
        with open(fix_path, "r") as f:
            data = json.load(f)
        total += add_item("fix_schedule.json is valid JSON", 10, 10, True)
    except (json.JSONDecodeError, Exception) as e:
        total += add_item("fix_schedule.json is valid JSON", 0, 10, False, str(e))
        result = {"total_score": total, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. Contains required fields (20 pts)
    required = ["account_id", "device_id", "schedule_id", "new_target_temperature"]
    missing = [f for f in required if f not in data]
    if not missing:
        total += add_item("Contains all required fields", 20, 20, True)
    else:
        total += add_item("Contains all required fields", 0, 20, False, f"Missing fields: {missing}")
        # Still continue to give partial feedback

    # 5. new_target_temperature must be 24 (20 pts)
    if data.get("new_target_temperature") == 24:
        total += add_item("new_target_temperature is 24", 20, 20, True)
    else:
        total += add_item("new_target_temperature is 24", 0, 20, False,
                          f"Got {data.get('new_target_temperature')}, expected 24")

    # 6. Correct account_id, device_id, schedule_id (30 pts)
    expected = {"account_id": "acc_001", "device_id": "dev_ac_1", "schedule_id": "sch_003"}
    correct = True
    reason_parts = []
    for key, val in expected.items():
        if data.get(key) != val:
            correct = False
            reason_parts.append(f"{key} expected '{val}', got '{data.get(key)}'")
    if correct:
        total += add_item("Correct account/device/schedule IDs", 30, 30, True)
    else:
        total += add_item("Correct account/device/schedule IDs", 0, 30, False, "; ".join(reason_parts))

    result = {"total_score": total, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(ws)
