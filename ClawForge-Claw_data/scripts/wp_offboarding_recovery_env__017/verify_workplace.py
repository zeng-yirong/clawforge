import sys
import os
import json

def verify(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # 1. Check handover_checklist.json exists
    checklist_path = os.path.join(workspace, "handover_checklist.json")
    if not os.path.isfile(checklist_path):
        details.append({
            "item": "handover_checklist.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # early exit – cannot continue without file
        total_score = 0
        write_score(workspace, total_score, details)
        return

    details.append({
        "item": "handover_checklist.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "File exists"
    })
    total_score += 10

    # 2. Parse JSON
    try:
        with open(checklist_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        # still continue to allow partial grading? better to stop
        total_score = 0
        write_score(workspace, total_score, details)
        return

    details.append({
        "item": "Valid JSON",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON parsed successfully"
    })
    total_score += 10

    # 3. employee_id is "EMP003"
    if data.get("employee_id") == "EMP003":
        details.append({
            "item": "employee_id == EMP003",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct employee"
        })
        total_score += 20
    else:
        details.append({
            "item": "employee_id == EMP003",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {data.get('employee_id')}"
        })

    # 4. systems_to_revoke contains both "Admin Portal" and "CRM"
    systems = data.get("systems_to_revoke", [])
    if isinstance(systems, list) and "Admin Portal" in systems and "CRM" in systems and len(systems) == 2:
        details.append({
            "item": "systems_to_revoke contains Admin Portal and CRM (exactly two, no extra)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct systems"
        })
        total_score += 20
    else:
        details.append({
            "item": "systems_to_revoke contains Admin Portal and CRM",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {systems}"
        })

    # 5. equipment_to_reclaim contains "LT-2041" and "BG-8821" (exactly two)
    equipment = data.get("equipment_to_reclaim", [])
    expected = ["LT-2041", "BG-8821"]
    if isinstance(equipment, list) and sorted(equipment) == sorted(expected):
        details.append({
            "item": "equipment_to_reclaim contains LT-2041 and BG-8821 (exactly two, no extra)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct equipment"
        })
        total_score += 20
    else:
        details.append({
            "item": "equipment_to_reclaim contains LT-2041 and BG-8821",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Got {equipment}"
        })

    # 6. No other unexpected top-level keys (cleanliness)
    allowed_keys = {"employee_id", "systems_to_revoke", "equipment_to_reclaim"}
    extra_keys = set(data.keys()) - allowed_keys
    if extra_keys:
        details.append({
            "item": "No extra top-level keys",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Unexpected keys: {extra_keys}"
        })
    else:
        details.append({
            "item": "No extra top-level keys",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Only expected keys present"
        })
        total_score += 10

    # Clamp total to 100
    total_score = min(total_score, 100)
    write_score(workspace, total_score, details)

def write_score(workspace, total, details):
    output = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
