import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result_path = os.path.join(workspace, "ops", "onboarding_result.json")

    details = []
    total_score = 0

    # ---- 1. Directory and file existence (10 points) ----
    ops_dir = os.path.join(workspace, "ops")
    file_exists = os.path.exists(result_path) and os.path.isfile(result_path)
    if file_exists:
        details.append({"item": "ops/onboarding_result.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found at expected path"})
        total_score += 10
    else:
        details.append({"item": "ops/onboarding_result.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        total_score += 0
        # If file missing, skip all further checks and write score
        _write_score(total_score, details)
        return

    # ---- 2. JSON validity (10 points) ----
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {str(e)}"})
        _write_score(total_score, details)
        return

    # ---- 3. Data content checks (80 points distributed) ----
    # Check employee_id (10 points)
    if data.get("employee_id") == "EMP007":
        details.append({"item": "employee_id is EMP007", "score": 10, "max_score": 10, "passed": True, "reason": "Correct employee ID"})
        total_score += 10
    else:
        details.append({"item": "employee_id is EMP007", "score": 0, "max_score": 10, "passed": False, "reason": f"Got '{data.get('employee_id')}' expected 'EMP007'"})

    # Check email (10 points)
    if data.get("email") == "alice@example.com":
        details.append({"item": "email is alice@example.com", "score": 10, "max_score": 10, "passed": True, "reason": "Correct email"})
        total_score += 10
    else:
        details.append({"item": "email is alice@example.com", "score": 0, "max_score": 10, "passed": False, "reason": f"Got '{data.get('email')}' expected 'alice@example.com'"})

    # Check equipment (20 points)
    if data.get("equipment") == "LAP-001":
        details.append({"item": "equipment asset tag is LAP-001", "score": 20, "max_score": 20, "passed": True, "reason": "Correct laptop asset tag"})
        total_score += 20
    else:
        details.append({"item": "equipment asset tag is LAP-001", "score": 0, "max_score": 20, "passed": False, "reason": f"Got '{data.get('equipment')}' expected 'LAP-001'"})

    # Check permissions list (20 points)
    expected_permissions = ["DevOps", "CodeRepo"]
    actual_permissions = data.get("permissions", [])
    if actual_permissions == expected_permissions:
        details.append({"item": "permissions match engineering pack", "score": 20, "max_score": 20, "passed": True, "reason": "Correct permission list"})
        total_score += 20
    else:
        details.append({"item": "permissions match engineering pack", "score": 0, "max_score": 20, "passed": False, "reason": f"Got {actual_permissions} expected {expected_permissions}"})

    # Check welcome_message (20 points)
    msg = data.get("welcome_message", "")
    if msg == "Welcome to the team, Alice Johnson!":
        details.append({"item": "welcome_message greeting", "score": 20, "max_score": 20, "passed": True, "reason": "Correct welcome message"})
        total_score += 20
    else:
        details.append({"item": "welcome_message greeting", "score": 0, "max_score": 20, "passed": False, "reason": f"Got '{msg}' expected 'Welcome to the team, Alice Johnson!'"})

    _write_score(total_score, details)


def _write_score(score, details):
    output = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
