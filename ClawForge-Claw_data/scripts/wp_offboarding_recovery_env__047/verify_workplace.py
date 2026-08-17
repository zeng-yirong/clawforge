import sys
import os
import json
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace).resolve()
    details = []
    total_score = 0

    # --- helper to load json safely ---
    def load_json(rel_path):
        try:
            with open(ws / rel_path, "r") as f:
                return json.load(f)
        except Exception as e:
            return None

    # ====== 1. Handover checklist file existence ======
    checklist_path = ws / "handover_checklist.json"
    item = {"item": "handover_checklist.json exists", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if checklist_path.exists():
        item["passed"] = True
        item["score"] = 10
        item["reason"] = "File found at expected path."
    else:
        item["reason"] = "File not found."
    details.append(item)
    total_score += item["score"]

    # ====== 2. Handover checklist valid JSON ======
    item = {"item": "handover_checklist.json valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if item["passed"]:  # only if file exists
        checklist_data = load_json("handover_checklist.json")
        if checklist_data is not None and isinstance(checklist_data, dict):
            item["passed"] = True
            item["score"] = 10
            item["reason"] = "Valid JSON object."
        else:
            item["reason"] = "Invalid or not a JSON object."
    else:
        item["reason"] = "Skipped because file missing."
    details.append(item)
    total_score += item["score"]

    # ====== 3. system_access.json exists and valid ======
    item = {"item": "system_access.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    sys_access = load_json("data/offboarding/system_access.json")
    if sys_access is not None and isinstance(sys_access, list):
        item["passed"] = True
        item["score"] = 10
        item["reason"] = "File exists and contains a list."
    else:
        item["reason"] = "Missing or invalid."
    details.append(item)
    total_score += item["score"]

    # ====== 4. equipment_assignments.json exists and valid ======
    item = {"item": "equipment_assignments.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    eq_assign = load_json("data/offboarding/equipment_assignments.json")
    if eq_assign is not None and isinstance(eq_assign, list):
        item["passed"] = True
        item["score"] = 10
        item["reason"] = "File exists and contains a list."
    else:
        item["reason"] = "Missing or invalid."
    details.append(item)
    total_score += item["score"]

    # ====== 5. system_access revocation for EMP003 ======
    item = {"item": "EMP003 system access revoked", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if sys_access is not None:
        emp3_systems = [entry for entry in sys_access if entry.get("employee_id") == "EMP003"]
        if emp3_systems:
            all_revoked = all(entry.get("status") == "revoked" for entry in emp3_systems)
            if all_revoked:
                item["passed"] = True
                item["score"] = 20
                item["reason"] = f"All {len(emp3_systems)} system(s) for EMP003 have status 'revoked'."
            else:
                item["reason"] = "Some systems for EMP003 still have a non-revoked status."
        else:
            item["reason"] = "No system access entries found for EMP003."
    else:
        item["reason"] = "system_access.json not available."
    details.append(item)
    total_score += item["score"]

    # ====== 6. equipment reclaimed for EMP003 ======
    item = {"item": "EMP003 equipment reclaimed", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if eq_assign is not None:
        emp3_eq = [entry for entry in eq_assign if entry.get("employee_id") == "EMP003"]
        if emp3_eq:
            all_reclaimed = all(entry.get("status") == "reclaimed" for entry in emp3_eq)
            if all_reclaimed:
                item["passed"] = True
                item["score"] = 20
                item["reason"] = f"All {len(emp3_eq)} equipment(s) for EMP003 have status 'reclaimed'."
            else:
                item["reason"] = "Some equipment for EMP003 still has a non-reclaimed status."
        else:
            item["reason"] = "No equipment assignments found for EMP003."
    else:
        item["reason"] = "equipment_assignments.json not available."
    details.append(item)
    total_score += item["score"]

    # ====== 7. Handover checklist content correctness ======
    item = {"item": "handover checklist fields", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if checklist_path.exists() and checklist_data is not None:
        # Load accounts for comparison
        accounts = load_json("data/accounts.json")
        expected_employee = None
        if accounts:
            for acc in accounts:
                if acc.get("account_id") == "EMP003":
                    expected_employee = acc
                    break

        errors = []
        # Check employee_id
        if checklist_data.get("employee_id") != "EMP003":
            errors.append("employee_id mismatch")
        # Check employee_name
        if expected_employee and checklist_data.get("employee_name") != expected_employee.get("display_name"):
            errors.append("employee_name mismatch")
        # Check department
        if expected_employee and checklist_data.get("department") != expected_employee.get("department"):
            errors.append("department mismatch")
        # Check systems_revoked list (should match systems from current system_access for EMP003)
        if sys_access:
            emp3_systems = [entry.get("system_name") for entry in sys_access if entry.get("employee_id") == "EMP003"]
            if sorted(checklist_data.get("systems_revoked", [])) != sorted(emp3_systems):
                errors.append("systems_revoked list does not match the systems in system_access.json")
        # Check equipment_reclaimed list
        if eq_assign:
            emp3_eq_assets = [entry.get("asset_tag") for entry in eq_assign if entry.get("employee_id") == "EMP003"]
            if sorted(checklist_data.get("equipment_reclaimed", [])) != sorted(emp3_eq_assets):
                errors.append("equipment_reclaimed list does not match assets in equipment_assignments.json")
        # Check checklist items existence
        if not isinstance(checklist_data.get("checklist"), list) or len(checklist_data["checklist"]) < 3:
            errors.append("checklist field must be a list with at least 3 items")

        if not errors:
            item["passed"] = True
            item["score"] = 20
            item["reason"] = "All required fields present and correct."
        else:
            item["reason"] = "; ".join(errors)
    else:
        item["reason"] = "Checklist missing or invalid, cannot check content."
    details.append(item)
    total_score += item["score"]

    # ====== Write score file ======
    score_output = {
        "total_score": total_score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(score_output, f, indent=2)

if __name__ == "__main__":
    main()
