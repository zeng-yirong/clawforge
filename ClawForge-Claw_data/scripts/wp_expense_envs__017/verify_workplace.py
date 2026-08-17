import json
import os
import sys
from collections import defaultdict

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(WORKSPACE, rel_path)
    if not os.path.exists(full):
        return None
    with open(full, 'r', encoding='utf-8') as f:
        return json.load(f)

def score():
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查必要目录和文件存在 (10分)
    exists_checks = [
        ("data/consumption_records.json", "消费记录文件"),
        ("data/trips.json", "行程信息文件"),
        ("policies/travel_policies_v2.json", "最新政策文件"),
        ("report/expense_analysis.json", "Agent 输出报告"),
    ]
    exist_score = 0
    for path, desc in exists_checks:
        full_path = os.path.join(WORKSPACE, path)
        if os.path.exists(full_path):
            exist_score += 2.5
            details.append({"item": f"文件存在: {desc}", "score": 2.5, "max_score": 2.5, "passed": True, "reason": f"找到 {path}"})
        else:
            details.append({"item": f"文件存在: {desc}", "score": 0, "max_score": 2.5, "passed": False, "reason": f"缺少 {path}"})
    details.append({"item": "文件存在性合计", "score": exist_score, "max_score": 10, "passed": exist_score==10, "reason": ""})
    total_score += exist_score

    # 2. 解析 Agent 输出报告 (10分)
    agent_report = load_json("report/expense_analysis.json")
    report_valid = False
    if agent_report is None:
        details.append({"item": "Agent 报告格式", "score": 0, "max_score": 10, "passed": False, "reason": "报告文件不存在或无法解析"})
    elif not isinstance(agent_report, dict):
        details.append({"item": "Agent 报告格式", "score": 0, "max_score": 10, "passed": False, "reason": "报告不是 JSON 对象"})
    else:
        required_keys = ["trip_id", "overbudget_items", "total_excess"]
        missing = [k for k in required_keys if k not in agent_report]
        if missing:
            details.append({"item": "Agent 报告格式", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少键: {missing}"})
        else:
            report_valid = True
            details.append({"item": "Agent 报告格式", "score": 10, "max_score": 10, "passed": True, "reason": "报告结构完整"})
    total_score += 10 if report_valid else 0

    if not report_valid:
        # 无法继续，输出结果
        final = {"total_score": int(total_score), "details": details}
        with open(os.path.join(WORKSPACE, "workplace_score.json"), 'w') as f:
            json.dump(final, f, indent=2)
        return

    # 3. 计算正确的预期结果 (使用工作区数据)
    # 3.1 加载 trips 找到目标 trip (TRIP-2024-001)
    trips_data = load_json("data/trips.json")
    if not trips_data or not isinstance(trips_data, list):
        details.append({"item": "行程数据", "score": 0, "max_score": 5, "passed": False, "reason": "无法读取 trips.json"})
        total_score += 0
    else:
        target_trip = None
        for t in trips_data:
            if t.get("trip_id") == "TRIP-2024-001":
                target_trip = t
                break
        if target_trip is None:
            details.append({"item": "行程数据", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 TRIP-2024-001"})
        else:
            duration_days = target_trip.get("duration_days", 3)
            details.append({"item": "行程数据", "score": 5, "max_score": 5, "passed": True, "reason": f"出差天数 {duration_days}"})
            total_score += 5

    # 3.2 加载最新政策
    policy = load_json("policies/travel_policies_v2.json")
    if not policy or "categories" not in policy:
        details.append({"item": "政策数据", "score": 0, "max_score": 5, "passed": False, "reason": "policy v2 加载失败"})
        total_score += 0
    else:
        details.append({"item": "政策数据", "score": 5, "max_score": 5, "passed": True, "reason": "政策加载成功"})
        total_score += 5

    # 3.3 加载消费记录，提取目标 trip 的有效记录
    records_data = load_json("data/consumption_records.json")
    if not records_data or "records" not in records_data:
        details.append({"item": "消费记录", "score": 0, "max_score": 5, "passed": False, "reason": "无法解析 consumption_records.json"})
        total_score += 0
    else:
        # 有效记录筛选：category 非空、amount>0、category 在 policy 中有定义（可报销且 category_id 合法）
        valid_categories = {c["category_id"] for c in policy["categories"] if c.get("reimbursable")}
        # 注意：目标 trip 的记录没有 trip_id 字段，只能从日期范围和描述推断？这里我们假设目标 trip 的记录都在 trip_id 字段中？实际上消费记录中没有 trip_id。因此 Agent 需要自行判断哪些记录属于该 trip。我们设计时让记录顺序没有分隔，但 Agent 可以通过日期范围与 trip 的日期匹配。因此这里我们也使用相同的逻辑：选择日期在 start_date ~ end_date 之间的记录。
        start = target_trip["start_date"]
        end = target_trip["end_date"]
        def date_in_range(d):
            return start <= d <= end
        effective_records = []
        for rec in records_data["records"]:
            cat = rec.get("category")
            amt = rec.get("amount", 0)
            date = rec.get("date", "")
            if cat is None or not isinstance(cat, str) or cat not in valid_categories:
                continue
            if not isinstance(amt, (int, float)) or amt <= 0:
                continue
            if not date or not date_in_range(date):
                continue
            effective_records.append(rec)
        details.append({"item": "消费记录筛选", "score": 5, "max_score": 5, "passed": True, "reason": f"提取到 {len(effective_records)} 条有效记录"})
        total_score += 5

    # 3.4 计算预算与实际
    policy_map = {c["category_id"]: c for c in policy["categories"]}
    # 按类别汇总实际金额
    actual_by_cat = defaultdict(float)
    nights_total = 0
    accommodation_records = []
    for rec in effective_records:
        cat = rec["category"]
        actual_by_cat[cat] += rec["amount"]
        if cat == "accommodation" and "nights" in rec and rec["nights"]:
            nights_total += rec["nights"]
            accommodation_records.append(rec)

    # 计算预算
    budget_by_cat = {}
    for cat in policy_map:
        if not policy_map[cat].get("reimbursable"):
            continue
        daily_limit = policy_map[cat]["max_daily_amount"]
        if cat == "accommodation":
            # 住宿按 nights 计算
            budget_by_cat[cat] = daily_limit * nights_total
        else:
            budget_by_cat[cat] = daily_limit * duration_days

    # 找出超支项
    overbudget = []
    for cat, actual in actual_by_cat.items():
        if cat not in budget_by_cat:
            continue
        budget = budget_by_cat[cat]
        if actual > budget:
            excess = actual - budget
            overbudget.append({
                "category": cat,
                "budget": budget,
                "actual": actual,
                "excess": excess
            })
    total_excess = sum(item["excess"] for item in overbudget)

    expected_report = {
        "trip_id": "TRIP-2024-001",
        "overbudget_items": overbudget,
        "total_excess": total_excess
    }

    # 4. 对比 Agent 报告与预期 (50分)
    compare_score = 0
    # 4.1 trip_id (5分)
    if agent_report.get("trip_id") == expected_report["trip_id"]:
        compare_score += 5
        details.append({"item": "trip_id 正确", "score": 5, "max_score": 5, "passed": True, "reason": f"trip_id = {expected_report['trip_id']}"})
    else:
        details.append({"item": "trip_id 正确", "score": 0, "max_score": 5, "passed": False, "reason": f"预期 {expected_report['trip_id']}, 实际 {agent_report.get('trip_id')}"})

    # 4.2 overbudget_items (35分)
    agent_items = agent_report.get("overbudget_items", [])
    expected_items = expected_report["overbudget_items"]
    # 比较数量
    if len(agent_items) != len(expected_items):
        details.append({"item": "超支项数量正确", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 {len(expected_items)} 项, 实际 {len(agent_items)} 项"})
        compare_score += 0
    else:
        details.append({"item": "超支项数量正确", "score": 10, "max_score": 10, "passed": True, "reason": f"共 {len(expected_items)} 项"})
        compare_score += 10
        # 比较每一项的内容 (25分)
        item_score = 0
        for i, (exp_item, agent_item) in enumerate(zip(expected_items, agent_items)):
            cat_ok = agent_item.get("category") == exp_item["category"]
            budget_ok = agent_item.get("budget") == exp_item["budget"]
            actual_ok = agent_item.get("actual") == exp_item["actual"]
            excess_ok = agent_item.get("excess") == exp_item["excess"]
            if all([cat_ok, budget_ok, actual_ok, excess_ok]):
                item_score += 12.5  # 每一项满分12.5
            else:
                # 部分正确给部分
                correct_parts = sum([cat_ok, budget_ok, actual_ok, excess_ok])
                item_score += correct_parts * 3.125
        item_score = min(item_score, 25)
        compare_score += item_score
        details.append({"item": "超支项明细正确", "score": item_score, "max_score": 25, "passed": item_score == 25, "reason": f"得分 {item_score}/25"})

    # 4.3 total_excess (10分)
    if agent_report.get("total_excess") == expected_report["total_excess"]:
        compare_score += 10
        details.append({"item": "总超支金额正确", "score": 10, "max_score": 10, "passed": True, "reason": f"总额 = {expected_report['total_excess']}"})
    else:
        details.append({"item": "总超支金额正确", "score": 0, "max_score": 10, "passed": False, "reason": f"预期 {expected_report['total_excess']}, 实际 {agent_report.get('total_excess')}"})

    total_score += compare_score
    details.append({"item": "报告内容比对合计", "score": compare_score, "max_score": 50, "passed": compare_score==50, "reason": ""})

    # 5. 无多余文件惩罚？不做了，只检查必须项

    total_score = min(total_score, 100)
    final = {"total_score": int(round(total_score)), "details": details}
    with open(os.path.join(WORKSPACE, "workplace_score.json"), 'w') as f:
        json.dump(final, f, indent=2)

if __name__ == '__main__':
    score()
