import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def read_json(rel_path):
    full = os.path.join(workspace, rel_path)
    if not os.path.isfile(full):
        return None, f"File not found: {full}"
    try:
        with open(full, "r") as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"JSON parse error in {full}: {e}"
    except Exception as e:
        return None, str(e)

def main():
    details = []
    total_score = 0

    # 1. 检查输出文件存在 (10分)
    result_path = os.path.join(workspace, "ops", "tier_labels.json")
    if os.path.isfile(result_path):
        details.append({
            "item": "Output file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/tier_labels.json exists"
        })
        total_score += 10
    else:
        details.append({
            "item": "Output file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/tier_labels.json not found"
        })
        # 无法继续检查，直接输出
        _write_score(details, total_score)
        return

    # 2. JSON 合法性 (10分)
    try:
        with open(result_path, "r") as f:
            result = json.load(f)
        details.append({
            "item": "Result JSON valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "Result JSON valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        _write_score(details, total_score)
        return

    # 3. 读取顾客主数据 (用于确定正确的客户列表)
    customers_data, err = read_json("data/customers/customers.json")
    if err:
        details.append({
            "item": "Read customers.json",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Failed: {err}"
        })
        _write_score(details, total_score)
        return
    customers_list = customers_data.get("customers", [])
    expected_customer_ids = {c["customer_id"] for c in customers_list}

    # 4. 检查输出键是否包含所有预期客户 (10分)
    actual_ids = set(result.keys())
    if actual_ids == expected_customer_ids:
        details.append({
            "item": "Include all customer IDs",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Exactly the expected customers"
        })
        total_score += 10
    elif actual_ids.issuperset(expected_customer_ids):
        details.append({
            "item": "Include all customer IDs",
            "score": 5,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra customers found: {actual_ids - expected_customer_ids}. Deduct 5"
        })
        total_score += 5
    else:
        missing = expected_customer_ids - actual_ids
        details.append({
            "item": "Include all customer IDs",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing customers: {missing}"
        })

    # 5. 读取活动日志和消费日志 (用于计算正确标签)
    act_data, err = read_json("data/logs/activity_logs.json")
    if err:
        details.append({
            "item": "Read activity_logs.json",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Failed: {err}"
        })
        _write_score(details, total_score)
        return
    act_logs = act_data.get("activity_logs", [])
    act_map = {log["customer_id"]: log for log in act_logs}

    cons_data, err = read_json("data/logs/consumption_logs.json")
    if err:
        details.append({
            "item": "Read consumption_logs.json",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Failed: {err}"
        })
        _write_score(details, total_score)
        return
    cons_logs = cons_data.get("consumption_logs", [])
    cons_map = {log["customer_id"]: log for log in cons_logs}

    # 6. 检查每个客户的标签是否正确 (每个客户10分，共6个客户60分)
    correct_count = 0
    incorrect_info = []
    for cid in expected_customer_ids:
        # 确定消费
        if cid in cons_map:
            spend = cons_map[cid]["quarter_spend_usd"]
        else:
            spend = 0
        # 确定活跃天数
        if cid in act_map:
            last_active = act_map[cid]["last_active_days"]
        else:
            last_active = 999

        # 规则计算
        if spend > 10000 and last_active <= 30:
            expected_label = "active_high_value"
        elif spend > 10000 and last_active > 30:
            expected_label = "inactive_high_value"
        elif spend <= 10000 and last_active <= 30:
            expected_label = "active_low_value"
        else:
            expected_label = "inactive_low_value"

        actual_label = result.get(cid)
        if actual_label == expected_label:
            correct_count += 1
        else:
            incorrect_info.append((cid, actual_label, expected_label))

    max_per_customer = 10  # 6个客户共60分
    score_per_customer = correct_count * (60 / len(expected_customer_ids))  # 每个客户10分
    if correct_count == len(expected_customer_ids):
        details.append({
            "item": "Customer label correctness",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": "All labels correct"
        })
        total_score += 60
    else:
        # 按比例给分
        partial = int(round(score_per_customer))
        details.append({
            "item": "Customer label correctness",
            "score": partial,
            "max_score": 60,
            "passed": False,
            "reason": f"Incorrect for: {incorrect_info}"
        })
        total_score += partial

    # 7. 检查标签值是否在允许枚举内 (10分)
    allowed_labels = {"active_high_value", "inactive_high_value", "active_low_value", "inactive_low_value"}
    bad_labels = []
    for cid, lbl in result.items():
        if lbl not in allowed_labels:
            bad_labels.append((cid, lbl))
    if not bad_labels:
        details.append({
            "item": "Label values in allowed set",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All labels are valid"
        })
        total_score += 10
    else:
        details.append({
            "item": "Label values in allowed set",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid labels: {bad_labels}"
        })

    # 8. 最终分数修正 (确保不超过100)
    total_score = min(total_score, 100)
    _write_score(details, total_score)

def _write_score(details, total_score):
    output = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
