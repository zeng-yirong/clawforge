import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total = 0

    # 1. Check ops/retention_mail_cache.json exists
    cache_path = os.path.join(workspace, "ops/retention_mail_cache.json")
    exists = os.path.isfile(cache_path)
    detail_1 = {
        "item": "Output file ops/retention_mail_cache.json exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "Found" if exists else "Not found"
    }
    score_details.append(detail_1)
    total += detail_1["score"]

    if not exists:
        # stop early
        _write_score(score_details, total, workspace)
        return

    # 2. validate JSON format
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        json_valid = True
    except:
        json_valid = False
    detail_2 = {
        "item": "Cache file is valid JSON",
        "score": 10 if json_valid else 0,
        "max_score": 10,
        "passed": json_valid,
        "reason": "Valid" if json_valid else "Invalid JSON"
    }
    score_details.append(detail_2)
    total += detail_2["score"]
    if not json_valid:
        _write_score(score_details, total, workspace)
        return

    # 3. Check that cache_data is a list
    if not isinstance(cache_data, list):
        detail_3 = {
            "item": "Cache data is a list",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Expected list, got {type(cache_data).__name__}"
        }
        score_details.append(detail_3)
        total += detail_3["score"]
        _write_score(score_details, total, workspace)
        return
    else:
        detail_3 = {
            "item": "Cache data is a list",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Is list"
        }
        score_details.append(detail_3)
        total += detail_3["score"]

    # 4. Load ground truth data from environment files
    try:
        with open(os.path.join(workspace, "data/customers/customers.json")) as f:
            customers = json.load(f)
        with open(os.path.join(workspace, "data/logs/activity_logs.json")) as f:
            logs = json.load(f)
        with open(os.path.join(workspace, "data/news/news_samples.json")) as f:
            news = json.load(f)
    except Exception as e:
        detail_4 = {
            "item": "Load reference data",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Error reading data files: {e}"
        }
        score_details.append(detail_4)
        total += detail_4["score"]
        _write_score(score_details, total, workspace)
        return

    detail_4 = {
        "item": "Load reference data",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "All reference files loaded"
    }
    score_details.append(detail_4)
    total += detail_4["score"]

    # Build customer lookup
    cust_map = {c["customer_id"]: c for c in customers}
    # Build news lookup per industry (only opportunity tone)
    news_by_industry = {}
    for n in news:
        if n["tone"] == "opportunity":
            news_by_industry.setdefault(n["industry"], []).append(n)

    # Determine expected high-risk customers:
    # risk_level=high, last_active_days>30, usage_trend=down, ticket_sentiment=negative
    expected_customer_ids = set()
    for log in logs:
        if (log["risk_level"] == "high" and
            log["last_active_days"] > 30 and
            log["usage_trend"] == "down" and
            log["ticket_sentiment"] == "negative"):
            expected_customer_ids.add(log["customer_id"])

    # expected: C001, C002, C005 (C003 last_active_days=10, C004 low)
    expected_ids_sorted = sorted(expected_customer_ids)
    expected_count = len(expected_ids_sorted)

    # 5. Check count of entries in cache
    actual_ids = set()
    for entry in cache_data:
        if isinstance(entry, dict) and "customer_id" in entry:
            actual_ids.add(entry["customer_id"])
    actual_count = len(actual_ids)

    count_match = (actual_count == expected_count)
    detail_5 = {
        "item": "Number of unique customers in cache matches expected high-risk count",
        "score": 15 if count_match else 0,
        "max_score": 15,
        "passed": count_match,
        "reason": f"Expected {expected_count}, got {actual_count}" if not count_match else f"Correct: {expected_count}"
    }
    score_details.append(detail_5)
    total += detail_5["score"]

    # 6. Check that each expected customer is present and no extra customers
    extra = actual_ids - expected_customer_ids
    missing = expected_customer_ids - actual_ids
    ids_correct = (len(extra) == 0 and len(missing) == 0)
    detail_6 = {
        "item": "Cache contains exactly the expected customers (no extra, no missing)",
        "score": 15 if ids_correct else 0,
        "max_score": 15,
        "passed": ids_correct,
        "reason": f"Extra: {extra}, Missing: {missing}" if not ids_correct else "All correct"
    }
    score_details.append(detail_6)
    total += detail_6["score"]

    # 7. For each expected customer, check that cache entry has required fields and correct industry news
    fields_ok = True
    news_match_ok = True
    field_fail_details = []
    news_fail_details = []

    for cid in expected_ids_sorted:
        # find entry in cache
        entry = None
        for e in cache_data:
            if isinstance(e, dict) and e.get("customer_id") == cid:
                entry = e
                break
        if entry is None:
            fields_ok = False
            field_fail_details.append(f"Entry for {cid} missing")
            continue
        # Check required fields: customer_name, industry, recommended_news (or similar)
        required_fields = ["customer_name", "industry", "headline", "summary"]
        for fld in required_fields:
            if fld not in entry:
                fields_ok = False
                field_fail_details.append(f"Entry {cid} missing field '{fld}'")
        # Check news industry match and opportunity tone
        cust_industry = cust_map.get(cid, {}).get("industry", "")
        expected_news = news_by_industry.get(cust_industry, [])
        if not expected_news:
            news_match_ok = False
            news_fail_details.append(f"No opportunity news for industry {cust_industry}")
            continue
        # Check that the headline in entry matches one of the expected news
        entry_headline = entry.get("headline", "")
        matched = any(n["headline"] == entry_headline for n in expected_news)
        if not matched:
            news_match_ok = False
            news_fail_details.append(f"Entry {cid}: headline '{entry_headline}' not in expected opportunity news for {cust_industry}")
        # Optionally check summary match (same news id)
        entry_summary = entry.get("summary", "")
        if not any(n["headline"] == entry_headline and n["summary"] == entry_summary for n in expected_news):
            news_match_ok = False
            news_fail_details.append(f"Entry {cid}: summary mismatch")

    detail_7 = {
        "item": "Each entry has required customer info fields",
        "score": 15 if fields_ok else 0,
        "max_score": 15,
        "passed": fields_ok,
        "reason": "; ".join(field_fail_details) if not fields_ok else "All fields present"
    }
    score_details.append(detail_7)
    total += detail_7["score"]

    detail_8 = {
        "item": "Each entry uses correct industry-matched opportunity news",
        "score": 20 if news_match_ok else 0,
        "max_score": 20,
        "passed": news_match_ok,
        "reason": "; ".join(news_fail_details) if not news_match_ok else "All news matched correctly"
    }
    score_details.append(detail_8)
    total += detail_8["score"]

    # final total cap at 100
    total = min(total, 100)
    _write_score(score_details, total, workspace)

def _write_score(details, total, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
