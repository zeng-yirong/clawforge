"""
验证脚本：检查 agent 生成的 ops/overbudget.json 是否与预期超支结果一致。
规则：
- 只考虑 TRIP-2024-001 的消费记录（receipt=true）。
- 预算 = 对应类别 daily_limit * 3（出差3天，从政策中获取 standard 等级的数据）。
- 超支定义为实际总和 > 预算。
- 输出 JSON 数组每个元素必须包含 category, budget, actual, over_budget 四个字段，数值允许 0.01 误差。
分数分配：
- 目录 ops 存在：5分
- 文件 ops/overbudget.json 存在且为合法 JSON：10分
- 包含正确数量的超支类别（3个）：15分
- 每个超支条目的字段齐全：20分（每个5分，共4个字段？按类别逐个检查，共3*4=12个字段，但简化：每个条目整体正确10分，共30分）
- 每个条目的预算数值正确：15分（每个5分）
- 每个条目的实际数值正确：15分（每个5分）
- 每个条目的超支数值正确：10分（每个3.33分，取整分配）
总分100分。
注意：policy 中 standard 等级的 daily_limit 可能有多条相同 category_id？我们只取第一条，或者按 category_id 去重。实际数据中每个 category_id 只有一条 standard 记录。
"""

import json
import sys
import os
from collections import defaultdict

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def verify(workspace):
    score_details = []
    total = 0

    # 1. 目录 ops 存在 (5)
    if os.path.isdir(os.path.join(workspace, "ops")):
        score_details.append({"item": "ops目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "ops目录已创建"})
        total += 5
    else:
        score_details.append({"item": "ops目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "缺少ops目录"})
        # 后续无法检查，直接返回
        write_result(workspace, total, score_details)
        return

    # 2. 文件 ops/overbudget.json 存在且合法 JSON (10)
    output_path = os.path.join(workspace, "ops", "overbudget.json")
    if not os.path.isfile(output_path):
        score_details.append({"item": "ops/overbudget.json存在且合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        write_result(workspace, total, score_details)
        return
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            agent_output = json.load(f)
        if not isinstance(agent_output, list):
            raise ValueError("不是数组")
        score_details.append({"item": "ops/overbudget.json存在且合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件有效"})
        total += 10
    except Exception as e:
        score_details.append({"item": "ops/overbudget.json存在且合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_result(workspace, total, score_details)
        return

    # 3. 读取原始数据，构建预期超支列表
    policies = load_json(os.path.join(workspace, "travel_policies.json"))
    records = load_json(os.path.join(workspace, "consumption_records.json"))

    # 提取 standard 等级的各 category daily_limit
    standard_limits = {}
    for cat in policies["categories"]:
        if cat.get("tier") == "standard" and cat.get("reimbursable", False):
            cid = cat["category_id"]
            if cid not in standard_limits:  # 取第一个（实际数据只有一个）
                standard_limits[cid] = cat["daily_limit"]

    # 筛选 TRIP-2024-001 且 receipt=True 的记录
    trip_records = [r for r in records["consumption_records"] if r["trip_id"] == "TRIP-2024-001" and r.get("receipt", False)]
    # 按 category 聚合实际
    actual_sum = defaultdict(float)
    for r in trip_records:
        actual_sum[r["category"]] += r["amount"]

    # 计算预算 (3天)
    days = 3
    expected_overbudget = []
    for cid, limit in standard_limits.items():
        budget = limit * days
        actual = actual_sum.get(cid, 0.0)
        if actual > budget + 0.001:  # 考虑浮点误差
            expected_overbudget.append({
                "category": cid,
                "budget": round(budget, 2),
                "actual": round(actual, 2),
                "over_budget": round(actual - budget, 2)
            })

    # 检查数量 (15分)
    if len(agent_output) == len(expected_overbudget):
        score_details.append({"item": "超支类别数量正确", "score": 15, "max_score": 15, "passed": True, "reason": f"期望{len(expected_overbudget)}个，实际{len(agent_output)}个"})
        total += 15
    else:
        score_details.append({"item": "超支类别数量正确", "score": 0, "max_score": 15, "passed": False, "reason": f"期望{len(expected_overbudget)}个，实际{len(agent_output)}个"})
        # 即使数量错误，仍然检查已有条目，但可能失分

    # 检查每个条目的字段和数值 (共5+15+15+10=45分，但为了简化按条目分配)
    # 每个条目满分15分（字段存在5，budget5，actual5，over_budget0? 我们汇总为每个条目15分，共45分）
    per_item_score = 15  # 三个条目共45分
    item_correct_count = 0
    total_items = len(expected_overbudget)
    for exp in expected_overbudget:
        # 在 agent 输出中寻找匹配类别
        found = None
        for item in agent_output:
            if item.get("category") == exp["category"]:
                found = item
                break
        if found is None:
            continue
        # 检查四个字段是否存在
        fields_ok = all(k in found for k in ["category", "budget", "actual", "over_budget"])
        if not fields_ok:
            continue
        # 检查数值（允许0.01误差）
        if (abs(found["budget"] - exp["budget"]) <= 0.01 and
            abs(found["actual"] - exp["actual"]) <= 0.01 and
            abs(found["over_budget"] - exp["over_budget"]) <= 0.01):
            item_correct_count += 1

    # 分配分数
    if total_items > 0:
        item_score_perfect = per_item_score * total_items  # 45
        item_score_actual = int(item_correct_count / total_items * item_score_perfect)
        score_details.append({
            "item": "每个超支条目的字段与数值准确性",
            "score": item_score_actual,
            "max_score": item_score_perfect,
            "passed": item_correct_count == total_items,
            "reason": f"正确条目数 {item_correct_count}/{total_items}"
        })
        total += item_score_actual
    else:
        # 没有期望超支项（理论上不应该）
        score_details.append({"item": "每个超支条目的字段与数值准确性", "score": 0, "max_score": 45, "passed": False, "reason": "无期望超支项，检查环境数据"})

    # 确保总分不超过100
    final_score = min(total, 100)
    write_result(workspace, final_score, score_details)

def write_result(workspace, score, details):
    result = {"total_score": score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"验证完成，总分: {score}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
