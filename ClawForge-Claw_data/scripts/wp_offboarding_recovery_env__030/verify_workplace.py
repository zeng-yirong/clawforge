import sys
import json
import os
import csv
from pathlib import Path

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    results = []
    total_score = 0

    # 1. File existence check: ops/handover_checklist.json
    checklist_path = ws / "ops" / "handover_checklist.json"
    if not checklist_path.exists():
        results.append({
            "item": "ops/handover_checklist.json 是否存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # Cannot proceed further, but score at least something
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": results}, f)
        return
    else:
        results.append({
            "item": "ops/handover_checklist.json 是否存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10

    # 2. Validate checklist JSON is valid and contains "handover_checklist" key
    try:
        checklist = load_json(checklist_path)
    except Exception as e:
        results.append({
            "item": "handover_checklist.json JSON 合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON解析失败: {e}"
        })
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f)
        return
    if "handover_checklist" not in checklist:
        results.append({
            "item": "handover_checklist.json 包含 handover_checklist 键",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 handover_checklist 键"
        })
        total_score += 0
    else:
        results.append({
            "item": "handover_checklist.json 包含 handover_checklist 键",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "键存在"
        })
        total_score += 10

    # 3. Check that checklist contains exactly the four approved employees
    #    Expected: E001, E002, E003, E005, E007 (all "approved" statuses in exit_requests.json)
    #    E002 has no systems/equipment; E007 already fully revoked/reclaimed.
    #    The agent should include all approved employees.
    checklist_entries = checklist.get("handover_checklist", [])
    expected_employees = ["E001", "E002", "E003", "E005", "E007"]
    employee_ids_in_checklist = [entry.get("employee_id") for entry in checklist_entries]
    # Check all expected are present
    missing = [eid for eid in expected_employees if eid not in employee_ids_in_checklist]
    extra = [eid for eid in employee_ids_in_checklist if eid not in expected_employees]
    if missing:
        results.append({
            "item": "handover_checklist 包含所有 approved 员工",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"缺失员工: {missing}"
        })
    elif extra:
        results.append({
            "item": "handover_checklist 包含所有 approved 员工",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"多余的员工: {extra}"
        })
    else:
        results.append({
            "item": "handover_checklist 包含所有 approved 员工",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "所有 approved 员工均已列出"
        })
        total_score += 15

    # 4. For each employee, verify revoked_systems and reclaimed_equipment
    #    We need to load the agent's modified system_access.json and equipment_assignments.json
    sys_access_path = ws / "data" / "offboarding" / "system_access.json"
    equip_path = ws / "data" / "offboarding" / "equipment_assignments.json"
    try:
        sys_data = load_json(sys_access_path)["system_access"]
        equip_data = load_json(equip_path)["equipment_assignments"]
    except Exception as e:
        results.append({
            "item": "加载修改后的 system_access/equipment_assignments",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"文件读取失败: {e}"
        })
        # cannot verify further
        with open(ws / "workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": results}, f)
        return

    # Helper to get the status for a given employee and system
    def get_sys_status(eid, system):
        for rec in sys_data:
            if rec["employee_id"] == eid and rec["system_name"] == system:
                return rec["status"]
        return None

    def get_equip_status(eid, asset_tag):
        for rec in equip_data:
            if rec["employee_id"] == eid and rec["asset_tag"] == asset_tag:
                return rec["status"]
        return None

    # Expected post-state (agent should have changed only active records):
    # E001: Admin Portal -> revoked, CRM -> revoked
    # E002: no records (do not expect anything)
    # E003: Admin Portal -> revoked, CRM stays revoked
    # E005: CRM -> revoked
    # E007: already revoked, unchanged
    expected_sys = {
        "E001": {"Admin Portal": "revoked", "CRM": "revoked"},
        "E003": {"Admin Portal": "revoked", "CRM": "revoked"},
        "E005": {"CRM": "revoked"},
        "E007": {"Admin Portal": "revoked", "CRM": "revoked"},  # unchanged
    }
    expected_equip = {
        "E001": {"BG-8821": "reclaimed"},
        "E003": {"LT-2041": "reclaimed", "BG-8821": "reclaimed"},  # BG-8821 already reclaimed
        "E005": {"BG-8821": "reclaimed"},
        "E007": {"BG-8821": "reclaimed"},  # unchanged
    }
    # Check each employee in checklist
    sys_ok = True
    equip_ok = True
    for entry in checklist_entries:
        eid = entry.get("employee_id")
        if eid not in expected_employees:
            continue  # extra employee already penalized above
        # Check revoked_systems in checklist matches post-state
        revoked_systems = entry.get("revoked_systems", [])
        # Build expected list from expected_sys (only systems that should be revoked, i.e. all active ones)
        expected_revoked = []
        for sys_name, status in expected_sys.get(eid, {}).items():
            if status == "revoked":
                expected_revoked.append(sys_name)
        # Order does not matter, use set comparison
        if set(revoked_systems) != set(expected_revoked):
            sys_ok = False
            # record reason later
        # Check reclaimed_equipment
        reclaimed = entry.get("reclaimed_equipment", [])
        expected_reclaimed = []
        for asset, status in expected_equip.get(eid, {}).items():
            if status == "reclaimed":
                expected_reclaimed.append(asset)
        if set(reclaimed) != set(expected_reclaimed):
            equip_ok = False

    sys_score = 15 if sys_ok else 0
    results.append({
        "item": "每个员工的 revoked_systems 与实际修改一致",
        "score": sys_score,
        "max_score": 15,
        "passed": sys_ok,
        "reason": "一致" if sys_ok else "不一致"
    })
    total_score += sys_score

    equip_score = 15 if equip_ok else 0
    results.append({
        "item": "每个员工的 reclaimed_equipment 与实际修改一致",
        "score": equip_score,
        "max_score": 15,
        "passed": equip_ok,
        "reason": "一致" if equip_ok else "不一致"
    })
    total_score += equip_score

    # 5. Verify that the source files (system_access.json, equipment_assignments.json) have been updated correctly
    #    Check that only the expected records changed status to revoked/reclaimed
    #    We'll check a sample: E001 Admin Portal must be "revoked", E003 Admin Portal "revoked", E005 CRM "revoked"
    #    And E007 unchanged, E006 unchanged (pending/rejected)
    status_correct = True
    # Check E001
    if get_sys_status("E001", "Admin Portal") != "revoked": status_correct = False
    if get_sys_status("E001", "CRM") != "revoked": status_correct = False
    # Check E003
    if get_sys_status("E003", "Admin Portal") != "revoked": status_correct = False
    if get_sys_status("E003", "CRM") != "revoked": status_correct = False  # was already revoked
    # Check E005
    if get_sys_status("E005", "CRM") != "revoked": status_correct = False
    # Check E006 (rejected) must still be "active"
    if get_sys_status("E006", "Admin Portal") != "active": status_correct = False
    # Check equipment
    if get_equip_status("E001", "BG-8821") != "reclaimed": status_correct = False
    if get_equip_status("E003", "LT-2041") != "reclaimed": status_correct = False
    if get_equip_status("E003", "BG-8821") != "reclaimed": status_correct = False
    if get_equip_status("E005", "BG-8821") != "reclaimed": status_correct = False
    if get_equip_status("E006", "LT-2041") != "assigned": status_correct = False  # unchanged
    if get_equip_status("E007", "BG-8821") != "reclaimed": status_correct = False  # unchanged

    source_score = 20 if status_correct else 0
    results.append({
        "item": "源文件 (system_access.json / equipment_assignments.json) 修改正确",
        "score": source_score,
        "max_score": 20,
        "passed": status_correct,
        "reason": "正确" if status_correct else "存在错误修改"
    })
    total_score += source_score

    # 6. Bonus: Ensure no extra fields or missing required keys in checklist entries
    format_ok = True
    for entry in checklist_entries:
        if not isinstance(entry, dict):
            format_ok = False
            break
        if not all(k in entry for k in ("employee_id", "employee_name", "revoked_systems", "reclaimed_equipment")):
            format_ok = False
            break
        if not isinstance(entry["revoked_systems"], list) or not isinstance(entry["reclaimed_equipment"], list):
            format_ok = False
            break
    format_score = 5 if format_ok else 0
    results.append({
        "item": "handover_checklist 条目格式正确（含必需字段且类型正确）",
        "score": format_score,
        "max_score": 5,
        "passed": format_ok,
        "reason": "格式正确" if format_ok else "格式错误或缺少字段"
    })
    total_score += format_score

    # Write score
    final_score = min(total_score, 100)
    with open(ws / "workplace_score.json", "w") as f:
        json.dump({"total_score": final_score, "details": results}, f, indent=2)

if __name__ == "__main__":
    main()
