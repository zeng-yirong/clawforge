import json
import os
import sys

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. cache目录存在 (10分)
    cache_dir = os.path.join(workspace, "cache")
    exists_cache = os.path.isdir(cache_dir)
    details.append({
        "item": "cache directory exists",
        "score": 10 if exists_cache else 0,
        "max_score": 10,
        "passed": exists_cache,
        "reason": "cache directory found" if exists_cache else "cache directory not found"
    })
    if exists_cache:
        total_score += 10

    # 2. retention_emails.json存在 (10分)
    email_file = os.path.join(cache_dir, "retention_emails.json")
    exists_file = os.path.isfile(email_file)
    details.append({
        "item": "retention_emails.json exists",
        "score": 10 if exists_file else 0,
        "max_score": 10,
        "passed": exists_file,
        "reason": "file found" if exists_file else "file not found"
    })
    if exists_file:
        total_score += 10

    if not exists_file:
        # 无法继续验证，给出剩余分数为0
        for item_name, max_s in [("JSON is valid", 10), ("Structure has retention_emails", 10),
                                  ("Array length == 1", 10), ("Required fields present", 10),
                                  ("Field values correct", 20), ("Email body contains headline and name", 10)]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "retention_emails.json missing"
            })
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return

    # 3. JSON合法 (10分)
    try:
        emails_data = load_json(email_file)
        json_valid = True
        details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "successfully parsed"
        })
        total_score += 10
    except Exception as e:
        json_valid = False
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {str(e)}"
        })
        # 剩余的无法继续
        for item_name, max_s in [("Structure has retention_emails", 10),
                                  ("Array length == 1", 10), ("Required fields present", 10),
                                  ("Field values correct", 20), ("Email body contains headline and name", 10)]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "JSON invalid"
            })
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return

    # 4. 结构包含retention_emails数组 (10分)
    if isinstance(emails_data, dict) and "retention_emails" in emails_data:
        arr = emails_data["retention_emails"]
        if isinstance(arr, list):
            struct_ok = True
            details.append({
                "item": "Structure has retention_emails array",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "found retention_emails list"
            })
            total_score += 10
        else:
            struct_ok = False
            details.append({
                "item": "Structure has retention_emails array",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "retention_emails is not a list"
            })
    else:
        struct_ok = False
        details.append({
            "item": "Structure has retention_emails array",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "retention_emails key missing or not a dict"
        })

    if not struct_ok:
        for item_name, max_s in [("Array length == 1", 10), ("Required fields present", 10),
                                  ("Field values correct", 20), ("Email body contains headline and name", 10)]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "structure invalid"
            })
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return

    # 5. 数组长度==1 (10分)
    length_ok = len(arr) == 1
    details.append({
        "item": "Array length == 1",
        "score": 10 if length_ok else 0,
        "max_score": 10,
        "passed": length_ok,
        "reason": f"found {len(arr)} entries" if not length_ok else "exactly one entry"
    })
    if length_ok:
        total_score += 10

    # 6. 必要字段存在 (10分)
    required_fields = ["customer_id", "customer_name", "industry", "headline"]
    entry = arr[0] if arr else {}
    fields_present = all(field in entry for field in required_fields)
    details.append({
        "item": "Required fields present",
        "score": 10 if fields_present else 0,
        "max_score": 10,
        "passed": fields_present,
        "reason": f"fields: {list(entry.keys())}" if fields_present else f"missing some of {required_fields}"
    })
    if fields_present:
        total_score += 10

    if not fields_present or not length_ok:
        # 字段值检查和body检查跳过
        for item_name, max_s in [("Field values correct", 20), ("Email body contains headline and name", 10)]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "prerequisite checks failed"
            })
        result = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(result, f)
        return

    # 7. 字段值正确 (20分, 每个字段5分)
    # 从参考文件中获取期望值
    # 读取customers.json找到C001的name和industry
    try:
        cust_path = os.path.join(workspace, "data/customers/customers.json")
        cust_data = load_json(cust_path)
        cust_list = cust_data.get("customers", [])
        target_cust = None
        for c in cust_list:
            if c["customer_id"] == "C001":
                target_cust = c
                break
        expected_name = target_cust["customer_name"] if target_cust else "LedgerFlow"
        expected_industry = target_cust["industry"] if target_cust else "fintech"
    except:
        expected_name = "LedgerFlow"
        expected_industry = "fintech"

    # 读取news_samples.json找到fintech行业的一条新闻headline
    try:
        news_path = os.path.join(workspace, "data/news/news_samples.json")
        news_data = load_json(news_path)
        news_list = news_data.get("news_samples", [])
        expected_headline = ""
        for n in news_list:
            if n.get("industry") == "fintech":
                expected_headline = n.get("headline", "Fintech Startup Raises $100M")
                break
        if not expected_headline:
            expected_headline = "Fintech Startup Raises $100M"
    except:
        expected_headline = "Fintech Startup Raises $100M"

    expected_id = "C001"

    checks = [
        ("customer_id", expected_id),
        ("customer_name", expected_name),
        ("industry", expected_industry),
        ("headline", expected_headline)
    ]
    field_score = 0
    field_reasons = []
    for field, expected in checks:
        val = entry.get(field)
        if val == expected:
            field_score += 5
            field_reasons.append(f"{field}: correct")
        else:
            field_reasons.append(f"{field}: got '{val}', expected '{expected}'")
    details.append({
        "item": "Field values correct",
        "score": field_score,
        "max_score": 20,
        "passed": field_score == 20,
        "reason": "; ".join(field_reasons)
    })
    total_score += field_score

    # 8. Email body包含headline和customer_name (10分, 各5分)
    body = entry.get("email_body", "")
    body_score = 0
    body_reasons = []
    if expected_headline and expected_headline in body:
        body_score += 5
        body_reasons.append("headline found in body")
    else:
        body_reasons.append(f"headline '{expected_headline}' not found in body")
    if expected_name and expected_name in body:
        body_score += 5
        body_reasons.append("customer_name found in body")
    else:
        body_reasons.append(f"customer_name '{expected_name}' not found in body")
    details.append({
        "item": "Email body contains headline and name",
        "score": body_score,
        "max_score": 10,
        "passed": body_score == 10,
        "reason": "; ".join(body_reasons)
    })
    total_score += body_score

    # 写入结果
    result = {
        "total_score": min(total_score, 100),
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    main()
