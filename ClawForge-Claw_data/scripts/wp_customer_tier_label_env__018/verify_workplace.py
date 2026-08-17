import json
import os
import sys

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None

def determine_label(customer_id, activity_map, consumption_map, rules):
    """根据规则计算客户标签，返回标签字符串"""
    act = activity_map.get(customer_id)
    cons = consumption_map.get(customer_id)
    if act is None or cons is None:
        # 如果任一指标缺失（或被过滤掉视为缺失），返回 Unknown
        # 注意：act 可能是 None，因为活动日志中没有该客户或脏数据被忽略
        return "Unknown"
    spend = cons
    inactive_days = act
    for rule in rules:
        if "min_spend" in rule:
            if spend >= rule["min_spend"] and inactive_days <= rule["max_inactive_days"]:
                return rule["label"]
        else:
            return rule["label"]
    return "Unknown"

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查输出文件是否存在
    output_path = os.path.join(workspace, "data/updated_customers.json")
    if not os.path.exists(output_path):
        details.append({"item": "输出文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 data/updated_customers.json 不存在"})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        print(f"Total: {total}")
        return

    details.append({"item": "输出文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    score += 10

    # 2. 解析 JSON 且为列表
    data = load_json(output_path)
    if data is None or not isinstance(data, list):
        details.append({"item": "JSON 合法且为列表", "score": 0, "max_score": 10, "passed": False, "reason": "输出文件不是合法 JSON 列表"})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f, indent=2)
        print(f"Total: {total}")
        return
    details.append({"item": "JSON 合法且为列表", "score": 10, "max_score": 10, "passed": True, "reason": "正确解析为列表"})
    score += 10

    # 3. 检查每个元素是否包含必要字段（至少 customer_id, customer_name, industry, tier, labels, owner_name）
    required_fields = ["customer_id", "customer_name", "industry", "tier", "labels", "owner_name"]
    field_errors = []
    for idx, cust in enumerate(data):
        missing = [f for f in required_fields if f not in cust]
        if missing:
            field_errors.append(f"索引{idx}（customer_id={cust.get('customer_id','?')}）缺失字段: {missing}")
    if field_errors:
        details.append({"item": "必要字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(field_errors[:5])})
        score += 0
    else:
        details.append({"item": "必要字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有记录包含必要字段"})
        score += 10

    # 4. 加载原始数据与规则（用于验证答案）
    # 原始客户
    src_customers_path = os.path.join(workspace, "data/customers/customers.json")
    src_customers = load_json(src_customers_path)
    # 活动日志
    act_path = os.path.join(workspace, "data/logs/activity_logs.json")
    act_raw = load_json(act_path)
    # 消费日志
    cons_path = os.path.join(workspace, "data/logs/consumption_logs.json")
    cons_raw = load_json(cons_path)
    # 规则
    rules_path = os.path.join(workspace, "ops/segment_rules.json")
    rules = load_json(rules_path)

    if not all([src_customers, act_raw, cons_raw, rules]):
        details.append({"item": "依赖数据完整性", "score": 0, "max_score": 10, "passed": False, "reason": "无法加载原始数据或规则文件"})
        score += 0
    else:
        # 构造活动映射（过滤脏数据: last_active_days 为负数视为缺失）
        act_map = {}
        for entry in act_raw:
            cid = entry.get("customer_id")
            days = entry.get("last_active_days")
            if cid and isinstance(days, int) and days >= 0:
                act_map[cid] = days  # 只保留一个值（如果有重复，取最后出现的，这里数据无重复）
        # 消费映射（过滤负数）
        cons_map = {}
        for entry in cons_raw:
            cid = entry.get("customer_id")
            spend = entry.get("quarter_spend_usd")
            if cid and isinstance(spend, (int, float)) and spend >= 0:
                cons_map[cid] = spend

        # 计算期望结果：只考虑有效客户（非 deleted）
        expected = []
        for cust in src_customers:
            if cust.get("is_deleted"):
                continue
            cid = cust["customer_id"]
            label = determine_label(cid, act_map, cons_map, rules)
            expected_cust = dict(cust)
            if "is_deleted" in expected_cust:
                del expected_cust["is_deleted"]  # 输出不应包含此字段
            expected_cust["labels"] = [label] if label != "Unknown" else ["Unknown"]  # 统一格式：列表
            # 注意：规则要求输出 labels 字段为列表，每个元素是一个标签字符串
            # 原数据中 labels 是空列表，更新后应为 [label]
            expected.append(expected_cust)

        # 比较数量
        if len(data) != len(expected):
            details.append({"item": "有效客户数量", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {len(expected)} 条，实际 {len(data)} 条"})
            score += 0
        else:
            details.append({"item": "有效客户数量", "score": 10, "max_score": 10, "passed": True, "reason": "数量匹配"})
            score += 10

        # 逐条比较（忽略顺序，按 customer_id 匹配）
        actual_map = {c["customer_id"]: c for c in data}
        correct_labels = 0
        total_compared = 0
        for exp in expected:
            cid = exp["customer_id"]
            act = actual_map.get(cid)
            if act is None:
                continue
            total_compared += 1
            # 检查 labels
            exp_labels = exp["labels"]
            act_labels = act.get("labels", [])
            if act_labels == exp_labels:
                correct_labels += 1
        if total_compared == 0:
            details.append({"item": "标签正确性", "score": 0, "max_score": 40, "passed": False, "reason": "无法找到任何可比较的客户"})
            score += 0
        else:
            label_score = int(40 * correct_labels / total_compared)
            if correct_labels == total_compared:
                passed = True
            else:
                passed = False
            details.append({"item": "标签正确性", "score": label_score, "max_score": 40, "passed": passed, "reason": f"共 {total_compared} 个有效客户，{correct_labels} 个标签正确"})
            score += label_score

    # 5. 检查是否有多余字段（不允许添加额外字段）
    extra_fields_allowed = {"customer_id", "customer_name", "industry", "tier", "labels", "owner_name"}  # 原字段集合
    extra_penalty = 0
    for idx, cust in enumerate(data):
        extra = set(cust.keys()) - extra_fields_allowed
        if extra:
            extra_penalty += 5  # 每个客户扣5分，最多扣10分
    if extra_penalty > 10:
        extra_penalty = 10
    score -= extra_penalty
    details.append({"item": "无额外字段", "score": 10 - extra_penalty, "max_score": 10, "passed": extra_penalty == 0, "reason": f"检测到 {extra_penalty} 分扣减" if extra_penalty > 0 else "无额外字段"})
    score = max(score, 0)

    # 最终总分
    total_score = min(score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total: {total_score}")

if __name__ == "__main__":
    main()
