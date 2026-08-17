import json
import sys
import os
from pathlib import Path

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_expected_tier_and_labels(customer_id, consumption_map, activity_map, rules):
    spend = consumption_map.get(customer_id)
    activity = activity_map.get(customer_id)
    if spend is None or activity is None:
        # 无数据，返回 None 表示应保留原值
        return None

    for rule in rules['rules']:
        cond = rule['conditions']
        # 检查所有非None条件
        pass_all = True
        if cond.get('min_spend') is not None and spend < cond['min_spend']:
            pass_all = False
        if cond.get('max_spend') is not None and spend > cond['max_spend']:
            pass_all = False
        if cond.get('max_active_days') is not None and activity['last_active_days'] > cond['max_active_days']:
            pass_all = False
        if cond.get('risk_level') is not None and activity['risk_level'] != cond['risk_level']:
            pass_all = False
        if pass_all:
            return (rule['tier'], rule['labels'])
    # 理论上应总能匹配到最后一个兜底规则，但安全返回
    return ("low_value", ["basic"])

def verify(workspace):
    ws = Path(workspace)
    score_details = []
    total_possible = 100

    # 1. 检查产物文件是否存在 (10分)
    output_file = ws / "ops" / "updated_labels.json"
    if output_file.exists():
        score_details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/updated_labels.json 存在"})
    else:
        score_details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/updated_labels.json 不存在"})
        # 后续步骤无法进行，直接输出
        total = sum(d['score'] for d in score_details)
        result = {"total_score": total, "details": score_details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 解析JSON合法性 (10分)
    try:
        output_data = load_json(output_file)
        if not isinstance(output_data, list):
            raise ValueError("不是列表")
        score_details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "是合法JSON数组"})
    except Exception as e:
        score_details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        total = sum(d['score'] for d in score_details)
        result = {"total_score": total, "details": score_details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 读取原始客户数据、日志、规则
    try:
        customers = load_json(ws / "data" / "customers" / "customers.json")
        consumption_list = load_json(ws / "data" / "logs" / "consumption_logs.json")
        activity_list = load_json(ws / "data" / "logs" / "activity_logs.json")
        rules = load_json(ws / "data" / "segmentation_rules.json")
    except Exception as e:
        score_details.append({"item": "环境数据读取", "score": 0, "max_score": 10, "passed": False, "reason": f"无法读取基础数据: {str(e)}"})
        total = sum(d['score'] for d in score_details)
        result = {"total_score": total, "details": score_details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 构建映射
    consumption_map = {c['customer_id']: c['quarter_spend_usd'] for c in consumption_list}
    activity_map = {a['customer_id']: a for a in activity_list}
    customer_map = {c['customer_id']: c for c in customers}

    # 4. 检查输出是否包含所有客户 (10分)
    output_ids = {item.get('customer_id') for item in output_data}
    all_customer_ids = {c['customer_id'] for c in customers}
    if output_ids == all_customer_ids:
        score_details.append({"item": "包含所有客户", "score": 10, "max_score": 10, "passed": True, "reason": "所有5个客户ID都出现在输出中"})
    else:
        missing = all_customer_ids - output_ids
        extra = output_ids - all_customer_ids
        reason = f"缺失: {missing}, 多余: {extra}"
        score_details.append({"item": "包含所有客户", "score": 0, "max_score": 10, "passed": False, "reason": reason})

    # 5. 检查每个客户的tier和labels (每个客户14分，共70分)
    # 每个客户细分：tier正确10分，labels正确4分
    for cust in customers:
        cid = cust['customer_id']
        output_item = next((x for x in output_data if x.get('customer_id') == cid), None)
        if output_item is None:
            score_details.append({"item": f"客户{cid}存在性", "score": 0, "max_score": 14, "passed": False, "reason": "输出中未找到该客户"})
            continue

        # 计算期望
        expected = get_expected_tier_and_labels(cid, consumption_map, activity_map, rules)
        if expected is None:
            # 无数据，期望保留原值
            expected_tier = cust['tier']
            expected_labels = cust['labels']
        else:
            expected_tier, expected_labels = expected

        # 检查tier
        tier_ok = output_item.get('tier') == expected_tier
        # 检查labels (集合相等，不考虑顺序)
        labels_ok = set(output_item.get('labels', [])) == set(expected_labels)
        item_score = (10 if tier_ok else 0) + (4 if labels_ok else 0)
        reason_parts = []
        if not tier_ok:
            reason_parts.append(f"期望tier={expected_tier}, 实际={output_item.get('tier')}")
        if not labels_ok:
            reason_parts.append(f"期望labels={expected_labels}, 实际={output_item.get('labels')}")
        reason = "; ".join(reason_parts) if reason_parts else "正确"
        score_details.append({
            "item": f"客户{cid}标签准确性",
            "score": item_score,
            "max_score": 14,
            "passed": tier_ok and labels_ok,
            "reason": reason
        })

    # 6. 检查是否有多余字段 (10分)
    allowed_fields = {'customer_id', 'tier', 'labels'}
    extra_fields_found = False
    for item in output_data:
        item_fields = set(item.keys())
        if not item_fields.issubset(allowed_fields):
            extra_fields_found = True
            break
    if extra_fields_found:
        score_details.append({"item": "无多余字段", "score": 0, "max_score": 10, "passed": False, "reason": "输出中存在不允许的字段（只允许customer_id, tier, labels）"})
    else:
        score_details.append({"item": "无多余字段", "score": 10, "max_score": 10, "passed": True, "reason": "所有条目字段符合要求"})

    # 计算总得分
    total = sum(d['score'] for d in score_details)
    # 确保在0-100
    total = min(total, 100)
    result = {"total_score": total, "details": score_details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"验证完成，得分: {total}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
