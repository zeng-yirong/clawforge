import sys
import os
import json

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(WORKSPACE, rel_path)
    if not os.path.isfile(full):
        return None, f"File not found: {rel_path}"
    try:
        with open(full, "r") as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"

def check_fields(entry, required_fields):
    for f in required_fields:
        if f not in entry:
            return False, f"Missing field '{f}'"
    return True, None

def evaluate():
    details = []
    total = 0

    # 1) 最终文件存在
    data, err = load_json("ops/retention_mail_cache.json")
    if err:
        details.append({"item": "File existence", "score": 0, "max_score": 10, "passed": False, "reason": err})
        # 不能继续检查，直接写分
        score = {"total_score": 0, "details": details}
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        print("FAIL: file not found or broken")
        return

    details.append({"item": "File existence", "score": 10, "max_score": 10, "passed": True, "reason": "ops/retention_mail_cache.json exists"})
    total += 10

    # 2) JSON 是列表
    if not isinstance(data, list):
        details.append({"item": "JSON root is list", "score": 0, "max_score": 10, "passed": False, "reason": "Root is not a list"})
        total += 0
    else:
        details.append({"item": "JSON root is list", "score": 10, "max_score": 10, "passed": True, "reason": "Root is a list"})
        total += 10

    # 3) 列表长度 (期望 2: cust-001, cust-002)
    expected_len = 2
    actual_len = len(data)
    if actual_len == expected_len:
        details.append({"item": "List length", "score": 10, "max_score": 10, "passed": True, "reason": f"Length is {actual_len}"})
        total += 10
    else:
        details.append({"item": "List length", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_len}, got {actual_len}"})

    # 4) 每个元素必备字段
    required_fields = ["customer_id", "industry", "matched_news_ids"]
    field_ok = True
    for i, entry in enumerate(data):
        ok, reason = check_fields(entry, required_fields)
        if not ok:
            details.append({"item": f"Required fields in entry {i}", "score": 0, "max_score": 15, "passed": False, "reason": reason})
            field_ok = False
            break
    if field_ok:
        details.append({"item": "All entries have required fields", "score": 15, "max_score": 15, "passed": True, "reason": "customer_id, industry, matched_news_ids present"})
        total += 15

    # 5) 客户 ID 属于正确的高风险客户集合（cust-001, cust-002）
    expected_customers = {"cust-001", "cust-002"}
    actual_customers = {entry.get("customer_id") for entry in data if isinstance(entry, dict)}
    if actual_customers == expected_customers:
        details.append({"item": "Customer IDs match expected set", "score": 15, "max_score": 15, "passed": True, "reason": "Only cust-001 and cust-002 present"})
        total += 15
    else:
        details.append({"item": "Customer IDs match expected set", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_customers}, got {actual_customers}"})

    # 6) matched_news_ids 正确
    expected_news = {
        "cust-001": ["news-001"],
        "cust-002": ["news-003"]
    }
    news_ok = True
    for entry in data:
        cid = entry.get("customer_id")
        expected_ids = set(expected_news.get(cid, []))
        actual_ids = set(entry.get("matched_news_ids", []))
        if actual_ids != expected_ids:
            news_ok = False
            details.append({"item": f"News match for {cid}", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_ids}, got {actual_ids}"})
            break
    if news_ok:
        details.append({"item": "News matching correct", "score": 20, "max_score": 20, "passed": True, "reason": "All matched_news_ids are correct"})
        total += 20

    # 7) 没有额外客户（如 cust-003, cust-999）
    if actual_customers.issuperset(expected_customers) and len(actual_customers) == len(expected_customers):
        details.append({"item": "No extra customers", "score": 10, "max_score": 10, "passed": True, "reason": "No unexpected customer IDs"})
        total += 10
    else:
        details.append({"item": "No extra customers", "score": 0, "max_score": 10, "passed": False, "reason": f"Extra customers present: {actual_customers - expected_customers}"})

    # 8) 字段类型检查
    type_ok = True
    for entry in data:
        if not isinstance(entry.get("customer_id"), str) or not isinstance(entry.get("industry"), str) or not isinstance(entry.get("matched_news_ids"), list):
            type_ok = False
            details.append({"item": "Field types", "score": 0, "max_score": 10, "passed": False, "reason": "Type mismatch (customer_id/industry must be str, matched_news_ids must be list)"})
            break
    if type_ok:
        details.append({"item": "Field types", "score": 10, "max_score": 10, "passed": True, "reason": "All field types correct"})
        total += 10

    # 写入评分文件
    score = {"total_score": total, "details": details}
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump(score, f, indent=2)
    print(f"Score: {total}/100")

if __name__ == "__main__":
    evaluate()
