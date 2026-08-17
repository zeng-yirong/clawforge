import os
import sys
import json
from pathlib import Path

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    details = []
    total = 0

    # 1. 检查 ops/ 目录是否存在
    ops_dir = workspace / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "Found ops/"})
        total += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "Missing ops/"})

    # 2. 检查 onboarding_summary.json
    summary_path = ops_dir / "onboarding_summary.json"
    if not summary_path.is_file():
        details.append({"item": "onboarding_summary.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 后续无法检查，直接返回
        write_score(total, details)
        return
    try:
        summary = load_json(summary_path)
        details.append({"item": "onboarding_summary.json valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        total += 10
    except Exception as e:
        details.append({"item": "onboarding_summary.json valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        write_score(total, details)
        return

    # 3. 检查 welcome_cache.json
    welcome_path = ops_dir / "welcome_cache.json"
    if not welcome_path.is_file():
        details.append({"item": "welcome_cache.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
    else:
        try:
            welcome = load_json(welcome_path)
            details.append({"item": "welcome_cache.json valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
            total += 10
        except Exception as e:
            details.append({"item": "welcome_cache.json valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
            welcome = None

    # 4. 检查 summary 字段
    # employee_id
    if summary.get("employee_id") == "EMP-037":
        details.append({"item": "employee_id correct", "score": 10, "max_score": 10, "passed": True, "reason": "EMP-037"})
        total += 10
    else:
        details.append({"item": "employee_id correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 'EMP-037', got {summary.get('employee_id')}"})

    # employee_name
    if summary.get("employee_name") == "Alice Johnson":
        details.append({"item": "employee_name correct", "score": 5, "max_score": 5, "passed": True, "reason": "Alice Johnson"})
        total += 5
    else:
        details.append({"item": "employee_name correct", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected 'Alice Johnson', got {summary.get('employee_name')}"})

    # email_profile (格式: firstname.lastname@company.com)
    email = summary.get("email_profile", "")
    expected_email = "alice.johnson@company.com"
    if email == expected_email:
        details.append({"item": "email_profile correct", "score": 10, "max_score": 10, "passed": True, "reason": expected_email})
        total += 10
    else:
        details.append({"item": "email_profile correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected '{expected_email}', got '{email}'"})

    # system_access – 应包含 pack_id 和 systems
    sys_access = summary.get("system_access", {})
    if isinstance(sys_access, dict) and sys_access.get("pack_id") == "PACK-002" and sorted(sys_access.get("systems", [])) == sorted(["slack", "portal", "email"]):
        details.append({"item": "system_access correct (pack_id & systems)", "score": 15, "max_score": 15, "passed": True, "reason": "PACK-002 with correct systems"})
        total += 15
    else:
        details.append({"item": "system_access correct (pack_id & systems)", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected pack_id PACK-002 and systems ['slack','portal','email'], got {sys_access}"})

    # equipment – 应包含 asset_tag LAP-042
    equip = summary.get("equipment", {})
    if isinstance(equip, dict) and equip.get("asset_tag") == "LAP-042":
        details.append({"item": "equipment asset_tag correct", "score": 15, "max_score": 15, "passed": True, "reason": "LAP-042"})
        total += 15
    else:
        details.append({"item": "equipment asset_tag correct", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected LAP-042, got {equip.get('asset_tag')}"})

    # welcome_message_posted 应存在且为 True
    wm_posted = summary.get("welcome_message_posted")
    if wm_posted is True:
        details.append({"item": "welcome_message_posted flag correct", "score": 5, "max_score": 5, "passed": True, "reason": "true"})
        total += 5
    else:
        details.append({"item": "welcome_message_posted flag correct", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected true, got {wm_posted}"})

    # 5. 检查 welcome_cache.json 内容
    if welcome is not None and isinstance(welcome, dict) and "message" in welcome:
        msg = welcome["message"]
        if "Alice Johnson" in msg:
            details.append({"item": "welcome_cache.json message contains employee name", "score": 15, "max_score": 15, "passed": True, "reason": f"Message: {msg}"})
            total += 15
        else:
            details.append({"item": "welcome_cache.json message contains employee name", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected 'Alice Johnson' in message, got '{msg}'"})
    else:
        details.append({"item": "welcome_cache.json message field exists", "score": 0, "max_score": 15, "passed": False, "reason": "Missing 'message' field or invalid structure"})

    # 确保总分在0-100
    total = min(max(total, 0), 100)
    write_score(total, details)

def write_score(total, details):
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    verify()
