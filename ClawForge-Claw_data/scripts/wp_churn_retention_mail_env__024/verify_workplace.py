import sys
import json
import os
import csv

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json_rel(path):
    full = os.path.join(workspace, path)
    if not os.path.exists(full):
        return None
    with open(full, "r") as f:
        return json.load(f)

def score():
    details = []
    total = 0

    # 1. 检查目录 ops 是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
        total += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ missing"})

    # 2. 检查产物文件 ops/retention_pairs.json 存在且合法JSON (20分)
    pairs_path = os.path.join(workspace, "ops", "retention_pairs.json")
    if not os.path.isfile(pairs_path):
        details.append({"item": "retention_pairs.json exists & valid", "score": 0, "max_score": 20, "passed": False, "reason": "file not found"})
        # 后续检查跳过
        print(json.dumps({"total_score": total, "details": details}))
        return
    try:
        with open(pairs_path, "r") as f:
            pairs = json.load(f)
        if not isinstance(pairs, list):
            raise ValueError("not a list")
        details.append({"item": "retention_pairs.json exists & valid", "score": 20, "max_score": 20, "passed": True, "reason": "file is valid JSON list"})
        total += 20
    except Exception as e:
        details.append({"item": "retention_pairs.json exists & valid", "score": 0, "max_score": 20, "passed": False, "reason": f"invalid JSON: {e}"})
        print(json.dumps({"total_score": total, "details": details}))
        return

    # 加载源数据用于比对
    customers_data = load_json_rel("data/customers/customers.json")
    logs_data = load_json_rel("data/logs/activity_logs.json")
    news_data = load_json_rel("data/news/news_samples.json")

    if not customers_data or not logs_data or not news_data:
        details.append({"item": "source data", "score": 0, "max_score": 10, "passed": False, "reason": "failed to load one or more source files"})
        print(json.dumps({"total_score": total, "details": details}))
        return

    # 3. 字段完整性 (20分) — 每个条目必须包含指定字段
    required_fields = {"customer_id", "customer_name", "industry", "news_headline", "news_summary"}
    field_ok = True
    for i, entry in enumerate(pairs):
        if not required_fields.issubset(entry.keys()):
            field_ok = False
            missing = required_fields - entry.keys()
            details.append({"item": f"entry {i} fields", "score": 0, "max_score": 20, "passed": False, "reason": f"missing fields: {missing}"})
            break
    if field_ok:
        details.append({"item": "all entries have required fields", "score": 20, "max_score": 20, "passed": True, "reason": ""})
        total += 20

    # 4. 筛选正确性 (30分) — 检查每个结果是否对应正确的高风险客户与匹配的新闻
    # 首先找出所有满足条件的高风险客户 (risk_level='high' and last_active_days>30)
    # 注意去重: 按customer_id取第一条满足条件的记录
    if not field_ok:
        # 后续检查不完整则跳过
        pass
    else:
        # 构建从logs中提取的满足条件的客户ID集合 (去重)
        valid_customer_ids = set()
        processed_ids = set()
        for log in logs_data.get("activity_logs", []):
            cid = log.get("customer_id")
            if cid and log.get("risk_level") == "high" and log.get("last_active_days", 0) > 30:
                if cid not in processed_ids:
                    valid_customer_ids.add(cid)
                    processed_ids.add(cid)

        # 构建从news中industry->opportunity headline,summary 映射 (取第一条，但此处只期望一条)
        industry_news = {}
        for news in news_data.get("news_samples", []):
            if news.get("tone") == "opportunity":
                ind = news.get("industry")
                if ind and ind not in industry_news:
                    industry_news[ind] = {
                        "headline": news.get("headline"),
                        "summary": news.get("summary")
                    }

        # 检查结果中每个条目
        result_customer_ids = set()
        all_match = True
        for entry in pairs:
            cid = entry.get("customer_id")
            result_customer_ids.add(cid)
            if cid not in valid_customer_ids:
                all_match = False
                details.append({"item": f"pair for {cid}", "score": 0, "max_score": 30, "passed": False, "reason": f"customer {cid} not a valid high-risk customer"})
                break
            # 匹配行业新闻
            industry = entry.get("industry")
            expected_news = industry_news.get(industry)
            if not expected_news:
                all_match = False
                details.append({"item": f"pair for {cid}", "score": 0, "max_score": 30, "passed": False, "reason": f"no opportunity news for industry {industry}"})
                break
            if entry.get("news_headline") != expected_news["headline"] or entry.get("news_summary") != expected_news["summary"]:
                all_match = False
                details.append({"item": f"pair for {cid}", "score": 0, "max_score": 30, "passed": False, "reason": f"expected headline '{expected_news['headline']}' got '{entry.get('news_headline')}'"})
                break
            # 客户名检查
            # 从 customers 中找
            cust_name = None
            for c in customers_data.get("customers", []):
                if c.get("customer_id") == cid:
                    cust_name = c.get("customer_name")
                    break
            if entry.get("customer_name") != cust_name:
                all_match = False
                details.append({"item": f"pair for {cid} name", "score": 0, "max_score": 30, "passed": False, "reason": f"expected name '{cust_name}' got '{entry.get('customer_name')}'"})
                break

        if all_match:
            # 同时检查是否覆盖了所有有效客户，并且没有多余客户
            if result_customer_ids == valid_customer_ids:
                details.append({"item": "correct filtering & matching", "score": 30, "max_score": 30, "passed": True, "reason": f"all valid customers covered: {valid_customer_ids}"})
                total += 30
            else:
                extra = result_customer_ids - valid_customer_ids
                missing = valid_customer_ids - result_customer_ids
                details.append({"item": "correct filtering & matching", "score": 15, "max_score": 30, "passed": False, "reason": f"extra: {extra}, missing: {missing}"})
                total += 15

    # 5. 重复处理 (10分) — 结果中不能有重复的customer_id
    cid_list = [entry.get("customer_id") for entry in pairs]
    if len(cid_list) == len(set(cid_list)):
        details.append({"item": "no duplicate customer_id", "score": 10, "max_score": 10, "passed": True, "reason": ""})
        total += 10
    else:
        details.append({"item": "no duplicate customer_id", "score": 0, "max_score": 10, "passed": False, "reason": f"duplicate IDs found"})

    # 6. 数值精确 (10分) — 验证客户名、行业等非空且来自源数据 (上面已部分覆盖，这里补满分)
    # 已经通过4和5覆盖，额外加10分作为精确性奖励
    if all_match and field_ok:
        details.append({"item": "value accuracy", "score": 10, "max_score": 10, "passed": True, "reason": "all values match source exactly"})
        total += 10
    else:
        details.append({"item": "value accuracy", "score": 0, "max_score": 10, "passed": False, "reason": "previous errors"})

    final_score = min(total, 100)
    # 写入文件
    result = {
        "total_score": final_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))

if __name__ == "__main__":
    score()
