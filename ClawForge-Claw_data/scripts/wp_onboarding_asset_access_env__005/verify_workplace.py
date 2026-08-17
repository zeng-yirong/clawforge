import sys
import os
import json
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace)
    score = 0
    details = []

    # 1) Check that result file exists
    result_path = ws / "onboarding_result.json"
    if result_path.exists():
        details.append({
            "item": "onboarding_result.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
        score += 10
    else:
        details.append({
            "item": "onboarding_result.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
        # If file doesn't exist, we can't check further — stop here or give 0 for rest
        _write_score(workspace, score, details)
        return

    # 2) Validate JSON format
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully."
        })
        score += 10
    except Exception as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        _write_score(workspace, score, details)
        return

    # 3) Check structure: must be a list under 'employees' key
    if not isinstance(data, dict) or "employees" not in data:
        details.append({
            "item": "Top-level key 'employees' present",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Expected dict with 'employees' list, got {type(data).__name__}"
        })
        _write_score(workspace, score, details)
        return
    details.append({
        "item": "Top-level key 'employees' present",
        "score": 5,
        "max_score": 5,
        "passed": True,
        "reason": "Key exists."
    })
    score += 5

    employees = data["employees"]
    if not isinstance(employees, list) or len(employees) != 2:
        details.append({
            "item": "Number of employees (exactly 2 signed contracts)",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Expected 2 employees, found {len(employees)}"
        })
        _write_score(workspace, score, details)
        return
    details.append({
        "item": "Number of employees (exactly 2 signed contracts)",
        "score": 5,
        "max_score": 5,
        "passed": True,
        "reason": "2 employees present."
    })
    score += 5

    # 4) Check each employee's fields and values
    # Expected results based on env_builder:
    # emp001 (Sarah Connor) -> email: sarah.connor@company.com, systems: engineering pack, equipment: first available laptop (LAPTOP-001)
    # emp002 (Mike Davis)   -> email: mike.davis@company.com, systems: sales pack, equipment: first available monitor (MONITOR-001)
    # Welcome files: ops/slack_cache/welcome_emp001.txt and welcome_emp002.txt must exist.

    expected = [
        {
            "employee_id": "emp001",
            "employee_name": "Sarah Connor",
            "email": "sarah.connor@company.com",
            "assigned_systems": ["jenkins", "code_repo", "monitoring", "jira"],
            "assigned_equipment": "LAPTOP-001"
        },
        {
            "employee_id": "emp002",
            "employee_name": "Mike Davis",
            "email": "mike.davis@company.com",
            "assigned_systems": ["crm", "email_marketing", "reporting"],
            "assigned_equipment": "MONITOR-001"
        }
    ]

    # Build a dict by employee_id for easy lookup
    result_by_id = {}
    for emp in employees:
        eid = emp.get("employee_id")
        result_by_id[eid] = emp

    all_passed = True
    for exp in expected:
        eid = exp["employee_id"]
        if eid not in result_by_id:
            details.append({
                "item": f"Employee {eid} present",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "Missing in result."
            })
            all_passed = False
            continue

        emp = result_by_id[eid]
        correct = True
        reasons = []

        # Check email
        if emp.get("email") != exp["email"]:
            correct = False
            reasons.append(f"email mismatch: {emp.get('email')} vs {exp['email']}")

        # Check systems (order-insensitive set)
        systems = emp.get("assigned_systems", [])
        if set(systems) != set(exp["assigned_systems"]):
            correct = False
            reasons.append(f"systems mismatch: {sorted(systems)} vs {sorted(exp['assigned_systems'])}")

        # Check equipment
        if emp.get("assigned_equipment") != exp["assigned_equipment"]:
            correct = False
            reasons.append(f"equipment mismatch: {emp.get('assigned_equipment')} vs {exp['assigned_equipment']}")

        # Check welcome_sent bool field (if present) – optional but we expect it to be true
        # Actually prompt says "whether the welcome tick was written" – we'll check the actual file existence later as separate item.
        # We require a boolean field welcome_sent.
        welcome_sent = emp.get("welcome_sent")
        if welcome_sent is not True:
            # This is a non-critical extra; we just note it in reason, but don't fail the whole employee
            if welcome_sent is None:
                pass  # we don't hard require this field for now; we check file separately
            else:
                pass  # it's fine if it's true

        # Check welcome file existence
        welcome_path = ws / f"ops/slack_cache/welcome_{eid}.txt"
        if not welcome_path.exists():
            correct = False
            reasons.append(f"welcome file welcome_{eid}.txt not found")

        if correct:
            details.append({
                "item": f"Employee {eid} ({exp['employee_name']}) details correct",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "All fields match expected."
            })
            score += 15
        else:
            details.append({
                "item": f"Employee {eid} ({exp['employee_name']}) details correct",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": "; ".join(reasons)
            })
            all_passed = False

    # Extra points: welcome_sent field presence and correctness for both
    for eid in ["emp001", "emp002"]:
        emp = result_by_id.get(eid)
        if emp and emp.get("welcome_sent") is True:
            details.append({
                "item": f"{eid} welcome_sent field is true",
                "score": 2.5,
                "max_score": 2.5,
                "passed": True,
                "reason": "Field present and true."
            })
            score += 2.5
        else:
            details.append({
                "item": f"{eid} welcome_sent field is true",
                "score": 0,
                "max_score": 2.5,
                "passed": False,
                "reason": "Missing or false."
            })

    total_max = 10 + 10 + 5 + 5 + 2*15 + 2*2.5   # = 10+10+5+5+30+5 = 65? wait recalc:
    # Actually: 10 (exist) + 10 (json) + 5 (employees key) + 5 (2 employees) + 15+15 (two employees) + 2.5+2.5 = 65
    # We need to reach 100. Let's adjust weights: add more items.
    # We'll add item for "no extra employees" (5), "welcome file content" (10 each) etc.

    # Check that only the two expected employees are present
    extra_ids = set(result_by_id.keys()) - {"emp001", "emp002"}
    if extra_ids:
        details.append({
            "item": "No extra employees",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Unexpected employee ids: {extra_ids}"
        })
    else:
        details.append({
            "item": "No extra employees",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Only emp001 and emp002 present."
        })
        score += 5

    # Check welcome file contents contain expected text
    for eid, name in [("emp001", "Sarah Connor"), ("emp002", "Mike Davis")]:
        welcome_path = ws / f"ops/slack_cache/welcome_{eid}.txt"
        if welcome_path.exists():
            content = welcome_path.read_text().strip()
            expected_text = f"Welcome to the team, {name}!"
            if content == expected_text:
                details.append({
                    "item": f"welcome_{eid}.txt content correct",
                    "score": 5,
                    "max_score": 5,
                    "passed": True,
                    "reason": "Content matches."
                })
                score += 5
            else:
                details.append({
                    "item": f"welcome_{eid}.txt content correct",
                    "score": 0,
                    "max_score": 5,
                    "passed": False,
                    "reason": f"Expected '{expected_text}', got '{content}'"
                })
        else:
            details.append({
                "item": f"welcome_{eid}.txt exists",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "File missing."
            })

    # Add overall format & completeness
    # Check that each employee record has all required fields
    required_fields = ["employee_id", "employee_name", "email", "assigned_systems", "assigned_equipment", "welcome_sent"]
    for emp in employees:
        missing = [f for f in required_fields if f not in emp]
        if missing:
            details.append({
                "item": f"Employee {emp.get('employee_id')} has all required fields",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Missing fields: {missing}"
            })
        else:
            details.append({
                "item": f"Employee {emp.get('employee_id')} has all required fields",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "All fields present."
            })
            score += 5

    # Ensure we didn't exceed 100; cap score at 100
    total_score = min(score, 100)
    # Round to integer
    total_score = int(total_score)

    _write_score(workspace, total_score, details)

def _write_score(workspace, score, details):
    # ensure not exceeding 100
    score = min(score, 100)
    result = {
        "total_score": score,
        "details": details
    }
    report_path = pathlib.Path(workspace) / "workplace_score.json"
    with open(report_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
