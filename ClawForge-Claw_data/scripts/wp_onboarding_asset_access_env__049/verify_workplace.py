import json, sys, os
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. ops 目录存在 (10分)
    ops_dir = ws / "ops"
    item = {"item": "ops directory exists", "max_score": 10}
    if ops_dir.is_dir():
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "Found ops/ directory"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "ops/ directory not found"
    details.append(item)
    total_score += item["score"]

    # 2. 汇总文件存在且合法 JSON (10分)
    summary_path = ops_dir / "onboarding_summary.json"
    item = {"item": "ops/onboarding_summary.json exists and valid JSON", "max_score": 10}
    if summary_path.is_file():
        try:
            data = json.loads(summary_path.read_text())
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "File exists and is valid JSON"
        except (json.JSONDecodeError, Exception) as e:
            item["score"] = 0
            item["passed"] = False
            item["reason"] = f"Invalid JSON: {e}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "File not found"
    details.append(item)
    total_score += item["score"]

    if not item["passed"]:
        # 如果汇总文件无效，后续检查无法进行，直接返回
        finish(total_score, details)
        return

    # 3. email_created 字段 (20分)
    item = {"item": "email_created field is true", "max_score": 20}
    if data.get("email_created") is True:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "email_created is true"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"email_created is {data.get('email_created')}, expected True"
    details.append(item)
    total_score += item["score"]

    # 4. systems_assigned 包含 CRM 和 ERP (20分)
    item = {"item": "systems_assigned contains CRM and ERP", "max_score": 20}
    assigned = data.get("systems_assigned", [])
    if isinstance(assigned, list) and set(["CRM", "ERP"]).issubset(set(assigned)):
        item["score"] = 20
        item["passed"] = True
        item["reason"] = f"systems_assigned contains CRM and ERP: {assigned}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"systems_assigned = {assigned}, expected ['CRM','ERP'] at least"
    details.append(item)
    total_score += item["score"]

    # 5. equipment_allocated 包含 LAP-001 和 MON-001 (20分)
    item = {"item": "equipment_allocated contains LAP-001 and MON-001", "max_score": 20}
    equip = data.get("equipment_allocated", [])
    if isinstance(equip, list) and set(["LAP-001", "MON-001"]).issubset(set(equip)):
        item["score"] = 20
        item["passed"] = True
        item["reason"] = f"equipment_allocated contains LAP-001 and MON-001: {equip}"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"equipment_allocated = {equip}, expected ['LAP-001','MON-001']"
    details.append(item)
    total_score += item["score"]

    # 6. welcome_message_posted 字段 (20分)
    item = {"item": "welcome_message_posted field is true", "max_score": 20}
    if data.get("welcome_message_posted") is True:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "welcome_message_posted is true"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = f"welcome_message_posted is {data.get('welcome_message_posted')}, expected True"
    details.append(item)
    total_score += item["score"]

    finish(total_score, details)

def finish(total, details):
    score = min(100, max(0, total))  # 确保 0-100
    result = {
        "total_score": score,
        "details": details
    }
    Path("workplace_score.json").write_text(json.dumps(result, indent=2))
    print(f"Verification finished. Total score: {score}/100")

if __name__ == "__main__":
    verify()
