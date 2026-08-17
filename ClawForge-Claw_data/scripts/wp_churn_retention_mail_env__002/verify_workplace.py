import sys
import os
import json
import re

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(os.path.join(WORKSPACE, path), "r", encoding="utf-8") as f:
        return json.load(f)

def check_file_exists(path):
    return os.path.isfile(os.path.join(WORKSPACE, path))

def main():
    scores = []
    total_score = 0
    max_total = 100

    # 1. 目录结构检查 (10分)
    score_item = {"item": "cache directory exists", "max_score": 5}
    if os.path.isdir(os.path.join(WORKSPACE, "cache")):
        scores.append({**score_item, "score": 5, "passed": True, "reason": "cache/ exists"})
        total_score += 5
    else:
        scores.append({**score_item, "score": 0, "passed": False, "reason": "cache/ not found"})

    score_item = {"item": "cache/retention_email_cache.json exists", "max_score": 5}
    if check_file_exists("cache/retention_email_cache.json"):
        scores.append({**score_item, "score": 5, "passed": True, "reason": "file exists"})
        total_score += 5
    else:
        scores.append({**score_item, "score": 0, "passed": False, "reason": "file not found"})
        # 后续检查无法进行，直接返回
        write_score(scores, total_score, max_total)
        return

    # 2. JSON 合法性 (10分)
    try:
        data = load_json("cache/retention_email_cache.json")
        scores.append({"item": "JSON is valid", "max_score": 10, "score": 10, "passed": True, "reason": "parsed successfully"})
        total_score += 10
    except Exception as e:
        scores.append({"item": "JSON is valid", "max_score": 10, "score": 0, "passed": False, "reason": f"parse error: {str(e)}"})
        write_score(scores, total_score, max_total)
        return

    # 3. 字段完整性 (20分)
    required_fields = {"customer_id", "subject", "body"}
    present_fields = set(data.keys())
    missing = required_fields - present_fields
    extra = present_fields - required_fields
    field_score = 20
    reason_parts = []
    if missing:
        field_score -= 5 * len(missing)
        reason_parts.append(f"missing: {missing}")
    if extra:
        field_score -= 2 * len(extra)  # 多余字段扣分，但不超过20
        reason_parts.append(f"extra fields: {extra}")
    field_score = max(0, field_score)
    passed = field_score == 20
    scores.append({
        "item": "required fields (customer_id, subject, body)",
        "max_score": 20,
        "score": field_score,
        "passed": passed,
        "reason": "; ".join(reason_parts) if reason_parts else "all required fields present, no extras"
    })
    total_score += field_score

    # 4. customer_id 正确性 (20分)
    cid = data.get("customer_id", "")
    expected_customer_id = "cust_ledgerflow"   # 从env_builder可知唯一正确
    cid_score = 20
    if cid == expected_customer_id:
        scores.append({"item": "customer_id is correct (cust_ledgerflow)", "max_score": 20, "score": 20, "passed": True, "reason": f"matches expected {expected_customer_id}"})
        total_score += 20
    else:
        scores.append({"item": "customer_id is correct (cust_ledgerflow)", "max_score": 20, "score": 0, "passed": False, "reason": f"got '{cid}', expected '{expected_customer_id}'"})

    # 5. subject 检查 (20分)
    subject = data.get("subject", "")
    sub_score = 0
    sub_reasons = []
    # 必须包含客户名 "LedgerFlow" 或 "LedgerFlow"（不区分大小写？大小写敏感，但最好灵活）
    if "LedgerFlow" in subject:
        sub_score += 10
        sub_reasons.append("contains 'LedgerFlow'")
    else:
        sub_reasons.append("missing 'LedgerFlow'")
    # 必须包含新闻中opportunity型headline的一部分 (至少包含 "Digital Payment" 或 "Early Adopters")
    news_headline = "Digital Payment Trends 2025: Why Early Adopters Win"
    if "Digital Payment" in subject or "Early Adopters" in subject:
        sub_score += 10
        sub_reasons.append("contains reference to news headline")
    else:
        sub_reasons.append("missing news headline reference")
    passed_sub = sub_score == 20
    scores.append({
        "item": "subject contains required elements",
        "max_score": 20,
        "score": sub_score,
        "passed": passed_sub,
        "reason": "; ".join(sub_reasons) if sub_reasons else "no reasons"
    })
    total_score += sub_score

    # 6. body 检查 (20分)
    body = data.get("body", "")
    body_score = 0
    body_reasons = []
    # 必须包含客户名
    if "LedgerFlow" in body:
        body_score += 10
        body_reasons.append("contains 'LedgerFlow'")
    else:
        body_reasons.append("missing 'LedgerFlow'")
    # 必须包含新闻headline（至少部分唯一标识词）
    if "Digital Payment Trends" in body or "Early Adopters Win" in body:
        body_score += 10
        body_reasons.append("contains news headline reference")
    else:
        body_reasons.append("missing news headline reference")
    passed_body = body_score == 20
    scores.append({
        "item": "body contains required elements",
        "max_score": 20,
        "score": body_score,
        "passed": passed_body,
        "reason": "; ".join(body_reasons) if body_reasons else "no reasons"
    })
    total_score += body_score

    # 写入结果
    write_score(scores, total_score, max_total)


def write_score(scores, total, max_total):
    result = {
        "total_score": total,
        "details": scores
    }
    out_path = os.path.join(WORKSPACE, "workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {out_path}: {total}/{max_total}")


if __name__ == "__main__":
    main()
