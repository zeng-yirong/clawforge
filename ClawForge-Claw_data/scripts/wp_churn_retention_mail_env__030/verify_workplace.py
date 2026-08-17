import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

results = []
total_score = 0
max_total = 100

# 1. 检查目录结构是否存在 (主要目录)
def check_dir(path, name):
    full = os.path.join(workspace, path)
    return os.path.isdir(full), f"{name} 目录存在" if os.path.isdir(full) else f"{name} 目录缺失"

# 检查必要目录
for d, dn in [("data/customers", "客户目录"), ("data/logs", "日志目录"), ("data/news", "新闻目录")]:
    ok, reason = check_dir(d, dn)
    results.append({"item": dn, "score": 5 if ok else 0, "max_score": 5, "passed": ok, "reason": reason})
    total_score += 5 if ok else 0

# 2. 检查目标文件 retention_email_draft.json 存在
target_file = os.path.join(workspace, "retention_email_draft.json")
file_exists = os.path.isfile(target_file)
if file_exists:
    results.append({"item": "目标邮件文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total_score += 10
else:
    results.append({"item": "目标邮件文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "找不到 retention_email_draft.json"})
    # 如果文件不存在，后续检查无法进行，直接输出
    # 但为了结构完整性，先添加其他项为0
    for item_name, max_s in [("JSON格式合法性",10), ("客户ID正确",20), ("客户名称正确",10), ("新闻标题正确",20), ("正文内容合理",20)]:
        results.append({"item": item_name, "score": 0, "max_score": max_s, "passed": False, "reason": "目标文件缺失"})
    total_score = sum(r["score"] for r in results)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)
    print(f"Total score: {total_score}/100")
    sys.exit(0)

# 3. 解析JSON
try:
    with open(target_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    results.append({"item": "JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
    total_score += 10
except Exception as e:
    results.append({"item": "JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
    # 后续无法检查
    for item_name, max_s in [("客户ID正确",20), ("客户名称正确",10), ("新闻标题正确",20), ("正文内容合理",20)]:
        results.append({"item": item_name, "score": 0, "max_score": max_s, "passed": False, "reason": "JSON解析失败"})
    total_score = sum(r["score"] for r in results)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2)
    print(f"Total score: {total_score}/100")
    sys.exit(0)

# 4. 检查必要字段
required_fields = ["customer_id", "customer_name", "news_headline", "email_body"]
missing = [f for f in required_fields if f not in data]
if not missing:
    results.append({"item": "必要字段完整性", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必要字段"})
    total_score += 10
else:
    results.append({"item": "必要字段完整性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {missing}"})
    # 后续检查依赖字段，如果缺失则部分得0
    # 后面单独检查每个字段

# 5. 客户ID正确 (应为 cust_001)
customer_id = data.get("customer_id", "")
if customer_id == "cust_001":
    results.append({"item": "客户ID正确", "score": 20, "max_score": 20, "passed": True, "reason": "客户ID为 cust_001"})
    total_score += 20
else:
    results.append({"item": "客户ID正确", "score": 0, "max_score": 20, "passed": False, "reason": f"客户ID为 {customer_id}，期望 cust_001"})

# 6. 客户名称正确 (应为 LedgerFlow)
customer_name = data.get("customer_name", "")
if customer_name == "LedgerFlow":
    results.append({"item": "客户名称正确", "score": 10, "max_score": 10, "passed": True, "reason": "客户名称正确"})
    total_score += 10
else:
    results.append({"item": "客户名称正确", "score": 0, "max_score": 10, "passed": False, "reason": f"客户名称 {customer_name}，期望 LedgerFlow"})

# 7. 新闻标题正确 (应包含 "Fintech startups face increased regulatory scrutiny")
headline = data.get("news_headline", "")
expected_headline = "Fintech startups face increased regulatory scrutiny"
if headline == expected_headline:
    results.append({"item": "新闻标题正确", "score": 20, "max_score": 20, "passed": True, "reason": "新闻标题精确匹配"})
    total_score += 20
else:
    # 允许模糊包含，但精确更好
    if expected_headline in headline:
        results.append({"item": "新闻标题正确", "score": 15, "max_score": 20, "passed": True, "reason": "新闻标题包含期望内容"})
        total_score += 15
    else:
        results.append({"item": "新闻标题正确", "score": 0, "max_score": 20, "passed": False, "reason": f"新闻标题 {headline}，期望包含 {expected_headline}"})

# 8. 正文合理：至少包含客户名称或新闻标题，长度>20
body = data.get("email_body", "")
body_ok = (len(body) > 20) and (customer_name in body or expected_headline in body)
if body_ok:
    results.append({"item": "正文内容合理", "score": 20, "max_score": 20, "passed": True, "reason": "正文包含客户名称或新闻标题且长度足够"})
    total_score += 20
else:
    if len(body) <= 20:
        results.append({"item": "正文内容合理", "score": 5, "max_score": 20, "passed": False, "reason": "正文长度过短"})
        total_score += 5
    else:
        results.append({"item": "正文内容合理", "score": 10, "max_score": 20, "passed": False, "reason": "正文未引用客户名称或新闻标题"})
        total_score += 10

# 确保总分不超过100
final_score = min(total_score, 100)
output = {"total_score": final_score, "details": results}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(output, f, indent=2)

print(f"Total score: {final_score}/100")
