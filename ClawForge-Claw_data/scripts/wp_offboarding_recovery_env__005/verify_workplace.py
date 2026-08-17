import sys
import json
import os
from pathlib import Path

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None

def verify(workspace):
    score_details = []
    total_score = 0

    # ---------- 1. 检查 ops/handover_checklist.json 是否存在 ----------
    checklist_path = Path(workspace) / "ops" / "handover_checklist.json"
    exists = checklist_path.exists()
    score_details.append({
        "item": "handover_checklist.json 文件存在",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "文件存在" if exists else "文件未找到"
    })
    if not exists:
        total_score = sum(d["score"] for d in score_details)
        final = {"total_score": total_score, "details": score_details}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # ---------- 2. 解析 checklist JSON ----------
    checklist = load_json(str(checklist_path))
    if checklist is None or not isinstance(checklist, dict):
        score_details.append({
            "item": "handover_checklist.json 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "JSON 解析失败或不是对象"
        })
        total_score = sum(d["score"] for d in score_details)
        final = {"total_score": total_score, "details": score_details}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return
    else:
        score_details.append({
            "item": "handover_checklist.json 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON 解析成功"
        })

    # ---------- 3. 检查 checklist 包含 items 列表 ----------
    items = checklist.get("items")
    if not isinstance(items, list):
        score_details.append({
            "item": "checklist 包含 items 列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 items 字段或不是列表"
        })
        total_score = sum(d["score"] for d in score_details)
        final = {"total_score": total_score, "details": score_details}
        with open(Path(workspace) / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return
    else:
        score_details.append({
            "item": "checklist 包含 items 列表",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"items 列表长度 {len(items)}"
        })

    # ---------- 4. 加载原始 exit_requests 获取已批准员工 ----------
    exit_req_path = Path(workspace) / "data" / "offboarding" / "exit_requests.json"
    exit_req = load_json(str(exit_req_path))
    if exit_req is None or "exit_requests" not in exit_req:
        score_details.append({
            "item": "读取 exit_requests.json",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "无法读取或格式错误"
        })
    else:
        score_details.append({
            "item": "读取 exit_requests.json",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "成功读取"
        })
        approved_employees = {}
        for emp_id, emp_info in exit_req["exit_requests"].items():
            if emp_info.get("approval_status") == "Approved":
                approved_employees[emp_id] = emp_info
        # 预期批准员工：E001, E002, E005
        expected_ids = {"E001", "E002", "E005"}
        actual_ids_in_checklist = {item.get("employee_id") for item in items if "employee_id" in item}

        # ---------- 5. 检查是否包含所有已批准员工 ----------
        missing = expected_ids - actual_ids_in_checklist
        extra = actual_ids_in_checklist - expected_ids
        missing_penalty = 0
        if missing:
            missing_penalty += 15  # 每个缺失扣15，最多扣15? 这里统一扣15
        if extra:
            missing_penalty += 10  # 多余扣10
        passed_5 = (len(missing) == 0 and len(extra) == 0)
        reason_5 = f"缺失员工: {missing if missing else '无'}, 多余员工: {extra if extra else '无'}"
        score_details.append({
            "item": "checklist 覆盖所有已批准员工，无多余",
            "score": 15 if passed_5 else max(0, 15 - missing_penalty),
            "max_score": 15,
            "passed": passed_5,
            "reason": reason_5
        })

    # ---------- 6. 检查每个已批准员工的系统和设备状态 ----------
    system_access_path = Path(workspace) / "data" / "offboarding" / "system_access.json"
    equip_assign_path = Path(workspace) / "data" / "offboarding" / "equipment_assignments.json"
    sys_acc = load_json(str(system_access_path))
    equip_assign = load_json(str(equip_assign_path))

    sys_items = {}
    if sys_acc and "system_access" in sys_acc:
        for key, val in sys_acc["system_access"].items():
            eid = val["employee_id"]
            sys_items.setdefault(eid, []).append(val)
    equip_items = {}
    if equip_assign and "equipment_assignments" in equip_assign:
        for key, val in equip_assign["equipment_assignments"].items():
            eid = val["employee_id"]
            equip_items.setdefault(eid, []).append(val)

    correct_systems = True
    correct_equipment = True
    system_mismatch_details = []
    equip_mismatch_details = []

    for item in items:
        eid = item.get("employee_id")
        if eid not in expected_ids:
            continue  # 多余员工忽略，已在之前扣分

        # 检查 systems
        systems = item.get("systems", [])
        expected_systems = sys_items.get(eid, [])
        expected_sys_names_status = {s["system_name"]: "Revoked" for s in expected_systems}
        for s in systems:
            sname = s.get("system_name")
            sstatus = s.get("status")
            if sname not in expected_sys_names_status:
                system_mismatch_details.append(f"{eid}: 未知系统 {sname}")
                correct_systems = False
            elif sstatus != "Revoked":
                system_mismatch_details.append(f"{eid}: {sname} 状态应为 Revoked，实际为 {sstatus}")
                correct_systems = False
            else:
                pass  # 正确
        # 检查是否遗漏了系统
        checklist_sys_names = {s.get("system_name") for s in systems}
        for s in expected_systems:
            if s["system_name"] not in checklist_sys_names:
                system_mismatch_details.append(f"{eid}: 缺少系统 {s['system_name']}")
                correct_systems = False

        # 检查 equipment
        equip = item.get("equipment", [])
        expected_equip = equip_items.get(eid, [])
        expected_asset_status = {e["asset_tag"]: "Reclaimed" for e in expected_equip}
        for e in equip:
            atag = e.get("asset_tag")
            estatus = e.get("status")
            if atag not in expected_asset_status:
                equip_mismatch_details.append(f"{eid}: 未知资产 {atag}")
                correct_equipment = False
            elif estatus != "Reclaimed":
                equip_mismatch_details.append(f"{eid}: {atag} 状态应为 Reclaimed，实际为 {estatus}")
                correct_equipment = False
        checklist_asset_tags = {e.get("asset_tag") for e in equip}
        for e in expected_equip:
            if e["asset_tag"] not in checklist_asset_tags:
                equip_mismatch_details.append(f"{eid}: 缺少资产 {e['asset_tag']}")
                correct_equipment = False

    score_sys = 20 if correct_systems else max(0, 20 - 5*len(system_mismatch_details))
    score_sys = min(score_sys, 20)  # 不超过满分
    score_details.append({
        "item": "所有已批准员工的系统状态均为 Revoked",
        "score": score_sys,
        "max_score": 20,
        "passed": correct_systems,
        "reason": "正确" if correct_systems else "; ".join(system_mismatch_details[:3])
    })

    score_equip = 20 if correct_equipment else max(0, 20 - 5*len(equip_mismatch_details))
    score_equip = min(score_equip, 20)
    score_details.append({
        "item": "所有已批准员工的设备状态均为 Reclaimed",
        "score": score_equip,
        "max_score": 20,
        "passed": correct_equipment,
        "reason": "正确" if correct_equipment else "; ".join(equip_mismatch_details[:3])
    })

    # ---------- 7. 检查 checklist 包含 employee_name 字段 ----------
    names_ok = all("employee_name" in item for item in items)
    score_details.append({
        "item": "每个 item 包含 employee_name",
        "score": 5 if names_ok else 0,
        "max_score": 5,
        "passed": names_ok,
        "reason": "所有 item 均有 employee_name" if names_ok else "存在缺失 employee_name 的 item"
    })

    # ---------- 8. 检查 checklist 中每个 item 的 systems 和 equipment 是列表 ----------
    struct_ok = True
    for item in items:
        if not isinstance(item.get("systems"), list):
            struct_ok = False
            break
        if not isinstance(item.get("equipment"), list):
            struct_ok = False
            break
    score_details.append({
        "item": "systems 和 equipment 字段均为列表",
        "score": 5 if struct_ok else 0,
        "max_score": 5,
        "passed": struct_ok,
        "reason": "所有结构正确" if struct_ok else "存在非列表字段"
    })

    # ---------- 计算总分 ----------
    total_score = sum(d["score"] for d in score_details)
    final = {"total_score": total_score, "details": score_details}
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
