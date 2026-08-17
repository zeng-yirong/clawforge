import sys
import os
import json
import re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

# ---------- 期望答案（与 env_builder 严格一致） ----------
EXPECTED_CUSTOMER_ID = "cust_002"
EXPECTED_CUSTOMER_NAME = "ShelfCloud"
EXPECTED_INDUSTRY = "retail"
EXPECTED_NEWS_HEADLINE = "Retailers Embrace AI for Personalized Shopping"
EXPECTED_NEWS_TONE = "opportunity"

score_details = []
total_score = 0

# 1. 目录 & 文件存在性 (10分)
def check_file_exists(path, weight):
    full = os.path.join(workspace, path)
    if os.path.isfile(full):
        return True, weight, f"文件 {path} 存在"
    else:
        return False, 0, f"文件 {path} 不存在"

passed, pts, reason = check_file_exists("ops/email_cache.json", 10)
score_details.append({"item": "目录与文件存在", "score": pts, "max_score": 10, "passed": passed, "reason": reason})
total_score += pts

if not passed:
    # 如果文件不存在，后续检查直接给0分（但为了详细，仍记录）
    pass

# 2. JSON 格式合法性 (10分)
json_valid = False
if passed:
    try:
        with open(os.path.join(workspace, "ops/email_cache.json"), "r") as f:
            data = json.load(f)
        json_valid = True
        score_details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
else:
    score_details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，无法检查"})

# 3. 数组结构 & 字段完整性 (10分)
if json_valid:
    if isinstance(data, list) and len(data) > 0:
        required_fields = {"customer_id", "customer_name", "industry", "news_headline", "email_body"}
        entry = data[0]
        missing = required_fields - set(entry.keys())
        extra = set(entry.keys()) - required_fields
        if not missing and not extra:
            score_details.append({"item": "字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有要求字段存在，无多余字段"})
            total_score += 10
        else:
            reason_parts = []
            if missing:
                reason_parts.append(f"缺少字段: {missing}")
            if extra:
                reason_parts.append(f"多余字段: {extra}")
            score_details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": " | ".join(reason_parts)})
    else:
        score_details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "数据不是数组或数组为空"})
else:
    score_details.append({"item": "字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": "JSON无效"})

# 4. 客户选择正确性 (30分)
customer_correct = False
if json_valid and isinstance(data, list) and len(data) > 0:
    entry = data[0]
    if entry.get("customer_id") == EXPECTED_CUSTOMER_ID:
        customer_correct = True
        score_details.append({"item": "客户选择", "score": 30, "max_score": 30, "passed": True, "reason": f"选择了正确的高风险客户 {EXPECTED_CUSTOMER_ID}"})
        total_score += 30
    else:
        actual = entry.get("customer_id", "未知")
        score_details.append({"item": "客户选择", "score": 0, "max_score": 30, "passed": False, "reason": f"客户ID应为 {EXPECTED_CUSTOMER_ID}，实际为 {actual}"})
else:
    score_details.append({"item": "客户选择", "score": 0, "max_score": 30, "passed": False, "reason": "数据无效"})

# 5. 新闻标题与行业匹配 (20分)
news_correct = False
if customer_correct:
    entry = data[0]
    if entry.get("industry") == EXPECTED_INDUSTRY and entry.get("news_headline") == EXPECTED_NEWS_HEADLINE:
        news_correct = True
        score_details.append({"item": "新闻选择（行业+标题）", "score": 20, "max_score": 20, "passed": True, "reason": "行业零售，新闻标题正确"})
        total_score += 20
    else:
        actual_industry = entry.get("industry", "无")
        actual_headline = entry.get("news_headline", "无")
        score_details.append({"item": "新闻选择（行业+标题）", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 industry={EXPECTED_INDUSTRY} headline={EXPECTED_NEWS_HEADLINE}，实际 industry={actual_industry} headline={actual_headline}"})
else:
    score_details.append({"item": "新闻选择（行业+标题）", "score": 0, "max_score": 20, "passed": False, "reason": "客户选择失败，跳过"})

# 6. 邮件正文包含客户名与新闻标题 (20分)
if customer_correct and news_correct:
    email_body = entry.get("email_body", "")
    if EXPECTED_CUSTOMER_NAME in email_body and EXPECTED_NEWS_HEADLINE in email_body:
        score_details.append({"item": "邮件正文内容", "score": 20, "max_score": 20, "passed": True, "reason": "正文包含客户名和新闻标题"})
        total_score += 20
    else:
        missing_items = []
        if EXPECTED_CUSTOMER_NAME not in email_body:
            missing_items.append("客户名")
        if EXPECTED_NEWS_HEADLINE not in email_body:
            missing_items.append("新闻标题")
        score_details.append({"item": "邮件正文内容", "score": 0, "max_score": 20, "passed": False, "reason": f"正文缺少: {'、'.join(missing_items)}"})
else:
    score_details.append({"item": "邮件正文内容", "score": 0, "max_score": 20, "passed": False, "reason": "前置条件未满足，跳过"})

# 总分
final_score = total_score
final_score = min(final_score, 100)  # 理论上上限100

result = {
    "total_score": final_score,
    "details": score_details
}

with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
