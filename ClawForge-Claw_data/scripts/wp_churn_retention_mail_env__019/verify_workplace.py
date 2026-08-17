import sys
import json
import os
from collections import defaultdict

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score = {"total_score": 0, "details": []}

def add_check(passed, item, max_score, reason=""):
    score["details"].append({
        "item": item,
        "score": max_score if passed else 0,
        "max_score": max_score,
        "passed": passed,
        "reason": reason if not passed else (reason if reason else "OK")
    })

# 1. 目录结构检查
ops_dir = os.path.join(workspace, "ops")
add_check(os.path.isdir(ops_dir), "ops 目录存在", 5)
cache_path = os.path.join(ops_dir, "retention_cache.json")
add_check(os.path.isfile(cache_path), "retention_cache.json 存在", 5)

# 2. JSON 合法性
data = None
if os.path.isfile(cache_path):
    try:
        with open(cache_path) as f:
            data = json.load(f)
        add_check(True, "JSON 格式合法", 10)
    except Exception as e:
        add_check(False, "JSON 格式合法", 10, f"解析失败: {e}")
else:
    add_check(False, "JSON 格式合法", 10, "文件不存在")
    data = []

# 3. 数据为列表且条目数正确
if isinstance(data, list):
    add_check(len(data) == 2, "缓存条目数量为 2", 20, f"实际条目数: {len(data)}")
else:
    add_check(False, "缓存条目数量为 2", 20, "数据不是一个列表")

# 4. 每个条目字段完整性
required_fields = ["customer_id", "customer_name", "industry", "news_headline", "news_summary"]
field_ok = True
missing = []
if isinstance(data, list):
    for i, entry in enumerate(data):
        for f in required_fields:
            if f not in entry:
                field_ok = False
                missing.append(f"第{i}条缺少字段 '{f}'")
    add_check(field_ok, "每条条目包含所有必需字段", 10, "; ".join(missing) if missing else "OK")
else:
    add_check(False, "每条条目包含所有必需字段", 10, "数据非列表")

# 5. 内容精确匹配
expected = {
    "C001": {
        "customer_name": "LedgerFlow",
        "industry": "fintech",
        "news_headline": "Fintech Market Opportunity",
        "news_summary": "Growing demand for digital payments."
    },
    "C002": {
        "customer_name": "ShelfCloud",
        "industry": "retail",
        "news_headline": "Retail Recovery Trends",
        "news_summary": "Retail sector sees rebound."
    }
}

match_count = 0
detail_reasons = []
if isinstance(data, list) and all(isinstance(e, dict) for e in data):
    # 建立客户ID映射
    entry_map = {}
    for e in data:
        cid = e.get("customer_id")
        if cid:
            entry_map[cid] = e
    for cid, exp in expected.items():
        if cid not in entry_map:
            detail_reasons.append(f"缺少客户 {cid}")
            continue
        entry = entry_map[cid]
        matched = True
        for key, val in exp.items():
            if entry.get(key) != val:
                matched = False
                detail_reasons.append(f"{cid}.{key} 应为 '{val}'，实际为 '{entry.get(key)}'")
                break
        if matched:
            match_count += 1
    add_check(match_count == 2, "每条缓存条目内容完全匹配预期", 50, f"匹配 {match_count}/2 条: {'; '.join(detail_reasons)}")
else:
    add_check(False, "每条缓存条目内容完全匹配预期", 50, "数据结构错误")

# 总分
total = sum(d["score"] for d in score["details"])
score["total_score"] = total

with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(score, f, indent=2)

print(f"Final score: {total}/100")
