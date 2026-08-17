import sys
import os
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # ---------- 1. Directory structure (10pts) ----------
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    if dir_exists:
        total_score += 10
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})

    # ---------- 2. handover_checklist.json exists (10pts) ----------
    checklist_path = os.path.join(ops_dir, "handover_checklist.json")
    file_exists = os.path.isfile(checklist_path)
    if file_exists:
        total_score += 10
        details.append({"item": "handover_checklist.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File present"})
    else:
        details.append({"item": "handover_checklist.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})
        # If file missing, no further checks possible
        return {"total_score": total_score, "details": details}

    # ---------- 3. JSON validity (10pts) ----------
    try:
        with open(checklist_path, "r") as f:
            data = json.load(f)
        total_score += 10
        details.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
    except Exception as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
        return {"total_score": total_score, "details": details}

    # ---------- 4. Top-level is list (5pts) ----------
    if isinstance(data, list):
        total_score += 5
        details.append({"item": "Top-level is list", "score": 5, "max_score": 5, "passed": True, "reason": "Root is an array"})
    else:
        details.append({"item": "Top-level is list", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected list, got {type(data).__name__}"})
        # No point checking further if not a list
        return {"total_score": total_score, "details": details}

    # ---------- 5. Exactly one entry (Alice) (15pts) ----------
    if len(data) == 1:
        total_score += 15
        details.append({"item": "Exactly one employee in list", "score": 15, "max_score": 15, "passed": True, "reason": "Only Alice should be present"})
    else:
        total_score += 0
        details.append({"item": "Exactly one employee in list", "score": 0, "max_score": 15, "passed": False, "reason": f"Got {len(data)} entries, expected 1"})
        # Continue to check the first entry anyway

    entry = data[0] if data else {}

    # ---------- 6. Field: employee_id (5pts) ----------
    expected_id = "E001"
    actual_id = entry.get("employee_id")
    if actual_id == expected_id:
        total_score += 5
        details.append({"item": "employee_id matches E001", "score": 5, "max_score": 5, "passed": True, "reason": "Correct ID"})
    else:
        details.append({"item": "employee_id matches E001", "score": 0, "max_score": 5, "passed": False, "reason": f"Got '{actual_id}', expected 'E001'"})

    # ---------- 7. Field: employee_name (5pts) ----------
    expected_name = "Alice Wang"
    actual_name = entry.get("employee_name")
    if actual_name == expected_name:
        total_score += 5
        details.append({"item": "employee_name matches", "score": 5, "max_score": 5, "passed": True, "reason": "Correct name"})
    else:
        details.append({"item": "employee_name matches", "score": 0, "max_score": 5, "passed": False, "reason": f"Got '{actual_name}', expected '{expected_name}'"})

    # ---------- 8. Field: department (5pts) ----------
    expected_dept = "Engineering"
    actual_dept = entry.get("department")
    if actual_dept == expected_dept:
        total_score += 5
        details.append({"item": "department matches", "score": 5, "max_score": 5, "passed": True, "reason": "Correct department"})
    else:
        details.append({"item": "department matches", "score": 0, "max_score": 5, "passed": False, "reason": f"Got '{actual_dept}', expected '{expected_dept}'"})

    # ---------- 9. Field: systems_revoked (20pts) ----------
    expected_systems = {"Admin Portal", "CRM"}
    actual_systems = entry.get("systems_revoked")
    if isinstance(actual_systems, list):
        actual_set = set(actual_systems)
        if actual_set == expected_systems:
            total_score += 20
            details.append({"item": "systems_revoked correct", "score": 20, "max_score": 20, "passed": True, "reason": "Both systems listed"})
        elif actual_set.issuperset(expected_systems) or actual_set.issubset(expected_systems):
            total_score += 10
            details.append({"item": "systems_revoked partially correct", "score": 10, "max_score": 20, "passed": True, "reason": f"Have {actual_set}, expected {expected_systems}"})
        else:
            details.append({"item": "systems_revoked incorrect", "score": 0, "max_score": 20, "passed": False, "reason": f"Got {actual_set}, expected {expected_systems}"})
    else:
        details.append({"item": "systems_revoked must be a list", "score": 0, "max_score": 20, "passed": False, "reason": "Not a list"})

    # ---------- 10. Field: equipment_reclaimed (20pts) ----------
    expected_equipment = {"LT-2041"}
    actual_equipment = entry.get("equipment_reclaimed")
    if isinstance(actual_equipment, list):
        actual_set = set(actual_equipment)
        if actual_set == expected_equipment:
            total_score += 20
            details.append({"item": "equipment_reclaimed correct", "score": 20, "max_score": 20, "passed": True, "reason": "Asset LT-2041 listed"})
        elif len(actual_set) == 0 or actual_set != expected_equipment:
            details.append({"item": "equipment_reclaimed incorrect", "score": 0, "max_score": 20, "passed": False, "reason": f"Got {actual_set}, expected {expected_equipment}"})
    else:
        details.append({"item": "equipment_reclaimed must be a list", "score": 0, "max_score": 20, "passed": False, "reason": "Not a list"})

    return {"total_score": min(total_score, 100), "details": details}

if __name__ == "__main__":
    result = verify()
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Verification complete. Score written to workplace_score.json")
