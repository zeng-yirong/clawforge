import sys
import os
import json
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = pathlib.Path(workspace)

    # 评分项定义
    details = []
    total_score = 0
    total_max = 0

    def add_check(item, score, max_score, passed, reason):
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # ---------- 1. 目录结构检查 (10分) ----------
    dirs_ok = True
    for d in ["data/offboarding", "ops"]:
        p = ws / d
        if not p.is_dir():
            dirs_ok = False
            break
    if dirs_ok:
        total_score += add_check("Directory structure exists", 10, 10, True, "data/offboarding/ and ops/ present")
    else:
        total_score += add_check("Directory structure exists", 0, 10, False, "Missing required directories")

    # ---------- 2. 关键源文件格式合法 (10分) ----------
    files_json = [
        "data/accounts.json",
        "data/contacts.json",
        "data/offboarding/exit_requests.json",
        "data/offboarding/system_access.json",
        "data/offboarding/equipment_assignments.json"
    ]
    valid_json = True
    for f in files_json:
        fp = ws / f
        if not fp.exists():
            valid_json = False
            break
        try:
            json.loads(fp.read_text())
        except:
            valid_json = False
            break
    if valid_json:
        total_score += add_check("Source JSON files valid", 10, 10, True, "All source JSON files exist and parse correctly")
    else:
        total_score += add_check("Source JSON files valid", 0, 10, False, "Some source files missing or invalid JSON")

    # ---------- 3. system_access 中 Carol 的记录已 revoke (30分) ----------
    sa_path = ws / "data/offboarding/system_access.json"
    if sa_path.exists():
        try:
            sa = json.loads(sa_path.read_text())
            access_list = sa.get("system_access", []) if isinstance(sa, dict) else sa
            carol_entries = [e for e in access_list if e.get("employee_id") == "E-1024"]
            # 应该有两条
            carol_revoked = all(e.get("status") == "revoked" for e in carol_entries)
            # 其他员工不应被改动 (保持 active)
            other_entries = [e for e in access_list if e.get("employee_id") != "E-1024"]
            other_unchanged = all(e.get("status") == "active" for e in other_entries)

            if carol_revoked and other_unchanged and len(carol_entries) == 2:
                total_score += add_check("System access correctly revoked for Carol", 30, 30, True,
                                         "Both Admin Portal and CRM revoked, others unchanged")
            elif carol_revoked and not other_unchanged:
                total_score += add_check("System access correctly revoked for Carol", 15, 30, False,
                                         "Carol's entries revoked but other employees were modified")
            else:
                total_score += add_check("System access correctly revoked for Carol", 0, 30, False,
                                         "Carol's entries not fully revoked")
        except:
            total_score += add_check("System access correctly revoked for Carol", 0, 30, False, "File parse error")
    else:
        total_score += add_check("System access correctly revoked for Carol", 0, 30, False, "File missing")

    # ---------- 4. equipment_assignments 中 Carol 的设备状态改为 reclaimed (20分) ----------
    eq_path = ws / "data/offboarding/equipment_assignments.json"
    if eq_path.exists():
        try:
            eq = json.loads(eq_path.read_text())
            eq_list = eq.get("equipment_assignments", []) if isinstance(eq, dict) else eq
            carol_eq = [e for e in eq_list if e.get("employee_id") == "E-1024"]
            # 应该只有一条 asset_tag "LT-2041"
            carol_reclaimed = all(e.get("status") == "reclaimed" for e in carol_eq)
            other_eq = [e for e in eq_list if e.get("employee_id") != "E-1024"]
            other_unchanged = all(e.get("status") == "assigned" for e in other_eq)

            if carol_reclaimed and other_unchanged and len(carol_eq) == 1:
                total_score += add_check("Equipment reclaimed for Carol", 20, 20, True,
                                         "LT-2041 reclaimed, other equipment unchanged")
            elif carol_reclaimed and not other_unchanged:
                total_score += add_check("Equipment reclaimed for Carol", 10, 20, False,
                                         "Carol's equipment reclaimed but others modified")
            else:
                total_score += add_check("Equipment reclaimed for Carol", 0, 20, False,
                                         "Carol's equipment not reclaimed")
        except:
            total_score += add_check("Equipment reclaimed for Carol", 0, 20, False, "File parse error")
    else:
        total_score += add_check("Equipment reclaimed for Carol", 0, 20, False, "File missing")

    # ---------- 5. handover_checklist.json 验证 (30分) ----------
    checklist_path = ws / "ops/handover_checklist.json"
    if not checklist_path.exists():
        total_score += add_check("Handover checklist exists", 0, 30, False, "ops/handover_checklist.json missing")
    else:
        try:
            hc = json.loads(checklist_path.read_text())
            # 必须包含字段
            required_fields = ["employee_id", "employee_name", "department", "email",
                               "systems_revoked", "equipment_reclaimed", "status"]
            missing = [f for f in required_fields if f not in hc]
            if missing:
                total_score += add_check("Handover checklist fields", 0, 30, False,
                                         f"Missing fields: {missing}")
            else:
                # 字段数值正确性
                field_checks = [
                    (hc["employee_id"] == "E-1024", "employee_id"),
                    (hc["employee_name"] == "Carol Danvers", "employee_name"),
                    (hc["department"] == "Engineering", "department"),
                    (hc["email"] == "carol.danvers@example.com", "email"),
                    (sorted(hc["systems_revoked"]) == sorted(["Admin Portal", "CRM"]), "systems_revoked"),
                    (sorted(hc["equipment_reclaimed"]) == sorted(["LT-2041"]), "equipment_reclaimed"),
                    (hc["status"] == "completed", "status (must be 'completed')")
                ]
                passed_all = True
                for cond, name in field_checks:
                    if not cond:
                        passed_all = False
                        # 给部分分数？这里我们选择完全正确30，否则0（因为核心信息必须精确）
                        break
                if passed_all:
                    total_score += add_check("Handover checklist content", 30, 30, True,
                                             "All fields and values correct")
                else:
                    total_score += add_check("Handover checklist content", 0, 30, False,
                                             "One or more field values incorrect")
        except json.JSONDecodeError:
            total_score += add_check("Handover checklist content", 0, 30, False, "Invalid JSON")

    # 最终总分，确保 0-100
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    output_path = ws / "workplace_score.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    # 打印结果方便调试
    print(f"Total score: {total_score}/100")
    for d in details:
        print(f"  {d['item']}: {d['score']}/{d['max_score']} {'PASS' if d['passed'] else 'FAIL'} - {d['reason']}")

if __name__ == "__main__":
    main()
