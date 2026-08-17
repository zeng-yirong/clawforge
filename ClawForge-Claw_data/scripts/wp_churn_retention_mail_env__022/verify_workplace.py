import sys
import os
import json

def verify(workspace):
    details = []
    total_score = 0

    # 检查 ops/retention_draft.json 是否存在
    draft_path = os.path.join(workspace, "ops", "retention_draft.json")
    if os.path.isfile(draft_path):
        details.append({"item": "产物文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/retention_draft.json 存在"})
        total_score += 10
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/retention_draft.json 不存在"})
        # 提前返回，避免后续读取错误
        score_dict = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_dict, f, indent=2)
        return

    # 检查JSON合法性
    try:
        with open(draft_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可正常解析"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        score_dict = {"total_score": total_score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(score_dict, f, indent=2)
        return

    # 检查必要字段
    required_fields = ["customer_id", "customer_name", "news_id", "headline", "email_body"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        details.append({"item": "包含所有必要字段", "score": 15, "max_score": 15, "passed": True, "reason": "字段齐全"})
        total_score += 15
    else:
        details.append({"item": "包含所有必要字段", "score": 0, "max_score": 15, "passed": False, "reason": f"缺少字段: {missing}"})
        # 仍然继续检查已有字段

    # 检查 customer_id 正确性 (必须是 cust_001)
    if data.get("customer_id") == "cust_001":
        details.append({"item": "customer_id 正确", "score": 15, "max_score": 15, "passed": True, "reason": "值为 cust_001"})
        total_score += 15
    else:
        details.append({"item": "customer_id 正确", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 cust_001，实际为 {data.get('customer_id')}"})

    # 检查 customer_name 正确性 (必须是 LedgerFlow)
    if data.get("customer_name") == "LedgerFlow":
        details.append({"item": "customer_name 正确", "score": 10, "max_score": 10, "passed": True, "reason": "值为 LedgerFlow"})
        total_score += 10
    else:
        details.append({"item": "customer_name 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 LedgerFlow，实际为 {data.get('customer_name')}"})

    # 检查 news_id 正确性 (必须是 news_001)
    if data.get("news_id") == "news_001":
        details.append({"item": "news_id 正确", "score": 15, "max_score": 15, "passed": True, "reason": "值为 news_001"})
        total_score += 15
    else:
        details.append({"item": "news_id 正确", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 news_001，实际为 {data.get('news_id')}"})

    # 检查 headline 正确性 (必须是 "AI in Banking")
    if data.get("headline") == "AI in Banking":
        details.append({"item": "headline 正确", "score": 10, "max_score": 10, "passed": True, "reason": "值为 'AI in Banking'"})
        total_score += 10
    else:
        details.append({"item": "headline 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 'AI in Banking'，实际为 {data.get('headline')}"})

    # 检查 email_body 是否包含客户名称和新闻标题
    body = data.get("email_body", "")
    contains_name = "LedgerFlow" in body
    contains_headline = "AI in Banking" in body
    if contains_name and contains_headline:
        details.append({"item": "email_body 包含客户名和新闻标题", "score": 10, "max_score": 10, "passed": True, "reason": "正文含 LedgerFlow 和 AI in Banking"})
        total_score += 10
    else:
        reason_parts = []
        if not contains_name:
            reason_parts.append("缺少客户名 LedgerFlow")
        if not contains_headline:
            reason_parts.append("缺少新闻标题 AI in Banking")
        details.append({"item": "email_body 包含客户名和新闻标题", "score": 0, "max_score": 10, "passed": False, "reason": "; ".join(reason_parts)})

    # 额外检查：是否使用了模板（可选加分，但模板内容不固定，仅检查通用问候语）
    if "Dear" in body and "Best regards" in body:
        details.append({"item": "email_body 使用模板格式", "score": 5, "max_score": 5, "passed": True, "reason": "包含 Dear 和 Best regards"})
        total_score += 5
    else:
        details.append({"item": "email_body 使用模板格式", "score": 0, "max_score": 5, "passed": False, "reason": "未检测到模板特征"})

    # 完成，写入得分
    score_dict = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(score_dict, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
