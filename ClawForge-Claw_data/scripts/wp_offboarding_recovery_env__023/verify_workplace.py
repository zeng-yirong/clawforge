#!/usr/bin/env python3
"""Verify the offboarding recovery task output.

Score breakdown (total 100):
  1. ops/ directory exists                         : 5
  2. ops/offboarding_checklist.json exists         : 10
  3. ops/offboarding_checklist.json is valid JSON  : 5
  4. data/offboarding/system_access.json valid JSON: 5
  5. data/offboarding/equipment_assignments.json valid JSON: 5
  6. system_access: E-1001 Admin Portal → revoked : 10
  7. system_access: E-1001 CRM → revoked          : 10
  8. equipment_assignments: E-1001 LT-2041 → reclaimed : 15
  9. checklist contains employee_id (E-1001)       : 5
  10. checklist contains employee_name (Alice)     : 5
  11. checklist contains revoked_systems (Admin Portal, CRM) : 10
  12. checklist contains reclaimed_equipment (LT-2041)       : 10
  13. checklist status field is "completed"        : 5
  (+ bonus) no unintended changes to other employees: 5 points
"""
import json
import sys
import os
from copy import deepcopy

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total = 0

    # ---------- 1. ops/ directory ----------
    ops_dir = "ops"
    exists_ops = os.path.isdir(ops_dir)
    details.append({
        "item": "ops/ directory exists",
        "score": 5 if exists_ops else 0,
        "max_score": 5,
        "passed": exists_ops,
        "reason": "ops/ directory found" if exists_ops else "ops/ directory missing"
    })
    if exists_ops:
        total += 5

    # ---------- 2. checklist file exists ----------
    checklist_path = os.path.join(ops_dir, "offboarding_checklist.json")
    exists_checklist = os.path.isfile(checklist_path)
    details.append({
        "item": "ops/offboarding_checklist.json exists",
        "score": 10 if exists_checklist else 0,
        "max_score": 10,
        "passed": exists_checklist,
        "reason": "checklist file present" if exists_checklist else "checklist file not found"
    })
    if exists_checklist:
        total += 10

    # ---------- 3. checklist valid JSON ----------
    if exists_checklist:
        try:
            checklist = load_json(checklist_path)
            valid_checklist = True
        except (json.JSONDecodeError, Exception):
            valid_checklist = False
    else:
        valid_checklist = False

    details.append({
        "item": "ops/offboarding_checklist.json is valid JSON",
        "score": 5 if valid_checklist else 0,
        "max_score": 5,
        "passed": valid_checklist,
        "reason": "checklist is valid JSON" if valid_checklist else "checklist is not valid JSON"
    })
    if valid_checklist:
        total += 5

    # ---------- 4. system_access.json valid ----------
    sys_access_path = "data/offboarding/system_access.json"
    try:
        sys_access = load_json(sys_access_path)
        valid_sys = True
    except:
        valid_sys = False
    details.append({
        "item": "data/offboarding/system_access.json valid JSON",
        "score": 5 if valid_sys else 0,
        "max_score": 5,
        "passed": valid_sys,
        "reason": "system_access.json is valid JSON" if valid_sys else "invalid or missing"
    })
    if valid_sys:
        total += 5

    # ---------- 5. equipment_assignments.json valid ----------
    equip_path = "data/offboarding/equipment_assignments.json"
    try:
        equip = load_json(equip_path)
        valid_equip = True
    except:
        valid_equip = False
    details.append({
        "item": "data/offboarding/equipment_assignments.json valid JSON",
        "score": 5 if valid_equip else 0,
        "max_score": 5,
        "passed": valid_equip,
        "reason": "equipment_assignments.json is valid JSON" if valid_equip else "invalid or missing"
    })
    if valid_equip:
        total += 5

    # ---------- 6 & 7. system_access: E-1001 revoked for Admin Portal and CRM ----------
    admin_revoked = False
    crm_revoked = False
    if valid_sys:
        records = sys_access.get("system_access", [])
        for rec in records:
            if rec["employee_id"] == "E-1001":
                if rec["system_name"] == "Admin Portal" and rec["status"] == "revoked":
                    admin_revoked = True
                if rec["system_name"] == "CRM" and rec["status"] == "revoked":
                    crm_revoked = True
    details.append({
        "item": "system_access: E-1001 Admin Portal → revoked",
        "score": 10 if admin_revoked else 0,
        "max_score": 10,
        "passed": admin_revoked,
        "reason": "Admin Portal revoked for Alice" if admin_revoked else "Admin Portal not revoked"
    })
    if admin_revoked:
        total += 10
    details.append({
        "item": "system_access: E-1001 CRM → revoked",
        "score": 10 if crm_revoked else 0,
        "max_score": 10,
        "passed": crm_revoked,
        "reason": "CRM revoked for Alice" if crm_revoked else "CRM not revoked"
    })
    if crm_revoked:
        total += 10

    # ---------- 8. equipment: E-1001 LT-2041 reclaimed ----------
    reclaimed_device = False
    if valid_equip:
        records = equip.get("equipment_assignments", [])
        for rec in records:
            if rec["employee_id"] == "E-1001" and rec["asset_tag"] == "LT-2041" and rec["status"] == "reclaimed":
                reclaimed_device = True
                break
    details.append({
        "item": "equipment_assignments: E-1001 LT-2041 → reclaimed",
        "score": 15 if reclaimed_device else 0,
        "max_score": 15,
        "passed": reclaimed_device,
        "reason": "Device LT-2041 reclaimed" if reclaimed_device else "Device not reclaimed"
    })
    if reclaimed_device:
        total += 15

    # ---------- 9-13. checklist content checks ----------
    if valid_checklist:
        # 9. employee_id
        eid_ok = checklist.get("employee_id") == "E-1001"
        details.append({
            "item": "checklist employee_id is E-1001",
            "score": 5 if eid_ok else 0,
            "max_score": 5,
            "passed": eid_ok,
            "reason": f"employee_id = {checklist.get('employee_id')}" if eid_ok else "employee_id missing or wrong"
        })
        if eid_ok:
            total += 5

        # 10. employee_name
        ename_ok = checklist.get("employee_name") == "Alice"
        details.append({
            "item": "checklist employee_name is Alice",
            "score": 5 if ename_ok else 0,
            "max_score": 5,
            "passed": ename_ok,
            "reason": f"employee_name = {checklist.get('employee_name')}" if ename_ok else "employee_name missing or wrong"
        })
        if ename_ok:
            total += 5

        # 11. revoked_systems (order doesn't matter)
        revoked_sys = checklist.get("revoked_systems", [])
        sys_set_ok = set(revoked_sys) == {"Admin Portal", "CRM"}
        details.append({
            "item": "checklist revoked_systems contains Admin Portal and CRM",
            "score": 10 if sys_set_ok else 0,
            "max_score": 10,
            "passed": sys_set_ok,
            "reason": f"revoked_systems = {revoked_sys}" if sys_set_ok else "missing systems"
        })
        if sys_set_ok:
            total += 10

        # 12. reclaimed_equipment
        reclaimed_eq = checklist.get("reclaimed_equipment", [])
        eq_set_ok = set(reclaimed_eq) == {"LT-2041"}
        details.append({
            "item": "checklist reclaimed_equipment contains LT-2041",
            "score": 10 if eq_set_ok else 0,
            "max_score": 10,
            "passed": eq_set_ok,
            "reason": f"reclaimed_equipment = {reclaimed_eq}" if eq_set_ok else "missing equipment"
        })
        if eq_set_ok:
            total += 10

        # 13. status = 'completed'
        status_ok = checklist.get("status") == "completed"
        details.append({
            "item": "checklist status field is 'completed'",
            "score": 5 if status_ok else 0,
            "max_score": 5,
            "passed": status_ok,
            "reason": f"status = {checklist.get('status')}" if status_ok else "status missing or incorrect"
        })
        if status_ok:
            total += 5
    else:
        # If checklist invalid, all sub-checks fail
        for label, maxs in [("employee_id",5),("employee_name",5),("revoked_systems",10),("reclaimed_equipment",10),("status",5)]:
            details.append({
                "item": f"checklist {label}",
                "score": 0,
                "max_score": maxs,
                "passed": False,
                "reason": "checklist file invalid"
            })

    # ---------- Bonus: No unintended changes ----------
    # Check that other employees (E-2001, E-3001, E-4001) in system_access and equipment are untouched.
    # We compare with original snapshot embedded in this script (simulated by reading initial data).
    # Since we cannot re-run builder, we will hardcode the expected initial states for other employees.
    # This is a simplified check: just ensure no unexpected status modifications.
    # For E-2001: Admin Portal should still be active (not revoked), E-3001 CRM inactive,
    # E-4001 Admin Portal and CRM revoked unchanged.
    # For equipment: E-2001 assigned, E-3001 returned, E-4001 reclaimed.
    bonus_ok = True
    bonus_reason_parts = []
    if valid_sys:
        expected = {
            "E-2001": {"Admin Portal": "active"},
            "E-3001": {"CRM": "inactive"},
            "E-4001": {"Admin Portal": "revoked", "CRM": "revoked"}
        }
        records = sys_access.get("system_access", [])
        for rec in records:
            eid = rec["employee_id"]
            sysn = rec["system_name"]
            st = rec["status"]
            if eid in expected and sysn in expected[eid]:
                if st != expected[eid][sysn]:
                    bonus_ok = False
                    bonus_reason_parts.append(f"{eid}/{sysn} changed unexpectedly to {st}")
    if valid_equip:
        equip_expected = {
            "E-2001": {"BG-8821": "assigned"},
            "E-3001": {"LT-2041": "returned"},
            "E-4001": {"BG-8821": "reclaimed"}
        }
        records = equip.get("equipment_assignments", [])
        for rec in records:
            eid = rec["employee_id"]
            tag = rec["asset_tag"]
            st = rec["status"]
            if eid in equip_expected and tag in equip_expected[eid]:
                if st != equip_expected[eid][tag]:
                    bonus_ok = False
                    bonus_reason_parts.append(f"{eid}/{tag} changed unexpectedly to {st}")
    details.append({
        "item": "Bonus: No unintended changes to other employees",
        "score": 5 if bonus_ok else 0,
        "max_score": 5,
        "passed": bonus_ok,
        "reason": "All other records preserved" if bonus_ok else "; ".join(bonus_reason_parts)
    })
    if bonus_ok:
        total += 5

    # ---------- Final score ----------
    total = min(total, 100)  # cap at 100
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
