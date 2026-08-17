import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/offboarding", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- exit_requests.json ---
    exit_requests = {
        "EMP001": {"employee_name": "Alice Wang", "approval_status": "rejected"},
        "EMP002": {"employee_name": "Bob Li", "approval_status": "pending"},
        "EMP003": {"employee_name": "Carol Zhang", "approval_status": "approved"},
        "EMP042": {"employee_name": "Jane Doe", "approval_status": "approved"}
    }
    with open("data/offboarding/exit_requests.json", "w") as f:
        json.dump({"exit_requests": exit_requests}, f, indent=2)

    # --- system_access.json ---
    system_access = {
        "EMP001": [
            {"system_name": "Admin Portal", "status": "active"},
            {"system_name": "CRM", "status": "active"}
        ],
        "EMP002": [
            {"system_name": "Admin Portal", "status": "active"},
            {"system_name": "CRM", "status": "active"}
        ],
        "EMP003": [
            {"system_name": "Admin Portal", "status": "revoked"},
            {"system_name": "CRM", "status": "revoked"}
        ],
        "EMP042": [
            {"system_name": "Admin Portal", "status": "active"},
            {"system_name": "CRM", "status": "active"}
        ]
    }
    with open("data/offboarding/system_access.json", "w") as f:
        json.dump({"system_access": system_access}, f, indent=2)

    # --- equipment_assignments.json ---
    equipment_assignments = {
        "EMP001": {"asset_tag": "BG-8821", "status": "assigned"},
        "EMP002": {"asset_tag": "LT-2041", "status": "assigned"},
        "EMP003": {"asset_tag": "BG-8821", "status": "reclaimed"},
        "EMP042": {"asset_tag": "LT-2041", "status": "assigned"}
    }
    with open("data/offboarding/equipment_assignments.json", "w") as f:
        json.dump({"equipment_assignments": equipment_assignments}, f, indent=2)

    # 额外干扰文件（可选，但这里不创建更多，因为足够）
    # 可以增加一些无用日志等，但为了聚焦，略过。

if __name__ == "__main__":
    build_env()
