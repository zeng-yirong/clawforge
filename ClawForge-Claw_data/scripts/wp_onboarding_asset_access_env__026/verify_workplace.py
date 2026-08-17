# verify_workplace.py — 纯代码验证 agent 产物
import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录结构 (10 分)
    ops_dir = os.path.join(workspace, "ops")
    data_dir = os.path.join(workspace, "data")
    contracts_path = os.path.join(workspace, "data", "onboarding", "contracts.json")
    packs_path = os.path.join(workspace, "data", "onboarding", "permission_packs.json")
    equip_path = os.path.join(workspace, "data", "onboarding", "equipment_inventory.json")

    dir_ok = os.path.isdir(ops_dir) and os.path.isdir(data_dir)
    if dir_ok:
        details.append({"item": "目录结构 ops/ 和 data/ 存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 和 data/ 目录均存在"})
        total_score += 10
    else:
        details.append({"item": "目录结构 ops/ 和 data/ 存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 ops/ 或 data/ 目录"})

    # 2. 检查目标文件 ops/onboarding_summary.json 存在 (10 分)
    summary_path = os.path.join(workspace, "ops", "onboarding_summary.json")
    if os.path.isfile(summary_path):
        details.append({"item": "产物文件 ops/onboarding_summary.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "产物文件 ops/onboarding_summary.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续检查无法进行，输出结果并退出
        _write_score(total_score, details)
        return

    # 3. 解析 JSON 合法性 (10 分)
    try:
        with open(summary_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        _write_score(total_score, details)
        return

    # 4. 检查 employee_id (10 分)
    expected_employee_id = "E001"
    actual_employee_id = data.get("employee_id")
    if actual_employee_id == expected_employee_id:
        details.append({"item": "employee_id 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"值为 {actual_employee_id}"})
        total_score += 10
    else:
        details.append({"item": "employee_id 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_employee_id}，实际 {actual_employee_id}"})

    # 5. 检查 employee_name (10 分)
    expected_name = "Xiao Ming"
    actual_name = data.get("employee_name")
    if actual_name == expected_name:
        details.append({"item": "employee_name 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"值为 {actual_name}"})
        total_score += 10
    else:
        details.append({"item": "employee_name 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_name}，实际 {actual_name}"})

    # 6. 检查 email_profile_created (10 分)
    expected_email = "xiao.ming@acme.com"
    actual_email = data.get("email_profile_created")
    if actual_email == expected_email:
        details.append({"item": "email_profile_created 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"值为 {actual_email}"})
        total_score += 10
    else:
        details.append({"item": "email_profile_created 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_email}，实际 {actual_email}"})

    # 7. 检查 system_access_granted (10 分)
    expected_systems = ["jenkins", "github", "jira"]
    actual_systems = data.get("system_access_granted")
    if isinstance(actual_systems, list) and sorted(actual_systems) == sorted(expected_systems):
        details.append({"item": "system_access_granted 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"值为 {actual_systems}"})
        total_score += 10
    else:
        details.append({"item": "system_access_granted 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_systems}，实际 {actual_systems}"})

    # 8. 检查 equipment_allocated (10 分)
    expected_equip = "LAP-001"
    actual_equip = data.get("equipment_allocated")
    if actual_equip == expected_equip:
        details.append({"item": "equipment_allocated 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"值为 {actual_equip}"})
        total_score += 10
    else:
        details.append({"item": "equipment_allocated 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_equip}，实际 {actual_equip}"})

    # 9. 检查 welcome_message (10 分)
    expected_msg = "Welcome Xiao Ming! You have been granted access to jenkins, github, jira."
    actual_msg = data.get("welcome_message")
    if actual_msg == expected_msg:
        details.append({"item": "welcome_message 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"值为 {actual_msg}"})
        total_score += 10
    else:
        details.append({"item": "welcome_message 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_msg}，实际 {actual_msg}"})

    # 10. 检查是否包含多余字段（额外扣分项，但这里不做扣分，只检查必需字段均存在）
    required_fields = ["employee_id", "employee_name", "email_profile_created", "system_access_granted", "equipment_allocated", "welcome_message"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        details.append({"item": "无缺失必需字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {missing}"})
        # 这里不扣分已计入各字段检查，但作为附加说明
    else:
        pass  # 已在各字段检查中计分

    _write_score(total_score, details)

def _write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total_score}/100")

if __name__ == "__main__":
    main()
