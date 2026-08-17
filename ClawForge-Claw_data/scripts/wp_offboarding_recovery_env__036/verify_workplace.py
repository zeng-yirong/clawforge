import sys
import os
import json

def verify(workspace):
    results = []
    total_score = 0
    max_total = 100

    # ---------- 辅助函数 ----------
    def add_detail(item, score, max_score, passed, reason):
        results.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. 检查必要目录是否存在 (5分)
    dirs = [
        "data/offboarding",
        "ops"
    ]
    dir_score = 0
    for d in dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            dir_score += 2
    add_detail("Required directories exist", dir_score, 5, dir_score == 5,
               f"Found directories: {[d for d in dirs if os.path.isdir(os.path.join(workspace, d))]}")

    # 2. 检查 system_access.json 和 equipment_assignments.json 是否被正确修改 (40分)
    #   2a. system_access 中小王所有记录 status 为 "revoked" (20分)
    sa_path = os.path.join(workspace, "data/offboarding/system_access.json")
    try:
        with open(sa_path) as f:
            sa_data = json.load(f)
        sa_list = sa_data.get("system_access", [])
        wang_records = [r for r in sa_list if r["employee_id"] == "E-2024-042"]
        if not wang_records:
            add_detail("Wang Wei's system access records exist", 0, 20, False,
                       "No records found for employee E-2024-042")
        else:
            all_revoked = all(r["status"] == "revoked" for r in wang_records)
            add_detail("All of Wang Wei's system accesses are revoked",
                       20 if all_revoked else 0, 20, all_revoked,
                       f"Records: {wang_records}")
    except Exception as e:
        add_detail("Read system_access.json", 0, 20, False, f"Error: {e}")

    #   2b. equipment_assignments 中小王设备 status 为 "reclaimed" (20分)
    ea_path = os.path.join(workspace, "data/offboarding/equipment_assignments.json")
    try:
        with open(ea_path) as f:
            ea_data = json.load(f)
        ea_list = ea_data.get("equipment_assignments", [])
        wang_equip = [e for e in ea_list if e["employee_id"] == "E-2024-042"]
        if not wang_equip:
            add_detail("Wang Wei's equipment record exists", 0, 20, False,
                       "No equipment record for E-2024-042")
        else:
            all_reclaimed = all(e["status"] == "reclaimed" for e in wang_equip)
            add_detail("Wang Wei's equipment is reclaimed",
                       20 if all_reclaimed else 0, 20, all_reclaimed,
                       f"Records: {wang_equip}")
    except Exception as e:
        add_detail("Read equipment_assignments.json", 0, 20, False, f"Error: {e}")

    # 3. 检查 ops/handover_checklist.json (55分)
    chk_path = os.path.join(workspace, "ops/handover_checklist.json")
    if not os.path.isfile(chk_path):
        add_detail("handover_checklist.json exists", 0, 55, False,
                   "File not found at ops/handover_checklist.json")
    else:
        try:
            with open(chk_path) as f:
                chk = json.load(f)
            checklist_items = [
                ("employee_id present and correct", 10,
                 chk.get("employee_id") == "E-2024-042"),
                ("employee_name present and correct", 5,
                 chk.get("employee_name") == "Wang Wei"),
                ("revoked_systems list contains expected systems", 15,
                 isinstance(chk.get("revoked_systems"), list) and
                 set(chk["revoked_systems"]) == {"Admin Portal", "CRM"}),
                ("reclaimed_equipment list contains LT-2041", 10,
                 isinstance(chk.get("reclaimed_equipment"), list) and
                 "LT-2041" in chk["reclaimed_equipment"]),
                ("checklist_items present and non-empty", 5,
                 isinstance(chk.get("checklist_items"), list) and
                 len(chk["checklist_items"]) > 0),
                ("No extra unexpected top-level fields", 10,
                 set(chk.keys()) <= {"employee_id", "employee_name",
                                      "revoked_systems", "reclaimed_equipment",
                                      "checklist_items"})
            ]
            for desc, score, passed in checklist_items:
                add_detail(desc, score if passed else 0, score, passed,
                           "OK" if passed else f"Expected condition not met")
        except json.JSONDecodeError:
            add_detail("handover_checklist.json is valid JSON", 0, 55, False,
                       "File is not valid JSON")
        except Exception as e:
            add_detail("Parse handover_checklist.json", 0, 55, False,
                       f"Error: {e}")

    # 计算总分
    total_score = sum(d["score"] for d in results)
    final = {
        "total_score": total_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    print(f"Score written: {total_score}/{max_total}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
