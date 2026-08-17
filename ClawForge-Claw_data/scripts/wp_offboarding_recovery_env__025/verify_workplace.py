import sys
import json
import os

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total = 0

    # 1. ops 目录存在 (5)
    ops_dir = "ops"
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ 目录已创建"})
        total += 5
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ 目录不存在"})

    # 2. checklist 文件存在且合法 JSON (10)
    checklist_path = "ops/handover_checklist.json"
    checklist = load_json(checklist_path)
    if checklist is None:
        details.append({"item": "handover_checklist.json 合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在或不是合法JSON"})
    else:
        if isinstance(checklist, dict):
            details.append({"item": "handover_checklist.json 合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且是合法JSON"})
            total += 10
        else:
            details.append({"item": "handover_checklist.json 合法", "score": 0, "max_score": 10, "passed": False, "reason": "JSON根节点不是字典"})

    # 3. checklist 内容关键字段 (20)
    field_score = 0
    field_reasons = []
    if checklist and isinstance(checklist, dict):
        required_fields = {
            "employee_id": "EMP001",
            "employee_name": "Jane Doe",
            "revoked_systems": ["Admin Portal", "CRM"],
            "reclaimed_assets": ["BG-8821"],
            "handover_status": "completed"
        }
        for key, expected in required_fields.items():
            if key not in checklist:
                field_reasons.append(f"缺少字段 {key}")
                continue
            value = checklist[key]
            if key in ("revoked_systems", "reclaimed_assets"):
                if not isinstance(value, list):
                    field_reasons.append(f"字段 {key} 不是列表")
                elif set(value) != set(expected):
                    field_reasons.append(f"字段 {key} 内容不匹配，期望 {expected}，实际 {value}")
                else:
                    field_score += 5 if key == "revoked_systems" else 3
            else:
                if value == expected:
                    field_score += 5 if key == "employee_id" else 3
                else:
                    field_reasons.append(f"字段 {key} 值不匹配，期望 {expected}，实际 {value}")
        # 额外加分：如果所有必需字段都存在且正确，给满20分
        if field_score >= 16:
            field_score = 20
            field_reasons = ["所有关键字段正确"]
        else:
            field_score = 0
            if not field_reasons:
                field_reasons.append("字段值不完整")
        details.append({"item": "checklist 关键字段正确", "score": field_score, "max_score": 20, "passed": field_score == 20, "reason": "; ".join(field_reasons)})
        total += field_score
    else:
        details.append({"item": "checklist 关键字段正确", "score": 0, "max_score": 20, "passed": False, "reason": "checklist 不可读取"})

    # 4. system_access.json 更新：EMP001 两个系统变为 revoked (20分)
    sa = load_json("data/offboarding/system_access.json")
    sa_score = 0
    sa_reasons = []
    if sa and "system_access" in sa:
        records = sa["system_access"]
        emp001_records = [r for r in records if r["employee_id"] == "EMP001"]
        for sys_name in ["Admin Portal", "CRM"]:
            match = [r for r in emp001_records if r["system_name"] == sys_name]
            if len(match) == 0:
                sa_reasons.append(f"EMP001 的 {sys_name} 记录不存在")
            elif match[0]["status"] == "revoked":
                sa_score += 10
                sa_reasons.append(f"EMP001 {sys_name} 已撤销")
            else:
                sa_reasons.append(f"EMP001 {sys_name} 状态为 {match[0]['status']}，期望 revoked")
    else:
        sa_reasons.append("system_access.json 不可读取")
    details.append({"item": "EMP001 系统访问已撤销", "score": sa_score, "max_score": 20, "passed": sa_score == 20, "reason": "; ".join(sa_reasons)})
    total += sa_score

    # 5. equipment_assignments.json 更新：EMP001 资产变为 reclaimed (15分)
    ea = load_json("data/offboarding/equipment_assignments.json")
    ea_score = 0
    ea_reasons = []
    if ea and "equipment_assignments" in ea:
        records = ea["equipment_assignments"]
        emp001_eq = [r for r in records if r["employee_id"] == "EMP001" and r["asset_tag"] == "BG-8821"]
        if len(emp001_eq) == 0:
            ea_reasons.append("EMP001 的 BG-8821 记录不存在")
        elif emp001_eq[0]["status"] == "reclaimed":
            ea_score = 15
            ea_reasons.append("EMP001 设备已回收")
        else:
            ea_reasons.append(f"EMP001 设备状态为 {emp001_eq[0]['status']}，期望 reclaimed")
    else:
        ea_reasons.append("equipment_assignments.json 不可读取")
    details.append({"item": "EMP001 设备已回收", "score": ea_score, "max_score": 15, "passed": ea_score == 15, "reason": "; ".join(ea_reasons)})
    total += ea_score

    # 6. 未误修改其他记录 (20分)
    other_score = 0
    other_reasons = []
    # 6a. EMP002 系统仍为 active (5)
    if sa and "system_access" in sa:
        emp002_records = [r for r in sa["system_access"] if r["employee_id"] == "EMP002"]
        if all(r["status"] == "active" for r in emp002_records):
            other_score += 5
            other_reasons.append("EMP002 系统未变")
        else:
            other_reasons.append("EMP002 系统被错误修改")
    else:
        other_reasons.append("无法检查 EMP002 系统")

    # 6b. EMP003 系统仍为 revoked (5)
    if sa and "system_access" in sa:
        emp003_records = [r for r in sa["system_access"] if r["employee_id"] == "EMP003"]
        if all(r["status"] == "revoked" for r in emp003_records):
            other_score += 5
            other_reasons.append("EMP003 系统未变")
        else:
            other_reasons.append("EMP003 系统被错误修改")
    else:
        other_reasons.append("无法检查 EMP003 系统")

    # 6c. EMP002 设备仍为 assigned (5)
    if ea and "equipment_assignments" in ea:
        emp002_eq = [r for r in ea["equipment_assignments"] if r["employee_id"] == "EMP002"]
        if all(r["status"] == "assigned" for r in emp002_eq):
            other_score += 5
            other_reasons.append("EMP002 设备未变")
        else:
            other_reasons.append("EMP002 设备被错误修改")
    else:
        other_reasons.append("无法检查 EMP002 设备")

    # 6d. EMP003 设备仍为 reclaimed (5)
    if ea and "equipment_assignments" in ea:
        emp003_eq = [r for r in ea["equipment_assignments"] if r["employee_id"] == "EMP003"]
        if all(r["status"] == "reclaimed" for r in emp003_eq):
            other_score += 5
            other_reasons.append("EMP003 设备未变")
        else:
            other_reasons.append("EMP003 设备被错误修改")
    else:
        other_reasons.append("无法检查 EMP003 设备")

    details.append({"item": "未误修改其他记录", "score": other_score, "max_score": 20, "passed": other_score == 20, "reason": "; ".join(other_reasons)})
    total += other_score

    # 7. 额外：exit_requests.json 未被修改 (5分)
    er = load_json("data/offboarding/exit_requests.json")
    er_score = 0
    if er and "exit_requests" in er:
        # 检查原始三条记录未被改动（简单检查数量）
        if len(er["exit_requests"]) == 3:
            er_score = 5
            details.append({"item": "exit_requests.json 未被修改", "score": 5, "max_score": 5, "passed": True, "reason": "请求列表保持3条"})
            total += 5
        else:
            details.append({"item": "exit_requests.json 未被修改", "score": 0, "max_score": 5, "passed": False, "reason": "记录数量变化"})
    else:
        details.append({"item": "exit_requests.json 未被修改", "score": 0, "max_score": 5, "passed": False, "reason": "文件不可读"})

    # 写入结果
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {total}/100")

if __name__ == "__main__":
    main()
