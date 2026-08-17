import json
import os
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 handover_checklist.json 是否存在 (5分)
    checklist_path = os.path.join(workspace, "ops", "handover_checklist.json")
    if os.path.isfile(checklist_path):
        details.append({"item": "handover_checklist.json 存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
    else:
        details.append({"item": "handover_checklist.json 存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续检查无法进行，直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return

    # 2. JSON 格式合法 (5分)
    try:
        with open(checklist_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 5, "max_score": 5, "passed": True, "reason": "解析成功"})
        total_score += 5
    except Exception as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 5, "passed": False, "reason": f"解析失败: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 必须包含 handover_date 字段 (5分)
    if "handover_date" in data:
        details.append({"item": "handover_date 字段存在", "score": 5, "max_score": 5, "passed": True, "reason": "字段存在"})
        total_score += 5
    else:
        details.append({"item": "handover_date 字段存在", "score": 0, "max_score": 5, "passed": False, "reason": "缺少 handover_date"})

    # 4. handover_date 必须与 today_date.txt 一致 (5分)
    expected_date = None
    date_file_path = os.path.join(workspace, "data", "offboarding", "today_date.txt")
    try:
        with open(date_file_path, "r") as f:
            expected_date = f.read().strip()
    except:
        pass
    if expected_date and data.get("handover_date") == expected_date:
        details.append({"item": "handover_date 正确", "score": 5, "max_score": 5, "passed": True, "reason": f"日期匹配: {expected_date}"})
        total_score += 5
    else:
        details.append({"item": "handover_date 正确", "score": 0, "max_score": 5, "passed": False, "reason": f"期望 {expected_date}, 实际 {data.get('handover_date')}"})

    # 5. 必须包含 employees 列表 (5分)
    if "employees" in data and isinstance(data["employees"], list):
        details.append({"item": "employees 列表存在", "score": 5, "max_score": 5, "passed": True, "reason": "字段存在且为列表"})
        total_score += 5
    else:
        details.append({"item": "employees 列表存在", "score": 0, "max_score": 5, "passed": False, "reason": "缺少 employees 或不是列表"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    employees = data["employees"]

    # 6. employees 长度必须为 3 (只处理 E001, E002, E003, 不包含 E010) (5分)
    if len(employees) == 3:
        details.append({"item": "employees 长度正确", "score": 5, "max_score": 5, "passed": True, "reason": "包含3个员工"})
        total_score += 5
    else:
        details.append({"item": "employees 长度正确", "score": 0, "max_score": 5, "passed": False, "reason": f"期望3个,实际{len(employees)}个"})

    # 7. 验证每个员工的必须字段 (employee_id, systems_revoked, equipment_reclaimed) (5分)
    field_ok = all("employee_id" in emp and "systems_revoked" in emp and "equipment_reclaimed" in emp for emp in employees)
    if field_ok:
        details.append({"item": "每个员工包含必需字段", "score": 5, "max_score": 5, "passed": True, "reason": "字段齐全"})
        total_score += 5
    else:
        details.append({"item": "每个员工包含必需字段", "score": 0, "max_score": 5, "passed": False, "reason": "缺少字段"})

    # 8. 检查员工 ID 集合是否正好为 {E001, E002, E003} (10分)
    emp_ids = {emp["employee_id"] for emp in employees}
    expected_ids = {"E001", "E002", "E003"}
    if emp_ids == expected_ids:
        details.append({"item": "员工 ID 正确", "score": 10, "max_score": 10, "passed": True, "reason": "只包含 E001,E002,E003"})
        total_score += 10
    else:
        details.append({"item": "员工 ID 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_ids}, 实际 {emp_ids}"})

    # 9. 检查每个员工的 systems_revoked (20分, 每个员工一项)
    # 预期:
    # E001: 撤销 Admin Portal, CRM (都是active)
    # E002: 撤销 Admin Portal
    # E003: 撤销 CRM (因为Admin Portal已是inactive)
    expected_systems = {
        "E001": ["Admin Portal", "CRM"],
        "E002": ["Admin Portal"],
        "E003": ["CRM"]
    }
    sys_score = 0
    sys_reason = []
    for emp in employees:
        eid = emp["employee_id"]
        actual = sorted(emp.get("systems_revoked", []))
        exp = sorted(expected_systems.get(eid, []))
        if actual == exp:
            sys_score += 10  # 每个员工最多10分，这里共20分（两个或两个员工？）实际三个员工，但满分20，每个员工6.67不精确，改为每个员工7分？
            # 重新分配：三个员工 systems_revoked 一共20分，每个大约6.67，不好。改为每个员工有7分，但总分超过20。调整：将该项总分设为20，每个员工得分7（允许近似）。或者直接每个员工正确给7分，满分21但可以截断。为了清晰，将systems_revoked总分为20，每个员工按比例：E001占8分（因为两个系统），E002占6分，E003占6分。
        else:
            sys_reason.append(f"{eid}: 期望 {exp}, 实际 {actual}")
    # 简化：根据实际匹配程度，我们将20分均匀分配，每完全匹配一个员工给6.67分？代码中我们逐项判断。
    # 这里我们用手动判断每个员工
    sub_score = 0
    for emp in employees:
        eid = emp["employee_id"]
        actual = sorted(emp.get("systems_revoked", []))
        exp = sorted(expected_systems.get(eid, []))
        if actual == exp:
            sub_score += 7  # 每个员工7分，总分21但稍后调整max，或者我们设三个员工共21分但max设为20，可容忍1分溢出。
        else:
            sub_score += 0
    # 限制不超过20
    sub_score = min(sub_score, 20)
    details.append({"item": "systems_revoked 正确性", "score": sub_score, "max_score": 20, "passed": sub_score == 20, "reason": "; ".join(sys_reason) if sys_reason else "全部正确"})
    total_score += sub_score

    # 10. 检查每个员工的 equipment_reclaimed (20分)
    # 预期:
    # E001: ["BG-8821"] (LT-2043已回收，不包含)
    # E002: ["LT-2041"]
    # E003: ["BG-8822"]
    expected_equip = {
        "E001": ["BG-8821"],
        "E002": ["LT-2041"],
        "E003": ["BG-8822"]
    }
    equip_score = 0
    equip_reason = []
    for emp in employees:
        eid = emp["employee_id"]
        actual = sorted(emp.get("equipment_reclaimed", []))
        exp = sorted(expected_equip.get(eid, []))
        if actual == exp:
            equip_score += 7  # 同上述分配
        else:
            equip_reason.append(f"{eid}: 期望 {exp}, 实际 {actual}")
    equip_score = min(equip_score, 20)
    details.append({"item": "equipment_reclaimed 正确性", "score": equip_score, "max_score": 20, "passed": equip_score == 20, "reason": "; ".join(equip_reason) if equip_reason else "全部正确"})
    total_score += equip_score

    # 11. 检查没有多余字段 (5分)
    extra_fields = False
    for emp in employees:
        allowed = {"employee_id", "systems_revoked", "equipment_reclaimed"}
        if set(emp.keys()) != allowed:
            extra_fields = True
            break
    if not extra_fields:
        details.append({"item": "没有多余字段", "score": 5, "max_score": 5, "passed": True, "reason": "每个员工只有必要字段"})
        total_score += 5
    else:
        details.append({"item": "没有多余字段", "score": 0, "max_score": 5, "passed": False, "reason": "存在多余字段"})

    # 12. 确认没有包含未批准的员工 (5分)
    disallowed = {"E004", "E005", "E010", "E006"}
    found_disallowed = emp_ids & disallowed
    if not found_disallowed:
        details.append({"item": "未包含未批准员工", "score": 5, "max_score": 5, "passed": True, "reason": "没有多余员工"})
        total_score += 5
    else:
        details.append({"item": "未包含未批准员工", "score": 0, "max_score": 5, "passed": False, "reason": f"包含了 {found_disallowed}"})

    # 确保总分不超过100
    total_score = min(total_score, 100)

    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
