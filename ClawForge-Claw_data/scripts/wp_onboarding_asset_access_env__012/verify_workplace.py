import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    score = 0
    max_score = 100
    details = []
    results_path = Path(workspace) / "ops" / "onboarding_plan.json"

    # 1. Check file existence (10 points)
    if results_path.exists():
        details.append({
            "item": "File ops/onboarding_plan.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
        score += 10
    else:
        details.append({
            "item": "File ops/onboarding_plan.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # No file, no further checks
        _write_score(score, details)
        return

    # 2. Validate JSON format (10 points)
    try:
        with open(results_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON format is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON."
        })
        score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON format is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        _write_score(score, details)
        return

    # 3. Required fields present (20 points)
    required_fields = ["employee_name", "email", "systems", "asset_tag"]
    missing = [f for f in required_fields if f not in data]
    extra = [k for k in data if k not in required_fields]
    if not missing:
        details.append({
            "item": "Required fields present (employee_name, email, systems, asset_tag)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "All required fields present."
        })
        score += 20
    else:
        details.append({
            "item": "Required fields present",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing fields: {missing}. Extra fields: {extra}" if extra else f"Missing fields: {missing}"
        })
        _write_score(score, details)
        return

    # Extra fields penalty (optional, but we'll deduct)
    if extra:
        details.append({
            "item": "No extra fields",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": f"Extra fields found: {extra}. Deducting 5 points."
        })
        score = max(0, score - 5)

    # 4. Field value correctness (60 points, 15 each)
    # 4a. employee_name
    if data["employee_name"] == "Alice Wang":
        details.append({
            "item": "employee_name is 'Alice Wang'",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Correct name."
        })
        score += 15
    else:
        details.append({
            "item": "employee_name is 'Alice Wang'",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Got '{data['employee_name']}', expected 'Alice Wang'."
        })

    # 4b. email
    if data["email"] == "alice@company.com":
        details.append({
            "item": "email is 'alice@company.com'",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Correct email."
        })
        score += 15
    else:
        details.append({
            "item": "email is 'alice@company.com'",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Got '{data['email']}', expected 'alice@company.com'."
        })

    # 4c. systems (order doesn't matter, use set comparison)
    expected_systems = ["gitlab", "jenkins", "aws"]
    actual_systems = data.get("systems", [])
    if isinstance(actual_systems, list) and set(actual_systems) == set(expected_systems):
        details.append({
            "item": "systems list matches Engineering pack (gitlab, jenkins, aws)",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Systems correct."
        })
        score += 15
    else:
        details.append({
            "item": "systems list matches Engineering pack",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Got {actual_systems}, expected {expected_systems}."
        })

    # 4d. asset_tag
    if data["asset_tag"] == "LT-001":
        details.append({
            "item": "asset_tag is 'LT-001'",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Correct asset tag."
        })
        score += 15
    else:
        details.append({
            "item": "asset_tag is 'LT-001'",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Got '{data['asset_tag']}', expected 'LT-001'."
        })

    # Finalize
    score = min(score, max_score)
    _write_score(score, details)

def _write_score(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
