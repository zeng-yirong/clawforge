import sys
import os
import json
import csv

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops目录已创建"})
        total_score += 5
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops目录不存在"})

    # 2. 检查 handover_checklist.json 文件存在 (5分)
    checklist_path = os.path.join(ops_dir, "handover_checklist.json")
    if os.path.isfile(checklist_path):
        details.append({"item": "handover_checklist.json文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
    else:
        details.append({"item": "handover_checklist.json文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "文件不存在"})
        # 如果文件不存在，后续无法检查，直接返回
        score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    # 3. 文件内容是否为合法 JSON (5分)
    try:
        with open(checklist_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 5, "max_score": 5, "passed": True, "reason": "解析成功"})
        total_score += 5
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 5, "passed": False, "reason": f"解析失败: {e}"})
        return {"total_score": total_score, "details": details}

    # 4. 检查清单中是否只包含已批准员工 (10分)
    # 期望 employee_ids: E001, E002 (E005 虽然批准但系统中无任何记录，应该也被包含？按业务逻辑应包含，因为存在退出请求)
    # 根据 prompt: "注意只处理已经批准的人"——E005 也是已批准，即使无访问/设备记录，也应出现在清单中（处理为空）
    # 为了简化，我们设计 E005 在 exit_requests 中已批准，但 system_access 和 equipment 均无记录，所以清单应包含 E005，但访问和设备状态应为 completed（因为无记录可撤销，但业务认为已完成）
    expected_approved = ["E001", "E002", "E005"]  # 注意 E005
    if isinstance(data, dict):
        # 假设清单是一个列表或字典包装
        if "checklist" in data:
            checklist = data["checklist"]
        elif isinstance(data, list):
            checklist = data
        else:
            checklist = []
    else:
        checklist = []

    approved_ids_found = [item.get("employee_id") for item in checklist if isinstance(item, dict)]
    # 检查是否包含所有预期员工
    missing = [eid for eid in expected_approved if eid not in approved_ids_found]
    extra = [eid for eid in approved_ids_found if eid not in expected_approved]
    if not missing and not extra:
        details.append({"item": "清单员工集合正确", "score": 10, "max_score": 10, "passed": True, "reason": "只包含已批准员工，无遗漏无多余"})
        total_score += 10
    else:
        reason = f"遗漏: {missing}，多余: {extra}" if missing or extra else ""
        details.append({"item": "清单员工集合正确", "score": 0, "max_score": 10, "passed": False, "reason": reason})

    # 5. 检查每个员工的字段完整性及状态 (每个员工15分, 共45分)
    # 预期字段: employee_id, employee_name, access_revocation_status, equipment_reclamation_status
    # 期望状态都为 "completed"
    employee_scores = {"E001": 15, "E002": 15, "E005": 15}
    for item in checklist:
        eid = item.get("employee_id")
        if eid not in employee_scores:
            continue
        item_score = 0
        reasons = []
        # 检查必要字段存在
        fields = ["employee_id", "employee_name", "access_revocation_status", "equipment_reclamation_status"]
        missing_fields = [f for f in fields if f not in item]
        if missing_fields:
            reasons.append(f"缺少字段: {missing_fields}")
        else:
            # 检查字段值
            if item["access_revocation_status"] != "completed":
                reasons.append(f"access_revocation_status应为completed, 实际为{item['access_revocation_status']}")
            if item["equipment_reclamation_status"] != "completed":
                reasons.append(f"equipment_reclamation_status应为completed, 实际为{item['equipment_reclamation_status']}")
            if item["employee_id"] == eid and item["employee_name"]:
                pass
            else:
                reasons.append("employee_id或employee_name不正确")
        if not reasons:
            item_score = 15
            total_score += 15
            details.append({"item": f"员工{eid}字段正确", "score": 15, "max_score": 15, "passed": True, "reason": "所有字段和值正确"})
        else:
            details.append({"item": f"员工{eid}字段正确", "score": 0, "max_score": 15, "passed": False, "reason": "; ".join(reasons)})
        employee_scores.pop(eid, None)

    # 对于未出现的预期员工，扣分
    for eid in employee_scores:
        details.append({"item": f"员工{eid}出现在清单中", "score": 0, "max_score": 15, "passed": False, "reason": f"未找到{eid}的记录"})

    # 6. 检查源文件是否被正确修改（即 system_access 和 equipment_assignments 中对应员工的状态已变更）(20分)
    # 需要打开原始数据检查（注意，agent 可能覆盖了原文件，我们假设它们已被修改）
    # 我们只关心已批准员工的状态，且未批准员工状态不应该被改变
    sys_access_path = os.path.join(workspace, "data/offboarding/system_access.json")
    equip_path = os.path.join(workspace, "data/offboarding/equipment_assignments.json")
    access_correct = True
    equip_correct = True
    access_reason = ""
    equip_reason = ""
    try:
        with open(sys_access_path) as f:
            sa_data = json.load(f)
        sa_list = sa_data.get("system_access", sa_data) if isinstance(sa_data, dict) else sa_data
        for rec in sa_list:
            eid = rec.get("employee_id")
            if eid in ["E001", "E002"]:
                if rec.get("status") != "revoked":
                    access_correct = False
                    access_reason += f"{eid} 在 system_access 中状态不是 revoked; "
            elif eid in ["E003", "E004", "E005"]:  # E005 无记录，忽略
                if rec.get("status") != "active":  # 原始是active，不应被修改
                    access_correct = False
                    access_reason += f"{eid} 未批准但状态被修改; "
    except Exception as e:
        access_correct = False
        access_reason = f"读取system_access.json失败: {e}"

    try:
        with open(equip_path) as f:
            eq_data = json.load(f)
        eq_list = eq_data.get("equipment_assignments", eq_data) if isinstance(eq_data, dict) else eq_data
        for rec in eq_list:
            eid = rec.get("employee_id")
            if eid in ["E001", "E002"]:
                if rec.get("status") != "reclaimed":
                    equip_correct = False
                    equip_reason += f"{eid} 在 equipment_assignments 中状态不是 reclaimed; "
            elif eid in ["E003", "E004"]:
                if rec.get("status") in ["assigned"]:  # E003 原始assigned，不应修改；E004原始returned，也不应修改
                    equip_correct = False
                    equip_reason += f"{eid} 未批准但状态被修改; "
    except Exception as e:
        equip_correct = False
        equip_reason = f"读取equipment_assignments.json失败: {e}"

    if access_correct:
        details.append({"item": "系统访问状态正确撤销", "score": 10, "max_score": 10, "passed": True, "reason": "已批准员工访问已 revoked，未批准未修改"})
        total_score += 10
    else:
        details.append({"item": "系统访问状态正确撤销", "score": 0, "max_score": 10, "passed": False, "reason": access_reason or "检查失败"})
    if equip_correct:
        details.append({"item": "设备回收状态正确更新", "score": 10, "max_score": 10, "passed": True, "reason": "已批准员工设备已 reclaimed，未批准未修改"})
        total_score += 10
    else:
        details.append({"item": "设备回收状态正确更新", "score": 0, "max_score": 10, "passed": False, "reason": equip_reason or "检查失败"})

    # 总分计算（已累计）
    final_score = min(total_score, 100)
    return {"total_score": final_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}/100")
