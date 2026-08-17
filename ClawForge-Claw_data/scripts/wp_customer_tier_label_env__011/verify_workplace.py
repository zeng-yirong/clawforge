import json
import os
import sys

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查ops/labels_update.json是否存在 (5分)
    result_path = os.path.join(workspace, "ops", "labels_update.json")
    if os.path.isfile(result_path):
        score_details.append({"item": "ops/labels_update.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "File found"})
        total_score += 5
    else:
        score_details.append({"item": "ops/labels_update.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "File not found"})
        # 如果文件不存在，后面的检查无法进行，直接输出结果
        final = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 2. JSON合法性 (5分)
    try:
        data = load_json(result_path)
        score_details.append({"item": "JSON valid", "score": 5, "max_score": 5, "passed": True, "reason": "Valid JSON"})
        total_score += 5
    except Exception as e:
        score_details.append({"item": "JSON valid", "score": 0, "max_score": 5, "passed": False, "reason": str(e)})
        final = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. 结构检查：必须是一个列表，每个元素包含customer_id和labels (10分)
    if isinstance(data, list):
        all_have_fields = all(
            isinstance(item, dict) and "customer_id" in item and "labels" in item and isinstance(item["labels"], list)
            for item in data
        )
        if all_have_fields:
            score_details.append({"item": "Structure correct (list of dicts with customer_id and labels)", "score": 10, "max_score": 10, "passed": True, "reason": "All entries valid"})
            total_score += 10
        else:
            score_details.append({"item": "Structure correct", "score": 0, "max_score": 10, "passed": False, "reason": "Some items missing required fields"})
    else:
        score_details.append({"item": "Structure correct", "score": 0, "max_score": 10, "passed": False, "reason": "Result is not a list"})
        final = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 4. 加载原始数据，计算预期标签 (30分)
    # 原始数据路径
    customers_path = os.path.join(workspace, "data", "customers", "customers.json")
    activity_path = os.path.join(workspace, "data", "logs", "activity_logs.json")
    consumption_path = os.path.join(workspace, "data", "logs", "consumption_logs.json")

    try:
        customers = load_json(customers_path)
        activities = load_json(activity_path)
        consumptions = load_json(consumption_path)
    except Exception as e:
        score_details.append({"item": "Loading original data", "score": 0, "max_score": 30, "passed": False, "reason": f"Cannot load original data: {str(e)}"})
        final = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 建立映射
    act_map = {a["customer_id"]: a for a in activities}
    cons_map = {c["customer_id"]: c for c in consumptions}
    cust_map = {c["customer_id"]: c for c in customers}

    expected_labels = {}
    for cust in customers:
        cid = cust["customer_id"]
        orig_labels = list(cust["labels"])  # 复制原有标签
        new_labels = set(orig_labels)

        act = act_map.get(cid)
        cons = cons_map.get(cid)
        if not act or not cons:
            continue  # 如果数据不完整，跳过（但任务中应有完整数据）

        spend = cons["quarter_spend_usd"]
        active_days = act["last_active_days"]
        risk = act["risk_level"]

        # 规则判断
        if spend >= 50000 and active_days <= 30:
            new_labels.add("VIP")
        elif spend >= 20000 and active_days <= 60:
            new_labels.add("Active Grower")
        elif spend < 20000 or active_days > 90:
            new_labels.add("At Risk")

        if risk == "high":
            new_labels.add("High Risk")

        expected_labels[cid] = sorted(list(new_labels))

    # 从result中提取
    result_labels = {}
    for item in data:
        cid = item["customer_id"]
        result_labels[cid] = sorted(item["labels"])

    # 比较每个客户
    correct_count = 0
    total_check = len(expected_labels)
    for cid, expected in expected_labels.items():
        got = result_labels.get(cid)
        if got == expected:
            correct_count += 1
        else:
            # 记录错误详情（可选）
            pass

    # 30分按比例分配
    if total_check > 0:
        label_score = int(30 * correct_count / total_check)
    else:
        label_score = 0
    passed = correct_count == total_check
    score_details.append({
        "item": "Customer labels match expected",
        "score": label_score,
        "max_score": 30,
        "passed": passed,
        "reason": f"Correct: {correct_count}/{total_check} customers"
    })
    total_score += label_score

    # 5. 干扰排除检查：是否错误使用了data_backup中的旧数据（10分）
    # 加载旧数据
    old_path = os.path.join(workspace, "data_backup", "consumption_logs_old.json")
    if os.path.isfile(old_path):
        try:
            old_data = load_json(old_path)
            old_map = {c["customer_id"]: c for c in old_data}
            # 检查是否有客户的消费被误用旧数据（比如如果C001消费用了30000而不是75000，将会导致不同标签）
            # 间接检查：如果C001的labels中不包含VIP（因为旧数据spend=30000不符合VIP），则说明误用了旧数据
            # 这里我们直接检查C001的labels是否包含VIP
            if c001_result := result_labels.get("C001"):
                if "VIP" not in c001_result:
                    # 可能是误用了旧数据，扣分
                    score_details.append({
                        "item": "Exclude old data interference",
                        "score": 0,
                        "max_score": 10,
                        "passed": False,
                        "reason": "C001 VIP label missing, possibly used old consumption data"
                    })
                else:
                    score_details.append({
                        "item": "Exclude old data interference",
                        "score": 10,
                        "max_score": 10,
                        "passed": True,
                        "reason": "No interference from backup data"
                    })
                    total_score += 10
            else:
                # C001不在结果中？特殊情况
                score_details.append({
                    "item": "Exclude old data interference",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "C001 not in result"
                })
        except:
            score_details.append({
                "item": "Exclude old data interference",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Could not parse old data"
            })
    else:
        # 如果旧数据不存在，跳过（但builder已创建）
        score_details.append({
            "item": "Exclude old data interference",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "No backup data to interfere"
        })
        total_score += 10

    # 6. 去重检查：确保没有重复标签 (10分)
    all_labels_no_dup = True
    for cid, labels in result_labels.items():
        if len(labels) != len(set(labels)):
            all_labels_no_dup = False
            break
    if all_labels_no_dup:
        score_details.append({"item": "No duplicate labels per customer", "score": 10, "max_score": 10, "passed": True, "reason": "All labels unique"})
        total_score += 10
    else:
        score_details.append({"item": "No duplicate labels per customer", "score": 0, "max_score": 10, "passed": False, "reason": "Duplicates found"})

    # 7. 客户覆盖面：是否包含了所有5个客户 (10分)
    expected_cids = set(c["customer_id"] for c in customers)
    result_cids = set(item["customer_id"] for item in data)
    if result_cids == expected_cids:
        score_details.append({"item": "All customers present", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly all 5 customers"})
        total_score += 10
    else:
        missing = expected_cids - result_cids
        extra = result_cids - expected_cids
        reason_parts = []
        if missing: reason_parts.append(f"Missing: {missing}")
        if extra: reason_parts.append(f"Extra: {extra}")
        score_details.append({"item": "All customers present", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(reason_parts)})

    # 8. 额外检查：是否输出多余的字段？超出的字段不扣分，但这里可以检查字段名仅包含customer_id和labels (5分)
    extra_fields_penalty = 0
    for item in data:
        keys = set(item.keys())
        if keys - {"customer_id", "labels"}:
            extra_fields_penalty = 5  # 有额外字段扣5分
            break
    if extra_fields_penalty == 0:
        score_details.append({"item": "No extra fields", "score": 5, "max_score": 5, "passed": True, "reason": "Only customer_id and labels"})
        total_score += 5
    else:
        score_details.append({"item": "No extra fields", "score": 0, "max_score": 5, "passed": False, "reason": "Extra fields present"})

    # 总分上限100
    total_score = min(total_score, 100)
    final = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
