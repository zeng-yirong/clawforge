import sys
import os
import json
import math

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify(workspace):
    details = []
    total_score = 0

    # 1) check ops/onboarding_complete.json exists
    target = os.path.join(workspace, "ops", "onboarding_complete.json")
    if not os.path.isfile(target):
        details.append({
            "item": "Final file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/onboarding_complete.json not found"
        })
        # cannot proceed – return zero
        total = 0
        write_result(workspace, total, details)
        return total

    details.append({
        "item": "Final file exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "ops/onboarding_complete.json found"
    })
    total_score += 10

    # 2) parse JSON
    try:
        data = load_json(target)
    except Exception as e:
        details.append({
            "item": "JSON valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        total = sum(d['score'] for d in details)
        write_result(workspace, total, details)
        return total

    details.append({
        "item": "JSON valid",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON"
    })
    total_score += 10

    # 3) required top-level keys present
    required_keys = ["employee_id", "employee_name", "email", "department",
                     "email_profile", "systems_access", "equipment", "welcome_message"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        details.append({
            "item": "Required top-level keys",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing keys: {', '.join(missing)}"
        })
    else:
        details.append({
            "item": "Required top-level keys",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All 8 required keys present"
        })
        total_score += 10

    # --- now check exact expected values (if any missing key, skip these checks?) ---
    # We'll still try to check; missing keys will cause KeyError -> handle gracefully
    try:
        # 4) employee_id
        if data.get("employee_id") == "E001":
            details.append({
                "item": "employee_id",
                "score": 7,
                "max_score": 7,
                "passed": True,
                "reason": "Correct employee_id"
            })
            total_score += 7
        else:
            details.append({
                "item": "employee_id",
                "score": 0,
                "max_score": 7,
                "passed": False,
                "reason": f"Expected 'E001', got {data.get('employee_id')}"
            })

        # 5) employee_name
        if data.get("employee_name") == "Alice Chen":
            details.append({
                "item": "employee_name",
                "score": 7,
                "max_score": 7,
                "passed": True,
                "reason": "Correct employee_name"
            })
            total_score += 7
        else:
            details.append({
                "item": "employee_name",
                "score": 0,
                "max_score": 7,
                "passed": False,
                "reason": f"Expected 'Alice Chen', got {data.get('employee_name')}"
            })

        # 6) email
        if data.get("email") == "alice@company.com":
            details.append({
                "item": "email",
                "score": 6,
                "max_score": 6,
                "passed": True,
                "reason": "Correct email"
            })
            total_score += 6
        else:
            details.append({
                "item": "email",
                "score": 0,
                "max_score": 6,
                "passed": False,
                "reason": f"Expected 'alice@company.com', got {data.get('email')}"
            })

        # 7) department
        if data.get("department") == "Engineering":
            details.append({
                "item": "department",
                "score": 6,
                "max_score": 6,
                "passed": True,
                "reason": "Correct department"
            })
            total_score += 6
        else:
            details.append({
                "item": "department",
                "score": 0,
                "max_score": 6,
                "passed": False,
                "reason": f"Expected 'Engineering', got {data.get('department')}"
            })

        # 8) email_profile
        ep = data.get("email_profile", {})
        if isinstance(ep, dict) and ep.get("email") == "alice@company.com" and ep.get("display_name") == "Alice Chen":
            details.append({
                "item": "email_profile",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Correct email_profile object"
            })
            total_score += 10
        else:
            details.append({
                "item": "email_profile",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Expected {{'email':'alice@company.com','display_name':'Alice Chen'}}, got {ep}"
            })

        # 9) systems_access
        sa = data.get("systems_access", [])
        # sort before compare
        expected_sa = ["git", "jira", "wiki"]
        if isinstance(sa, list) and sorted(sa) == sorted(expected_sa):
            details.append({
                "item": "systems_access",
                "score": 12,
                "max_score": 12,
                "passed": True,
                "reason": "Correct systems list (order ignored)"
            })
            total_score += 12
        else:
            details.append({
                "item": "systems_access",
                "score": 0,
                "max_score": 12,
                "passed": False,
                "reason": f"Expected systems {expected_sa}, got {sa}"
            })

        # 10) equipment
        eq = data.get("equipment", {})
        if isinstance(eq, dict) and eq.get("asset_tag") == "LAP001" and eq.get("asset_type") == "laptop":
            details.append({
                "item": "equipment",
                "score": 12,
                "max_score": 12,
                "passed": True,
                "reason": "Correct equipment object"
            })
            total_score += 12
        else:
            details.append({
                "item": "equipment",
                "score": 0,
                "max_score": 12,
                "passed": False,
                "reason": f"Expected {{'asset_tag':'LAP001','asset_type':'laptop'}}, got {eq}"
            })

        # 11) welcome_message
        wm = data.get("welcome_message", "")
        if wm == "Welcome aboard, Alice Chen!":
            details.append({
                "item": "welcome_message",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Correct welcome message"
            })
            total_score += 10
        else:
            details.append({
                "item": "welcome_message",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Expected 'Welcome aboard, Alice Chen!', got {repr(wm)}"
            })

    except Exception as e:
        # If any unexpected error, cap the score
        details.append({
            "item": "Unexpected error during detailed checks",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": str(e)
        })

    # Ensure total does not exceed 100
    final_score = min(total_score, 100)
    write_result(workspace, final_score, details)
    return final_score

def write_result(workspace, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    path = os.path.join(workspace, "workplace_score.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
