import sys
import json
import os
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 目录结构与基础文件存在性 (10分)
    dirs = ["data/customers", "data/logs", "data/news", "ops"]
    all_dirs_exist = all(os.path.isdir(os.path.join(workspace, d)) for d in dirs)
    if all_dirs_exist:
        score_details.append({"item": "Required directories exist", "score": 5, "max_score": 5, "passed": True, "reason": "All required directories found."})
    else:
        score_details.append({"item": "Required directories exist", "score": 0, "max_score": 5, "passed": False, "reason": "Missing one or more directories."})

    required_files = ["data/customers/customers.json", "data/logs/activity_logs.json", "data/news/news_samples.json"]
    all_files_exist = all(os.path.isfile(os.path.join(workspace, f)) for f in required_files)
    if all_files_exist:
        score_details.append({"item": "Required source files exist", "score": 5, "max_score": 5, "passed": True, "reason": "All three source files present."})
    else:
        score_details.append({"item": "Required source files exist", "score": 0, "max_score": 5, "passed": False, "reason": "Missing source file(s)."})
    total_score += (5 if all_dirs_exist else 0) + (5 if all_files_exist else 0)

    # 2. 读取源数据并解析 (10分)
    try:
        with open(os.path.join(workspace, "data/customers/customers.json"), "r") as f:
            customers_data = json.load(f)
        with open(os.path.join(workspace, "data/logs/activity_logs.json"), "r") as f:
            logs_data = json.load(f)
        with open(os.path.join(workspace, "data/news/news_samples.json"), "r") as f:
            news_data = json.load(f)
        parsed_ok = True
    except Exception as e:
        parsed_ok = False
        reason = f"JSON parse error: {e}"
    if parsed_ok and isinstance(customers_data, dict) and isinstance(logs_data, dict) and isinstance(news_data, dict):
        customers = customers_data.get("customers", [])
        logs = logs_data.get("activity_logs", [])
        news = news_data.get("news_samples", [])
        if isinstance(customers, list) and isinstance(logs, list) and isinstance(news, list):
            score_details.append({"item": "Source JSON structure valid", "score": 10, "max_score": 10, "passed": True, "reason": "All three JSON files have correct wrapper keys and lists."})
            total_score += 10
        else:
            score_details.append({"item": "Source JSON structure valid", "score": 0, "max_score": 10, "passed": False, "reason": "Expected list under wrapper key."})
            total_score += 0
    else:
        score_details.append({"item": "Source JSON structure valid", "score": 0, "max_score": 10, "passed": False, "reason": "Failed to parse or wrong type."})
        total_score += 0
        # Early exit? We'll continue but scoring will be low.

    # 3. 从源数据中推导正确答案 (用于后续比较)
    # 定义规则：risk_level == "high" and last_active_days > 30
    high_risk_ids = set()
    for log in logs:
        if log.get("risk_level") == "high" and log.get("last_active_days", 0) > 30:
            high_risk_ids.add(log["customer_id"])
    # 过滤掉不在 customers 中的 ID（如 c999）
    valid_high_risk_ids = {cid for cid in high_risk_ids if any(c["customer_id"] == cid for c in customers)}
    # 构建 customer_id -> industry 映射
    customer_industry = {c["customer_id"]: c["industry"] for c in customers}
    # 构建 industry -> 第一条 tone=opportunity 的 news_id (按 news_id 排序)
    industry_news = {}
    for n in sorted(news, key=lambda x: x["news_id"]):
        if n["tone"] == "opportunity":
            industry = n["industry"]
            if industry not in industry_news:
                industry_news[industry] = n["news_id"]
    expected_entries = {}
    for cid in valid_high_risk_ids:
        industry = customer_industry.get(cid)
        if industry and industry in industry_news:
            expected_entries[cid] = {"news_id": industry_news[industry], "customer_name": next(c["customer_name"] for c in customers if c["customer_id"]==cid)}

    # 4. 检查 agent 输出文件 (ops/retention_campaign.json)
    output_path = os.path.join(workspace, "ops/retention_campaign.json")
    if not os.path.isfile(output_path):
        score_details.append({"item": "Agent output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/retention_campaign.json not found."})
        total_score += 0
        # 不再往下检查
        write_score(workspace, total_score, score_details)
        return

    try:
        with open(output_path, "r") as f:
            output_data = json.load(f)
        output_valid = True
    except:
        output_valid = False
    if not output_valid or not isinstance(output_data, list):
        score_details.append({"item": "Agent output is valid JSON array", "score": 0, "max_score": 10, "passed": False, "reason": "Output is not a valid JSON array."})
        total_score += 0
        write_score(workspace, total_score, score_details)
        return
    else:
        score_details.append({"item": "Agent output is valid JSON array", "score": 10, "max_score": 10, "passed": True, "reason": "output is a list."})
        total_score += 10

    # 5. 检查输出内容是否正确 (80分)
    # 5a. 是否包含所有预期客户且没有多余客户 (30分)
    output_customers = {}
    for entry in output_data:
        if not isinstance(entry, dict):
            continue
        cid = entry.get("customer_id")
        if cid:
            # 检查必要字段
            if not all(k in entry for k in ["customer_id", "customer_name", "news_id", "news_headline", "subject", "body"]):
                continue
            output_customers[cid] = entry

    expected_ids = set(expected_entries.keys())
    output_ids = set(output_customers.keys())
    missing_ids = expected_ids - output_ids
    extra_ids = output_ids - expected_ids
    if not missing_ids and not extra_ids:
        score_details.append({"item": "Output contains exactly the expected high-risk customers (no missing, no extra)", "score": 30, "max_score": 30, "passed": True, "reason": f"All {len(expected_ids)} customers present, no extras."})
        total_score += 30
    else:
        msg = []
        if missing_ids:
            msg.append(f"Missing: {missing_ids}")
        if extra_ids:
            msg.append(f"Extra: {extra_ids}")
        score_details.append({"item": "Output contains exactly the expected high-risk customers", "score": 0, "max_score": 30, "passed": False, "reason": "; ".join(msg)})
        total_score += 0

    # 5b. 每个客户的 news_id 是否正确 (30分)
    news_correct = True
    for cid, expected in expected_entries.items():
        if cid in output_customers:
            actual_news = output_customers[cid].get("news_id")
            if actual_news != expected["news_id"]:
                news_correct = False
                break
    if news_correct and not missing_ids:
        score_details.append({"item": "Each customer's news_id matches the derived industry opportunity news", "score": 30, "max_score": 30, "passed": True, "reason": "All news_ids correct."})
        total_score += 30
    else:
        score_details.append({"item": "Each customer's news_id matches the derived industry opportunity news", "score": 0, "max_score": 30, "passed": False, "reason": "One or more news_ids incorrect."})
        total_score += 0

    # 5c. 其他字段完整性: subject和body非空, customer_name正确 (20分)
    field_ok = True
    for cid, entry in output_customers.items():
        if not isinstance(entry.get("subject"), str) or len(entry["subject"].strip()) == 0:
            field_ok = False
            break
        if not isinstance(entry.get("body"), str) or len(entry["body"].strip()) == 0:
            field_ok = False
            break
        # 可选的: 检查 customer_name 是否匹配
        expected_name = expected_entries.get(cid, {}).get("customer_name")
        if expected_name and entry.get("customer_name") != expected_name:
            field_ok = False
            break
    if field_ok:
        score_details.append({"item": "Other required fields (subject, body, customer_name) are present and non-empty", "score": 20, "max_score": 20, "passed": True, "reason": "All fields filled correctly."})
        total_score += 20
    else:
        score_details.append({"item": "Other required fields are present and non-empty", "score": 0, "max_score": 20, "passed": False, "reason": "Missing or empty fields, or customer_name mismatch."})
        total_score += 0

    # 写最终分数
    total_score = min(total_score, 100)  # 确保不超过100
    write_score(workspace, total_score, score_details)

def write_score(workspace, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
