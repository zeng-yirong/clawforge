import os
import json
import random
from datetime import datetime

def build_env():
    # 确保 data 和 ops 目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- stocks.json ----
    stocks = {
        "stocks": [
            {
                "ticker": "NXTC",
                "company_name": "Nexa Technologies",
                "sector": "Technology",
                "current_price": 42.50,
                "open_price": 41.80,
                "change_pct": 1.67,
                "volume": 3400000,
                "market_cap": 8500000000,
                "pe_ratio": 34.0,
                "revenue_growth_yoy": 12.5,
                "eps_growth_yoy": 22.3,
                "dividend_yield": 0.0
            },
            {
                "ticker": "TECH",
                "company_name": "TechVentures Inc",
                "sector": "Technology",
                "current_price": 88.20,
                "open_price": 87.50,
                "change_pct": 0.80,
                "volume": 1200000,
                "market_cap": 17640000000,
                "pe_ratio": 45.2,
                "revenue_growth_yoy": 18.7,
                "eps_growth_yoy": 25.1,
                "dividend_yield": 0.5
            },
            {
                "ticker": "MFST",
                "company_name": "MegaFast Shipping",
                "sector": "Industrials",
                "current_price": 145.30,
                "open_price": 144.00,
                "change_pct": 0.90,
                "volume": 890000,
                "market_cap": 29060000000,
                "pe_ratio": 22.8,
                "revenue_growth_yoy": 5.2,
                "eps_growth_yoy": 8.1,
                "dividend_yield": 1.2
            }
        ]
    }
    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ---- earnings.json (干扰：包含 Q1 和 Q2，还有另一支股票的旧数据) ----
    earnings = {
        "earnings": [
            {
                "earnings_id": "er_nxtc_q1_2026",
                "ticker": "NXTC",
                "quarter": "Q1 2026",
                "report_date": "2026-04-15",
                "revenue_actual": 480000000,
                "revenue_estimate": 475000000,
                "revenue_beat": True,
                "revenue_beat_pct": 1.05,
                "eps_actual": 1.02,
                "eps_estimate": 0.98,
                "eps_beat": True,
                "eps_beat_pct": 4.08
            },
            {
                "earnings_id": "er_nxtc_q2_2026",
                "ticker": "NXTC",
                "quarter": "Q2 2026",
                "report_date": "2026-07-20",
                "revenue_actual": 520000000,
                "revenue_estimate": 500000000,
                "revenue_beat": True,
                "revenue_beat_pct": 4.0,
                "eps_actual": 1.25,
                "eps_estimate": 1.10,
                "eps_beat": True,
                "eps_beat_pct": 13.64
            },
            {
                "earnings_id": "er_tech_q2_2026",
                "ticker": "TECH",
                "quarter": "Q2 2026",
                "report_date": "2026-07-22",
                "revenue_actual": 320000000,
                "revenue_estimate": 310000000,
                "revenue_beat": True,
                "revenue_beat_pct": 3.23,
                "eps_actual": 2.05,
                "eps_estimate": 1.90,
                "eps_beat": True,
                "eps_beat_pct": 7.89
            }
        ]
    }
    with open("data/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # ---- news.json (干扰：多条新闻，只有一条与 NXTC 相关且情感为 bullish) ----
    news = {
        "news": [
            {
                "news_id": "nw_001",
                "headline": "Nexa Technologies Q2 Earnings Beat Estimates, Guidance Raised",
                "summary": "NXTC reported stronger-than-expected results and lifted FY2026 guidance.",
                "category": "earnings",
                "source": "Bloomberg",
                "published_at": "2026-07-20T22:30:00Z",
                "sentiment": "bullish",
                "impact": "high",
                "related_tickers": ["NXTC"]
            },
            {
                "news_id": "nw_002",
                "headline": "TechVentures Partners with Global Cloud Provider",
                "summary": "TECH announces strategic alliance to expand AI capabilities.",
                "category": "partnership",
                "source": "TechCrunch",
                "published_at": "2026-07-21T14:00:00Z",
                "sentiment": "bullish",
                "impact": "medium",
                "related_tickers": ["TECH"]
            },
            {
                "news_id": "nw_003",
                "headline": "Fed Signals Rate Pause – Markets Rally",
                "summary": "Macro sentiment improves as Fed holds rates steady.",
                "category": "macro",
                "source": "Reuters",
                "published_at": "2026-07-19T18:00:00Z",
                "sentiment": "neutral",
                "impact": "medium",
                "related_tickers": ["MFST", "NXTC"]  # 虽然相关，但情感 neutral，不影响主结论
            }
        ]
    }
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # ---- analysts.json (干扰：覆盖 TECH 的分析师，以及一个旧版本分析师数据) ----
    analysts = {
        "analysts": [
            {
                "analyst_id": "a_emily",
                "name": "Emily Brown",
                "firm": "Capital Markets",
                "coverage": ["NXTC", "TECH"],
                "rating": "Senior",
                "price_target": 48.0
            },
            {
                "analyst_id": "a_mike",
                "name": "Mike Johnson",
                "firm": "Global Equities",
                "coverage": ["NXTC"],
                "rating": "Analyst",
                "price_target": 52.5
            },
            {
                "analyst_id": "a_sarah",
                "name": "Sarah Chen",
                "firm": "InvestWise Research",
                "coverage": ["TECH"],
                "rating": "Associate",
                "price_target": 55.0  # 不覆盖 NXTC，作为干扰
            },
            {
                "analyst_id": "a_tom_old",
                "name": "Tom Davis",
                "firm": "Old Research",
                "coverage": ["NXTC", "MFST"],
                "rating": "Analyst",
                "price_target": 38.0,  # 过时数据，但仍在文件里，agent 应视为有效？为了唯一性，我们要求只考虑包含 NXTC 的分析师，且不排除，所以平均值会包含 Tom Davis。但这样平均值会变成 (48+52.5+38)/3=46.17，与之前不同。我们需要决定是否排除。考虑到干扰，可以保留，但必须确定唯一平均值。我们可以在 prompt 中暗示“算一下覆盖它的那些分析师的目标价均值”，Tom Davis 覆盖的 "coverage": ["NXTC","MFST"]，所以他也算。那么平均值变为 (48+52.5+38)/3=46.166666... 四舍五入到两位小数 46.17。为了更好地区分干扰，我们可以让 Tom Davis 的 coverage 不包含 NXTC？这样他就不算了。但既然已经写了，我们修改：让 Tom Davis 的 coverage 只有 ["MFST"]，这样就不参与。更干净。
            }
        ]
    }
    # 修正：Tom Davis 不覆盖 NXTC
    analysts["analysts"][3]["coverage"] = ["MFST"]
    with open("data/analysts.json", "w") as f:
        json.dump(analysts, f, indent=2)

    # 额外干扰：一个过期 earnings 备份
    with open("data/earnings_archive_2025.json", "w") as f:
        json.dump({"dummy": True}, f)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
