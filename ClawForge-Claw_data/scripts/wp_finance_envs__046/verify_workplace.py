import sys
import os
import json
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score_details = []
total_score = 0
max_total = 100

def add_score(item, score, max_score, passed, reason):
    total_score = score_details[-1]["score"] if score_details else 0
    total_score += score
    score_details.append({
        "item": item,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": reason
    })
    return total_score

# 1. 检查 ops/recommendation.json 是否存在 (10分)
rec_path = os.path.join(workspace, "ops", "recommendation.json")
if os.path.exists(rec_path):
    add_score("推荐文件存在", 10, 10, True, "ops/recommendation.json 存在")
    current_total = 10
else:
    add_score("推荐文件存在", 0, 10, False, "ops/recommendation.json 不存在")
    # 无法继续检查，直接输出
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": 0, "details": score_details}, f, indent=2)
    sys.exit(0)

# 2. 解析 JSON 并验证合法性 (10分)
try:
    with open(rec_path, "r") as f:
        data = json.load(f)
    add_score("JSON 格式合法", 10, 10, True, "ops/recommendation.json 解析成功")
    current_total = 20
except Exception as e:
    add_score("JSON 格式合法", 0, 10, False, f"JSON 解析失败: {e}")
    # 输出当前 score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": current_total, "details": score_details}, f, indent=2)
    sys.exit(0)

# 3-7: 检查关键字段 (每个 12 分，共 60 分)
# 预期值通过读取原始数据计算得到
# 先读取原始数据
def load_json(path):
    with open(os.path.join(workspace, path), "r") as f:
        return json.load(f)

stocks = load_json("data/stocks.json")["stocks"]
earnings_list = load_json("data/earnings.json")["earnings"]
news_list = load_json("data/news.json")["news"]
analysts_list = load_json("data/analysts.json")["analysts"]

# 找到 NXTC 的股票和 Q2 2026 earnings
nxtc_stock = next(s for s in stocks if s["ticker"] == "NXTC")
nxtc_eps_beat_pct = next(e for e in earnings_list if e["ticker"] == "NXTC" and e["quarter"] == "Q2 2026")["eps_beat_pct"]
nxtc_revenue_beat_pct = next(e for e in earnings_list if e["ticker"] == "NXTC" and e["quarter"] == "Q2 2026")["revenue_beat_pct"]

# 情感：找到 related_tickers 包含 NXTC 的新闻中 published_at 最新的那条的情感
nxtc_news = [n for n in news_list if "NXTC" in n.get("related_tickers", [])]
latest_news = max(nxtc_news, key=lambda x: x.get("published_at", ""))
expected_sentiment = latest_news["sentiment"]

# 分析师平均目标价：只考虑 coverage 包含 "NXTC" 的分析师
relevant_analysts = [a for a in analysts_list if "NXTC" in a.get("coverage", [])]
if relevant_analysts:
    avg_target = sum(a["price_target"] for a in relevant_analysts) / len(relevant_analysts)
    expected_target = round(avg_target, 2)
else:
    expected_target = None

# 推荐逻辑：如果 eps_beat_pct > 10 且 sentiment == "bullish" 则 STRONG_BUY，否则 BUY
if nxtc_eps_beat_pct > 10 and expected_sentiment == "bullish":
    expected_recommendation = "STRONG_BUY"
else:
    expected_recommendation = "BUY"

# 开始逐项检查
check_items = [
    ("ticker", data.get("ticker"), "NXTC", 12),
    ("eps_beat_pct", data.get("eps_beat_pct"), nxtc_eps_beat_pct, 12),
    ("revenue_beat_pct", data.get("revenue_beat_pct"), nxtc_revenue_beat_pct, 12),
    ("sentiment", data.get("sentiment"), expected_sentiment, 12),
    ("recommendation", data.get("recommendation"), expected_recommendation, 12),
    ("target_price", data.get("target_price"), expected_target, 12)
]

for item_name, actual, expected, max_score in check_items:
    if actual is None:
        add_score(f"字段 {item_name}", 0, max_score, False, f"缺失字段 {item_name}")
        current_total += 0
        continue
    # 数值比较 (允许浮点误差)
    if isinstance(expected, float):
        if abs(actual - expected) < 0.005:
            add_score(f"字段 {item_name}", max_score, max_score, True, f"正确: {actual}")
        else:
            add_score(f"字段 {item_name}", 0, max_score, False, f"期望 {expected}, 实际 {actual}")
    elif isinstance(expected, str):
        if actual == expected:
            add_score(f"字段 {item_name}", max_score, max_score, True, f"正确: {actual}")
        else:
            add_score(f"字段 {item_name}", 0, max_score, False, f"期望 '{expected}', 实际 '{actual}'")
    else:
        if actual == expected:
            add_score(f"字段 {item_name}", max_score, max_score, True, f"正确: {actual}")
        else:
            add_score(f"字段 {item_name}", 0, max_score, False, f"期望 {expected}, 实际 {actual}")
    current_total += 0  # 积分已累加

# 计算当前总分
total_score = sum(d["score"] for d in score_details)

# 8. 检查是否有多余的字段 (扣分项，最多扣 10 分)
allowed_keys = {"ticker", "eps_beat_pct", "revenue_beat_pct", "sentiment", "recommendation", "target_price"}
extra_keys = set(data.keys()) - allowed_keys
if extra_keys:
    penalty = min(len(extra_keys) * 5, 10)
    add_score("多余字段检查", -penalty, 0, False, f"存在额外字段: {extra_keys}")
    total_score = sum(d["score"] for d in score_details)  # 重新计算，可能有负数
else:
    add_score("多余字段检查", 0, 0, True, "没有多余字段")

# 确保总分为 0-100 之间，不低于0
total_score = max(0, total_score)
total_score = min(100, total_score)

# 写入结果
output = {
    "total_score": total_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(output, f, indent=2)

print(f"Verification complete. Score: {total_score}/100")
