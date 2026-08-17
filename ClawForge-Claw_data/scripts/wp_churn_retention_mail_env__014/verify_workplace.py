import sys
import json
import os
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0
    max_total = 100

    # 1. cache 目录存在 (5分)
    cache_dir = ws / "cache"
    if cache_dir.is_dir():
        details.append({"item": "Cache directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "cache/ found"})
        total_score += 5
    else:
        details.append({"item": "Cache directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "cache/ missing"})

    # 2. 产物文件存在 (10分)
    result_file = cache_dir / "retention_emails.json"
    if result_file.is_file():
        details.append({"item": "retention_emails.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "retention_emails.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # 如果文件不存在，后续检查全部跳过
        details.append({"item": "JSON is valid and non-empty", "score": 0, "max_score": 15, "passed": False, "reason": "file missing"})
        details.append({"item": "Correct number of records (should be 1)", "score": 0, "max_score": 15, "passed": False, "reason": "file missing"})
        details.append({"item": "Record contains required fields", "score": 0, "max_score": 20, "passed": False, "reason": "file missing"})
        details.append({"item": "customer_id is correct", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        details.append({"item": "customer_name is correct", "score": 0, "max_score": 5, "passed": False, "reason": "file missing"})
        details.append({"item": "industry is correct", "score": 0, "max_score": 5, "passed": False, "reason": "file missing"})
        details.append({"item": "news_id is correct", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        details.append({"item": "news_headline is correct", "score": 0, "max_score": 5, "passed": False, "reason": "file missing"})
        details.append({"item": "email_body is present and non-empty", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        write_score(details, total_score, max_total)
        return

    # 3. JSON 合法性 (15分)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        if isinstance(data, list) and len(data) > 0:
            details.append({"item": "JSON is valid and non-empty", "score": 15, "max_score": 15, "passed": True, "reason": "valid array with records"})
            total_score += 15
        else:
            details.append({"item": "JSON is valid and non-empty", "score": 0, "max_score": 15, "passed": False, "reason": "not an array or empty"})
            write_score(details, total_score, max_total)
            return
    except Exception as e:
        details.append({"item": "JSON is valid and non-empty", "score": 0, "max_score": 15, "passed": False, "reason": f"parse error: {e}"})
        write_score(details, total_score, max_total)
        return

    # 4. 记录数量应为1 (15分)
    if len(data) == 1:
        details.append({"item": "Correct number of records (should be 1)", "score": 15, "max_score": 15, "passed": True, "reason": "exactly 1 record"})
        total_score += 15
    else:
        details.append({"item": "Correct number of records (should be 1)", "score": 0, "max_score": 15, "passed": False, "reason": f"found {len(data)} records"})

    record = data[0]

    # 5. 必备字段检查 (20分)
    required = ["customer_id", "customer_name", "industry", "news_id", "news_headline", "email_body"]
    missing = [f for f in required if f not in record]
    if not missing:
        details.append({"item": "Record contains required fields", "score": 20, "max_score": 20, "passed": True, "reason": "all required fields present"})
        total_score += 20
    else:
        details.append({"item": "Record contains required fields", "score": 0, "max_score": 20, "passed": False, "reason": f"missing: {missing}"})

    # 6. customer_id 正确 (10分)
    if record.get("customer_id") == "C001":
        details.append({"item": "customer_id is correct", "score": 10, "max_score": 10, "passed": True, "reason": "C001"})
        total_score += 10
    else:
        details.append({"item": "customer_id is correct", "score": 0, "max_score": 10, "passed": False, "reason": f"got {record.get('customer_id')}"})

    # 7. customer_name 正确 (5分)
    if record.get("customer_name") == "LedgerFlow":
        details.append({"item": "customer_name is correct", "score": 5, "max_score": 5, "passed": True, "reason": "LedgerFlow"})
        total_score += 5
    else:
        details.append({"item": "customer_name is correct", "score": 0, "max_score": 5, "passed": False, "reason": f"got {record.get('customer_name')}"})

    # 8. industry 正确 (5分)
    if record.get("industry") == "fintech":
        details.append({"item": "industry is correct", "score": 5, "max_score": 5, "passed": True, "reason": "fintech"})
        total_score += 5
    else:
        details.append({"item": "industry is correct", "score": 0, "max_score": 5, "passed": False, "reason": f"got {record.get('industry')}"})

    # 9. news_id 正确 (10分)
    if record.get("news_id") == "N001":
        details.append({"item": "news_id is correct", "score": 10, "max_score": 10, "passed": True, "reason": "N001"})
        total_score += 10
    else:
        details.append({"item": "news_id is correct", "score": 0, "max_score": 10, "passed": False, "reason": f"got {record.get('news_id')}"})

    # 10. news_headline 正确 (5分)
    expected_headline = "Regulatory Costs Squeeze Fintech Margins"
    if record.get("news_headline") == expected_headline:
        details.append({"item": "news_headline is correct", "score": 5, "max_score": 5, "passed": True, "reason": "matches expected"})
        total_score += 5
    else:
        details.append({"item": "news_headline is correct", "score": 0, "max_score": 5, "passed": False, "reason": f"got '{record.get('news_headline')}'"})

    # 11. email_body 非空 (10分)
    body = record.get("email_body", "")
    if isinstance(body, str) and len(body.strip()) > 0:
        details.append({"item": "email_body is present and non-empty", "score": 10, "max_score": 10, "passed": True, "reason": "non-empty string"})
        total_score += 10
    else:
        details.append({"item": "email_body is present and non-empty", "score": 0, "max_score": 10, "passed": False, "reason": "missing or empty"})

    write_score(details, total_score, max_total)


def write_score(details, total_score, max_total):
    # 确保总分不超过 max_total
    total_score = min(total_score, max_total)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/{max_total}")


if __name__ == "__main__":
    verify()
