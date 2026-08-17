import json
import os
import sys
from pathlib import Path

def score(workspace: str):
    details = []
    total_score = 0
    ws = Path(workspace)

    # 1. 检查 handover_checklist.json 是否存在（10分）
    checklist_path = ws / "handover_checklist.json"
    if checklist_path.exists() and checklist_path.is_file():
        details.append({
            "item": "handover_checklist.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        details.append({
            "item": "handover_checklist.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"未找到 {checklist_path}"
        })
        # 后续检查依赖该文件，直接返回
        _write_score(total_score, details, ws)
        return

    # 2. 解析 handover_checklist.json 并验证结构（10分）
    try:
        with open(checklist_path, "r") as f:
            checklist = json.load(f)
        if not isinstance(checklist, list):
            raise ValueError("不是数组")
        if len(checklist) == 0:
            details.append({"item": "清单结构合法", "score": 5, "max_score": 10, "passed": False, "reason": "空数组"})
            _write_score(total_score + 5, details, ws)
            return
        details.append({"item": "清单结构合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 数组"})
        total_score += 10
    except Exception as e:
        details.append({"item": "清单结构合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        _write_score(total_score, details, ws)
        return

    # 3. 验证只有 approved 员工被处理（15分）
    # 加载原始退出请求
    exit_req_path = ws / "data/offboarding/exit_requests.json"
    try:
        with open(exit_req_path, "r") as f:
            exit_reqs = json.load(f)
    except:
        details.append({"item": "只包含 approved 员工", "score": 0, "max_score": 15, "passed": False, "reason": "无法读取 exit_requests.json"})
        _write_score(total_score, details, ws)
        return

    approved_ids = {r["employee_id"] for r in exit_reqs if r["approval_status"] == "approved"}
    checklist_ids = {item.get("employee_id") for item in checklist if item.get("employee_id")}
    if checklist_ids == approved_ids:
        details.append({"item": "只包含 approved 员工", "score": 15, "max_score": 15, "passed": True, "reason": f"清单中的员工 ID 与批准的完全一致: {approved_ids}"})
        total_score += 15
    else:
        missing = approved_ids - checklist_ids
        extra = checklist_ids - approved_ids
        reason = f"缺失: {missing}, 多余: {extra}" if missing or extra else "ID 集合不匹配"
        details.append({"item": "只包含 approved 员工", "score": 0, "max_score": 15, "passed": False, "reason": reason})
        # 标记后继续检查其他项

    # 4. 验证每个清单项包含必要字段 (employee_id, employee_name, revoked_systems, reclaimed_equipment)（10分）
    field_ok = True
    for item in checklist:
        if not all(k in item for k in ("employee_id", "employee_name", "revoked_systems", "reclaimed_equipment")):
            field_ok = False
            break
        if not isinstance(item["revoked_systems"], list) or not isinstance(item["reclaimed_equipment"], list):
            field_ok = False
            break
    if field_ok:
        details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "每个对象包含四个必须字段"})
        total_score += 10
    else:
        details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "缺少字段或类型错误"})

    # 5. 验证系统访问原始文件已被正确修改 (revoked)（25分）
    sys_acc_path = ws / "data/offboarding/system_access.json"
    try:
        with open(sys_acc_path, "r") as f:
            sys_accs = json.load(f)
    except:
        details.append({"item": "system_access.json 已修改", "score": 0, "max_score": 25, "passed": False, "reason": "文件读取失败"})
        _write_score(total_score, details, ws)
        return

    sys_mod_ok = True
    for rec in sys_accs:
        emp_id = rec["employee_id"]
        if emp_id in approved_ids:
            if rec["status"] != "revoked":
                sys_mod_ok = False
                break
        else:
            # 未批准的员工应保持 active
            if rec["status"] != "active":
                sys_mod_ok = False
                break
    if sys_mod_ok:
        details.append({"item": "system_access.json 已修改", "score": 25, "max_score": 25, "passed": True, "reason": "approved 员工全部 revoked，其余 active"})
        total_score += 25
    else:
        details.append({"item": "system_access.json 已修改", "score": 0, "max_score": 25, "passed": False, "reason": "状态修改不正确"})

    # 6. 验证设备分配原始文件已被正确修改 (reclaimed)（20分）
    equip_path = ws / "data/offboarding/equipment_assignments.json"
    try:
        with open(equip_path, "r") as f:
            equip_assign = json.load(f)
    except:
        details.append({"item": "equipment_assignments.json 已修改", "score": 0, "max_score": 20, "passed": False, "reason": "文件读取失败"})
        _write_score(total_score, details, ws)
        return

    equip_mod_ok = True
    for rec in equip_assign:
        emp_id = rec["employee_id"]
        if emp_id in approved_ids:
            if rec["status"] != "reclaimed":
                equip_mod_ok = False
                break
        else:
            if rec["status"] != "assigned":
                equip_mod_ok = False
                break
    if equip_mod_ok:
        details.append({"item": "equipment_assignments.json 已修改", "score": 20, "max_score": 20, "passed": True, "reason": "approved 员工全部 reclaimed，其余 assigned"})
        total_score += 20
    else:
        details.append({"item": "equipment_assignments.json 已修改", "score": 0, "max_score": 20, "passed": False, "reason": "状态修改不正确"})

    # 7. 额外校验：清单中的 revoked_systems 应等于原始记录中该员工拥有的系统列表（10分）
    # 构造原始系统字典
    sys_map = {}
    for rec in sys_accs:  # 这里用的是修改后的文件，但原始记录我们已通过加载得到（注意上面修改后，sys_accs是修改后的内容）
        # 实际上我们需要原始的系统列表（修改前的），但原始数据已丢失。不过我们可以从修改后的文件反向：如果状态是revoked，说明原始是active
        # 为简化，我们直接从env_builder的预期构造（但这里不能依赖env_builder，我们用exit_reqs和system_access的原始数据？）
        # 更好的做法：我们重新读取system_access.json（已修改），但status变为revoked，我们无法知道原始系统名列表。
        # 所以我们设定一个规则：清单中的revoked_systems应等于从修改后的system_access.json中筛选出该员工的所有system_name（不论status）
        pass
    # 由于设计复杂度，跳过这一项，将分数分配给前面的项。
    # 这里我们增加一个可选检查：确保清单中每个员工的 revoked_systems 不为空（对于有系统记录的人）且包含所有系统名
    # 我们利用修改后文件：对于approved员工，所有记录的system_name应该在清单中
    detail_revoked_sys = True
    for emp_id in approved_ids:
        emp_sys_names = [rec["system_name"] for rec in sys_accs if rec["employee_id"] == emp_id]
        if not emp_sys_names:
            continue  # 没有系统记录，清单中revoked_systems应为空列表
        checklist_item = next((item for item in checklist if item["employee_id"] == emp_id), None)
        if checklist_item is None:
            detail_revoked_sys = False
            break
        if set(emp_sys_names) != set(checklist_item["revoked_systems"]):
            detail_revoked_sys = False
            break
    if detail_revoked_sys:
        details.append({"item": "revoked_systems 内容正确", "score": 10, "max_score": 10, "passed": True, "reason": "每个员工的 revoked_systems 与原始系统匹配"})
        total_score += 10
    else:
        details.append({"item": "revoked_systems 内容正确", "score": 0, "max_score": 10, "passed": False, "reason": "系统列表不匹配或缺失"})

    # 修正总分上限为100（前面各项分数总和：10+10+15+10+25+20+10 = 100）
    # 但第7项额外加了10分，实际总分应为110？我们调整：第3项改为15分，第4项10分，第5项25分，第6项20分，第7项10分，前两项20分 = 100
    # 刚才第3项已经15，第4项10，第5项25，第6项20，第7项10，加上前两项20 = 100，正确。
    # 但第3项我们用了15，第5项25，第6项20，第7项10，总数=10+10+15+10+25+20+10=100。

    # 确保总分不超过100（如果前面有0分，可能少）
    if total_score > 100:
        total_score = 100

    _write_score(total_score, details, ws)


def _write_score(total, details, ws: Path):
    result = {"total_score": total, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total}/100")
    sys.exit(0 if total == 100 else 1)


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score(workspace)
