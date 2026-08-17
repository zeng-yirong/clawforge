import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # 1. 检查 output 目录是否存在（10分）
    output_dir = os.path.join(workspace, "output")
    if os.path.isdir(output_dir):
        details.append({"item": "output directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "output folder present"})
        total += 10
    else:
        details.append({"item": "output directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "output folder missing"})

    # 2. 检查 retention_email_cache.json 是否存在且合法（20分）
    cache_path = os.path.join(output_dir, "retention_email_cache.json")
    if os.path.isfile(cache_path):
        try:
            with open(cache_path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) or isinstance(data, list):
                details.append({"item": "cache file valid JSON", "score": 20, "max_score": 20, "passed": True, "reason": "file exists and valid JSON"})
                total += 20
            else:
                raise ValueError
        except:
            details.append({"item": "cache file valid JSON", "score": 0, "max_score": 20, "passed": False, "reason": "invalid JSON structure"})
    else:
        details.append({"item": "cache file valid JSON", "score": 0, "max_score": 20, "passed": False, "reason": "file not found"})
        # 如果文件不存在，后续无法继续，直接返回
        write_score(total, details)
        return

    # 假设 data 是列表，如果不是，尝试适配（但期望是列表）
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict) and "emails" in data:
        entries = data["emails"]
    else:
        # 尝试将字典转为列表（如果只有一个客户）
        if any(k.startswith("cust_") for k in data):
            entries = [data]
        else:
            details.append({"item": "cache structure", "score": 0, "max_score": 10, "passed": False, "reason": "expected list or dict with 'emails' key"})
            write_score(total, details)
            return

    # 3. 检查条目数量是否为2（只有两个高风险客户）（20分）
    expected_count = 2
    count_score = 0
    if len(entries) == expected_count:
        count_score = 20
        details.append({"item": "correct number of entries (2)", "score": 20, "max_score": 20, "passed": True, "reason": f"found {len(entries)} entries"})
    else:
        details.append({"item": "correct number of entries (2)", "score": 0, "max_score": 20, "passed": False, "reason": f"found {len(entries)} entries, expected {expected_count}"})
    total += count_score

    # 4. 检查每个条目是否包含必要字段（customer_id, subject, body, news_headline 或类似）（10分）
    required_fields = {"customer_id", "subject", "body", "news_headline"}
    # 可选字段 news_summary
    fields_ok = True
    field_reason = []
    for i, entry in enumerate(entries):
        missing = required_fields - set(entry.keys())
        if missing:
            fields_ok = False
            field_reason.append(f"Entry {i} missing fields: {missing}")
    if fields_ok:
        details.append({"item": "all entries contain required fields", "score": 10, "max_score": 10, "passed": True, "reason": "customer_id, subject, body, news_headline present"})
        total += 10
    else:
        details.append({"item": "all entries contain required fields", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(field_reason)})

    # 5. 检查具体客户 ID 是否正确（必须为 cust_001 和 cust_002）（10分）
    customer_ids = set(entry.get("customer_id") for entry in entries)
    expected_ids = {"cust_001", "cust_002"}
    if customer_ids == expected_ids:
        details.append({"item": "correct customer IDs (cust_001, cust_002)", "score": 10, "max_score": 10, "passed": True, "reason": f"found {customer_ids}"})
        total += 10
    else:
        details.append({"item": "correct customer IDs (cust_001, cust_002)", "score": 0, "max_score": 10, "passed": False, "reason": f"found {customer_ids}, expected {expected_ids}"})

    # 6. 检查新闻分配是否正确（每个客户应匹配对应行业的机会新闻）（20分）
    # LedgerFlow (fintech) 应引用 news_001 或 news_006？但最佳选择是 news_001（最直接匹配）
    # ShelfCloud (retail) 应引用 news_003
    # 我们检查 news_headline 是否包含预期新闻标题的关键词
    news_correct = True
    news_reason = []
    for entry in entries:
        cid = entry.get("customer_id")
        headline = entry.get("news_headline", "")
        if cid == "cust_001":
            if "Open Banking" in headline or "LedgerFlow Solutions" in headline:
                pass
            else:
                news_correct = False
                news_reason.append("cust_001: expected fintech opportunity news")
        elif cid == "cust_002":
            if "Retail AI" in headline or "ShelfCloud" in headline:
                pass
            else:
                news_correct = False
                news_reason.append("cust_002: expected retail opportunity news")
        else:
            news_correct = False
            news_reason.append(f"unexpected customer {cid}")
    if news_correct:
        details.append({"item": "correct news assigned per customer", "score": 20, "max_score": 20, "passed": True, "reason": "opportunity news matched industry"})
        total += 20
    else:
        details.append({"item": "correct news assigned per customer", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(news_reason)})

    # 额外：确保没有低风险或无关客户混入（如果混入则从其他项扣分，但这里作为额外验证不重复扣分，已在客户ID检查中处理）

    write_score(total, details)

def write_score(total, details):
    total = min(total, 100)
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
