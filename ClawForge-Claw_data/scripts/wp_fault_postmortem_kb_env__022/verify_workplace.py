import sys
import os
import json

def verify_workspace(workspace):
    details = []
    total_score = 0

    # 1. 检查必要的目录结构 (10分)
    dirs = ["ops", "data", "data/faults", "data/attachments"]
    dir_score = 10
    dir_passed = True
    for d in dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dir_passed = False
            details.append({"item": f"目录 {d} 存在", "score": 0, "max_score": 10,
                            "passed": False, "reason": f"缺少目录 {d}"})
            break
    if dir_passed:
        total_score += 10
        details.append({"item": "必要目录结构", "score": 10, "max_score": 10,
                        "passed": True, "reason": "目录齐全"})

    # 2. 检查目标文件 ops/postmortem.json 是否存在 (10分)
    postmortem_path = os.path.join(workspace, "ops", "postmortem.json")
    if not os.path.isfile(postmortem_path):
        total_score = 0  # 文件缺失直接0分？但按梯度给0，后续不执行
        total_score = 0
        details.append({"item": "ops/postmortem.json 文件", "score": 0, "max_score": 10,
                        "passed": False, "reason": "文件不存在"})
        # 但为了完整性，继续添加其他项分数为0
        for item in ["JSON格式", "fault_id字段", "severity字段", "root_cause字段", "repair_plan字段", "内容准确性"]:
            details.append({"item": item, "score": 0, "max_score": 10, "passed": False, "reason": "因文件缺失跳过"})
        # 写入结果
        result = {"total_score": 0, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    total_score += 10
    details.append({"item": "ops/postmortem.json 文件", "score": 10, "max_score": 10,
                    "passed": True, "reason": "文件存在"})

    # 3. 检查 JSON 格式合法性 (10分)
    try:
        with open(postmortem_path, "r") as f:
            data = json.load(f)
        total_score += 10
        details.append({"item": "JSON 格式", "score": 10, "max_score": 10,
                        "passed": True, "reason": "合法 JSON"})
    except (json.JSONDecodeError, ValueError) as e:
        total_score += 0
        details.append({"item": "JSON 格式", "score": 0, "max_score": 10,
                        "passed": False, "reason": f"JSON解析失败: {e}"})
        # 后续无法检查字段，直接写结果
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. 检查必需字段 (共40分，每字段10分)
    required_fields = ["fault_id", "severity", "root_cause", "repair_plan"]
    field_scores = {"fault_id": 10, "severity": 10, "root_cause": 10, "repair_plan": 10}
    for field in required_fields:
        if field in data and data[field] is not None:
            total_score += field_scores[field]
            details.append({"item": f"字段 {field}", "score": field_scores[field], "max_score": field_scores[field],
                            "passed": True, "reason": f"字段存在，值类型正确"})
        else:
            details.append({"item": f"字段 {field}", "score": 0, "max_score": field_scores[field],
                            "passed": False, "reason": f"缺失或为空"})

    # 5. 检查内容准确性 (30分)
    # 预期 fault_id = "fault_003"
    # severity = "critical"
    # root_cause 应包含 "connection pool" 或 "pool exhaustion" 或 "long-running"
    # repair_plan 应包含 "increase" 或 "max-pool" 或 "monitor"
    accuracy_score = 0
    accuracy_max = 30
    reasons = []

    if data.get("fault_id") == "fault_003":
        accuracy_score += 10
        reasons.append("fault_id 正确")
    else:
        reasons.append(f"fault_id 期望 fault_003，实际 {data.get('fault_id')}")

    if data.get("severity") == "critical":
        accuracy_score += 5
        reasons.append("severity 正确")
    else:
        reasons.append(f"severity 期望 critical，实际 {data.get('severity')}")

    # root_cause 检查（模糊但基于关键词）
    root_cause = data.get("root_cause", "")
    if any(kw in root_cause.lower() for kw in ["connection pool", "pool exhaustion", "long-running", "hikari"]):
        accuracy_score += 7.5
        reasons.append("root_cause 包含关键线索")
    else:
        reasons.append(f"root_cause 缺少关键信息: {root_cause}")

    repair_plan = data.get("repair_plan", "")
    if any(kw in repair_plan.lower() for kw in ["increase", "max-pool", "pool size", "monitor", "optimize"]):
        accuracy_score += 7.5
        reasons.append("repair_plan 包含关键方案")
    else:
        reasons.append(f"repair_plan 缺少关键方案: {repair_plan}")

    total_score += accuracy_score
    details.append({
        "item": "内容准确性（ID/级别/根因/修复）",
        "score": accuracy_score,
        "max_score": accuracy_max,
        "passed": accuracy_score == accuracy_max,
        "reason": "; ".join(reasons)
    })

    # 最终总分
    result = {"total_score": int(total_score), "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workspace(workspace)
