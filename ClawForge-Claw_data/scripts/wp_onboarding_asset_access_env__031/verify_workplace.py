import os
import sys
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0

    # ---------- Helper ----------
    def check_item(name, max_score, condition_func):
        nonlocal total_score
        try:
            passed, reason = condition_func()
            score = max_score if passed else 0
        except Exception as e:
            passed = False
            reason = f"Exception: {e}"
            score = 0
        total_score += score
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # ---------- 1. ops directory exists (5 pts) ----------
    def dir_exists():
        return os.path.isdir("ops"), "ops directory found"
    check_item("ops directory exists", 5, dir_exists)

    # ---------- 2. ops/email_profile.json exists and valid JSON (10 pts) ----------
    def email_profile_valid():
        if not os.path.isfile("ops/email_profile.json"):
            return False, "file missing"
        with open("ops/email_profile.json") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False, "not a JSON object"
        # Must contain employee_name, email, department
        required = ["employee_name", "email", "department"]
        for field in required:
            if field not in data:
                return False, f"missing field: {field}"
        return True, "valid JSON with required fields"
    check_item("ops/email_profile.json format", 10, email_profile_valid)

    # ---------- 2b. email_profile content matches Alice Johnson ----------
    def email_content():
        with open("ops/email_profile.json") as f:
            data = json.load(f)
        # Expected values from contract
        expected_name = "Alice Johnson"
        expected_email = "alice.johnson@corp.com"
        expected_dept = "Engineering"
        errors = []
        if data.get("employee_name") != expected_name:
            errors.append(f"employee_name: got '{data.get('employee_name')}', expected '{expected_name}'")
        if data.get("email") != expected_email:
            errors.append(f"email: got '{data.get('email')}', expected '{expected_email}'")
        if data.get("department") != expected_dept:
            errors.append(f"department: got '{data.get('department')}', expected '{expected_dept}'")
        if errors:
            return False, "; ".join(errors)
        return True, "all fields match signed contract"
    check_item("email_profile content correctness", 15, email_content)

    # ---------- 3. ops/system_access.json exists and valid ----------
    def sys_access_valid():
        if not os.path.isfile("ops/system_access.json"):
            return False, "file missing"
        with open("ops/system_access.json") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False, "not a JSON object"
        if "employee_id" not in data:
            return False, "missing employee_id"
        if "assigned_systems" not in data:
            return False, "missing assigned_systems"
        if not isinstance(data["assigned_systems"], list):
            return False, "assigned_systems not a list"
        return True, "valid JSON with required keys"
    check_item("ops/system_access.json format", 10, sys_access_valid)

    # ---------- 3b. system_access content matches Engineering pack ----------
    def sys_content():
        expected_id = "E001"
        expected_systems = sorted(["gitlab", "jira", "kubernetes", "internal-docs", "ci-cd"])
        with open("ops/system_access.json") as f:
            data = json.load(f)
        errors = []
        if data.get("employee_id") != expected_id:
            errors.append(f"employee_id: got '{data.get('employee_id')}', expected '{expected_id}'")
        got_sys = sorted(data.get("assigned_systems", []))
        if got_sys != expected_systems:
            errors.append(f"assigned_systems: got {got_sys}, expected {expected_systems}")
        if errors:
            return False, "; ".join(errors)
        return True, "systems match Engineering permission pack"
    check_item("system_access content correctness", 15, sys_content)

    # ---------- 4. ops/equipment_assignment.json exists and valid ----------
    def equip_valid():
        if not os.path.isfile("ops/equipment_assignment.json"):
            return False, "file missing"
        with open("ops/equipment_assignment.json") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False, "not a JSON object"
        if "employee_id" not in data:
            return False, "missing employee_id"
        if "asset_tag" not in data:
            return False, "missing asset_tag"
        return True, "valid JSON with required keys"
    check_item("ops/equipment_assignment.json format", 10, equip_valid)

    # ---------- 4b. equipment assignment must be an available laptop ----------
    def equip_content():
        with open("ops/equipment_assignment.json") as f:
            data = json.load(f)
        employee_id = data.get("employee_id")
        asset_tag = data.get("asset_tag")
        if employee_id != "E001":
            return False, f"employee_id should be E001, got {employee_id}"
        # Check that asset_tag exists in inventory and was available
        inv_path = "data/onboarding/equipment_inventory.json"
        if not os.path.isfile(inv_path):
            return False, "inventory file missing (cannot verify)"
        with open(inv_path) as f:
            inv_data = json.load(f)
        assets = inv_data.get("equipment_inventory", [])
        found = None
        for a in assets:
            if a["asset_tag"] == asset_tag:
                found = a
                break
        if found is None:
            return False, f"asset_tag '{asset_tag}' not found in inventory"
        if found["status"] != "available":
            return False, f"asset '{asset_tag}' had status '{found['status']}', expected 'available'"
        if found["asset_type"] != "laptop":
            return False, f"asset '{asset_tag}' is type '{found['asset_type']}', expected 'laptop'"
        return True, "assigned a valid available laptop to Alice"
    check_item("equipment_assignment content correctness", 15, equip_content)

    # ---------- 5. ops/welcome_message.json exists and valid ----------
    def welcome_valid():
        if not os.path.isfile("ops/welcome_message.json"):
            return False, "file missing"
        with open("ops/welcome_message.json") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False, "not a JSON object"
        if "message" not in data:
            return False, "missing 'message' key"
        if not isinstance(data["message"], str):
            return False, "'message' is not a string"
        return True, "valid JSON with message string"
    check_item("ops/welcome_message.json format", 10, welcome_valid)

    # ---------- 5b. welcome message must contain Alice's name ----------
    def welcome_content():
        with open("ops/welcome_message.json") as f:
            data = json.load(f)
        msg = data.get("message", "")
        if "Alice" in msg and "Johnson" in msg:
            return True, "message includes Alice Johnson"
        elif "Alice" in msg or "Johnson" in msg:
            return False, "message only contains part of name"
        else:
            return False, "message does not contain Alice Johnson"
    check_item("welcome_message content (name present)", 15, welcome_content)

    # ---------- Bonus: ensure no extra top-level files (penalty idea not applied, but separate check) ----------
    # (Optional, but we keep it simple)

    # Write results
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {total_score}/100")
    for d in details:
        status = "PASS" if d["passed"] else "FAIL"
        print(f"  [{status}] {d['item']}: {d['score']}/{d['max_score']} - {d['reason']}")

if __name__ == "__main__":
    main()
