import os
import sys
import json
import math

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def calc_sentiment_score(sentiment):
    mapping = {'bullish': 1, 'neutral': 0, 'bearish': -1}
    return mapping.get(sentiment, 0)

def calc_analyst_rating(level):
    mapping = {'Senior': 3, 'Analyst': 2, 'Associate': 1}
    return mapping.get(level, 0)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 output 目录是否存在 (5分)
    output_dir = os.path.join(workspace, "output")
    dir_exists = os.path.isdir(output_dir)
    details.append({
        "item": "output directory exists",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "output/ found" if dir_exists else "output/ missing"
    })
    if not dir_exists:
        # 无法继续，直接写结果
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return

    # 2. 检查 tech_brief.json 是否存在 (10分)
    brief_path = os.path.join(output_dir, "tech_brief.json")
    file_exists = os.path.isfile(brief_path)
    details.append({
        "item": "output/tech_brief.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "file found" if file_exists else "file missing"
    })
    if not file_exists:
        total_score = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 解析 JSON 合法性 (10分)
    try:
        brief = load_json(brief_path)
        if not isinstance(brief, list):
            details.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": "root is not a list"})
            # 仍有部分得分，但为了简化，直接给0
        else:
            details.append({"item": "JSON is a list", "score": 10, "max_score": 10, "passed": True, "reason": "valid list"})
    except Exception as e:
        details.append({"item": "JSON parseable", "score": 0, "max_score": 10, "passed": False, "reason": f"parse error: {str(e)}"})
        total_score = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. 读取原始数据重新计算期望结果 (该步骤不扣分，但用于后续比对)
    # 读取 stocks (去重，取最后一条作为有效数据; 但实际业务中代理应处理重复，这里按我们设计：重复的TECH旧记录应被忽略，我们只取 sector Technology 且去重后唯一)
    stocks_raw = load_json(os.path.join(workspace, "data/stocks/stocks.json"))
    # 构建 ticker 到最新记录（按 index 大的覆盖小的）只取 Technology
    tech_stocks = {}
    for s in stocks_raw:
        if s["sector"] != "Technology":
            continue
        ticker = s["ticker"]
        # 如果有多个，用后出现的覆盖（但预期代理应去重，我们按最后一条）
        tech_stocks[ticker] = s
    # 期望的股票列表：TECH, NXTC
    expected_tickers = sorted(tech_stocks.keys())  # ["NXTC","TECH"]

    # 读取 earnings, 筛选 Q2 2026
    earnings_raw = load_json(os.path.join(workspace, "data/earnings/earnings.json"))
    earnings_q2 = {}
    for e in earnings_raw:
        if e["quarter"] == "Q2 2026":
            earnings_q2[e["ticker"]] = e

    # 读取 news，筛选 published_at 在 2026-04-08 00:00:00 UTC 及之后
    from datetime import datetime, timezone
    cutoff = datetime(2026, 4, 8, tzinfo=timezone.utc)
    news_raw = load_json(os.path.join(workspace, "data/news/news.json"))
    news_by_ticker = {}
    for n in news_raw:
        pub = datetime.fromisoformat(n["published_at"].replace("Z","+00:00"))
        if pub >= cutoff:
            for t in n["related_tickers"]:
                news_by_ticker.setdefault(t, []).append(n)

    # 读取 analysts
    analysts_raw = load_json(os.path.join(workspace, "data/analysts/analysts.json"))
    analysts_by_ticker = {}
    for a in analysts_raw:
        for t in a["coverage"]:
            analysts_by_ticker.setdefault(t, []).append(a)

    # 计算期望评分
    expected_output = []
    for ticker in expected_tickers:
        s = tech_stocks[ticker]
        revenue_growth = s["revenue_growth_yoy"]
        eps_growth = s["eps_growth_yoy"]

        # news sentiment
        news_list = news_by_ticker.get(ticker, [])
        if news_list:
            avg_sentiment = sum(calc_sentiment_score(n["sentiment"]) for n in news_list) / len(news_list)
        else:
            avg_sentiment = 0.0

        # analyst rating
        analysts_list = analysts_by_ticker.get(ticker, [])
        if analysts_list:
            avg_rating = sum(calc_analyst_rating(a["rating"]) for a in analysts_list) / len(analysts_list)
        else:
            avg_rating = 0.0

        composite = revenue_growth * 0.3 + eps_growth * 0.3 + avg_sentiment * 10 + avg_rating * 0.2
        expected_output.append({
            "ticker": ticker,
            "company_name": s["company_name"],
            "current_price": s["current_price"],
            "revenue_growth_yoy": revenue_growth,
            "eps_growth_yoy": eps_growth,
            "avg_sentiment_score": round(avg_sentiment, 4),
            "avg_analyst_rating": round(avg_rating, 4),
            "composite_score": round(composite, 4)
        })
    # 按 composite_score 降序
    expected_output.sort(key=lambda x: x["composite_score"], reverse=True)

    # 5. 验证输出数组长度 (10分)
    len_ok = len(brief) == len(expected_output)
    details.append({
        "item": "output array length matches expected (2)",
        "score": 10 if len_ok else 0,
        "max_score": 10,
        "passed": len_ok,
        "reason": f"length {len(brief)}" if len_ok else f"expected {len(expected_output)}, got {len(brief)}"
    })

    # 6. 验证每个股票的必要字段 (15分)
    required_fields = ["ticker", "company_name", "current_price", "revenue_growth_yoy",
                       "eps_growth_yoy", "avg_sentiment_score", "avg_analyst_rating", "composite_score"]
    fields_ok = all(
        all(field in item for field in required_fields) for item in brief
    )
    details.append({
        "item": "all required fields present in each item",
        "score": 15 if fields_ok else 0,
        "max_score": 15,
        "passed": fields_ok,
        "reason": "fields ok" if fields_ok else "missing fields"
    })
    if not fields_ok:
        brief = []  # 不继续检查数值

    # 7. 验证排序正确性 (15分)
    sorted_ok = True
    if len(brief) >= 2:
        for i in range(len(brief)-1):
            try:
                if brief[i]["composite_score"] < brief[i+1]["composite_score"]:
                    sorted_ok = False
                    break
            except:
                sorted_ok = False
                break
    details.append({
        "item": "items sorted by composite_score descending",
        "score": 15 if sorted_ok else 0,
        "max_score": 15,
        "passed": sorted_ok,
        "reason": "correct order" if sorted_ok else "order incorrect"
    })

    # 8. 验证关键数值 (35分：TECH 和 NXTC 各 17.5分，近似匹配)
    numeric_score = 0
    if len(brief) >= 2 and fields_ok:
        # 将输出按 ticker 索引
        output_map = {item["ticker"]: item for item in brief}
        for exp in expected_output:
            ticker = exp["ticker"]
            if ticker not in output_map:
                numeric_score += 0
                continue
            act = output_map[ticker]
            match = True
            # 检查 composite_score 误差在 0.01 内
            if abs(act["composite_score"] - exp["composite_score"]) > 0.01:
                match = False
            # 检查 avg_sentiment_score
            if abs(act["avg_sentiment_score"] - exp["avg_sentiment_score"]) > 0.01:
                match = False
            # 检查 avg_analyst_rating
            if abs(act["avg_analyst_rating"] - exp["avg_analyst_rating"]) > 0.01:
                match = False
            # 检查 revenue_growth_yoy
            if abs(act["revenue_growth_yoy"] - exp["revenue_growth_yoy"]) > 0.001:
                match = False
            # 检查 eps_growth_yoy
            if abs(act["eps_growth_yoy"] - exp["eps_growth_yoy"]) > 0.001:
                match = False
            # 检查 current_price
            if abs(act["current_price"] - exp["current_price"]) > 0.01:
                match = False
            if match:
                numeric_score += 17.5
        numeric_score = min(35, int(numeric_score))  # 整数
    details.append({
        "item": "numerical accuracy for both stocks",
        "score": numeric_score,
        "max_score": 35,
        "passed": numeric_score >= 35,
        "reason": f"scored {numeric_score}/35"
    })

    total_score = sum(d["score"] for d in details)
    # 确保总分0-100整数
    result = {
        "total_score": round(total_score),
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
