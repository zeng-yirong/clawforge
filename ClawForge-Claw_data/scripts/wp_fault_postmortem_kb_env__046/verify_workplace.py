import sys
import os
import json
import math

def verify(workspace):
    details = []
    total_score = 0

    # 0. 检查目标文件是否存在
    target_path = os.path.join(workspace, "ops", "postmortem_archive.json")
    item = {"item": "ops/postmortem_archive.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if not os.path.exists(target_path):
        item["reason"] = "文件未找到"
        item["score"] = 0
    else:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "文件存在"
    details.append(item)
    total_score += item["score"]

    # 如果文件不存在，直接返回总分（后面项无法检查，给0分）
    if not os.path.exists(target_path):
        # 但还需写入剩余项（标记为未检查）
        missing_items = [
            ("JSON 格式合法", 10),
            ("包含 fault_id 字段", 10),
            ("fault_id 值正确", 20),
            ("包含 root_cause 字段", 10),
            ("root_cause 内容正确", 20),
            ("包含 repair_plan 字段", 10),
            ("repair_plan 内容正确", 10)
        ]
        for name, maxs in missing_items:
            details.append({
                "item": name,
                "score": 0,
                "max_score": maxs,
                "passed": False,
                "reason": "目标文件不存在，跳过"
            })
        total_score = sum(d["score"] for d in details)
        return details, total_score

    # 1. JSON 格式合法
    item = {"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "JSON 解析成功"
    except (json.JSONDecodeError, Exception) as e:
        item["reason"] = f"JSON 解析失败: {str(e)}"
        item["score"] = 0
    details.append(item)
    total_score += item["score"]

    # 如果JSON不合法，后续字段检查无法进行，给0分并返回
    if not item["passed"]:
        missing_items = [
            ("包含 fault_id 字段", 10),
            ("fault_id 值正确", 20),
            ("包含 root_cause 字段", 10),
            ("root_cause 内容正确", 20),
            ("包含 repair_plan 字段", 10),
            ("repair_plan 内容正确", 10)
        ]
        for name, maxs in missing_items:
            details.append({
                "item": name,
                "score": 0,
                "max_score": maxs,
                "passed": False,
                "reason": "JSON 不合法，无法检查"
            })
        total_score = sum(d["score"] for d in details)
        return details, total_score

    # 2. 检查 fault_id 字段
    item = {"item": "包含 fault_id 字段", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if "fault_id" in data:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "存在 fault_id 字段"
    else:
        item["reason"] = "缺少 fault_id 字段"
    details.append(item)
    total_score += item["score"]

    # 3. fault_id 值正确 (必须为 "F-2025-003")
    item = {"item": "fault_id 值正确", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    if data.get("fault_id") == "F-2025-003":
        item["score"] = 20
        item["passed"] = True
        item["reason"] = "fault_id 为 F-2025-003"
    else:
        item["reason"] = f"期望 'F-2025-003'，实际得到 '{data.get('fault_id')}'"
        item["score"] = 0
    details.append(item)
    total_score += item["score"]

    # 4. root_cause 字段存在
    item = {"item": "包含 root_cause 字段", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if "root_cause" in data:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "存在 root_cause 字段"
    else:
        item["reason"] = "缺少 root_cause 字段"
    details.append(item)
    total_score += item["score"]

    # 5. root_cause 内容正确（必须包含核心短语 "deadlock" 或 "connection pool"）
    #    我们允许两种表达：必须含 "deadlock" 且含 "connection pool" 或 "pool" 根据附件内容
    item = {"item": "root_cause 内容正确", "score": 0, "max_score": 20, "passed": False, "reason": ""}
    root_cause = data.get("root_cause", "")
    # 标准化：去除空格和标点，转小写
    cleaned = root_cause.lower().replace(" ", "").replace("-", "").replace("_", "")
    # 预期关键词：deadlock 和 pool（因为附件明确说deadlock on connection pool）
    if "deadlock" in cleaned and "pool" in cleaned:
        item["score"] = 20
        item["passed"] = True
        item["reason"] = f"root_cause 包含 'deadlock' 和 'pool'，内容合理: {root_cause}"
    else:
        item["reason"] = f"root_cause 内容不匹配预期，得到: {root_cause}"
        item["score"] = 0
    details.append(item)
    total_score += item["score"]

    # 6. repair_plan 字段存在
    item = {"item": "包含 repair_plan 字段", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    if "repair_plan" in data:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "存在 repair_plan 字段"
    else:
        item["reason"] = "缺少 repair_plan 字段"
    details.append(item)
    total_score += item["score"]

    # 7. repair_plan 内容正确（必须包含 "pool size" 或 "increase" 以及 "retry" 或 "timeout" 相关）
    item = {"item": "repair_plan 内容正确", "score": 0, "max_score": 10, "passed": False, "reason": ""}
    plan = data.get("repair_plan", "")
    plan_lower = plan.lower()
    # 期望提及 pool size 增加和 retry/backoff
    has_pool = ("pool" in plan_lower and ("size" in plan_lower or "max" in plan_lower))
    has_retry = "retry" in plan_lower or "backoff" in plan_lower or "timeout" in plan_lower
    if has_pool and has_retry:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"repair_plan 包含 pool 调整和重试机制: {plan}"
    else:
        item["reason"] = f"repair_plan 不完整，得到: {plan}"
        item["score"] = 0
    details.append(item)
    total_score += item["score"]

    # 计算总分（确保在0-100）
    total_score = sum(d["score"] for d in details)
    total_score = max(0, min(100, total_score))

    return details, total_score


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details, total_score = verify(workspace)

    result = {
        "total_score": total_score,
        "details": details
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {output_path}: {total_score}/100")


if __name__ == "__main__":
    main()
