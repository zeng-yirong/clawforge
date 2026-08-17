import sys
import os
import json
import csv
import re

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查缓存文件是否存在 (10分)
    cache_path = os.path.join(workspace, "cache", "retention_mail_cache.json")
    exists = os.path.isfile(cache_path)
    if exists:
        details.append({"item": "缓存文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "缓存文件存在", "score": 0, "max_score": 10, "passed": False, "reason": f"未找到 {cache_path}"})
        # 如果文件不存在，无法继续，直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. JSON 合法性 (10分)
    try:
        with open(cache_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({"item": "JSON 合法且为数组", "score": 10, "max_score": 10, "passed": True, "reason": "格式正确"})
            total_score += 10
        else:
            details.append({"item": "JSON 合法且为数组", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 根元素不是数组"})
            # 无法继续
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump({"total_score": total_score, "details": details}, f, indent=2)
            return
    except Exception as e:
        details.append({"item": "JSON 合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析异常: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 记录数量 (20分) - 已知高风险客户应为2个（C001和C003）
    # 先读取活动日志以确认真实高风险客户（排除干扰）
    log_path = os.path.join(workspace, "data", "activity_logs.json")
    with open(log_path, "r") as f:
        log_data = json.load(f)
    high_risk_ids = set()
    for entry in log_data.get("activity_logs", []):
        if entry.get("risk_level") == "high" and entry["customer_id"] not in high_risk_ids:
            # 注意有重复记录（C001 low），我们要取 high 版本
            high_risk_ids.add(entry["customer_id"])
    # 但重复记录中 C001 有一条 low，但 high 版本也在，所以 C001 仍是 high
    expected_count = len(high_risk_ids)  # 应为2
    actual_count = len(data)
    if actual_count == expected_count:
        details.append({"item": "记录数量正确", "score": 20, "max_score": 20, "passed": True, "reason": f"期望 {expected_count} 条，实际 {actual_count} 条"})
        total_score += 20
    else:
        details.append({"item": "记录数量正确", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 {expected_count} 条，实际 {actual_count} 条"})

    # 4. 字段完整性 (10分) - 每个记录必须有 customer_id, email, subject, body
    field_ok = True
    for i, rec in enumerate(data):
        required = ["customer_id", "email", "subject", "body"]
        missing = [f for f in required if f not in rec]
        if missing:
            field_ok = False
            break
    if field_ok:
        details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "每条记录都包含必需字段"})
        total_score += 10
    else:
        details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"存在缺失字段的记录（缺失: {missing}）"})

    # 5. 客户 ID 准确性 (15分) - 必须包含且只包含 C001 和 C003
    customer_ids = [rec["customer_id"] for rec in data]
    expected_ids = sorted(["C001", "C003"])
    actual_ids = sorted(customer_ids)
    if actual_ids == expected_ids:
        details.append({"item": "客户 ID 准确", "score": 15, "max_score": 15, "passed": True, "reason": "高风险客户ID正确"})
        total_score += 15
    else:
        details.append({"item": "客户 ID 准确", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 {expected_ids}，实际 {actual_ids}"})

    # 6. 邮箱匹配 (10分) - 检查每个记录的 email 是否与 customers.json 一致
    cust_path = os.path.join(workspace, "data", "customers", "customers.json")
    with open(cust_path, "r") as f:
        cust_data = json.load(f)
    email_map = {c["customer_id"]: c["email"] for c in cust_data.get("customers", [])}
    email_ok = True
    for rec in data:
        cid = rec["customer_id"]
        expected_email = email_map.get(cid)
        if rec.get("email") != expected_email:
            email_ok = False
            break
    if email_ok:
        details.append({"item": "邮箱匹配", "score": 10, "max_score": 10, "passed": True, "reason": "所有邮箱与客户资料一致"})
        total_score += 10
    else:
        details.append({"item": "邮箱匹配", "score": 0, "max_score": 10, "passed": False, "reason": "存在邮箱不匹配的记录"})

    # 7. 新闻引用 (25分) - 每个记录的 subject 和 body 必须包含对应行业的新闻 headline 和 summary
    news_path = os.path.join(workspace, "data", "news", "news_samples.json")
    with open(news_path, "r") as f:
        news_data = json.load(f)
    # 构建行业->新闻映射（只取与高风险客户行业匹配的新闻，即 fintech 和 retail）
    industry_news = {}
    for article in news_data.get("news_samples", []):
        if article["industry"] in ("fintech", "retail"):
            industry_news[article["industry"]] = article  # 每个行业只有一个，所以安全
    # 同时需要客户行业映射
    customer_industry = {c["customer_id"]: c["industry"] for c in cust_data.get("customers", [])}

    news_ok = True
    news_fail_reason = ""
    for rec in data:
        cid = rec["customer_id"]
        ind = customer_industry.get(cid)
        if not ind:
            continue
        news = industry_news.get(ind)
        if not news:
            news_ok = False
            news_fail_reason = f"客户 {cid} 行业 {ind} 无对应新闻"
            break
        # 检查 subject 是否包含 headline
        if news["headline"] not in rec.get("subject", ""):
            news_ok = False
            news_fail_reason = f"客户 {cid} 的 subject 未包含 headline '{news['headline']}'"
            break
        # 检查 body 是否包含 summary（允许部分匹配，但整段 summary 应出现）
        if news["summary"] not in rec.get("body", ""):
            news_ok = False
            news_fail_reason = f"客户 {cid} 的 body 未包含 summary '{news['summary']}'"
            break

    if news_ok:
        details.append({"item": "新闻引用正确", "score": 25, "max_score": 25, "passed": True, "reason": "所有记录的subject/body正确引用了匹配行业的新闻头条和摘要"})
        total_score += 25
    else:
        details.append({"item": "新闻引用正确", "score": 0, "max_score": 25, "passed": False, "reason": news_fail_reason})

    # 额外扣分项（不在list中但可记录）: 如果有额外字段，每个扣5分，最多扣10分
    extra_field_penalty = 0
    allowed = set(["customer_id", "email", "subject", "body"])
    for rec in data:
        extra = set(rec.keys()) - allowed
        if extra:
            extra_field_penalty += 5
    if extra_field_penalty > 10:
        extra_field_penalty = 10
    if extra_field_penalty > 0:
        details.append({"item": "无多余字段", "score": -extra_field_penalty, "max_score": 0, "passed": False, "reason": f"存在多余字段，扣{extra_field_penalty}分"})
        total_score -= extra_field_penalty

    # 确保总分在0-100之间
    total_score = max(0, min(100, total_score))

    # 写入结果
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
