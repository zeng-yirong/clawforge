import os
import json

def build_env():
    # Ensure offboarding directory exists
    os.makedirs("offboarding", exist_ok=True)
    
    # Exit requests – only EMP-042 is approved; others are distractors
    exit_requests = {
        "exit_requests": [
            {"employee_id": "EMP-042", "employee_name": "Li Xue", "approval_status": "Approved"},
            {"employee_id": "EMP-099", "employee_name": "Zhang San", "approval_status": "Pending"},
            {"employee_id": "EMP-101", "employee_name": "Wang Wu", "approval_status": "Rejected"}
        ]
    }
    with open("offboarding/exit_requests.json", "w") as f:
        json.dump(exit_requests, f, indent=2)

    # System access – Li Xue has two active entries; other employee as distractor
    system_access = {
        "system_access": [
            {"employee_id": "EMP-042", "system_name": "Admin Portal", "status": "active"},
            {"employee_id": "EMP-042", "system_name": "CRM", "status": "active"},
            {"employee_id": "EMP-099", "system_name": "Admin Portal", "status": "active"}
        ]
    }
    with open("offboarding/system_access.json", "w") as f:
        json.dump(system_access, f, indent=2)

    # Equipment assignments – Li Xue: one duplicate (returned) and two active; another employee has a separate assignment
    equipment_assignments = {
        "equipment_assignments": [
            {"employee_id": "EMP-042", "asset_tag": "BG-8821", "status": "assigned"},
            {"employee_id": "EMP-042", "asset_tag": "BG-8821", "status": "returned"},
            {"employee_id": "EMP-042", "asset_tag": "LT-2041", "status": "assigned"},
            {"employee_id": "EMP-099", "asset_tag": "LT-2041", "status": "assigned"}
        ]
    }
    with open("offboarding/equipment_assignments.json", "w") as f:
        json.dump(equipment_assignments, f, indent=2)

    # Create ops directory for the agent to write into (empty)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
