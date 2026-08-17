import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def check_path(path):
    return os.path.exists(os.path.join(workspace, path))

def load_json(path):
    with open(os.path.join(workspace, path), 'r') as f:
        return json.load(f)

score = 0
details = []

# 1. 缓存目录是否存在
if check_path("ops/cache"):
    details.append({"item": "Cache directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/cache/ found"})
    score += 10
else:
    details.append({"item": "Cache directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/cache/ not found"})

# 2. 目标文件是否存在
target = "ops/cache/retention_mail_cache.json"
if check_path(target):
    details.append({"item": "Target file exists", "score": 10, "max_score": 10, "passed": True, "reason": "retention_mail_cache.json exists"})
    score += 10
else:
    details.append({"item": "Target file exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
    # 关键错误，提前结束
    output = {"total_score": score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output))
    sys.exit(0)

# 3. JSON 语法检查
try:
    data = load_json(target)
    details.append({"item": "JSON parseable", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
    score += 10
except Exception as e:
    details.append({"item": "JSON parseable", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
    output = {"total_score": score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    print(json.dumps(output))
    sys.exit(0)

# 4. 顶层必须是列表
if isinstance(data, list):
    details.append({"item": "Top-level structure is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Array of emails"})
    score += 10
    emails = data
else:
    details.append({"item": "Top-level structure is a list", "score": 0, "max_score": 10, "passed": False, "reason": "Not a list"})
    emails = []

# 5. 数组长度（期望 1 条记录）
expected_count = 1
if len(emails) == expected_count:
    details.append({"item": "Correct number of emails", "score": 10, "max_score": 10, "passed": True, "reason": f"Exactly {expected_count} email(s)"})
    score += 10
else:
    details.append({"item": "Correct number of emails", "score": 0, "max_score": 10, "passed": False, "reason": f"Found {len(emails)} email(s), expected {expected_count}"})

# 如果列表非空，逐字段验证
if len(emails) > 0:
    mail = emails[0]

    # 6. customer_id
    if mail.get("customer_id") == "cust_001":
        details.append({"item": "customer_id correct", "score": 10, "max_score": 10, "passed": True, "reason": "cust_001"})
        score += 10
    else:
        details.append({"item": "customer_id correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {mail.get('customer_id')}, expected cust_001"})

    # 7. email
    if mail.get("email") == "alice@ledgerflow.com":
        details.append({"item": "email correct", "score": 10, "max_score": 10, "passed": True, "reason": "alice@ledgerflow.com"})
        score += 10
    else:
        details.append({"item": "email correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {mail.get('email')}, expected alice@ledgerflow.com"})

    # 8. headline
    expected_headline = "New regulations increase compliance costs for fintech firms"
    if mail.get("headline") == expected_headline:
        details.append({"item": "headline correct", "score": 10, "max_score": 10, "passed": True, "reason": "Correct headline"})
        score += 10
    else:
        details.append({"item": "headline correct", "score": 0, "max_score": 10, "passed": False, "reason": f"Got {mail.get('headline')}, expected {expected_headline}"})

    # 9. body 非空
    body = mail.get("body", "")
    if isinstance(body, str) and len(body) > 0:
        details.append({"item": "body non-empty string", "score": 10, "max_score": 10, "passed": True, "reason": "Body present"})
        score += 10
    else:
        details.append({"item": "body non-empty string", "score": 0, "max_score": 10, "passed": False, "reason": "Body missing or empty"})
else:
    # 列表为空，无法检查字段
    for name in ["customer_id", "email", "headline", "body"]:
        details.append({"item": f"{name} correct", "score": 0, "max_score": 10, "passed": False, "reason": "No emails to check"})

# 10. 没有引入无关客户（如 cust_003）
cust_ids = [e.get("customer_id") for e in emails]
if "cust_003" not in cust_ids:
    details.append({"item": "No unintended customers", "score": 10, "max_score": 10, "passed": True, "reason": "cust_003 not included"})
    score += 10
else:
    details.append({"item": "No unintended customers", "score": 0, "max_score": 10, "passed": False, "reason": "cust_003 found unexpectedly"})

# 总分封顶 100
total_score = min(score, 100)
output = {"total_score": total_score, "details": details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(output, f, indent=2)
print(json.dumps(output))
