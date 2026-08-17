import sys
import json
import os
from pathlib import Path

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    ws = Path(WORKSPACE)
    details = []
    total_score = 0

    # 1. 目录和文件存在性 (10分)
    score_item = {"item": "ops/ 目录存在", "max_score": 5}
    if (ws / "ops").is_dir():
        score_item["score"] = 5
        score_item["passed"] = True
        score_item["reason"] = "ops/ 目录存在"
    else:
        score_item["score"] = 0
        score_item["passed"] = False
        score_item["reason"] = "ops/ 目录不存在"
    details.append(score_item)
    total_score += score_item["score"]

    score_item = {"item": "ops/handover_checklist.json 文件存在", "max_score": 5}
    checklist_path = ws / "ops" / "handover_checklist.json"
    if checklist_path.is_file():
        score_item["score"] = 5
        score_item["passed"] = True
        score_item["reason"] = "文件存在"
    else:
        score_item["score"] = 0
        score_item["passed"] = False
        score_item["reason"] = "文件不存在"
    details.append(score_item)
    total_score += score_item["score"]

    if not checklist_path.is_file():
        # 无法继续，保存结果并退出
        final = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        print(f"Total score: {total_score}")
        return

    # 2. 解析 JSON 格式 (10分)
    score_item = {"item": "handover_checklist.json 格式合法", "max_score": 10}
    try:
        checklist_data = load_json(checklist_path)
        # 期望是列表，或者包裹在 'handover_checklist' 键下的列表
        if isinstance(checklist_data, list):
            checklist = checklist_data
        elif isinstance(checklist_data, dict) and "handover_checklist" in checklist_data:
            checklist = checklist_data["handover_checklist"]
        else:
            raise ValueError("格式不支持")
        score_item["score"] = 10
        score_item["passed"] = True
        score_item["reason"] = "JSON 合法且解析为列表或 wrapper"
    except Exception as e:
        score_item["score"] = 0
        score_item["passed"] = False
        score_item["reason"] = f"JSON 解析失败: {e}"
        details.append(score_item)
        total_score += score_item["score"]
        # 后续检查无法进行
        final = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        print(f"Total score: {total_score}")
        return
    details.append(score_item)
    total_score += score_item["score"]

    # 加载参考数据
    try:
        exit_req = load_json(ws / "data" / "offboarding" / "exit_requests.json")["exit_requests"]
        sys_acc = load_json(ws / "data" / "offboarding" / "system_access.json")["system_access"]
        equip = load_json(ws / "data" / "offboarding" / "equipment_assignments.json")["equipment_assignments"]
    except Exception as e:
        # 参考数据缺失（自己的 env 应该存在）
        score_item = {"item": "参考数据加载失败", "max_score": 0, "score": 0, "passed": False, "reason": str(e)}
        details.append(score_item)
        final = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        print(f"Total score: {total_score}")
        return

    # 筛选已批准员工
    approved_emps = [emp for emp in exit_req if emp["approval_status"] == "approved"]
    expected_ids = {emp["employee_id"] for emp in approved_emps}
    expected_names = {emp["employee_id"]: emp["employee_name"] for emp in approved_emps}

    # 构建每个员工预期系统列表（所有系统名）
    expected_systems = {}
    for entry in sys_acc:
        eid = entry["employee_id"]
        if eid in expected_ids:
            expected_systems.setdefault(eid, []).append(entry["system_name"])

    # 构建每个员工预期设备标签列表
    expected_equipment = {}
    for entry in equip:
        eid = entry["employee_id"]
        if eid in expected_ids:
            expected_equipment.setdefault(eid, []).append(entry["asset_tag"])

    # 3. 条目数量匹配 (20分)
    score_item = {"item": "checklist 条目数量等于已批准员工数", "max_score": 20}
    if len(checklist) == len(approved_emps):
        score_item["score"] = 20
        score_item["passed"] = True
        score_item["reason"] = f"条目数 {len(checklist)} 正确"
    else:
        score_item["score"] = 0
        score_item["passed"] = False
        score_item["reason"] = f"期望 {len(approved_emps)} 条，实际 {len(checklist)} 条"
    details.append(score_item)
    total_score += score_item["score"]

    # 4. 逐员工检查 (30分: 字段完整性10 + 系统列表10 + 设备列表10)
    # 先构建一个字典方便查找
    emp_in_checklist = {item.get("employee_id"): item for item in checklist}
    field_score = 0
    system_score = 0
    equipment_score = 0

    for emp in approved_emps:
        eid = emp["employee_id"]
        item = emp_in_checklist.get(eid)
        if item is None:
            # 缺失员工，扣分
            continue

        # 检查必要字段是否存在
        required_fields = ["employee_id", "employee_name", "systems_revoked", "equipment_reclaimed", "completion_date"]
        if all(f in item for f in required_fields):
            field_score += 5  # 每个员工5分，两个共10分
        else:
            missing = [f for f in required_fields if f not in item]
            reason = f"{eid} 缺少字段: {missing}"
            # 不扣分？但分数按检查项算

        # 检查 employee_name 正确
        if item.get("employee_name") == expected_names[eid]:
            pass
        else:
            # 名称错误，可以扣分但整体字段完整性已经考虑
            pass

        # 检查 systems_revoked (使用set)
        expected_sys_set = set(expected_systems.get(eid, []))
        actual_sys_set = set(item.get("systems_revoked", []))
        if actual_sys_set == expected_sys_set:
            system_score += 5  # 每个员工5分，共10分
        else:
            # 部分正确？ 这里简单处理为0分
            pass

        # 检查 equipment_reclaimed
        expected_equip_set = set(expected_equipment.get(eid, []))
        actual_equip_set = set(item.get("equipment_reclaimed", []))
        if actual_equip_set == expected_equip_set:
            equipment_score += 5  # 每个员工5分，共10分

    score_item = {"item": "每个员工的字段完整性 (employee_id, name, systems_revoked, equipment_reclaimed, completion_date)", "max_score": 10}
    score_item["score"] = field_score
    score_item["passed"] = field_score == 10
    score_item["reason"] = f"得到 {field_score}/10"
    details.append(score_item)
    total_score += field_score

    score_item = {"item": "每个员工的 systems_revoked 正确", "max_score": 10}
    score_item["score"] = system_score
    score_item["passed"] = system_score == 10
    score_item["reason"] = f"得到 {system_score}/10"
    details.append(score_item)
    total_score += system_score

    score_item = {"item": "每个员工的 equipment_reclaimed 正确", "max_score": 10}
    score_item["score"] = equipment_score
    score_item["passed"] = equipment_score == 10
    score_item["reason"] = f"得到 {equipment_score}/10"
    details.append(score_item)
    total_score += equipment_score

    # 5. 日期检查 (10分) —— 要求 completion_date 为 "2025-04-15"（与 env_builder 中硬编码一致）
    score_item = {"item": "completion_date 字段值固定为 '2025-04-15'", "max_score": 10}
    date_ok = True
    for item in checklist:
        if item.get("completion_date") != "2025-04-15":
            date_ok = False
            break
    if date_ok and len(checklist) > 0:
        score_item["score"] = 10
        score_item["passed"] = True
        score_item["reason"] = "所有条目日期正确"
    elif len(checklist) == 0:
        score_item["score"] = 0
        score_item["passed"] = False
        score_item["reason"] = "无条目可检查"
    else:
        score_item["score"] = 0
        score_item["passed"] = False
        score_item["reason"] = "至少一个条目日期错误"
    details.append(score_item)
    total_score += score_item["score"]

    # 确保总分不超过100
    total_score = min(total_score, 100)

    final = {"total_score": total_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)
    print(f"Total score: {total_score}")

if __name__ == "__main__":
    main()
