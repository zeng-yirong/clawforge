import json
import os
import sys

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1) 目录结构检查：cache/ 是否存在 (10分)
    cache_path = os.path.join(workspace, "cache")
    if os.path.isdir(cache_path):
        details.append({"item": "cache directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "cache/ found"})
        total_score += 10
    else:
        details.append({"item": "cache directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "cache/ missing"})

    # 2) 文件存在性：cache/retention_emails.json (10分)
    email_path = os.path.join(cache_path, "retention_emails.json")
    if os.path.isfile(email_path):
        details.append({"item": "retention_emails.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "retention_emails.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        # 无法继续检查，返回当前结果
        return {"total_score": total_score, "details": details}

    # 3) JSON 合法性 (10分)
    try:
        with open(email_path, "r") as f:
            content = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parse success"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {str(e)}"})
        return {"total_score": total_score, "details": details}

    # 4) 关键字段存在性 (15分)
    required_keys = {"customer_id", "customer_name", "subject", "body", "news_id", "news_headline"}
    if isinstance(content, dict) and required_keys.issubset(content.keys()):
        details.append({"item": "all required keys present", "score": 15, "max_score": 15, "passed": True, "reason": "keys found"})
        total_score += 15
    else:
        missing = required_keys - set(content.keys())
        details.append({"item": "all required keys present", "score": 0, "max_score": 15, "passed": False, "reason": f"missing keys: {missing}"})

    # 5) 客户ID 正确 (20分)
    if content.get("customer_id") == "C001":
        details.append({"item": "customer_id is C001", "score": 20, "max_score": 20, "passed": True, "reason": "correct high-risk customer"})
        total_score += 20
    else:
        details.append({"item": "customer_id is C001", "score": 0, "max_score": 20, "passed": False, "reason": f"got {content.get('customer_id')}"})

    # 6) 客户名称正确 (5分)
    if content.get("customer_name") == "LedgerFlow":
        details.append({"item": "customer_name is LedgerFlow", "score": 5, "max_score": 5, "passed": True, "reason": "name match"})
        total_score += 5
    else:
        details.append({"item": "customer_name is LedgerFlow", "score": 0, "max_score": 5, "passed": False, "reason": f"got {content.get('customer_name')}"})

    # 7) 新闻ID 正确 (15分)
    if content.get("news_id") == "N001":
        details.append({"item": "news_id is N001", "score": 15, "max_score": 15, "passed": True, "reason": "correct opportunity news for fintech"})
        total_score += 15
    else:
        details.append({"item": "news_id is N001", "score": 0, "max_score": 15, "passed": False, "reason": f"got {content.get('news_id')}"})

    # 8) 新闻标题正确 (5分)
    expected_headline = "Open Banking Regulation Boosts Fintech Growth"
    if content.get("news_headline") == expected_headline:
        details.append({"item": "news_headline matches expected", "score": 5, "max_score": 5, "passed": True, "reason": "headline match"})
        total_score += 5
    else:
        details.append({"item": "news_headline matches expected", "score": 0, "max_score": 5, "passed": False, "reason": f"got {content.get('news_headline')}"})

    # 9) 主题行包含客户名 (5分)
    subject = content.get("subject", "")
    if "LedgerFlow" in subject:
        details.append({"item": "subject contains company name", "score": 5, "max_score": 5, "passed": True, "reason": "company name in subject"})
        total_score += 5
    else:
        details.append({"item": "subject contains company name", "score": 0, "max_score": 5, "passed": False, "reason": "subject missing company name"})

    # 10) 正文包含新闻标题或关键词 (5分)
    body = content.get("body", "")
    if "Open Banking" in body or "Boosts Fintech Growth" in body:
        details.append({"item": "body references selected news", "score": 5, "max_score": 5, "passed": True, "reason": "news reference detected"})
        total_score += 5
    else:
        details.append({"item": "body references selected news", "score": 0, "max_score": 5, "passed": False, "reason": "body missing news reference"})

    # 最终总分 (应100分)
    return {"total_score": min(total_score, 100), "details": details}


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {result['total_score']}/100")
