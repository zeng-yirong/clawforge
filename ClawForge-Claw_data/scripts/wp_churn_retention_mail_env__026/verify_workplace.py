#!/usr/bin/env python3
"""Verify the retention cache file created by the agent."""
import json
import os
import sys
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    total = 0

    # 1) 目录 ops/ 是否存在 (10分)
    ops_dir = Path(workspace) / "ops"
    if ops_dir.is_dir():
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    # 2) ops/retention_cache.json 存在且是合法 JSON (10分)
    cache_path = ops_dir / "retention_cache.json"
    if not cache_path.is_file():
        details.append({
            "item": "retention_cache.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 后续检查无法进行，返回当前结果
        return {"total_score": total, "details": details}

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({
            "item": "retention_cache.json exists and valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON file"
        })
        total += 10
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({
            "item": "retention_cache.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        return {"total_score": total, "details": details}

    # 3) 检查数据结构——应该是一个列表或包含"emails"键的对象 (10分)
    emails = None
    if isinstance(data, list):
        emails = data
    elif isinstance(data, dict) and "emails" in data:
        emails = data["emails"]
    else:
        details.append({
            "item": "Data structure contains an array of emails",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Expected a list or object with 'emails' key"
        })
        total += 0
        # 仍尝试继续检查
        emails = []

    if emails is not None and isinstance(emails, list):
        details.append({
            "item": "Data structure contains an array of emails",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found {len(emails)} email entries"
        })
        total += 10
    else:
        details.append({
            "item": "Data structure contains an array of emails",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "emails is not a list"
        })

    # 4) 每个邮件条目必须包含字段：customer_id, customer_name, industry, news_id, headline, email_body (15分)
    required_fields = ["customer_id", "customer_name", "industry", "news_id", "headline", "email_body"]
    field_score = 0
    field_passed = True
    for i, entry in enumerate(emails):
        missing = [f for f in required_fields if f not in entry]
        if missing:
            field_passed = False
            field_score = 0
            details.append({
                "item": f"Required fields present in entry {i}",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Missing fields: {missing}"
            })
            break
    if field_passed and len(emails) > 0:
        field_score = 15
        details.append({
            "item": "Required fields present in all entries",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "All entries contain required fields"
        })
        total += 15
    elif len(emails) == 0:
        details.append({
            "item": "Required fields present in all entries",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "No email entries to check"
        })

    # 5) 正确识别高风险客户：必须包含 C001 和 C003，且每个只出现一次 (20分)
    expected_high_risk = {"C001", "C003"}
    actual_ids = set()
    for entry in emails:
        cid = entry.get("customer_id", "")
        if cid in actual_ids:
            details.append({
                "item": "Correct high-risk customers identified",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"Duplicate customer_id: {cid}"
            })
            break
        actual_ids.add(cid)
    else:
        if actual_ids == expected_high_risk:
            details.append({
                "item": "Correct high-risk customers identified",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "Exactly C001 and C003 found"
            })
            total += 20
        else:
            missing = expected_high_risk - actual_ids
            extra = actual_ids - expected_high_risk
            reason = f"Missing: {missing}, Extra: {extra}" if missing or extra else "Unexpected set"
            details.append({
                "item": "Correct high-risk customers identified",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": reason
            })

    # 6) 为每个高风险客户匹配正确的新闻（必须使用fintech opportunity新闻 N001） (20分)
    expected_industry = "fintech"
    expected_news_id = "N001"
    news_match_pass = True
    correct_count = 0
    for entry in emails:
        cid = entry.get("customer_id", "")
        ind = entry.get("industry", "")
        nid = entry.get("news_id", "")
        if cid in expected_high_risk:
            if ind == expected_industry and nid == expected_news_id:
                correct_count += 1
            else:
                news_match_pass = False
                details.append({
                    "item": "Correct news assignment for high-risk customers",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": f"Customer {cid}: expected industry=fintech, news_id=N001; got industry={ind}, news_id={nid}"
                })
                break
    if news_match_pass and correct_count == 2:
        details.append({
            "item": "Correct news assignment for high-risk customers",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Both C001 and C003 assigned fintech opportunity news N001"
        })
        total += 20

    # 7) 所有 email_body 非空 (15分)
    empty_bodies = [entry.get("customer_id") for entry in emails if not entry.get("email_body", "").strip()]
    if not empty_bodies:
        details.append({
            "item": "All email_body fields are non-empty",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "All entries have content"
        })
        total += 15
    else:
        details.append({
            "item": "All email_body fields are non-empty",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Empty email_body for customers: {empty_bodies}"
        })

    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(Path(workspace) / "workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {result['total_score']}")
