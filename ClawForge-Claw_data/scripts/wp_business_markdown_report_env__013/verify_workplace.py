import sys
import os
import json
import csv
import re
from pathlib import Path

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
workspace = Path(workspace)

score_details = []
total_score = 0

def add_detail(item, score, max_score, passed, reason):
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    global total_score
    total_score += score

# 1. 检查目录结构 (5分)
report_dir = workspace / "reports"
if report_dir.is_dir():
    add_detail("reports directory exists", 5, 5, True, "目录存在")
else:
    add_detail("reports directory exists", 0, 5, False, "目录缺失")

# 2. 检查报告文件存在 (10分)
report_file = report_dir / "quarterly_summary.md"
if report_file.is_file():
    add_detail("quarterly_summary.md exists", 10, 10, True, "文件存在")
else:
    add_detail("quarterly_summary.md exists", 0, 10, False, "文件缺失")
    # 无法继续后续，直接输出结果
    result = {"total_score": total_score, "details": score_details}
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)

# 3. 读取文件内容，提取JSON代码块 (10分)
content = report_file.read_text(encoding="utf-8")
json_match = re.search(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
if json_match:
    json_str = json_match.group(1).strip()
    try:
        data = json.loads(json_str)
        add_detail("JSON block is valid", 10, 10, True, "JSON解析成功")
    except json.JSONDecodeError as e:
        add_detail("JSON block is valid", 0, 10, False, f"JSON解析失败: {e}")
        data = None
else:
    # 尝试匹配没有语言标识的代码块
    json_match2 = re.search(r"```\s*\n(.*?)\n```", content, re.DOTALL)
    if json_match2:
        json_str = json_match2.group(1).strip()
        try:
            data = json.loads(json_str)
            add_detail("JSON block (no language) is valid", 10, 10, True, "无语言标识的JSON")
        except:
            add_detail("JSON block (no language) is valid", 0, 10, False, "无语言标识的JSON解析失败")
            data = None
    else:
        add_detail("JSON block found", 0, 10, False, "未找到任何代码块")
        data = None

# 4. 验证JSON内容结构 (10分)
expected_ledgers = ["customer", "ops", "product"]
expected_keys_in_ledger = ["revenue", "cost"]

def check_json_structure(data):
    if not isinstance(data, dict):
        return False, "根元素不是字典"
    for ledger in expected_ledgers:
        if ledger not in data:
            return False, f"缺少分类账: {ledger}"
        if not isinstance(data[ledger], dict):
            return False, f"{ledger} 不是字典"
        for key in expected_keys_in_ledger:
            if key not in data[ledger]:
                return False, f"{ledger} 缺少 {key}"
            if not isinstance(data[ledger][key], (int, float)):
                return False, f"{ledger}.{key} 不是数字"
    if "total_profit" not in data:
        return False, "缺少 total_profit"
    if not isinstance(data["total_profit"], (int, float)):
        return False, "total_profit 不是数字"
    return True, "结构正确"

if data is not None:
    ok, reason = check_json_structure(data)
    if ok:
        add_detail("JSON structure correct", 10, 10, True, reason)
    else:
        add_detail("JSON structure correct", 0, 10, False, reason)
else:
    add_detail("JSON structure correct", 0, 10, False, "无数据可检查")

# 5-7. 数值精确匹配 (50分)
# 根据 env_builder 产生的有效数据：
# customer: revenue=15000, cost=8000
# ops: revenue=5000, cost=3000  (注意有一行cost带空格，应解析为3000)
# product: revenue=20000, cost=12000
# total_profit = (15000+5000+20000) - (8000+3000+12000) = 40000-23000=17000
expected = {
    "customer": {"revenue": 15000, "cost": 8000},
    "ops": {"revenue": 5000, "cost": 3000},
    "product": {"revenue": 20000, "cost": 12000},
    "total_profit": 17000
}

if data is not None and ok:
    # 5. 各分类账revenue (15分)
    revenue_correct = True
    for ledger in expected_ledgers:
        if abs(data[ledger].get("revenue", 0) - expected[ledger]["revenue"]) > 0.01:
            revenue_correct = False
            break
    if revenue_correct:
        add_detail("Revenue values correct", 15, 15, True, "所有分类账revenue匹配")
    else:
        add_detail("Revenue values correct", 0, 15, False, "存在不匹配的revenue")
    
    # 6. 各分类账cost (15分)
    cost_correct = True
    for ledger in expected_ledgers:
        if abs(data[ledger].get("cost", 0) - expected[ledger]["cost"]) > 0.01:
            cost_correct = False
            break
    if cost_correct:
        add_detail("Cost values correct", 15, 15, True, "所有分类账cost匹配")
    else:
        add_detail("Cost values correct", 0, 15, False, "存在不匹配的cost")
    
    # 7. total_profit (20分)
    if abs(data.get("total_profit", 0) - expected["total_profit"]) <= 0.01:
        add_detail("Total profit correct", 20, 20, True, "总利润17000匹配")
    else:
        add_detail("Total profit correct", 0, 20, False, f"期望17000, 得到{data.get('total_profit')}")
else:
    # 无法验证数值
    add_detail("Revenue values correct", 0, 15, False, "前置检查失败")
    add_detail("Cost values correct", 0, 15, False, "前置检查失败")
    add_detail("Total profit correct", 0, 20, False, "前置检查失败")

# 汇总
result = {"total_score": total_score, "details": score_details}
with open(workspace / "workplace_score.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"Scoring complete. Total: {total_score}/100")
