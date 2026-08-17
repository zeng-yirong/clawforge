import json
import os
import sys

def verify(workspace: str):
    details = []
    total_score = 0

    # 1. Check ops/onboarding_plan.json exists (10 points)
    plan_path = os.path.join(workspace, "ops", "onboarding_plan.json")
    if os.path.isfile(plan_path):
        details.append({"item": "File existence", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10
    else:
        details.append({"item": "File existence", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # No point continuing if file missing
        return finalize(total_score, details)

    # 2. JSON parse (10 points)
    try:
        with open(plan_path, "r") as f:
            plan = json.load(f)
        details.append({"item": "JSON validity", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON validity", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        return finalize(total_score, details)

    # 3. employee_id (15 points)
    if plan.get("employee_id") == "EMP-045":
        details.append({"item": "employee_id", "score": 15, "max_score": 15, "passed": True, "reason": "Correct"})
        total_score += 15
    else:
        details.append({"item": "employee_id", "score": 0, "max_score": 15, "passed": False, "reason": f"Got {plan.get('employee_id')}, expected EMP-045"})

    # 4. employee_name (10 points)
    if plan.get("employee_name") == "John Doe":
        details.append({"item": "employee_name", "score": 10, "max_score": 10, "passed": True, "reason": "Correct"})
        total_score += 10
    else:
        details.append({"item": "employee_name", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {plan.get('employee_name')}, expected John Doe"})

    # 5. email_profile (15 points)
    expected_email = "john.doe@company.com"
    if plan.get("email_profile") == expected_email:
        details.append({"item": "email_profile", "score": 15, "max_score": 15, "passed": True, "reason": "Correct"})
        total_score += 15
    else:
        details.append({"item": "email_profile", "score": 0, "max_score": 15, "passed": False, "reason": f"Got {plan.get('email_profile')}, expected {expected_email}"})

    # 6. system_access (20 points) – must be exactly the Engineering pack systems
    expected_systems = ["GitLab", "Jira", "Docker"]
    got_systems = plan.get("system_access", [])
    if got_systems == expected_systems:
        details.append({"item": "system_access", "score": 20, "max_score": 20, "passed": True, "reason": "Correct systems"})
        total_score += 20
    else:
        details.append({"item": "system_access", "score": 0, "max_score": 20, "passed": False, "reason": f"Got {got_systems}, expected {expected_systems}"})

    # 7. equipment (20 points)
    expected_equip = "LT-045"
    if plan.get("equipment") == expected_equip:
        details.append({"item": "equipment", "score": 20, "max_score": 20, "passed": True, "reason": "Correct asset tag"})
        total_score += 20
    else:
        details.append({"item": "equipment", "score": 0, "max_score": 20, "passed": False, "reason": f"Got {plan.get('equipment')}, expected {expected_equip}"})

    # 8. welcome_message (10 points) – must contain name and department
    welcome = plan.get("welcome_message", "")
    if "John Doe" in welcome and "Engineering" in welcome:
        details.append({"item": "welcome_message (contains name & department)", "score": 10, "max_score": 10, "passed": True, "reason": "Content valid"})
        total_score += 10
    else:
        details.append({"item": "welcome_message (contains name & department)", "score": 0, "max_score": 10, "passed": False, "reason": f"Got '{welcome}', missing required substrings"})

    # Bonus: if welcome_message exactly matches the correct template (not required, but extra check for consistency)
    # We don't add bonus points; just document.
    return finalize(total_score, details)


def finalize(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    return score


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = verify(workspace)
    print(f"Score: {score}/100")
    sys.exit(0 if score == 100 else 1)
