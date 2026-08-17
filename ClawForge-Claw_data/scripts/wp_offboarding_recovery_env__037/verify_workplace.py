import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores = []
    total_max = 100

    # Helper to read json
    def read_json(path):
        with open(os.path.join(workspace, path), "r") as f:
            return json.load(f)

    # 1. ops directory exists (10 pts)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        scores.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
    else:
        scores.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ missing"})
        # if ops missing, subsequent checks fail
        write_score(scores, 0, workspace)
        return

    # 2. handover_checklist.json exists and valid JSON (10 pts)
    checklist_path = os.path.join(workspace, "ops/handover_checklist.json")
    try:
        with open(checklist_path, "r") as f:
            checklist = json.load(f)
        scores.append({"item": "handover_checklist.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "file ok"})
    except Exception as e:
        scores.append({"item": "handover_checklist.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        write_score(scores, 0, workspace)
        return

    # 3. Check checklist content (40 pts)
    checklist_items = [
        ("employee_id", "EMP-003", 5),
        ("employee_name", "John Doe", 5),
        ("department", "IT", 5),
        ("revoked_systems", ["Admin Portal", "CRM"], 10),
        ("reclaimed_equipment", ["BG-8821"], 10),
        ("checklist", {"system_access_revoked": True, "equipment_reclaimed": True, "handover_completed": True}, 5)
    ]
    checklist_score = 0
    checklist_max = 45  # adjust: 5+5+5+10+10+5 = 40? Actually 5+5+5+10+10+5=40. Let's keep 40
    for key, expected, pts in checklist_items:
        actual = checklist.get(key)
        if key == "checklist":
            # check subkeys
            if isinstance(actual, dict) and all(actual.get(k) == v for k, v in expected.items()):
                checklist_score += pts
                reason = f"{key} matches expected"
            else:
                reason = f"{key} mismatch: got {actual}"
        elif isinstance(expected, list):
            if isinstance(actual, list) and sorted(actual) == sorted(expected):
                checklist_score += pts
                reason = f"{key} matches expected"
            else:
                reason = f"{key} mismatch: got {actual}"
        else:
            if actual == expected:
                checklist_score += pts
                reason = f"{key} matches expected"
            else:
                reason = f"{key} mismatch: got {actual}"
        scores.append({"item": f"checklist.{key}", "score": pts if reason.startswith("matches") else 0, "max_score": pts, "passed": reason.startswith("matches"), "reason": reason})

    # 4. System access revocation for EMP-003 (10 pts, 5 per system)
    try:
        access_data = read_json("data/offboarding/system_access.json")
        access_records = access_data.get("system_access", [])
        emp3_access = [r for r in access_records if r["employee_id"] == "EMP-003"]
        if len(emp3_access) != 2:
            scores.append({"item": "EMP-003 system access records", "score": 0, "max_score": 10, "passed": False, "reason": f"expected 2 records, got {len(emp3_access)}"})
        else:
            sys_revoked = 0
            for rec in emp3_access:
                if rec["status"] == "revoked":
                    sys_revoked += 1
            if sys_revoked == 2:
                scores.append({"item": "EMP-003 system access revoked", "score": 10, "max_score": 10, "passed": True, "reason": "both systems revoked"})
            else:
                scores.append({"item": "EMP-003 system access revoked", "score": sys_revoked * 5, "max_score": 10, "passed": False, "reason": f"{sys_revoked}/2 revoked"})
    except Exception as e:
        scores.append({"item": "EMP-003 system access", "score": 0, "max_score": 10, "passed": False, "reason": f"read error: {e}"})

    # 5. Equipment reclaim for EMP-003 (10 pts)
    try:
        equip_data = read_json("data/offboarding/equipment_assignments.json")
        equip_records = equip_data.get("equipment_assignments", [])
        emp3_equip = [r for r in equip_records if r["employee_id"] == "EMP-003"]
        if len(emp3_equip) != 1:
            scores.append({"item": "EMP-003 equipment record", "score": 0, "max_score": 10, "passed": False, "reason": f"expected 1, got {len(emp3_equip)}"})
        else:
            if emp3_equip[0]["status"] == "reclaimed":
                scores.append({"item": "EMP-003 equipment reclaimed", "score": 10, "max_score": 10, "passed": True, "reason": "asset BG-8821 reclaimed"})
            else:
                scores.append({"item": "EMP-003 equipment reclaimed", "score": 0, "max_score": 10, "passed": False, "reason": f"status is {emp3_equip[0]['status']}"})
    except Exception as e:
        scores.append({"item": "EMP-003 equipment", "score": 0, "max_score": 10, "passed": False, "reason": f"read error: {e}"})

    # 6. Bonus: ensure no extra unwanted modifications (optional, but we can check other employees unchanged)
    # Not strictly required, but we can add a small penalty if we want. For simplicity, skip.

    # Calculate total
    total_score = sum(s["score"] for s in scores)
    # Ensure total_score <= 100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": scores
    }
    write_score(result, total_score, workspace)

def write_score(result, total, workspace):
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/100")

if __name__ == "__main__":
    main()
