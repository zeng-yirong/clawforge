import sys
import os
import json

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score = 0
details = []
max_score = 0

def add_detail(item, score, max_score, passed, reason):
    details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return score

# 1. 检查 cache 目录是否存在 (5分)
max_score += 5
cache_dir = os.path.join(workspace, "cache")
if os.path.isdir(cache_dir):
    score += add_detail("cache 目录存在", 5, 5, True, "cache 目录已创建")
else:
    score += add_detail("cache 目录存在", 0, 5, False, "cache 目录未找到")

# 2. 检查 retention_mail.json 文件是否存在 (10分)
max_score += 10
target_file = os.path.join(workspace, "cache", "retention_mail.json")
if os.path.isfile(target_file):
    score += add_detail("retention_mail.json 文件存在", 10, 10, True, "文件存在")
else:
    score += add_detail("retention_mail.json 文件存在", 0, 10, False, "文件未找到，请检查路径 cache/retention_mail.json")
    # 如果文件不存在，后续检查直接跳过
    final_score = score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": details}, f, indent=2)
    sys.exit(0)

# 3. 解析 JSON 合法性 (10分)
max_score += 10
try:
    with open(target_file, "r") as f:
        data = json.load(f)
    if isinstance(data, list):
        score += add_detail("JSON 为合法数组", 10, 10, True, "文件内容为合法 JSON 数组")
    else:
        score += add_detail("JSON 为合法数组", 0, 10, False, "根元素不是数组，应为 list")
        final_score = score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f, indent=2)
        sys.exit(0)
except Exception as e:
    score += add_detail("JSON 解析", 0, 10, False, f"JSON 解析失败: {str(e)}")
    final_score = score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": details}, f, indent=2)
    sys.exit(0)

# 4. 数组长度应为1 (15分)
max_score += 15
if len(data) == 1:
    score += add_detail("数组长度恰好为1个高风险客户", 15, 15, True, f"数组包含 {len(data)} 个元素")
else:
    score += add_detail("数组长度恰好为1个高风险客户", 0, 15, False, f"期望 1 个，实际 {len(data)}")

# 5. 检查每个元素的必含字段 (15分)
max_score += 15
required_fields = {"customer_id", "email_to", "news_id", "subject"}
element = data[0]
missing = required_fields - set(element.keys())
if not missing:
    score += add_detail("元素包含所有必要字段", 15, 15, True, "字段完整")
else:
    score += add_detail("元素包含所有必要字段", 0, 15, False, f"缺少字段: {missing}")

# 6. 验证 customer_id = "C001" (15分)
max_score += 15
if element.get("customer_id") == "C001":
    score += add_detail("customer_id 正确", 15, 15, True, "值为 C001")
else:
    score += add_detail("customer_id 正确", 0, 15, False, f"期望 C001，实际 {element.get('customer_id')}")

# 7. 验证 email_to = "ledgerflow@example.com" (10分)
max_score += 10
if element.get("email_to") == "ledgerflow@example.com":
    score += add_detail("email_to 正确", 10, 10, True, "值为 ledgerflow@example.com")
else:
    score += add_detail("email_to 正确", 0, 10, False, f"期望 ledgerflow@example.com，实际 {element.get('email_to')}")

# 8. 验证 news_id = "N001" (10分)
max_score += 10
if element.get("news_id") == "N001":
    score += add_detail("news_id 正确", 10, 10, True, "值为 N001")
else:
    score += add_detail("news_id 正确", 0, 10, False, f"期望 N001，实际 {element.get('news_id')}")

# 9. 验证 subject = "Re: Fintech Regulations Tighten" (10分)
max_score += 10
expected_subject = "Re: Fintech Regulations Tighten"
if element.get("subject") == expected_subject:
    score += add_detail("subject 正确", 10, 10, True, f"值为 {expected_subject}")
else:
    score += add_detail("subject 正确", 0, 10, False, f"期望 '{expected_subject}'，实际 '{element.get('subject')}'")

# 额外：确保没有多余字段（扣分项，但不超过总分）
extra_fields = set(element.keys()) - required_fields
if extra_fields:
    score -= 5  # 扣5分
    add_detail("无多余字段", -5, 0, False, f"发现多余字段: {extra_fields}")
else:
    add_detail("无多余字段", 0, 0, True, "没有多余字段")

# 总分限制在0-100
final_score = max(0, min(100, score))

# 写入 workplace_score.json
result = {
    "total_score": final_score,
    "details": details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
