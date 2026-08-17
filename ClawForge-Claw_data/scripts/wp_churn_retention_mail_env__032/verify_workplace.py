import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    score_details.append({
        "item": "ops directory exists",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })

    # 2. 检查 retention_drafts.json 是否存在
    drafts_path = os.path.join(ops_path, "retention_drafts.json") if dir_exists else None
    file_exists = drafts_path and os.path.isfile(drafts_path)
    score_details.append({
        "item": "retention_drafts.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "File not found"
    })

    if not file_exists:
        # 如果文件不存在，直接返回当前分数
        finish(score_details, total_score)
        return

    # 3. 解析 JSON 并检查格式
    try:
        with open(drafts_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        finish(score_details, total_score)
        return
    else:
        score_details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON"
        })

    # 4. 检查是数组
    if not isinstance(data, list):
        score_details.append({
            "item": "Top-level is array",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Top-level is not a list"
        })
        finish(score_details, total_score)
        return
    else:
        score_details.append({
            "item": "Top-level is array",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Array with {len(data)} elements"
        })

    # 5. 检查每个元素必需字段
    required_fields = ["customer_id", "customer_name", "industry", "news_headline", "news_summary", "draft_body"]
    all_have_required = True
    missing_fields = []
    for idx, entry in enumerate(data):
        for field in required_fields:
            if field not in entry:
                all_have_required = False
                missing_fields.append(f"Element {idx} missing '{field}'")
    if all_have_required:
        score_details.append({
            "item": "All entries have required fields",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "All required fields present"
        })
    else:
        score_details.append({
            "item": "All entries have required fields",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "; ".join(missing_fields)
        })

    # 6. 筛选逻辑：只包含 cust_001 和 cust_002（高风险 + usage_trend down）
    expected_ids = {"cust_001", "cust_002"}
    actual_ids = {entry["customer_id"] for entry in data}
    correct_ids = actual_ids == expected_ids
    if correct_ids:
        score_details.append({
            "item": "Correct customer set (high risk + down trend)",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"Contains exactly {expected_ids}"
        })
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        reason = ""
        if missing:
            reason += f"Missing: {missing}. "
        if extra:
            reason += f"Extra: {extra}. "
        score_details.append({
            "item": "Correct customer set",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": reason
        })

    # 7. 检查行业匹配和新闻准确性（按 news_id 排序取第一个 pain_point）
    # cust_001 (fintech) -> first pain_point fintech news = news_001
    # cust_002 (retail) -> first pain_point retail news = news_003
    correct_news = {
        "cust_001": ("Fintech Regulations Tighten: What It Means for Your Business",
                     "New compliance requirements could slow down operations."),
        "cust_002": ("Retail Apocalypse? Not Yet – How Smart Brands Adapt",
                     "Traditional retailers face fierce online competition.")
    }
    news_correct = True
    news_errors = []
    for entry in data:
        cid = entry["customer_id"]
        if cid in correct_news:
            exp_headline, exp_summary = correct_news[cid]
            if entry.get("news_headline") != exp_headline or entry.get("news_summary") != exp_summary:
                news_correct = False
                news_errors.append(f"{cid}: headline mismatch or summary mismatch")
    if news_correct:
        score_details.append({
            "item": "News headline and summary match expected (pain point, first by news_id)",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "All selected news are correct"
        })
    else:
        score_details.append({
            "item": "News correctness",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "; ".join(news_errors)
        })

    # 8. 检查 draft_body 非空且长度不超过200
    draft_ok = True
    draft_issues = []
    for idx, entry in enumerate(data):
        body = entry.get("draft_body", "")
        if not isinstance(body, str) or len(body.strip()) == 0:
            draft_ok = False
            draft_issues.append(f"Entry {idx} empty draft_body")
        elif len(body) > 200:
            draft_ok = False
            draft_issues.append(f"Entry {idx} draft_body too long ({len(body)} chars)")
    if draft_ok:
        score_details.append({
            "item": "draft_body non-empty and ≤200 chars",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All drafts valid"
        })
    else:
        score_details.append({
            "item": "draft_body validation",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "; ".join(draft_issues)
        })

    # 计算总分
    total_score = sum(d["score"] for d in score_details)
    finish(score_details, total_score)

def finish(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    # 输出到 stdout 以便 CI 查看
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    verify()
