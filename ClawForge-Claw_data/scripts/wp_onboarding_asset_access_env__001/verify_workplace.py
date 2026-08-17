import json
import os
import sys

def verify(workspace: str) -> dict:
    details = []
    total = 0

    # 1. 检查目标文件是否存在 (10分)
    target_path = os.path.join(workspace, "onboarding", "processed_onboarding.json")
    if os.path.isfile(target_path):
        details.append({"item": "目标文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件路径正确"})
        total += 10
    else:
        details.append({"item": "目标文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 onboarding/processed_onboarding.json"})
        # 后续检查跳过
        return {"total_score": total, "details": details}

    # 2. 文件是否为合法 JSON (10分)
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        return {"total_score": total, "details": details}

    # 3. 包含 successful 和 failed 字段 (10分)
    if "successful" in data and "failed" in data:
        details.append({"item": "顶层结构包含 successful 和 failed", "score": 10, "max_score": 10, "passed": True, "reason": "结构完整"})
        total += 10
    else:
        details.append({"item": "顶层结构", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 successful 或 failed 字段"})
        return {"total_score": total, "details": details}

    # 4. successful 列表长度应为1，且内容正确 (30分)
    succ = data["successful"]
    if len(succ) == 1:
        emp = succ[0]
        # 检查 employee_id, email, assigned_systems, equipment_tag, welcome_message
        score_item = 30
        sub_score = 0
        reasons = []
        if emp.get("employee_id") == "EMP1003":
            sub_score += 10
        else:
            reasons.append("employee_id 应为 EMP1003")
        if emp.get("email") == "frank.zhang@company.com":
            sub_score += 5
        else:
            reasons.append("email 错误")
        # assigned_systems 应为 Engineering 对应的权限包 ["gitlab", "jenkins", "aws-dev"]
        expected_systems = {"gitlab", "jenkins", "aws-dev"}
        actual_systems = set(emp.get("assigned_systems", []))
        if actual_systems == expected_systems:
            sub_score += 10
        else:
            reasons.append(f"assigned_systems 应为 {expected_systems}")
        # equipment_tag 应为 LT-001 (唯一可用笔记本)
        if emp.get("equipment_tag") == "LT-001":
            sub_score += 5
        else:
            reasons.append("equipment_tag 应为 LT-001")
        # welcome_message 非空（字符串）即可
        if isinstance(emp.get("welcome_message"), str) and len(emp["welcome_message"]) > 0:
            sub_score += 0  # 不给分，但如果有问题则扣分？
        else:
            reasons.append("welcome_message 缺失或无效")
        # 实际得分
        passed = sub_score >= 20  # 至少20分才算核心通过？但为了细粒度，直接给sub_score
        details.append({"item": "successful 员工详情", "score": sub_score, "max_score": 30, "passed": sub_score == 30, "reason": "; ".join(reasons) if reasons else "完全正确"})
        total += sub_score
    else:
        details.append({"item": "successful 员工详情", "score": 0, "max_score": 30, "passed": False, "reason": f"成功员工数为 {len(succ)}，应为1"})

    # 5. failed 列表长度应为2，且原因合理 (20分)
    fail = data["failed"]
    if len(fail) == 2:
        # 检查两个失败记录的 employee_id 分别为 EMP1001 和 EMP1002（或 EMP1004, EMP1005? 注意：只有 signed 状态才考虑，所以 EMP1004, EMP1005 是 pending，也应该出现在 failed 中？按逻辑，pending 不应该出现在“处理”流程中，因为合同未签，根本不应该考虑。但 prompt 说“只处理那些合同已经签署、邮箱没有被占用、并且库存里有可用设备的员工”，所以对于未签署的合同，可能不需要列入 failed？但为了全面，agent 可能选择把未签署的员工也放入 failed 列表。我们需要确定唯一答案。最佳设计：successful 只放成功的一个，failed 放两个 signed 但失败的原因（EMP1001邮箱冲突，EMP1002设备不足）。pending 的两个不应该出现在任何列表中，因为根本不在处理范围内。这样答案唯一。但 agent 可能会错误地把 pending 也放进 failed。因此验证时应该严格：failed 列表应该只有两个 signed 失败的，不能有 pending。
        # 我们期望 failed 包含 EMP1001 和 EMP1002，且原因分别匹配 "邮箱冲突" 和 "设备不足"。
        ids = [e.get("employee_id") for e in fail]
        if sorted(ids) == ["EMP1001", "EMP1002"]:
            sub_score = 10
        else:
            sub_score = 0
        # 检查原因（关键词）
        reasons_field = [e.get("reason", "") for e in fail]
        # EMP1001 原因包含 "邮箱" 或 "已存在"；EMP1002 原因包含 "设备" 或 "库存"
        # 简单判断
        if any("邮箱" in r or "冲突" in r for r in reasons_field):
            sub_score += 5
        if any("设备" in r or "库存" in r for r in reasons_field):
            sub_score += 5
        details.append({"item": "failed 员工详情", "score": sub_score, "max_score": 20, "passed": sub_score == 20, "reason": f"IDs: {ids}, reasons: {reasons_field}"})
        total += sub_score
    else:
        details.append({"item": "failed 员工详情", "score": 0, "max_score": 20, "passed": False, "reason": f"失败员工数为 {len(fail)}，应为2"})

    # 6. 检查是否有多余的字段/员工（例如不准出现 pending 员工） (10分)
    extra_items = []
    for emp in data.get("successful", []):
        if emp.get("employee_id") not in ["EMP1003"]:
            extra_items.append(emp.get("employee_id"))
    for emp in data.get("failed", []):
        if emp.get("employee_id") not in ["EMP1001", "EMP1002"]:
            extra_items.append(emp.get("employee_id"))
    if not extra_items:
        details.append({"item": "无多余员工", "score": 10, "max_score": 10, "passed": True, "reason": "未出现不应处理的员工"})
        total += 10
    else:
        details.append({"item": "无多余员工", "score": 0, "max_score": 10, "passed": False, "reason": f"发现了不应出现的员工 {extra_items}"})

    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入结果文件
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
