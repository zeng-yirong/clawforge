import json
import os
import sys

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."

    details = []
    total_score = 0

    # 1. 检查输出文件是否存在 (10分)
    out_path = os.path.join(workspace, "ops", "retention_email_cache.json")
    if os.path.isfile(out_path):
        details.append({"item": "输出文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/retention_email_cache.json 存在"})
        total_score += 10
    else:
        details.append({"item": "输出文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/retention_email_cache.json 不存在"})
        # 如果文件不存在，后续检查都无法进行，直接返回
        write_score(total_score, details)
        return

    # 2. 读取并验证 JSON 合法性 (10分)
    try:
        with open(out_path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            details.append({"item": "JSON 合法性", "score": 10, "max_score": 10, "passed": True, "reason": "有效的 JSON 对象"})
            total_score += 10
        else:
            details.append({"item": "JSON 合法性", "score": 0, "max_score": 10, "passed": False, "reason": "顶层不是 JSON 对象"})
            write_score(total_score, details)
            return
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON 合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(total_score, details)
        return

    # 3. 检查必需字段 (每个10分，共30分)
    required_fields = ["recipient", "subject", "body"]
    for field in required_fields:
        if field in data and data[field] is not None and data[field] != "":
            msg = f"字段 '{field}' 存在且非空"
            details.append({"item": f"字段 '{field}'", "score": 10, "max_score": 10, "passed": True, "reason": msg})
            total_score += 10
        else:
            details.append({"item": f"字段 '{field}'", "score": 0, "max_score": 10, "passed": False, "reason": f"字段 '{field}' 缺失或为空"})

    # 如果必须字段缺失，提前结束（因为后续依赖它们）
    if not all(f in data and data[f] for f in required_fields):
        write_score(total_score, details)
        return

    # 4. 读取原始数据，构造预期值 (20分)
    try:
        with open(os.path.join(workspace, "data/customers/customers.json"), "r") as f:
            cust_raw = json.load(f)
        with open(os.path.join(workspace, "data/news/news_samples.json"), "r") as f:
            news_raw = json.load(f)

        # 找到预期客户 (CUST-001)
        expected_customer = None
        for c in cust_raw.get("customers", []):
            if c["customer_id"] == "CUST-001":
                expected_customer = c
                break
        if expected_customer is None:
            details.append({"item": "预期客户存在", "score": 0, "max_score": 20, "passed": False, "reason": "未能从 customers.json 中找到 CUST-001"})
            write_score(total_score, details)
            return

        expected_email = expected_customer["email"]          # "ledgerflow@example.com"
        expected_cust_name = expected_customer["customer_name"]  # "LedgerFlow"

        # 找到预期新闻 (fintech 且 tone=opportunity)
        expected_news_headline = None
        for n in news_raw.get("news_samples", []):
            if n["industry"] == "fintech" and n["tone"] == "opportunity":
                expected_news_headline = n["headline"]   # "Fintech Boom in Asia"
                break
        if expected_news_headline is None:
            details.append({"item": "预期新闻存在", "score": 0, "max_score": 20, "passed": False, "reason": "未能从 news_samples.json 中找到 fintech+opportunity 的新闻"})
            write_score(total_score, details)
            return

        # 检查 recipient 是否正确 (10分)
        if data["recipient"] == expected_email:
            details.append({"item": "收件人邮箱", "score": 10, "max_score": 10, "passed": True, "reason": f"recipient 正确: {expected_email}"})
            total_score += 10
        else:
            details.append({"item": "收件人邮箱", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {expected_email}，实际 {data['recipient']}"})

        # 检查 subject 是否包含客户名和新闻标题 (10分)
        subject = data["subject"]
        if expected_cust_name in subject and expected_news_headline in subject:
            details.append({"item": "邮件主题包含客户名和新闻标题", "score": 10, "max_score": 10, "passed": True, "reason": f"主题包含 '{expected_cust_name}' 和 '{expected_news_headline}'"})
            total_score += 10
        else:
            missing = []
            if expected_cust_name not in subject: missing.append("客户名")
            if expected_news_headline not in subject: missing.append("新闻标题")
            details.append({"item": "邮件主题包含客户名和新闻标题", "score": 0, "max_score": 10, "passed": False, "reason": f"主题缺少: {', '.join(missing)}"})

        # 检查 body 是否包含新闻标题 (10分)
        body = data["body"]
        if expected_news_headline in body:
            details.append({"item": "邮件正文包含新闻标题", "score": 10, "max_score": 10, "passed": True, "reason": f"正文包含 '{expected_news_headline}'"})
            total_score += 10
        else:
            details.append({"item": "邮件正文包含新闻标题", "score": 0, "max_score": 10, "passed": False, "reason": "正文未包含新闻标题"})

    except Exception as e:
        details.append({"item": "读取原始数据异常", "score": 0, "max_score": 20, "passed": False, "reason": f"读取出错: {str(e)}"})

    # 写入最终结果
    write_score(total_score, details)

def write_score(total_score, details):
    # 总分上限100，超出则截断
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    # 写入 workplace_score.json 到工作区
    score_path = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
