"""
评分脚本：检查 Agent 产出的挽留邮件缓存文件
"""
import sys
import json
import os
from pathlib import Path

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops directory"})
        total_score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Missing ops directory"})

    # 2. 检查 retention_emails.json 是否存在
    email_file = ops_dir / "retention_emails.json"
    if email_file.is_file():
        details.append({"item": "retention_emails.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total_score += 10
    else:
        details.append({"item": "retention_emails.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 后续项无法检查，直接返回
        result = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 检查 JSON 格式合法性
    try:
        data = load_json(str(email_file))
        details.append({"item": "JSON format valid", "score": 10, "max_score": 10, "passed": True, "reason": "Parsed successfully"})
        total_score += 10
    except Exception as e:
        details.append({"item": "JSON format valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {str(e)}"})
        result = {"total_score": total_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 期望的高风险客户（根据 activity_logs 筛选）
    # 规则：risk_level=high, last_active_days>30, usage_trend=down, ticket_sentiment=negative
    expected_customers = []
    try:
        logs_data = load_json(str(ws / "data/logs/activity_logs.json"))
        for rec in logs_data.get("activity_logs", []):
            if (rec["risk_level"] == "high" and rec["last_active_days"] > 30
                    and rec["usage_trend"] == "down" and rec["ticket_sentiment"] == "negative"):
                expected_customers.append(rec["customer_id"])
    except Exception:
        expected_customers = []  # 如果日志文件有问题，当作0个

    # 对每个预期客户，计算期望的 news_id
    # 从 news_samples 中找行业匹配 + tone=opportunity 的第一条
    expected_news_map = {}
    try:
        news_data = load_json(str(ws / "data/news/news_samples.json"))
        news_by_industry = {}
        for n in news_data.get("news_samples", []):
            if n["tone"] == "opportunity":
                news_by_industry.setdefault(n["industry"], []).append(n["news_id"])
    except Exception:
        news_by_industry = {}

    # 需要 customer 的 industry 信息，从 customers.json 获取
    industry_map = {}
    try:
        cust_data = load_json(str(ws / "data/customers/customers.json"))
        for c in cust_data.get("customers", []):
            industry_map[c["customer_id"]] = c["industry"]
    except Exception:
        industry_map = {}

    for cid in expected_customers:
        ind = industry_map.get(cid, "")
        news_ids = news_by_industry.get(ind, [])
        if news_ids:
            expected_news_map[cid] = news_ids[0]  # 取第一条

    # 4. 检查 emails 列表长度
    emails = data.get("emails", [])
    expected_len = len(expected_customers)
    if len(emails) == expected_len:
        details.append({"item": "email list length correct", "score": 20, "max_score": 20, "passed": True, "reason": f"Expected {expected_len}, got {len(emails)}"})
        total_score += 20
    else:
        details.append({"item": "email list length correct", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_len}, got {len(emails)}"})

    # 5. 检查每个 email 的 customer_id 是否正确
    customer_id_ok = True
    customer_ids_in_emails = {e.get("customer_id") for e in emails}
    expected_set = set(expected_customers)
    if customer_ids_in_emails == expected_set:
        details.append({"item": "customer IDs match expected set", "score": 20, "max_score": 20, "passed": True, "reason": "All expected customer IDs present"})
        total_score += 20
    else:
        missing = expected_set - customer_ids_in_emails
        extra = customer_ids_in_emails - expected_set
        reason = f"Missing: {missing}, Extra: {extra}"
        details.append({"item": "customer IDs match expected set", "score": 0, "max_score": 20, "passed": False, "reason": reason})
        customer_id_ok = False

    # 6. 检查每个 email 的 news_id 是否正确
    news_id_ok = True
    for e in emails:
        cid = e.get("customer_id")
        expected_nid = expected_news_map.get(cid)
        actual_nid = e.get("news_id")
        if expected_nid and actual_nid != expected_nid:
            news_id_ok = False
            break
    if news_id_ok:
        details.append({"item": "news IDs match expected per customer", "score": 20, "max_score": 20, "passed": True, "reason": "All news IDs correct"})
        total_score += 20
    else:
        details.append({"item": "news IDs match expected per customer", "score": 0, "max_score": 20, "passed": False, "reason": "One or more news IDs wrong"})

    # 7. 检查 subject 和 body 非空且有一定长度
    content_ok = True
    reason_content = ""
    for e in emails:
        subj = e.get("subject", "")
        body = e.get("body", "")
        if len(subj) < 5 or len(body) < 20:
            content_ok = False
            reason_content = f"Customer {e.get('customer_id')}: subject len={len(subj)}, body len={len(body)}"
            break
    if content_ok:
        details.append({"item": "subject and body have meaningful content", "score": 10, "max_score": 10, "passed": True, "reason": "All emails have valid subject and body"})
        total_score += 10
    else:
        details.append({"item": "subject and body have meaningful content", "score": 0, "max_score": 10, "passed": False, "reason": reason_content})

    # 最终分数
    total_score = min(total_score, 100)  # 防止溢出
    result = {"total_score": total_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
