import sys
import os
import json

def verify(workspace):
    if not os.path.isdir(workspace):
        print("Workspace does not exist.")
        sys.exit(1)

    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    if dir_exists:
        total_score += 10
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    # 2. 检查 label_updates.json 是否存在 (10分)
    result_file = os.path.join(workspace, "ops", "label_updates.json")
    file_exists = os.path.isfile(result_file)
    if file_exists:
        total_score += 10
        details.append({
            "item": "label_updates.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/label_updates.json found"
        })
    else:
        details.append({
            "item": "label_updates.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/label_updates.json not found"
        })
        # 如果文件不存在，直接结束
        score_data = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_data, f)
        return

    # 3. 解析 JSON 合法性 (10分)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Root must be a list")
        total_score += 10
        details.append({
            "item": "JSON format and structure",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON list"
        })
    except Exception as e:
        total_score += 0
        details.append({
            "item": "JSON format and structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Parse error: {str(e)}"
        })
        score_data = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_data, f)
        return

    # 4. 检查字段完整性：每个对象必须有 customer_id 和 new_tier (20分)
    field_score = 20
    field_passed = True
    field_reason = ""
    for idx, record in enumerate(data):
        if not isinstance(record, dict):
            field_passed = False
            field_reason = f"Record {idx} is not a dict"
            break
        if "customer_id" not in record or "new_tier" not in record:
            field_passed = False
            field_reason = f"Record {idx} missing customer_id or new_tier"
            break
    if field_passed:
        total_score += field_score
        details.append({
            "item": "All records contain customer_id and new_tier",
            "score": field_score,
            "max_score": field_score,
            "passed": True,
            "reason": "Fields present for all entries"
        })
    else:
        details.append({
            "item": "All records contain customer_id and new_tier",
            "score": 0,
            "max_score": field_score,
            "passed": False,
            "reason": field_reason
        })

    # 5. 检查是否包含所有需要的客户 (20分)
    expected_customers = {"CarePulse", "LedgerFlow"}
    found_customers = set(record.get("customer_id") for record in data if isinstance(record, dict))
    if found_customers == expected_customers:
        total_score += 20
        details.append({
            "item": "Customer coverage",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Both CarePulse and LedgerFlow present"
        })
    else:
        missing = expected_customers - found_customers
        extra = found_customers - expected_customers
        total_score += 0
        details.append({
            "item": "Customer coverage",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing: {missing}. Extra: {extra}" if missing or extra else "Unexpected"
        })

    # 6. 校验每个客户的标签是否正确 (50分 = 每个客户25分)
    correct_labels = {
        "CarePulse": "gold",
        "LedgerFlow": "bronze"
    }
    tier_score_per = 25
    tier_score_total = 0
    tier_items = []
    for cid, expected_tier in correct_labels.items():
        # 找到该客户记录
        rec = None
        for record in data:
            if isinstance(record, dict) and record.get("customer_id") == cid:
                rec = record
                break
        if rec is None:
            tier_items.append({
                "item": f"Tier for {cid}",
                "score": 0,
                "max_score": tier_score_per,
                "passed": False,
                "reason": "Not found in result"
            })
            continue
        actual_tier = rec.get("new_tier")
        if actual_tier == expected_tier:
            tier_score_total += tier_score_per
            tier_items.append({
                "item": f"Tier for {cid}",
                "score": tier_score_per,
                "max_score": tier_score_per,
                "passed": True,
                "reason": f"Correct: {actual_tier}"
            })
        else:
            tier_items.append({
                "item": f"Tier for {cid}",
                "score": 0,
                "max_score": tier_score_per,
                "passed": False,
                "reason": f"Expected {expected_tier}, got {actual_tier}"
            })
    total_score += tier_score_total
    details.extend(tier_items)

    # 7. 额外扣分项：不允许有多余字段，每个多余字段扣5分（最多扣10分）
    extra_field_deduction = 0
    for record in data:
        if isinstance(record, dict):
            keys = set(record.keys())
            allowed = {"customer_id", "new_tier"}
            extra = keys - allowed
            if extra:
                extra_field_deduction += 5 * len(extra)
                if extra_field_deduction >= 10:
                    break
    if extra_field_deduction > 0:
        actual_deduction = min(extra_field_deduction, 10)
        total_score = max(total_score - actual_deduction, 0)
        details.append({
            "item": "No extra fields penalty",
            "score": -actual_deduction,
            "max_score": 0,
            "passed": actual_deduction == 0,
            "reason": f"Deducted {actual_deduction} points for extra fields"
        })

    # 确保总分在0-100之间
    total_score = max(0, min(total_score, 100))

    # 写入评分结果
    score_data = {"total_score": total_score, "details": details}
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
