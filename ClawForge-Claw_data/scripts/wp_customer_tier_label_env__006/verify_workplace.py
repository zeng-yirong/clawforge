import json
import sys
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    max_total = 100

    # 检查文件是否存在
    target_path = os.path.join(workspace, "ops/customer_tier_update.json")
    if not os.path.isfile(target_path):
        score_details.append({"item": "output file existence", "score": 0, "max_score": 10, "passed": False, "reason": "ops/customer_tier_update.json not found"})
        # 后续无法检查，直接输出
        result = {"total_score": 0, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        sys.exit(0)

    score_details.append({"item": "output file existence", "score": 10, "max_score": 10, "passed": True, "reason": "file exists"})
    total_score += 10

    # 读取并解析JSON
    try:
        with open(target_path, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
        total_score += 10
    except (json.JSONDecodeError, ValueError) as e:
        score_details.append({"item": "JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": f"invalid JSON: {e}"})
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        sys.exit(0)

    # 检查结构：必须是列表
    if not isinstance(data, list):
        score_details.append({"item": "output structure", "score": 0, "max_score": 10, "passed": False, "reason": "expected a list of objects"})
        total_score += 0
    else:
        score_details.append({"item": "output structure", "score": 10, "max_score": 10, "passed": True, "reason": "is a list"})
        total_score += 10

    # 检查每个元素字段
    field_ok = True
    for item in data:
        if not isinstance(item, dict) or "customer_id" not in item or "label" not in item:
            field_ok = False
            break
    if field_ok:
        score_details.append({"item": "fields correctness", "score": 10, "max_score": 10, "passed": True, "reason": "all items have customer_id and label"})
        total_score += 10
    else:
        score_details.append({"item": "fields correctness", "score": 0, "max_score": 10, "passed": False, "reason": "missing required fields in some items"})

    # 检查是否包含测试客户 (必须排除)
    test_ids_present = [item["customer_id"] for item in data if item["customer_id"].startswith("test_")]
    if test_ids_present:
        score_details.append({"item": "exclude test customers", "score": 0, "max_score": 15, "passed": False, "reason": f"test customer(s) included: {test_ids_present}"})
        total_score += 0
    else:
        score_details.append({"item": "exclude test customers", "score": 15, "max_score": 15, "passed": True, "reason": "no test customers in output"})
        total_score += 15

    # 检查正式客户是否完整 (5个)
    expected_ids = {"C001", "C002", "C003", "C004", "C005"}
    actual_ids = set(item["customer_id"] for item in data)
    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids
    if missing or extra:
        if missing:
            reason = f"missing customers: {missing}"
        else:
            reason = f"extra customers: {extra}"
        score_details.append({"item": "customer completeness", "score": 0, "max_score": 15, "passed": False, "reason": reason})
        total_score += 0
    else:
        score_details.append({"item": "customer completeness", "score": 15, "max_score": 15, "passed": True, "reason": "all 5 official customers present"})
        total_score += 15

    # 检查标签值 (基于规则，读取原始数据进行精确计算)
    # 读取原始数据
    try:
        with open(os.path.join(workspace, "data/customers/customers.json"), "r") as f:
            cust_data = json.load(f)["customers"]
        with open(os.path.join(workspace, "data/logs/consumption_logs.json"), "r") as f:
            cons_data = json.load(f)["consumption_logs"]
        with open(os.path.join(workspace, "data/logs/activity_logs.json"), "r") as f:
            act_data = json.load(f)["activity_logs"]
    except Exception as e:
        score_details.append({"item": "reading source data", "score": 0, "max_score": 20, "passed": False, "reason": f"could not read source files: {e}"})
        total_score += 0
        result = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        sys.exit(0)

    # 构建查找字典
    cons_map = {item["customer_id"]: item["quarter_spend_usd"] for item in cons_data}
    act_map = {item["customer_id"]: item for item in act_data}

    # 计算预期标签
    expected_labels = {}
    for cust in cust_data:
        cid = cust["customer_id"]
        if cid.startswith("test_"):
            continue  # 测试客户忽略
        spend = cons_map.get(cid)
        activity = act_map.get(cid)
        if spend is None or activity is None:
            continue  # 数据缺失则跳过（但设计上都有）
        if spend > 50000 and activity["last_active_days"] > 30:
            label = "Churn Risk"
        elif spend < 10000:
            label = "Low Spender"
        else:  # 10000 <= spend <= 50000
            if activity["usage_trend"] == "up":
                label = "Growth"
            else:
                label = "Steady"
        expected_labels[cid] = label

    # 比较
    correct_count = 0
    wrong_items = []
    for item in data:
        cid = item["customer_id"]
        actual_label = item["label"]
        expected = expected_labels.get(cid)
        if expected is None:
            wrong_items.append(f"{cid} not expected")
        elif actual_label != expected:
            wrong_items.append(f"{cid}: got '{actual_label}', expected '{expected}'")
        else:
            correct_count += 1

    if correct_count == len(expected_labels) and len(data) == len(expected_labels):
        score_details.append({"item": "label correctness", "score": 20, "max_score": 20, "passed": True, "reason": "all labels match expected values"})
        total_score += 20
    else:
        reason = f"correct: {correct_count}/{len(expected_labels)}; errors: {wrong_items[:3]}"
        score_details.append({"item": "label correctness", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 写结果
    result = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
