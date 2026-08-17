import json
import os
import sys

def verify(workspace):
    results = []
    total_score = 0

    # 1. 目录结构检查 (权重10)
    dirs_to_check = ["ops", "data/customers", "data/logs", "data/news"]
    dir_missing = False
    for d in dirs_to_check:
        if not os.path.isdir(os.path.join(workspace, d)):
            dir_missing = True
            break
    if not dir_missing:
        results.append({"item": "Required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories present."})
        total_score += 10
    else:
        results.append({"item": "Required directories exist", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing directories: {d}"})

    # 2. 产物文件存在性 (权重10)
    target_file = os.path.join(workspace, "ops", "retention_email_cache.json")
    if os.path.isfile(target_file):
        results.append({"item": "Output file ops/retention_email_cache.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
        total_score += 10
    else:
        results.append({"item": "Output file ops/retention_email_cache.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found."})
        # 后续检查无法进行，直接返回
        return finalize(results, total_score)

    # 3. JSON 合法性 (权重10)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            results.append({"item": "Output is valid JSON list", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed as list."})
            total_score += 10
        else:
            results.append({"item": "Output is valid JSON list", "score": 0, "max_score": 10, "passed": False, "reason": "Not a list."})
            return finalize(results, total_score)
    except (json.JSONDecodeError, IOError) as e:
        results.append({"item": "Output is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        return finalize(results, total_score)

    # 4. 记录数量 (权重20) — 预期只有1条（C001）
    if len(data) == 1:
        results.append({"item": "Number of retention emails (expected 1)", "score": 20, "max_score": 20, "passed": True, "reason": "Correct count."})
        total_score += 20
    else:
        results.append({"item": "Number of retention emails (expected 1)", "score": 0, "max_score": 20, "passed": False, "reason": f"Got {len(data)} records."})

    # 5. 必要字段 (权重20)
    record = data[0] if data else {}
    required_fields = ["customer_id", "email_subject", "email_body"]
    field_ok = all(field in record for field in required_fields)
    if field_ok:
        results.append({"item": "Record contains required fields", "score": 20, "max_score": 20, "passed": True, "reason": "customer_id, email_subject, email_body present."})
        total_score += 20
    else:
        missing = [f for f in required_fields if f not in record]
        results.append({"item": "Record contains required fields", "score": 0, "max_score": 20, "passed": False, "reason": f"Missing fields: {missing}"})

    # 6. 客户ID正确性 (权重15)
    expected_customer_id = "C001"
    if record.get("customer_id") == expected_customer_id:
        results.append({"item": "Email targets correct high-risk customer (C001)", "score": 15, "max_score": 15, "passed": True, "reason": "Customer ID matches."})
        total_score += 15
    else:
        results.append({"item": "Email targets correct high-risk customer (C001)", "score": 0, "max_score": 15, "passed": False, "reason": f"Got {record.get('customer_id')} instead."})

    # 7. 新闻标题引用 (权重15)
    # 期望引用 "Blockchain Revolution in Fintech" (完整或部分)
    expected_news_keyword = "Blockchain Revolution"
    body = record.get("email_body", "")
    subject = record.get("email_subject", "")
    if expected_news_keyword in body or expected_news_keyword in subject:
        results.append({"item": "Email references correct opportunity news (Blockchain Revolution in Fintech)", "score": 15, "max_score": 15, "passed": True, "reason": "News headline found."})
        total_score += 15
    else:
        results.append({"item": "Email references correct opportunity news (Blockchain Revolution in Fintech)", "score": 0, "max_score": 15, "passed": False, "reason": "Expected news not found in email."})

    # 汇总得分
    return finalize(results, total_score)

def finalize(results, total_score):
    # 写入 workplace_score.json
    score_data = {
        "total_score": total_score,
        "details": results
    }
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)
    # 也可打印
    print(f"Total score: {total_score}/100")
    for r in results:
        print(f"  {r['item']}: {r['score']}/{r['max_score']} {'✓' if r['passed'] else '✗'} - {r['reason']}")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)
    verify(workspace)
