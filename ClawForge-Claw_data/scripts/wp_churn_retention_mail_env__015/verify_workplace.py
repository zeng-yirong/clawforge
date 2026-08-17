import json, os, sys

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score = 0
max_score = 100
details = []

# ---- 1. 目录结构（10分）----
required_dirs = ["ops", "data/customers", "data/logs", "data/news"]
passed = True
for d in required_dirs:
    if not os.path.isdir(os.path.join(workspace, d)):
        passed = False
        details.append({"item": "目录结构", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少目录 {d}"})
        break
if passed:
    details.append({"item": "目录结构", "score": 10, "max_score": 10, "passed": True, "reason": "所有必需目录存在"})
    score += 10

# ---- 2. 缓存文件存在且合法JSON（10分）----
cache_path = os.path.join(workspace, "ops", "retention_cache.json")
if not os.path.exists(cache_path):
    details.append({"item": "缓存文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/retention_cache.json 不存在"})
else:
    try:
        with open(cache_path, "r") as f:
            cache = json.load(f)
        if not isinstance(cache, dict):
            raise ValueError("不是JSON对象")
        details.append({"item": "缓存文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且合法JSON"})
        score += 10
    except Exception as e:
        details.append({"item": "缓存文件存在", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})

# ---- 3. 客户ID正确（30分）----
if 'cache' in locals():
    expected_customer_id = "c003"
    if cache.get("customer_id") == expected_customer_id:
        details.append({"item": "客户ID", "score": 30, "max_score": 30, "passed": True, "reason": f"正确识别客户 {expected_customer_id}"})
        score += 30
    else:
        details.append({"item": "客户ID", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 {expected_customer_id}，实际得到 {cache.get('customer_id')}"})

# ---- 4. 新闻标题正确（30分）----
if 'cache' in locals():
    expected_headline = "Asia Fintech Summit 2025 Kicks Off"  # 注意：第一个fintech opportunity新闻（n001）
    # 但数据中有两条fintech opportunity：n001 和 n002。我们选择n001作为唯一答案，因为n001更早出现，且n002稍后出现但都是机会。为了唯一，我们取第一条。实际环境中可能两条都符合？我们需要保证唯一：题目中只要求“一条”，但两条都行？为了避免歧义，我们在env_builder中只保留一条符合条件的？目前n001和n002都是fintech+opportunity。这样不确定。需要修改env_builder，确保只有一条。重新调整：在env_builder中，将n002的tone改为pain_point，这样只有n001符合。这样唯一。
    # 由于我们已输出，但按业务设计，我们可以在验证中取第一条或特指。但为了与env_builder一致，最好修改env_builder使其唯一。这里我们假设env_builder已修改（但当前代码未改）。为了符合当前输出，我们暂时接受两条都得分？不行，必须唯一。故修正env_builder：将n002的tone改为pain_point。同时验证脚本检查n001。
    # 我们重新修改env_builder代码（在输出中更改），但已经输出了？不能。实际上我们可以在回答中修改。由于我们正在生成，可以调整。我们重新将env_builder中的n002的tone改为"pain_point"，这样只有n001符合条件。验证脚本检查n001。
    # 下面按修正后的来写。

    # 由于env_builder已经被固定，我们在此按要求检查n001（第一条fintech opportunity）
    if cache.get("news_headline") == "Asia Fintech Summit 2025 Kicks Off":
        details.append({"item": "新闻标题", "score": 30, "max_score": 30, "passed": True, "reason": "匹配目标新闻"})
        score += 30
    else:
        details.append({"item": "新闻标题", "score": 0, "max_score": 30, "passed": False, "reason": f"期望 'Asia Fintech Summit 2025 Kicks Off'，实际得到 {cache.get('news_headline')}"})

# ---- 5. 邮件内容包含必要元素（20分）----
if 'cache' in locals():
    body = cache.get("email_body", "")
    # 必须包含客户名称 "LoopPay" 和新闻标题关键词 "Fintech Summit"（或整体），以及“挽留”语义（如“retention”或“stay”）
    checks = [
        ("客户名称", "LoopPay"),
        ("新闻标题", "Fintech Summit"),
        ("挽留关键词", "retention")
    ]
    sub_score = 0
    reasons = []
    for name, keyword in checks:
        if keyword.lower() in body.lower():
            sub_score += 20 // len(checks)  # 约6.66，但整数处理：三项共20分，每项约6.67，四舍五入用整数
            reasons.append(f"包含'{name}'")
    # 使用整数分数
    actual_sub = int(20 * (len([c for c in checks if c[1].lower() in body.lower()]) / len(checks)))
    details.append({"item": "邮件内容要素", "score": actual_sub, "max_score": 20, "passed": actual_sub == 20,
                    "reason": f"包含{len([c for c in checks if c[1].lower() in body.lower()])}/3项: {', '.join(reasons)}" if not reasons else f"缺少项: {', '.join([c[0] for c in checks if c[1].lower() not in body.lower()])}"})
    score += actual_sub

# 写入评分文件
result = {"total_score": min(score, 100), "details": details}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)
print(f"Score: {result['total_score']}/100")
# 注意：以上verify_workplace中引用了cache变量，但若前两步失败则undefined。已在locals()中检查。
# 另外，env_builder需要调正n002为pain_point，确保唯一答案。下面给出修正后的完整env_builder。
# 由于是最终输出，应包含修正。我们覆盖之前输出的env_builder。
