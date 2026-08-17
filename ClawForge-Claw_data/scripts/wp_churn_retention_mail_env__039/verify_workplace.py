import os
import json
import sys
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # 1. 检查目录结构 (10分)
    required_dirs = ["data", "data/customers", "data/logs", "data/news"]
    dir_score = 0
    for d in required_dirs:
        path = os.path.join(workspace, d)
        if os.path.isdir(path):
            dir_score += 2.5
        else:
            results.append({"item": f"Directory {d} exists", "score": 0, "max_score": 2.5, "passed": False, "reason": f"Missing directory: {d}"})
    if dir_score == 10:
        results.append({"item": "All required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "Directory structure verified."})
    else:
        results.append({"item": "Required directories", "score": dir_score, "max_score": 10, "passed": dir_score==10, "reason": f"Only {int(dir_score/2.5)} of 4 directories present."})

    # 2. 检查输出文件 data/retention_emails.json 是否存在且合法 (10分)
    output_path = os.path.join(workspace, "data/retention_emails.json")
    if not os.path.isfile(output_path):
        results.append({"item": "Output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "File data/retention_emails.json not found."})
        # 无法继续后续验证，直接输出总分
        final_score = 0
        results.append({"item": "Total", "score": 0, "max_score": 100, "passed": False, "reason": "Aborted due to missing output."})
        write_score(workspace, final_score, results)
        return

    try:
        with open(output_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        results.append({"item": "Output file valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        final_score = sum(r["score"] for r in results if "score" in r)
        write_score(workspace, final_score, results)
        return
    results.append({"item": "Output file valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully."})

    # 3. 验证内容结构: 必须是列表，每个列表项包含必须字段 (20分)
    if not isinstance(data, list):
        results.append({"item": "Output is a list", "score": 0, "max_score": 10, "passed": False, "reason": "Expected list, got "+str(type(data))})
        final_score = sum(r["score"] for r in results if "score" in r)
        write_score(workspace, final_score, results)
        return
    results.append({"item": "Output is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Data is a list."})

    required_fields_per_item = ["customer_id", "headline", "summary", "email_recipient"]
    field_score = 0
    for idx, item in enumerate(data):
        missing = [f for f in required_fields_per_item if f not in item]
        if missing:
            results.append({"item": f"Item {idx} has required fields", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing fields: {missing}"})
            field_score = -1
            break
    if field_score != -1:
        results.append({"item": "All items have required fields (customer_id, headline, summary, email_recipient)", "score": 10, "max_score": 10, "passed": True, "reason": f"All {len(data)} items contain required fields."})

    # 4. 核心业务逻辑验证：正确筛选高风险客户 (30分)
    # 读取初始数据以验证答案
    customers_path = os.path.join(workspace, "data/customers/customers.json")
    logs_path = os.path.join(workspace, "data/logs/activity_logs.json")
    news_path = os.path.join(workspace, "data/news/news_samples.json")
    try:
        with open(customers_path) as f:
            customers_data = json.load(f)["customers"]
        with open(logs_path) as f:
            logs_data = json.load(f)["activity_logs"]
        with open(news_path) as f:
            news_data = json.load(f)["news_samples"]
    except Exception as e:
        results.append({"item": "Reading source data", "score": 0, "max_score": 30, "passed": False, "reason": f"Could not read source files: {e}"})
        final_score = sum(r["score"] for r in results if "score" in r)
        write_score(workspace, final_score, results)
        return

    # 构建客户字典 key=customer_id
    customer_dict = {c["customer_id"]: c for c in customers_data}
    # 构建新闻按行业分类（只留opportunity）
    opportunity_news = {}
    for n in news_data:
        if n["tone"] == "opportunity":
            industry = n["industry"]
            if industry not in opportunity_news:
                opportunity_news[industry] = []
            opportunity_news[industry].append(n)

    # 正确的高风险客户（根据规则：risk_level=high, last_active_days>=30, usage_trend=down, ticket_sentiment=negative）
    valid_customer_ids = set()
    for log in logs_data:
        if (log["risk_level"] == "high" and
            log["last_active_days"] >= 30 and
            log["usage_trend"] == "down" and
            log["ticket_sentiment"] == "negative"):
            valid_customer_ids.add(log["customer_id"])

    # 期望输出列表：对每个valid_customer_id，找匹配行业的第一条opportunity新闻
    expected_output = []
    for cid in sorted(valid_customer_ids):
        if cid not in customer_dict:
            continue
        cust = customer_dict[cid]
        industry = cust["industry"]
        news_list = opportunity_news.get(industry, [])
        if not news_list:
            continue  # 没有机会新闻，按理不会发生
        chosen_news = news_list[0]  # 取第一条
        # 收件人邮箱？客户数据中未提供email字段，但我们可以从客户名称构造一个默认邮箱，或者要求agent自己决定。
        # 根据prompt：“发给谁”可以用customer_name或干脆用customer_id。但为了可验证，我们可以允许任何合理的email格式。
        # 但我们需要固定一个规则，否则答案不唯一。更好的做法：让agent使用客户名称+@company.com格式？
        # 但客户数据中没有email。为了客观验证，我们可以在env_builder中加入contacts数据？prompt里没有提到contacts。
        # 另一种方案：要求agent输出customer_id和headline等，而不需要email。但prompt说“发给谁”，可能隐含收件人。
        # 我们可以在env_builder中为客户增加邮箱字段？但数据结构中客户有email吗？参考领域结构：customers.json没有email，
        # 但accounts.json有email。为了简化，我们将“email_recipient”定义为使用customer_name加上默认后缀。
        # 我们可以在验证时接受任何非空字符串即可，只要不是空字符串。但这样太模糊。最好要求一个具体格式。
        # 为了确保唯一答案，在env_builder中为每个客户添加一个email字段？但题目初始架构不包含。可修改env_builder不依赖外部。
        # 或者我们要求agent用customer_id作为收件人标识。prompt说“发给谁”，可以理解为customer_name。
        # 我们可以在verify中检查customer_id是否存在并且customer_id是有效的，同时headline/summary必须匹配。
        # 对于email_recipient，我们允许任意字符串非空，因为prompt没有指定格式。但这样会不够严格。
        # 更合理的做法：将 email_recipient 改为 customer_name 或 customer_id，并验证其正确性。
        # 重新定义required_fields_per_item：["customer_id", "headline", "summary"] 不需要 email_recipient。
        # 但prompt里说“写清楚发给谁”，意味着需要标识收件人。我们可以接受customer_id或customer_name。
        # 为了简化，我们保留customer_id作为关键标识，并额外检查headline和summary的一致性。
        # 修改：将email_recipient改为customer_name，并验证customer_name与初始数据一致。
        # 但我们已经定义了required_fields_per_item，现在要修改verify代码。实际上在verify顶部，我们已经定义了字段列表，可以调整。
        # 重新计划：在verify中，将required_fields_per_item改为 ["customer_id", "headline", "summary"] ，并额外检查customer_id是否在valid集合中，headline和summary是否匹配第一条新闻。
        # 但这样会丢失“发给谁”的验证，不过可以通过customer_id间接验证。prompt要求“发给谁”，agent可能输出customer_name或customer_id，我们不强制其字段名。
        # 为了简单且唯一，我们只要求customer_id, headline, summary。但必须确保customer_id正确。
        # 开始调整：在输出结构检查时，要求每个item包含customer_id, headline, summary。然后验证headline和summary是否与期望一致。
        # 重新开始verify核心部分？不行，已经写了很多。最好重新设计，确保一致性。
        # 为了快速，我们保持现有字段，但将email_recipient定义为任意字符串，只要非空给分。然后主要靠headline和summary匹配。
        # 但这样不够精确。考虑到时间，我们实现为：如果email_recipient非空就给分。同时验证customer_id在valid集合中且headline/summary匹配。
        # 调整验证逻辑。
        pass  # 继续按当前计划，但下面重写验证逻辑

    # 由于上述思考，我们重新组织验证逻辑：
    # 4.1 检查输出中每个item的customer_id是否属于valid_customer_ids (10分)
    # 4.2 检查每个item对应的headline和summary是否匹配该客户行业的第一条opportunity新闻 (20分)

    # 先构建期望映射
    expected_news_map = {}
    for cid in sorted(valid_customer_ids):
        cust = customer_dict.get(cid)
        if not cust:
            continue
        industry = cust["industry"]
        news_list = opportunity_news.get(industry, [])
        if news_list:
            expected_news_map[cid] = news_list[0]  # 第一条

    # 实际输出映射
    output_map = {}
    for item in data:
        cid = item.get("customer_id")
        if cid:
            output_map[cid] = item

    # 检查是否覆盖了所有valid_customer_ids
    missing_valid = [cid for cid in valid_customer_ids if cid not in output_map]
    extra = [cid for cid in output_map if cid not in valid_customer_ids]
    coverage_score = 0
    if len(missing_valid) == 0 and len(extra) == 0:
        coverage_score = 10
        results.append({"item": "Output covers all valid high-risk customers and no extra", "score": 10, "max_score": 10, "passed": True, "reason": f"All {len(valid_customer_ids)} valid customers included, no extras."})
    else:
        results.append({"item": "Output covers all valid high-risk customers", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing: {missing_valid}, Extra: {extra}"})

    # 检查每条新闻正确性
    news_correct_score = 0
    max_news_score = 20
    if len(expected_news_map) == 0:
        news_correct_score = 20  # 如果没有符合条件的客户，空列表也正确
    else:
        total_items = len(expected_news_map)
        correct = 0
        for cid, expected_news in expected_news_map.items():
            actual = output_map.get(cid)
            if actual is None:
                continue
            if actual.get("headline") == expected_news["headline"] and actual.get("summary") == expected_news["summary"]:
                correct += 1
        news_correct_score = int((correct / total_items) * 20)
        results.append({"item": "Headline and summary match expected news", "score": news_correct_score, "max_score": 20, "passed": correct == total_items, "reason": f"Correct: {correct}/{total_items} items."})

    # 5. 邮箱收件人合理性检查 (10分) - 非空即给分
    email_score = 0
    if all("email_recipient" in item and item["email_recipient"] for item in data):
        email_score = 10
        results.append({"item": "Each item has non-empty email_recipient", "score": 10, "max_score": 10, "passed": True, "reason": "All items have a valid email_recipient."})
    else:
        results.append({"item": "Each item has non-empty email_recipient", "score": 0, "max_score": 10, "passed": False, "reason": "Some items missing or empty email_recipient."})

    # 汇总得分
    # 前面有目录10，文件存在+JSON合法10，列表结构10，字段存在10，覆盖率10，新闻正确20，邮箱10 => 共80
    # 加上其他可能的权重？我们还有80分，但总分要100。可以增加对customer_name的检查或数据完整性。
    # 再增加10分用于检查customer_id是否真实存在于初始客户数据中（已在覆盖中体现），再加10分用于判断是否使用了正确的行业新闻（已在新闻正确中）。
    # 实际上我们已经覆盖了80分，还差20分。可以将“字段存在”改为20分？不，我们已经有字段存在10分。还可以增加对数据中customer_name的检查？但输出不需要customer_name。
    # 另外可以增加输出格式排序检查？不必要。
    # 增加一个检查：输出中每个item的customer_id必须存在于初始客户数据中（而不是仅仅在valid集合中）。这可以防止用无效ID。给10分。
    id_exists_score = 0
    if all(cid in customer_dict for cid in output_map):
        id_exists_score = 10
        results.append({"item": "All customer_ids exist in source data", "score": 10, "max_score": 10, "passed": True, "reason": "All customer IDs are valid."})
    else:
        results.append({"item": "All customer_ids exist in source data", "score": 0, "max_score": 10, "passed": False, "reason": "Some customer IDs not found in customers.json."})

    # 再增加10分用于检查输出列表长度与valid_customer_ids一致（其实覆盖已经检查了，但可以复用）
    # 或者增加一条关于行业匹配的深度检查：每个item的行业是否与客户行业一致？但输出中没有industry字段，可以忽略。
    # 改为检查email_recipient是否包含有意义的字符串（比如非空且包含@）？更严格。给10分。
    email_format_score = 0
    if all("@" in item.get("email_recipient","") for item in data):
        email_format_score = 10
        results.append({"item": "email_recipient contains '@' (seems like an email)", "score": 10, "max_score": 10, "passed": True, "reason": "All email_recipient have @ symbol."})
    else:
        results.append({"item": "email_recipient contains '@'", "score": 0, "max_score": 10, "passed": False, "reason": "Some email_recipient missing @."})

    # 现在总分：目录10 + json合法10 + 列表10 + 字段存在10 + 覆盖率10 + 新闻正确20 + 邮箱10 + id存在10 + email格式10 = 100
    total_score = sum(r["score"] for r in results if "score" in r)
    # 确保总分不超过100
    total_score = min(total_score, 100)
    results.append({"item": "Total", "score": total_score, "max_score": 100, "passed": total_score>=60, "reason": f"Aggregated score {total_score}/100"})
    write_score(workspace, total_score, results)

def write_score(workspace, total_score, details):
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
