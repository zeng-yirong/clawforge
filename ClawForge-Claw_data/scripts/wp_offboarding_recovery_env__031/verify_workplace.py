import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    score = 0

    # 1. 检查 ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ not found"})
        # 后续检查无法进行，直接返回
        _write_score(0, details)
        return

    # 2. 检查三个产物文件是否存在并合法 (每个10分，共30分)
    required_files = [
        "ops/revoked_access.json",
        "ops/reclaimed_equipment.json",
        "ops/handover_checklist.json"
    ]
    file_valid = {}
    for fname in required_files:
        fpath = os.path.join(workspace, fname)
        if os.path.isfile(fpath):
            try:
                with open(fpath, "r") as f:
                    json.load(f)
                file_valid[fname] = True
                details.append({"item": f"{fname} exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "file parse OK"})
                score += 10
            except (json.JSONDecodeError, Exception):
                file_valid[fname] = False
                details.append({"item": f"{fname} exists but invalid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "not valid JSON"})
        else:
            file_valid[fname] = False
            details.append({"item": f"{fname} exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})

    # 如果任一文件缺失，后续无法验证内容，提前返回
    if not all(file_valid.values()):
        _write_score(score, details)
        return

    # 3. 验证 revoked_access.json 内容 (20分)
    with open(os.path.join(workspace, "ops/revoked_access.json")) as f:
        revoked = json.load(f)
    # 预期：两条记录，系统名分别为 Admin Portal 和 CRM，状态 revoked，员工 E-0431
    expected_revoked = [
        {"employee_id": "E-0431", "system_name": "Admin Portal", "status": "revoked"},
        {"employee_id": "E-0431", "system_name": "CRM", "status": "revoked"}
    ]
    # 转换为比较方便的元组集合（忽略顺序）
    revoked_set = {(r["employee_id"], r["system_name"], r["status"]) for r in revoked}
    expected_set = {(r["employee_id"], r["system_name"], r["status"]) for r in expected_revoked}
    if revoked_set == expected_set and len(revoked) == 2:
        details.append({"item": "revoked_access.json content correct", "score": 20, "max_score": 20, "passed": True, "reason": "both systems revoked for E-0431"})
        score += 20
    else:
        details.append({"item": "revoked_access.json content correct", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_revoked}, got {revoked}"})

    # 4. 验证 reclaimed_equipment.json 内容 (20分)
    with open(os.path.join(workspace, "ops/reclaimed_equipment.json")) as f:
        reclaimed = json.load(f)
    expected_reclaimed = [
        {"employee_id": "E-0431", "asset_tag": "BG-8821", "status": "reclaimed"}
    ]
    reclaimed_set = {(r["employee_id"], r["asset_tag"], r["status"]) for r in reclaimed}
    expected_reclaimed_set = {(r["employee_id"], r["asset_tag"], r["status"]) for r in expected_reclaimed}
    if reclaimed_set == expected_reclaimed_set and len(reclaimed) == 1:
        details.append({"item": "reclaimed_equipment.json content correct", "score": 20, "max_score": 20, "passed": True, "reason": "asset BG-8821 reclaimed for E-0431"})
        score += 20
    else:
        details.append({"item": "reclaimed_equipment.json content correct", "score": 0, "max_score": 20, "passed": False, "reason": f"expected {expected_reclaimed}, got {reclaimed}"})

    # 5. 验证 handover_checklist.json 内容 (20分)
    with open(os.path.join(workspace, "ops/handover_checklist.json")) as f:
        checklist = json.load(f)
    # 必须包含字段: employee_id, employee_name, department, email, systems_revoked, equipment_reclaimed, handover_notes
    required_fields = ["employee_id", "employee_name", "department", "email", "systems_revoked", "equipment_reclaimed", "handover_notes"]
    field_ok = all(field in checklist for field in required_fields)
    if not field_ok:
        details.append({"item": "handover_checklist.json field presence", "score": 0, "max_score": 20, "passed": False, "reason": f"missing fields, expected {required_fields}, got {list(checklist.keys())}"})
    else:
        # 检查员工信息是否匹配 accounts.json
        try:
            with open(os.path.join(workspace, "data/accounts.json")) as f:
                accounts_data = json.load(f)
                accounts_list = accounts_data.get("accounts", [])
                emma_info = None
                for a in accounts_list:
                    if a["account_id"] == "E-0431":
                        emma_info = a
                        break
                if emma_info is None:
                    details.append({"item": "handover_checklist.json field presence", "score": 0, "max_score": 20, "passed": False, "reason": "E-0431 not found in accounts.json"})
                else:
                    name_ok = checklist["employee_name"] == emma_info["display_name"]
                    dept_ok = checklist["department"] == emma_info["department"]
                    email_ok = checklist["email"] == emma_info["email"]
                    # systems_revoked 应该等于 revoked_access 中的系统名列表
                    expected_systems = sorted(["Admin Portal", "CRM"])
                    actual_systems = sorted(checklist["systems_revoked"])
                    sys_ok = actual_systems == expected_systems
                    # equipment_reclaimed 应该等于 ["BG-8821"]
                    expected_equip = ["BG-8821"]
                    actual_equip = sorted(checklist["equipment_reclaimed"])
                    equip_ok = actual_equip == expected_equip
                    # handover_notes 非空字符串
                    notes_ok = isinstance(checklist["handover_notes"], str) and len(checklist["handover_notes"].strip()) > 0
                    if name_ok and dept_ok and email_ok and sys_ok and equip_ok and notes_ok:
                        details.append({"item": "handover_checklist.json content correct", "score": 20, "max_score": 20, "passed": True, "reason": "all fields match expected values"})
                        score += 20
                    else:
                        reasons = []
                        if not name_ok: reasons.append("name mismatch")
                        if not dept_ok: reasons.append("department mismatch")
                        if not email_ok: reasons.append("email mismatch")
                        if not sys_ok: reasons.append(f"systems_revoked mismatch, expected {expected_systems}, got {actual_systems}")
                        if not equip_ok: reasons.append(f"equipment_reclaimed mismatch, expected {expected_equip}, got {actual_equip}")
                        if not notes_ok: reasons.append("handover_notes empty or not string")
                        details.append({"item": "handover_checklist.json content correct", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(reasons)})
        except Exception as e:
            details.append({"item": "handover_checklist.json content correct", "score": 0, "max_score": 20, "passed": False, "reason": f"error reading accounts.json: {str(e)}"})

    _write_score(score, details)

def _write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
