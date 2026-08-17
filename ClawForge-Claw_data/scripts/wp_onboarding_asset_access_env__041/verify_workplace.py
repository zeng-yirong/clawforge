#!/usr/bin/env python3
import json
import os
import sys
import pathlib

def verify(workspace: str):
    workspace_path = pathlib.Path(workspace)
    summary_path = workspace_path / "onboarding_summary.json"
    details = []
    total_score = 0
    max_total = 100

    # 1. File presence (10 pts)
    if summary_path.exists():
        details.append({
            "item": "onboarding_summary.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
        total_score += 10
    else:
        details.append({
            "item": "onboarding_summary.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # Write score and exit early
        _write_score(total_score, details)
        return

    # 2. Valid JSON (10 pts)
    try:
        with open(summary_path) as f:
            data = json.load(f)
        details.append({
            "item": "Valid JSON format",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully."
        })
        total_score += 10
    except (json.JSONDecodeError, ValueError) as e:
        details.append({
            "item": "Valid JSON format",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        _write_score(total_score, details)
        return

    # 3. Required fields present (20 pts) – each of 6 fields contributes 3.33 ≈ 20 total
    required_fields = ["employee_id", "employee_name", "email", "systems_assigned", "equipment_allocated", "welcome_posted"]
    missing = [f for f in required_fields if f not in data]
    extra = [k for k in data if k not in required_fields]
    if missing:
        details.append({
            "item": "All required fields present",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing fields: {missing}"
        })
        # Still check extra fields penalty later
    else:
        details.append({
            "item": "All required fields present",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "All required fields found."
        })
        total_score += 20

    # 4. Extra fields penalty (up to -10, but we treat as 10 pts for "no unexpected fields")
    # Award 10 pts if no extra fields, else 0.
    extra_fields_ok = True
    if extra:
        extra_fields_ok = False
        reason = f"Unexpected fields: {extra}"
    else:
        reason = "No unexpected fields."
    if extra_fields_ok:
        details.append({
            "item": "No unexpected fields",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": reason
        })
        total_score += 10
    else:
        details.append({
            "item": "No unexpected fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": reason
        })

    # 5. Correct values (50 pts) – 5 sub-items, each 10 pts
    # 5.1 employee_id = "E-001"
    sub_score = 0
    expected_id = "E-001"
    passed = data.get("employee_id") == expected_id
    details.append({
        "item": "employee_id is 'E-001'",
        "score": 10 if passed else 0,
        "max_score": 10,
        "passed": passed,
        "reason": f"Got '{data.get('employee_id')}', expected '{expected_id}'"
    })
    if passed:
        sub_score += 10

    # 5.2 employee_name = "John Doe"
    expected_name = "John Doe"
    passed = data.get("employee_name") == expected_name
    details.append({
        "item": "employee_name is 'John Doe'",
        "score": 10 if passed else 0,
        "max_score": 10,
        "passed": passed,
        "reason": f"Got '{data.get('employee_name')}', expected '{expected_name}'"
    })
    if passed:
        sub_score += 10

    # 5.3 email = "john.doe@company.com"
    expected_email = "john.doe@company.com"
    passed = data.get("email") == expected_email
    details.append({
        "item": "email is 'john.doe@company.com'",
        "score": 10 if passed else 0,
        "max_score": 10,
        "passed": passed,
        "reason": f"Got '{data.get('email')}', expected '{expected_email}'"
    })
    if passed:
        sub_score += 10

    # 5.4 systems_assigned = ["CRM", "ERP", "Git"] (order matters? We'll accept any order but require exact set)
    expected_systems = {"CRM", "ERP", "Git"}
    actual_systems = set(data.get("systems_assigned", []))
    passed = actual_systems == expected_systems
    if not passed:
        # Check if it's a list at least
        if isinstance(data.get("systems_assigned"), list):
            reason = f"Got {actual_systems}, expected {expected_systems}"
        else:
            reason = f"systems_assigned is not a list"
        score_val = 0
    else:
        reason = "Systems match exactly"
        score_val = 10
    details.append({
        "item": "systems_assigned contains ['CRM','ERP','Git']",
        "score": score_val,
        "max_score": 10,
        "passed": passed,
        "reason": reason
    })
    if passed:
        sub_score += 10

    # 5.5 equipment_allocated = ["LAP-101", "MON-202"] (set check)
    expected_equip = {"LAP-101", "MON-202"}
    actual_equip = set(data.get("equipment_allocated", []))
    passed = actual_equip == expected_equip
    if not passed:
        if isinstance(data.get("equipment_allocated"), list):
            reason = f"Got {actual_equip}, expected {expected_equip}"
        else:
            reason = "equipment_allocated is not a list"
        score_val = 0
    else:
        reason = "Equipment match exactly"
        score_val = 10
    details.append({
        "item": "equipment_allocated contains ['LAP-101','MON-202']",
        "score": score_val,
        "max_score": 10,
        "passed": passed,
        "reason": reason
    })
    if passed:
        sub_score += 10

    # 5.6 welcome_posted = true (boolean)
    expected_welcome = True
    passed = data.get("welcome_posted") is True
    details.append({
        "item": "welcome_posted is true",
        "score": 10 if passed else 0,
        "max_score": 10,
        "passed": passed,
        "reason": f"Got {data.get('welcome_posted')}, expected true"
    })
    if passed:
        sub_score += 10

    total_score += sub_score

    _write_score(total_score, details)

def _write_score(total_score, details):
    output = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
