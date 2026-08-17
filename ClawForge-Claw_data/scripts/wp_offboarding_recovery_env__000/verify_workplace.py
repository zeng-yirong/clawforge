import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0
    max_total = 100

    # 1. 目录结构 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops/ 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops 目录存在"})
        total += 5
    else:
        details.append({"item": "ops/ 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops 目录不存在"})

    checklist_path = os.path.join(ops_dir, "handover_checklist.json")
    if os.path.isfile(checklist_path):
        details.append({"item": "handover_checklist.json 文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total += 5
    else:
        details.append({"item": "handover_checklist.json 文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件不存在"})
        # 后续检查无法继续，直接输出结果
        finish(total, details, max_total)
        return

    # 2. JSON合法性 (10分)
    try:
        with open(checklist_path, 'r') as f:
            data = json.load(f)
        details.append({"item": "JSON 解析合法", "score": 10, "max_score": 10, "passed": True, "reason": "合法 JSON"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON 解析合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        finish(total, details, max_total)
        return

    # 3. 必需字段存在 (20分)
    required_fields = ["employee_id", "employee_name", "department", "revoked_systems", "reclaimed_equipment", "handover_to"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        details.append({"item": "必需字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {missing}"})
    else:
        details.append({"item": "必需字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有必需字段均存在"})
        total += 20

    # 4. 员工基本信息精确匹配 (15分)
    if data.get("employee_id") == "EMP-003":
        details.append({"item": "employee_id = EMP-003", "score": 5, "max_score": 5, "passed": True, "reason": "正确"})
        total += 5
    else:
        details.append({"item": "employee_id = EMP-003", "score": 0, "max_score": 5, "passed": False, "reason": f"值为 {data.get('employee_id')}"})

    if data.get("employee_name") == "Bob Johnson":
        details.append({"item": "employee_name = Bob Johnson", "score": 5, "max_score": 5, "passed": True, "reason": "正确"})
        total += 5
    else:
        details.append({"item": "employee_name = Bob Johnson", "score": 0, "max_score": 5, "passed": False, "reason": f"值为 {data.get('employee_name')}"})

    if data.get("department") == "Finance":
        details.append({"item": "department = Finance", "score": 5, "max_score": 5, "passed": True, "reason": "正确"})
        total += 5
    else:
        details.append({"item": "department = Finance", "score": 0, "max_score": 5, "passed": False, "reason": f"值为 {data.get('department')}"})

    # 5. 撤销系统访问 (30分)
    revoked = data.get("revoked_systems", [])
    expected_systems = {"Admin Portal": "revoked", "CRM": "revoked"}
    passed_systems = 0
    for sys_item in revoked:
        if isinstance(sys_item, dict) and sys_item.get("system_name") in expected_systems and sys_item.get("status") == expected_systems[sys_item["system_name"]]:
            passed_systems += 1
    if passed_systems == 2:
        details.append({"item": "撤销 Admin Portal (状态 revoked)", "score": 15, "max_score": 15, "passed": True, "reason": "正确"})
        total += 15
        details.append({"item": "撤销 CRM (状态 revoked)", "score": 15, "max_score": 15, "passed": True, "reason": "正确"})
        total += 15
    else:
        if len(revoked) != 2:
            details.append({"item": "撤销的系统数量正确", "score": 0, "max_score": 30, "passed": False, "reason": f"期望2个系统，实际{len(revoked)}个"})
        else:
            # 逐个报告
            for sys_name in ["Admin Portal", "CRM"]:
                found = False
                for s in revoked:
                    if s.get("system_name") == sys_name and s.get("status") == "revoked":
                        found = True
                        break
                if found:
                    details.append({"item": f"撤销 {sys_name} (状态 revoked)", "score": 15, "max_score": 15, "passed": True, "reason": "正确"})
                    total += 15
                else:
                    details.append({"item": f"撤销 {sys_name} (状态 revoked)", "score": 0, "max_score": 15, "passed": False, "reason": f"未找到正确记录: {revoked}"})

    # 6. 回收设备 (15分)
    reclaimed = data.get("reclaimed_equipment", [])
    if len(reclaimed) == 1 and reclaimed[0].get("asset_tag") == "LT-2041" and reclaimed[0].get("status") == "reclaimed":
        details.append({"item": "回收设备 LT-2041 (状态 reclaimed)", "score": 15, "max_score": 15, "passed": True, "reason": "正确"})
        total += 15
    else:
        details.append({"item": "回收设备 LT-2041 (状态 reclaimed)", "score": 0, "max_score": 15, "passed": False, "reason": f"实际数据: {reclaimed}"})

    # 7. 交接人信息 (15分)
    handover = data.get("handover_to", {})
    if isinstance(handover, dict) and handover.get("name") == "Alice Wang" and handover.get("role") == "HR Manager":
        details.append({"item": "交接人 name = Alice Wang", "score": 7.5, "max_score": 7.5, "passed": True, "reason": "正确"})
        total += 7.5
        details.append({"item": "交接人 role = HR Manager", "score": 7.5, "max_score": 7.5, "passed": True, "reason": "正确"})
        total += 7.5
    else:
        if handover.get("name") != "Alice Wang":
            details.append({"item": "交接人 name = Alice Wang", "score": 0, "max_score": 7.5, "passed": False, "reason": f"值为 {handover.get('name')}"})
        else:
            details.append({"item": "交接人 name = Alice Wang", "score": 7.5, "max_score": 7.5, "passed": True, "reason": "正确"})
            total += 7.5
        if handover.get("role") != "HR Manager":
            details.append({"item": "交接人 role = HR Manager", "score": 0, "max_score": 7.5, "passed": False, "reason": f"值为 {handover.get('role')}"})
        else:
            details.append({"item": "交接人 role = HR Manager", "score": 7.5, "max_score": 7.5, "passed": True, "reason": "正确"})
            total += 7.5

    # 处理浮点数
    total_int = int(round(total))
    finish(total_int, details, max_total)

def finish(total, details, max_total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/{max_total}")

if __name__ == "__main__":
    main()
