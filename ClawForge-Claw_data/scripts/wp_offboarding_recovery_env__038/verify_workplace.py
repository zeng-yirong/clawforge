import json
import os
import sys

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores = []
    total_score = 0

    # ---------- helper: 计算期望员工 ----------
    # 读取原始数据（从工作区）
    try:
        exit_req_path = os.path.join(workspace, "data/offboarding/exit_requests.json")
        sys_acc_path = os.path.join(workspace, "data/offboarding/system_access.json")
        equip_path = os.path.join(workspace, "data/offboarding/equipment_assignments.json")

        exit_data = load_json(exit_req_path)
        sys_data = load_json(sys_acc_path)
        equip_data = load_json(equip_path)
    except Exception as e:
        # 原始数据缺失，直接打0分
        details = [{"item": "原始数据可读性", "score": 0, "max_score": 100, "passed": False, "reason": f"无法读取原始数据: {str(e)}"}]
        result = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 筛选已批准的请求
    approved = {r["employee_id"]: r["employee_name"] for r in exit_data["exit_requests"] if r["approval_status"] == "approved"}

    # 对于每个已批准的员工，检查系统访问是否全部撤销
    def all_systems_revoked(eid):
        systems = [s for s in sys_data["system_access"] if s["employee_id"] == eid]
        if not systems:
            return False
        return all(s["status"] == "revoked" for s in systems)

    # 检查设备是否全部回收
    def all_equipment_returned(eid):
        equipments = [e for e in equip_data["equipment_assignments"] if e["employee_id"] == eid]
        if not equipments:
            return False
        return all(e["status"] == "returned" for e in equipments)

    expected = []
    for eid, name in approved.items():
        if all_systems_revoked(eid) and all_equipment_returned(eid):
            expected.append({"employee_id": eid, "employee_name": name})

    # 按 employee_id 排序以便比较
    expected.sort(key=lambda x: x["employee_id"])

    # ---------- 检查产物 ----------
    # 1. 目录 ops/ 是否存在
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    scores.append({
        "item": "ops/ 目录存在",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "" if dir_exists else "ops/ 目录未创建"
    })

    # 2. 文件 ops/handover_checklist.json 是否存在
    checklist_path = os.path.join(workspace, "ops", "handover_checklist.json")
    file_exists = os.path.isfile(checklist_path)
    scores.append({
        "item": "handover_checklist.json 存在",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "" if file_exists else "文件未找到"
    })

    if not file_exists:
        # 文件缺失，剩余项均为0
        for _ in range(3):
            scores.append({"item": "", "score": 0, "max_score": 0, "passed": False, "reason": "前置文件缺失"})
        total = sum(s["score"] for s in scores)
        result = {"total_score": total, "details": scores}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 文件格式合法（JSON）
    try:
        with open(checklist_path, 'r') as f:
            actual = json.load(f)
        json_valid = True
        reason = ""
    except json.JSONDecodeError as e:
        json_valid = False
        reason = f"JSON 解析失败: {str(e)}"
    scores.append({
        "item": "handover_checklist.json 是合法 JSON",
        "score": 15 if json_valid else 0,
        "max_score": 15,
        "passed": json_valid,
        "reason": reason
    })

    if not json_valid:
        # 无法进一步验证
        for _ in range(2):
            scores.append({"item": "", "score": 0, "max_score": 0, "passed": False, "reason": "JSON格式错误"})
        total = sum(s["score"] for s in scores)
        result = {"total_score": total, "details": scores}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 内容是 list
    is_list = isinstance(actual, list)
    scores.append({
        "item": "内容为 JSON 数组",
        "score": 10 if is_list else 0,
        "max_score": 10,
        "passed": is_list,
        "reason": "" if is_list else f"实际类型: {type(actual).__name__}"
    })

    if not is_list:
        total = sum(s["score"] for s in scores)
        result = {"total_score": total, "details": scores}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 5. 数组长度匹配
    len_match = len(actual) == len(expected)
    scores.append({
        "item": "清单中员工数量正确",
        "score": 15 if len_match else 0,
        "max_score": 15,
        "passed": len_match,
        "reason": f"期望 {len(expected)} 个，实际 {len(actual)} 个" if not len_match else ""
    })

    # 6. 每个元素结构及内容正确
    # 规范化实际数组：排序
    try:
        actual_sorted = sorted(actual, key=lambda x: x.get("employee_id", ""))
    except Exception:
        actual_sorted = actual

    content_match = True
    content_reason = ""
    if len_match:
        for i, (exp, act) in enumerate(zip(expected, actual_sorted)):
            if not isinstance(act, dict):
                content_match = False
                content_reason = f"第 {i} 个元素不是字典"
                break
            # 检查必要字段
            if "employee_id" not in act or "employee_name" not in act:
                content_match = False
                content_reason = f"第 {i} 个元素缺少 employee_id 或 employee_name"
                break
            # 不允许多余字段
            extra = set(act.keys()) - {"employee_id", "employee_name"}
            if extra:
                content_match = False
                content_reason = f"第 {i} 个元素包含多余字段: {extra}"
                break
            if act["employee_id"] != exp["employee_id"] or act["employee_name"] != exp["employee_name"]:
                content_match = False
                content_reason = f"第 {i} 个元素值不匹配: 期望 {exp}，实际 {act}"
                break
    else:
        content_match = False
        content_reason = "长度不匹配，无法逐项比较"

    scores.append({
        "item": "清单内容完全正确（员工ID、姓名、无多余字段）",
        "score": 40 if content_match else 0,
        "max_score": 40,
        "passed": content_match,
        "reason": content_reason if not content_match else ""
    })

    total_score = sum(s["score"] for s in scores)
    result = {"total_score": total_score, "details": scores}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
