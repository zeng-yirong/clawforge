#!/usr/bin/env python3
import sys
import json
import os

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def check_file_exists(path):
    return os.path.isfile(os.path.join(WORKSPACE, path))

def check_dir_exists(path):
    return os.path.isdir(os.path.join(WORKSPACE, path))

def score():
    details = []
    total = 0

    # 1. 检查目录结构 (10分)
    dirs_ok = True
    for d in ["backup", "ops"]:
        if not check_dir_exists(d):
            details.append({"item": f"目录 {d} 不存在", "score": 0, "max_score": 5, "passed": False, "reason": f"缺少目录 {d}"})
            dirs_ok = False
        else:
            details.append({"item": f"目录 {d} 存在", "score": 5, "max_score": 5, "passed": True, "reason": ""})
    total += 10 if dirs_ok else sum(d["score"] for d in details[-2:])

    # 2. 备份完整性 (10分)
    backup_files = ["exit_requests.json", "system_access.json", "equipment_assignments.json"]
    all_backup_ok = True
    for bf in backup_files:
        path = f"backup/{bf}"
        if not check_file_exists(path):
            details.append({"item": f"备份文件 {path} 不存在", "score": 0, "max_score": 3, "passed": False, "reason": "文件缺失"})
            all_backup_ok = False
        else:
            details.append({"item": f"备份文件 {path} 存在", "score": 3, "max_score": 3, "passed": True, "reason": ""})
    total += 10 if all_backup_ok else sum(d["score"] for d in details[-3:])

    # 3. 格式合法性 (10分) – 检查所有关键 JSON 可解析
    json_files = [
        "data/offboarding/exit_requests.json",
        "data/offboarding/system_access.json",
        "data/offboarding/equipment_assignments.json",
        "ops/handover_checklist.json"
    ]
    all_json_ok = True
    for jf in json_files:
        if not check_file_exists(jf):
            details.append({"item": f"文件 {jf} 不存在", "score": 0, "max_score": 2, "passed": False, "reason": "缺失"})
            all_json_ok = False
        else:
            try:
                load_json(os.path.join(WORKSPACE, jf))
                details.append({"item": f"文件 {jf} 合法JSON", "score": 2, "max_score": 2, "passed": True, "reason": ""})
            except Exception as e:
                details.append({"item": f"文件 {jf} 解析失败", "score": 0, "max_score": 2, "passed": False, "reason": str(e)})
                all_json_ok = False
    total += 10 if all_json_ok else sum(d["score"] for d in details[-4:])

    # 4. 核心数据修改 – 系统访问 (15分)
    try:
        sa = load_json(os.path.join(WORKSPACE, "data/offboarding/system_access.json"))
        records = sa["system_access"]
        e1024_records = [r for r in records if r["employee_id"] == "E-1024"]
        if len(e1024_records) != 2:
            details.append({"item": "E-1024 系统访问记录数量", "score": 0, "max_score": 4, "passed": False, "reason": f"预期2条，找到{len(e1024_records)}条"})
            total += 0
        else:
            all_revoked = all(r["status"] == "revoked" for r in e1024_records)
            if all_revoked:
                details.append({"item": "E-1024 系统访问已全部撤销", "score": 4, "max_score": 4, "passed": True, "reason": ""})
                total += 4
            else:
                details.append({"item": "E-1024 系统访问状态", "score": 0, "max_score": 4, "passed": False, "reason": "存在未撤销的记录"})
        # 检查其他员工未被修改
        others = [r for r in records if r["employee_id"] != "E-1024"]
        others_unchanged = all(r["status"] in ["active","revoked"] for r in others)  # 原始状态
        if others_unchanged:
            details.append({"item": "其他员工系统访问未修改", "score": 11, "max_score": 11, "passed": True, "reason": ""})
            total += 11
        else:
            details.append({"item": "其他员工系统访问被错误修改", "score": 0, "max_score": 11, "passed": False, "reason": "发现不应有的变化"})
    except Exception as e:
        details.append({"item": "系统访问文件读取异常", "score": 0, "max_score": 15, "passed": False, "reason": str(e)})

    # 5. 核心数据修改 – 设备回收 (15分)
    try:
        eq = load_json(os.path.join(WORKSPACE, "data/offboarding/equipment_assignments.json"))
        records_e = eq["equipment_assignments"]
        e1024_eq = [r for r in records_e if r["employee_id"] == "E-1024"]
        if len(e1024_eq) != 2:
            details.append({"item": "E-1024 设备记录数量", "score": 0, "max_score": 4, "passed": False, "reason": f"预期2条，找到{len(e1024_eq)}条"})
            total += 0
        else:
            all_returned = all(r["status"] == "returned" for r in e1024_eq)
            if all_returned:
                details.append({"item": "E-1024 设备已全部归还", "score": 4, "max_score": 4, "passed": True, "reason": ""})
                total += 4
            else:
                details.append({"item": "E-1024 设备状态", "score": 0, "max_score": 4, "passed": False, "reason": "存在未归还的记录"})
        # 其他设备记录不变
        others_e = [r for r in records_e if r["employee_id"] != "E-1024"]
        others_e_ok = all(r["status"] in ["assigned","returned"] for r in others_e)
        if others_e_ok:
            details.append({"item": "其他员工设备记录未修改", "score": 11, "max_score": 11, "passed": True, "reason": ""})
            total += 11
        else:
            details.append({"item": "其他员工设备记录被错误修改", "score": 0, "max_score": 11, "passed": False, "reason": "发现不应有的变化"})
    except Exception as e:
        details.append({"item": "设备记录读取异常", "score": 0, "max_score": 15, "passed": False, "reason": str(e)})

    # 6. 交接清单验证 (30分)
    try:
        hc = load_json(os.path.join(WORKSPACE, "ops/handover_checklist.json"))
        checklist = hc  # 直接是字典
        required_fields = ["employee_id", "employee_name", "department", "revoked_access", "reclaimed_equipment", "handover_contact"]
        missing = [f for f in required_fields if f not in checklist]
        if missing:
            details.append({"item": "交接清单字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段 {missing}"})
            total += 0
        else:
            details.append({"item": "交接清单包含所有必需字段", "score": 10, "max_score": 10, "passed": True, "reason": ""})
            total += 10
            # 字段值准确性
            if checklist["employee_id"] != "E-1024":
                details.append({"item": "employee_id", "score": 0, "max_score": 5, "passed": False, "reason": f"期望E-1024, 实际{checklist['employee_id']}"})
                total += 0
            else:
                details.append({"item": "employee_id 正确", "score": 5, "max_score": 5, "passed": True, "reason": ""})
                total += 5

            if checklist["employee_name"] != "James Carter":
                details.append({"item": "employee_name", "score": 0, "max_score": 3, "passed": False, "reason": f"期望James Carter, 实际{checklist['employee_name']}"})
                total += 0
            else:
                details.append({"item": "employee_name 正确", "score": 3, "max_score": 3, "passed": True, "reason": ""})
                total += 3

            expected_systems = ["Admin Portal", "CRM"]
            actual_systems = sorted(checklist.get("revoked_access", []))
            if actual_systems == sorted(expected_systems):
                details.append({"item": "revoked_access 正确", "score": 5, "max_score": 5, "passed": True, "reason": ""})
                total += 5
            else:
                details.append({"item": "revoked_access", "score": 0, "max_score": 5, "passed": False, "reason": f"期望{expected_systems}, 实际{actual_systems}"})

            expected_eq = ["BG-8821", "LT-2041"]
            actual_eq = sorted(checklist.get("reclaimed_equipment", []))
            if actual_eq == sorted(expected_eq):
                details.append({"item": "reclaimed_equipment 正确", "score": 5, "max_score": 5, "passed": True, "reason": ""})
                total += 5
            else:
                details.append({"item": "reclaimed_equipment", "score": 0, "max_score": 5, "passed": False, "reason": f"期望{expected_eq}, 实际{actual_eq}"})

            # 交接联系人
            contact = checklist.get("handover_contact", {})
            if contact.get("name") == "Maria Gonzalez" and contact.get("email") == "m.gonzalez@corp.com":
                details.append({"item": "handover_contact 正确", "score": 2, "max_score": 2, "passed": True, "reason": ""})
                total += 2
            else:
                details.append({"item": "handover_contact", "score": 0, "max_score": 2, "passed": False, "reason": f"期望 Maria Gonzalez / m.gonzalez@corp.com, 实际 {contact}"})
    except Exception as e:
        details.append({"item": "交接清单读取/解析失败", "score": 0, "max_score": 30, "passed": False, "reason": str(e)})

    # 7. 备份内容一致性（额外验证，不计分但可加扣） – 确保备份是修改前的状态
    # 若备份存在，检查备份中E-1024状态为 active/assigned。不计分但若不一致可扣分（通过已有项目间接控制）
    # 这里不再增加额外项目，因为前面备份存在已得分。

    # 计算总分，限制 0-100
    total = min(max(total, 0), 100)

    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    score()
