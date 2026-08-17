import json
import sys
import os
import copy

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # 1. 检查必需的输入文件是否存在且可解析（不算分，但作为前提）
    exit_req_path = os.path.join(workspace, "data/offboarding/exit_requests.json")
    sys_access_path = os.path.join(workspace, "data/offboarding/system_access.json")
    equip_path = os.path.join(workspace, "data/offboarding/equipment_assignments.json")
    checklist_path = os.path.join(workspace, "handover_checklist.json")

    # 前置检查：退出请求文件
    try:
        exit_req = load_json(exit_req_path)["exit_requests"]
    except Exception as e:
        details.append({"item": "exit_requests.json 可读", "score": 0, "max_score": 0, "passed": False, "reason": f"无法读取或解析: {e}"})
        # 无法继续，直接写结果
        _write_score(workspace, total, details)
        return

    # 前置检查：系统访问文件
    try:
        sys_access_orig = load_json(sys_access_path)["system_access"]
    except Exception as e:
        details.append({"item": "system_access.json 可读", "score": 0, "max_score": 0, "passed": False, "reason": f"无法读取或解析: {e}"})
        _write_score(workspace, total, details)
        return

    # 前置检查：设备分配文件
    try:
        equip_orig = load_json(equip_path)["equipment_assignments"]
    except Exception as e:
        details.append({"item": "equipment_assignments.json 可读", "score": 0, "max_score": 0, "passed": False, "reason": f"无法读取或解析: {e}"})
        _write_score(workspace, total, details)
        return

    # 2. 确定批准的员工ID
    approved_ids = set()
    approved_names = {}
    for rec in exit_req:
        if rec["approval_status"] == "approved":
            eid = rec["employee_id"]
            approved_ids.add(eid)
            approved_names[eid] = rec["employee_name"]

    if len(approved_ids) != 3:
        details.append({"item": "找到批准的员工数", "score": 0, "max_score": 20, "passed": False, "reason": f"期望3个approved，实际{len(approved_ids)}"})
    else:
        details.append({"item": "找到批准的员工数", "score": 20, "max_score": 20, "passed": True, "reason": f"正确识别E001,E002,E005"})
        total += 20

    # 3. 检查系统访问是否已撤销（只针对approved员工）
    sys_score = 0
    sys_max = 30
    sys_reasons = []
    try:
        sys_access_new = load_json(sys_access_path)["system_access"]
    except:
        sys_access_new = None

    if sys_access_new is None:
        details.append({"item": "系统访问撤销", "score": 0, "max_score": sys_max, "passed": False, "reason": "system_access.json损坏"})
    else:
        # 构建每个employee的state
        all_employees_sys = set()
        for rec in sys_access_new:
            all_employees_sys.add(rec["employee_id"])

        # 检查每个approved员工的每一条记录
        all_ok = True
        for eid in approved_ids:
            records = [r for r in sys_access_new if r["employee_id"] == eid]
            if len(records) == 0:
                sys_reasons.append(f"{eid}没有系统记录")
                all_ok = False
                continue
            for r in records:
                if r["status"] != "revoked":
                    sys_reasons.append(f"{eid}的{r['system_name']}状态为{r['status']}")
                    all_ok = False
        # 检查非approved员工是否被误改
        for eid in all_employees_sys:
            if eid not in approved_ids and eid != "E099":
                # E099已经revoked，不会被改，但检查其他未approved是否保持active
                records = [r for r in sys_access_new if r["employee_id"] == eid]
                for r in records:
                    if r["status"] != "active":
                        sys_reasons.append(f"非批准员工{eid}的{r['system_name']}被误改为{r['status']}")
                        all_ok = False
        if all_ok:
            sys_score = sys_max
            details.append({"item": "系统访问撤销", "score": sys_max, "max_score": sys_max, "passed": True, "reason": "所有批准员工系统已撤销，其他未修改"})
            total += sys_max
        else:
            details.append({"item": "系统访问撤销", "score": 0, "max_score": sys_max, "passed": False, "reason": "; ".join(sys_reasons[:5])})

    # 4. 检查设备回收
    equip_score = 0
    equip_max = 30
    equip_reasons = []
    try:
        equip_new = load_json(equip_path)["equipment_assignments"]
    except:
        equip_new = None

    if equip_new is None:
        details.append({"item": "设备回收", "score": 0, "max_score": equip_max, "passed": False, "reason": "equipment_assignments.json损坏"})
    else:
        all_equip_ids = set()
        for rec in equip_new:
            all_equip_ids.add(rec["employee_id"])

        all_ok = True
        for eid in approved_ids:
            records = [r for r in equip_new if r["employee_id"] == eid]
            if len(records) == 0:
                equip_reasons.append(f"{eid}没有设备记录")
                all_ok = False
                continue
            for r in records:
                if r["status"] != "reclaimed":
                    equip_reasons.append(f"{eid}的{r['asset_tag']}状态为{r['status']}")
                    all_ok = False
        # 检查非approved员工是否被误改
        for eid in all_equip_ids:
            if eid not in approved_ids and eid != "E099":
                records = [r for r in equip_new if r["employee_id"] == eid]
                for r in records:
                    if r["status"] != "assigned":
                        equip_reasons.append(f"非批准员工{eid}的{r['asset_tag']}被误改为{r['status']}")
                        all_ok = False
        if all_ok:
            equip_score = equip_max
            details.append({"item": "设备回收", "score": equip_max, "max_score": equip_max, "passed": True, "reason": "所有批准员工设备已回收，其他未修改"})
            total += equip_max
        else:
            details.append({"item": "设备回收", "score": 0, "max_score": equip_max, "passed": False, "reason": "; ".join(equip_reasons[:5])})

    # 5. 检查handover_checklist.json
    checklist_score = 0
    checklist_max = 20
    checklist_reasons = []
    if not os.path.exists(checklist_path):
        details.append({"item": "交接清单存在", "score": 0, "max_score": checklist_max, "passed": False, "reason": "handover_checklist.json不存在"})
    else:
        try:
            with open(checklist_path, 'r') as f:
                checklist = json.load(f)
        except json.JSONDecodeError:
            details.append({"item": "交接清单格式", "score": 0, "max_score": checklist_max, "passed": False, "reason": "不是合法JSON"})
            _write_score(workspace, total + 0, details)
            return

        # 期望结构：顶层字段 checkliset? 或者直接数组？我们要求是 {"checklist": [...]}
        if not isinstance(checklist, dict) or "checklist" not in checklist:
            # 也可能是数组？按prompt没有明确，但为了统一，允许顶层是列表
            if isinstance(checklist, list):
                items = checklist
            else:
                details.append({"item": "交接清单结构", "score": 0, "max_score": checklist_max, "passed": False, "reason": "应为包含'checklist'键的字典或直接数组"})
                _write_score(workspace, total + 0, details)
                return
        else:
            items = checklist["checklist"]

        if not isinstance(items, list):
            details.append({"item": "交接清单结构", "score": 0, "max_score": checklist_max, "passed": False, "reason": "checklist值应为数组"})
            _write_score(workspace, total + 0, details)
            return

        # 检查每个条目
        item_ok = True
        for eid in approved_ids:
            # 在清单中找到该员工
            found = None
            for it in items:
                if it.get("employee_id") == eid:
                    found = it
                    break
            if found is None:
                checklist_reasons.append(f"缺少员工{eid}")
                item_ok = False
                continue
            # 检查必要字段
            for field in ["employee_name", "systems_revoked", "equipment_reclaimed"]:
                if field not in found:
                    checklist_reasons.append(f"{eid}缺少字段{field}")
                    item_ok = False
            # 可选检查systems_revoked是否为列表且长度正确
            if "systems_revoked" in found:
                sys_list = found["systems_revoked"]
                if not isinstance(sys_list, list):
                    checklist_reasons.append(f"{eid}的systems_revoked不是列表")
                    item_ok = False
                else:
                    # 期望正好撤销两个系统 Admin Portal 和 CRM
                    if set(sys_list) != {"Admin Portal", "CRM"}:
                        checklist_reasons.append(f"{eid}的systems_revoked内容不完整")
                        item_ok = False

        # 检查是否有多余员工
        for it in items:
            eid = it.get("employee_id")
            if eid not in approved_ids and eid is not None:
                checklist_reasons.append(f"出现非批准员工{eid}")
                item_ok = False

        if item_ok and len(items) == len(approved_ids):
            checklist_score = checklist_max
            details.append({"item": "交接清单内容", "score": checklist_max, "max_score": checklist_max, "passed": True, "reason": "包含所有批准员工，字段完整"})
            total += checklist_max
        else:
            details.append({"item": "交接清单内容", "score": 0, "max_score": checklist_max, "passed": False, "reason": "; ".join(checklist_reasons[:5])})

    # 6. 额外扣分：如果handover_checklist.json不存在但前面已处理
    # 汇总
    final_score = min(total, 100)
    # 确保不超过100
    _write_score(workspace, final_score, details)

def _write_score(workspace, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
