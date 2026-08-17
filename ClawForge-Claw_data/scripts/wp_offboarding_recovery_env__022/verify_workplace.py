import sys
import json
import os
from pathlib import Path

def verify(workspace):
    ws = Path(workspace).resolve()
    details = []
    total_score = 0

    # ---------- 1. 检查 ops 目录和 checklist 文件 (5分) ----------
    ops_dir = ws / "ops"
    checklist_path = ops_dir / "handover_checklist.json"
    item1_score = 0
    item1_max = 5
    reasons1 = []
    if not ops_dir.is_dir():
        reasons1.append("ops/ 目录不存在")
    elif not checklist_path.is_file():
        reasons1.append("ops/handover_checklist.json 文件不存在")
    else:
        item1_score = 5
        reasons1.append("ops/ 和 checklist 文件都存在")
    details.append({"item": "ops/handover_checklist.json 存在", "score": item1_score, "max_score": item1_max, "passed": item1_score == item1_max, "reason": "; ".join(reasons1)})
    total_score += item1_score

    # ---------- 2. checklist JSON 合法性 + 字段完整性 (10+5+5+5+5+10+5+5 = 50分) ----------
    if not checklist_path.is_file():
        # 如果文件不存在，所有字段检查直接得0
        field_items = [
            ("JSON 合法", 10),
            ("employee_id", 5),
            ("employee_name", 5),
            ("department", 5),
            ("email", 5),
            ("systems_revoked 包含 Admin Portal 和 CRM", 10),
            ("equipment_reclaimed", 5),
            ("handover_date", 5)
        ]
        for fname, fmax in field_items:
            details.append({"item": f"checklist 字段: {fname}", "score": 0, "max_score": fmax, "passed": False, "reason": "checklist 文件缺失"})
        total_score += 0
    else:
        try:
            with open(str(checklist_path), 'r') as f:
                cl = json.load(f)
            valid = True
        except Exception as e:
            cl = None
            valid = False
            details.append({"item": "checklist JSON 合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
            total_score += 0
            # 后续字段检查跳过
            field_checks = ["employee_id", "employee_name", "department", "email", "systems_revoked", "equipment_reclaimed", "handover_date"]
            for fc in field_checks:
                details.append({"item": f"checklist 字段: {fc}", "score": 0, "max_score": 5 if fc != "systems_revoked" else 10, "passed": False, "reason": "前置 JSON 检查失败"})
            # 跳过剩余逻辑
            pass

        if valid and cl is not None:
            # 2.1 JSON 合法
            details.append({"item": "checklist JSON 合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
            total_score += 10

            # 2.2 employee_id = "EMP-007"
            eid = cl.get("employee_id")
            eid_ok = (eid == "EMP-007")
            details.append({"item": "checklist 字段: employee_id", "score": 5 if eid_ok else 0, "max_score": 5, "passed": eid_ok, "reason": f"期望 EMP-007，实际 {eid}" if not eid_ok else "正确"})
            total_score += 5 if eid_ok else 0

            # 2.3 employee_name = "Alice Wang"
            ename = cl.get("employee_name")
            ename_ok = (ename == "Alice Wang")
            details.append({"item": "checklist 字段: employee_name", "score": 5 if ename_ok else 0, "max_score": 5, "passed": ename_ok, "reason": f"期望 Alice Wang，实际 {ename}" if not ename_ok else "正确"})
            total_score += 5 if ename_ok else 0

            # 2.4 department = "Engineering"
            dept = cl.get("department")
            dept_ok = (dept == "Engineering")
            details.append({"item": "checklist 字段: department", "score": 5 if dept_ok else 0, "max_score": 5, "passed": dept_ok, "reason": f"期望 Engineering，实际 {dept}" if not dept_ok else "正确"})
            total_score += 5 if dept_ok else 0

            # 2.5 email = "alice@company.com"
            email = cl.get("email")
            email_ok = (email == "alice@company.com")
            details.append({"item": "checklist 字段: email", "score": 5 if email_ok else 0, "max_score": 5, "passed": email_ok, "reason": f"期望 alice@company.com，实际 {email}" if not email_ok else "正确"})
            total_score += 5 if email_ok else 0

            # 2.6 systems_revoked 包含 "Admin Portal" 和 "CRM" (顺序任意)
            sr = cl.get("systems_revoked", [])
            sr_ok = isinstance(sr, list) and "Admin Portal" in sr and "CRM" in sr
            sr_score = 10 if sr_ok else 0
            details.append({"item": "checklist 字段: systems_revoked 包含 Admin Portal 和 CRM", "score": sr_score, "max_score": 10, "passed": sr_ok, "reason": f"实际值 {sr}" if not sr_ok else "正确"})
            total_score += sr_score

            # 2.7 equipment_reclaimed = "LT-2041"
            eq = cl.get("equipment_reclaimed")
            eq_ok = (eq == "LT-2041")
            details.append({"item": "checklist 字段: equipment_reclaimed", "score": 5 if eq_ok else 0, "max_score": 5, "passed": eq_ok, "reason": f"期望 LT-2041，实际 {eq}" if not eq_ok else "正确"})
            total_score += 5 if eq_ok else 0

            # 2.8 handover_date = "2025-04-01"
            hd = cl.get("handover_date")
            hd_ok = (hd == "2025-04-01")
            details.append({"item": "checklist 字段: handover_date", "score": 5 if hd_ok else 0, "max_score": 5, "passed": hd_ok, "reason": f"期望 2025-04-01，实际 {hd}" if not hd_ok else "正确"})
            total_score += 5 if hd_ok else 0

    # ---------- 3. system_access.json 中 EMP-007 记录是否被 revoke (各10分，共20分) ----------
    sys_access_path = ws / "data" / "offboarding" / "system_access.json"
    access_ok_ap = False
    access_ok_crm = False
    access_reasons = []
    if not sys_access_path.is_file():
        details.append({"item": "system_access.json 中 EMP-007 Admin Portal revoked", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        details.append({"item": "system_access.json 中 EMP-007 CRM revoked", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        total_score += 0
    else:
        try:
            with open(str(sys_access_path), 'r') as f:
                sa = json.load(f)
            records = sa.get("system_access", [])
            for r in records:
                if r.get("employee_id") == "EMP-007":
                    if r.get("system_name") == "Admin Portal":
                        access_ok_ap = (r.get("status") == "revoked")
                    if r.get("system_name") == "CRM":
                        access_ok_crm = (r.get("status") == "revoked")
            details.append({"item": "system_access.json 中 EMP-007 Admin Portal revoked", "score": 10 if access_ok_ap else 0, "max_score": 10, "passed": access_ok_ap, "reason": "状态正确" if access_ok_ap else "状态未改为 revoked"})
            details.append({"item": "system_access.json 中 EMP-007 CRM revoked", "score": 10 if access_ok_crm else 0, "max_score": 10, "passed": access_ok_crm, "reason": "状态正确" if access_ok_crm else "状态未改为 revoked"})
            total_score += (10 if access_ok_ap else 0) + (10 if access_ok_crm else 0)
        except Exception as e:
            details.append({"item": "system_access.json 中 EMP-007 Admin Portal revoked", "score": 0, "max_score": 10, "passed": False, "reason": f"读取/解析错误: {e}"})
            details.append({"item": "system_access.json 中 EMP-007 CRM revoked", "score": 0, "max_score": 10, "passed": False, "reason": f"读取/解析错误: {e}"})
            total_score += 0

    # ---------- 4. equipment_assignments.json 中 EMP-007 状态是否 reclaimed (10分) ----------
    equip_path = ws / "data" / "offboarding" / "equipment_assignments.json"
    equip_ok = False
    if not equip_path.is_file():
        details.append({"item": "equipment_assignments.json 中 EMP-007 reclaimed", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        total_score += 0
    else:
        try:
            with open(str(equip_path), 'r') as f:
                eq = json.load(f)
            records = eq.get("equipment_assignments", [])
            for r in records:
                if r.get("employee_id") == "EMP-007":
                    equip_ok = (r.get("status") == "reclaimed")
                    break
            details.append({"item": "equipment_assignments.json 中 EMP-007 reclaimed", "score": 10 if equip_ok else 0, "max_score": 10, "passed": equip_ok, "reason": "状态正确" if equip_ok else "状态未改为 reclaimed"})
            total_score += 10 if equip_ok else 0
        except Exception as e:
            details.append({"item": "equipment_assignments.json 中 EMP-007 reclaimed", "score": 0, "max_score": 10, "passed": False, "reason": f"读取/解析错误: {e}"})
            total_score += 0

    # ---------- 5. 检查其他记录未被意外修改 (10分) ----------
    other_ok = True
    other_reasons = []
    # 5.1 system_access 中 EMP-001 的 Admin Portal 仍为 revoked
    if sys_access_path.is_file():
        with open(str(sys_access_path), 'r') as f:
            sa = json.load(f)
        for r in sa.get("system_access", []):
            if r.get("employee_id") == "EMP-001" and r.get("system_name") == "Admin Portal":
                if r.get("status") != "revoked":
                    other_ok = False
                    other_reasons.append("EMP-001 Admin Portal 状态被意外修改")
            if r.get("employee_id") == "EMP-002" and r.get("system_name") == "VPN":
                if r.get("status") != "active":
                    other_ok = False
                    other_reasons.append("EMP-002 VPN 状态被意外修改")
        # 5.2 equipment 中 EMP-002 的 LT-2041 仍为 assigned
        with open(str(equip_path), 'r') as f:
            eq = json.load(f)
        for r in eq.get("equipment_assignments", []):
            if r.get("employee_id") == "EMP-002" and r.get("asset_tag") == "LT-2041":
                if r.get("status") != "assigned":
                    other_ok = False
                    other_reasons.append("EMP-002 设备状态被意外修改")
    else:
        other_ok = False
        other_reasons.append("无法读取 system_access.json 或 equipment_assignments.json")

    details.append({"item": "其他记录未被意外修改", "score": 10 if other_ok else 0, "max_score": 10, "passed": other_ok, "reason": "无异常" if other_ok else "; ".join(other_reasons)})
    total_score += 10 if other_ok else 0

    # ---------- 6. 没有多余的文件要求 (不扣分，但作为加分项？这里不检查) ----------
    # 忽略

    # 规范化总分 0-100
    total_score = min(total_score, 100)

    result = {
        "total_score": total_score,
        "details": details
    }

    # 写入 workplace_score.json
    score_path = ws / "workplace_score.json"
    with open(str(score_path), 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
