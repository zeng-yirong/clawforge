import sys
import os
import json
import pathlib

def verify(workspace: str):
    details = []
    total_score = 0

    # 1. Directory structure (10 pts)
    expected_dirs = ["data/onboarding", "outputs"]
    all_dirs_exist = True
    for d in expected_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            all_dirs_exist = False
            details.append({"item": f"Directory {d} exists", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing directory: {d}"})
            break
    if all_dirs_exist:
        details.append({"item": "Directory structure", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories present"})
        total_score += 10
    else:
        # Already added detail
        pass

    # 2. Check onboarding bundle exists (10 pts)
    bundle_path = os.path.join(workspace, "outputs", "onboarding_bundle.json")
    if not os.path.isfile(bundle_path):
        details.append({"item": "outputs/onboarding_bundle.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # cannot proceed further, write partial score
        final_score = total_score
        result = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        sys.exit(0)
    else:
        details.append({"item": "outputs/onboarding_bundle.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists"})
        total_score += 10

    # 3. Parse JSON and validate structure (10 pts)
    try:
        with open(bundle_path, "r") as f:
            bundle = json.load(f)
    except json.JSONDecodeError as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        # write partial
        final_score = total_score
        result = {"total_score": final_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        sys.exit(0)

    required_keys = ["employee_id", "email_profile", "system_access", "equipment", "welcome_message"]
    missing_keys = [k for k in required_keys if k not in bundle]
    if missing_keys:
        details.append({"item": "Required keys in bundle", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing keys: {missing_keys}"})
    else:
        details.append({"item": "Required keys in bundle", "score": 10, "max_score": 10, "passed": True, "reason": "All required keys present"})
        total_score += 10

    # 4. Check employee_id is correct (10 pts) - must be "E005"
    emp_id = bundle.get("employee_id")
    if emp_id == "E005":
        details.append({"item": "employee_id is E005", "score": 10, "max_score": 10, "passed": True, "reason": "Correct employee_id"})
        total_score += 10
    else:
        details.append({"item": "employee_id is E005", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected E005, got {emp_id}"})

    # 5. email_profile validation (15 pts)
    expected_email_profile = {"email": "alice.chen@company.com", "display_name": "Alice Chen", "department": "Engineering"}
    profile = bundle.get("email_profile", {})
    profile_ok = True
    for key, val in expected_email_profile.items():
        if profile.get(key) != val:
            profile_ok = False
            break
    if profile_ok:
        details.append({"item": "email_profile correct", "score": 15, "max_score": 15, "passed": True, "reason": "All fields match"})
        total_score += 15
    else:
        details.append({"item": "email_profile correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_email_profile}, got {profile}"})

    # 6. system_access validation (20 pts) - must have 3 systems from eng_standard pack
    expected_systems = [
        {"system": "Jira", "permission": "write"},
        {"system": "GitLab", "permission": "read"},
        {"system": "Slack", "permission": "read"}
    ]
    actual_systems = bundle.get("system_access", [])
    # check length and content (order doesn't matter)
    if len(actual_systems) != len(expected_systems):
        details.append({"item": "system_access correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {len(expected_systems)} entries, got {len(actual_systems)}"})
    else:
        # convert to set of tuples for comparison
        expected_set = set((s["system"], s["permission"]) for s in expected_systems)
        actual_set = set((s["system"], s["permission"]) for s in actual_systems)
        if expected_set == actual_set:
            details.append({"item": "system_access correct", "score": 20, "max_score": 20, "passed": True, "reason": "All systems match"})
            total_score += 20
        else:
            details.append({"item": "system_access correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Mismatch: expected {expected_set}, got {actual_set}"})

    # 7. equipment validation (15 pts)
    expected_equipment = {"asset_tag": "TAG-005", "asset_type": "Laptop"}
    equipment = bundle.get("equipment")
    if equipment is None:
        details.append({"item": "equipment correct", "score": 0, "max_score": 15, "passed": False, "reason": "equipment is null"})
    else:
        if equipment.get("asset_tag") == "TAG-005" and equipment.get("asset_type") == "Laptop":
            # also check that the inventory was updated (we don't require it in bundle, but we can check if the original file is modified? Not mandatory for agent)
            details.append({"item": "equipment correct", "score": 15, "max_score": 15, "passed": True, "reason": "Correct laptop assigned"})
            total_score += 15
        else:
            details.append({"item": "equipment correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected TAG-005 Laptop, got {equipment}"})

    # 8. welcome_message validation (10 pts)
    expected_welcome = {"channel": "#general", "text": "欢迎 Alice Chen 加入 Engineering！"}
    welcome = bundle.get("welcome_message", {})
    if welcome.get("channel") == "#general" and welcome.get("text") == "欢迎 Alice Chen 加入 Engineering！":
        details.append({"item": "welcome_message correct", "score": 10, "max_score": 10, "passed": True, "reason": "Welcome message matches"})
        total_score += 10
    else:
        details.append({"item": "welcome_message correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_welcome}, got {welcome}"})

    # compute final score
    final_score = min(total_score, 100)
    result = {
        "total_score": final_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
