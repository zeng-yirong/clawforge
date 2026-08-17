import os
import json
import shutil

def build_env():
    # 确保从  开始（cwd 已为此）
    base = "."

    # 清理残留
    for p in ["data", "reports"]:
        if os.path.exists(p):
            shutil.rmtree(p)

    # ---------- data/stocks/stocks.json ----------
    os.makedirs(os.path.join(base, "data", "stocks"), exist_ok=True)
    stocks = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 145.20,
            "open_price": 148.0,
            "change_pct": -1.89,
            "volume": 3200000,
            "market_cap": 29000000000,
            "pe_ratio": 32.5,
            "revenue_growth_yoy": 8.2,
            "eps_growth_yoy": -2.4,
            "dividend_yield": 0.0
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "current_price": 87.60,
            "open_price": 84.20,
            "change_pct": 4.04,
            "volume": 5600000,
            "market_cap": 17500000000,
            "pe_ratio": 28.1,
            "revenue_growth_yoy": 15.6,
            "eps_growth_yoy": 22.3,
            "dividend_yield": 0.5
        },
        {
            "ticker": "HLTH",
            "company_name": "HealthLink Systems",
            "sector": "Healthcare",
            "current_price": 212.40,
            "open_price": 210.0,
            "change_pct": 1.14,
            "volume": 1800000,
            "market_cap": 42000000000,
            "pe_ratio": 45.2,
            "revenue_growth_yoy": 12.1,
            "eps_growth_yoy": 9.8,
            "dividend_yield": 1.2
        },
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Industrials",
            "current_price": 63.80,
            "open_price": 64.50,
            "change_pct": -1.08,
            "volume": 4100000,
            "market_cap": 31000000000,
            "pe_ratio": 18.6,
            "revenue_growth_yoy": 5.4,
            "eps_growth_yoy": 3.2,
            "dividend_yield": 2.3
        },
        {
            "ticker": "CONS",
            "company_name": "ConsumerFirst Brands",
            "sector": "Consumer Defensive",
            "current_price": 98.10,
            "open_price": 98.0,
            "change_pct": 0.10,
            "volume": 2200000,
            "market_cap": 18000000000,
            "pe_ratio": 22.3,
            "revenue_growth_yoy": 3.8,
            "eps_growth_yoy": 4.1,
            "dividend_yield": 1.8
        }
    ]
    with open(os.path.join(base, "data", "stocks", "stocks.json"), "w") as f:
        json.dump(stocks, f, indent=2)

    # ---------- data/earnings/earnings.json ----------
    os.makedirs(os.path.join(base, "data", "earnings"), exist_ok=True)
    earnings = [
        {
            "earnings_id": "ern_001",
            "ticker": "NXTC",
            "quarter": "Q2 2026",
            "report_date": "2026-07-10",
            "revenue_actual": 1240000000,
            "revenue_estimate": 1180000000,
            "revenue_beat": True,
            "revenue_beat_pct": 5.1,
            "eps_actual": 1.52,
            "eps_estimate": 1.32,
            "eps_beat": True,
            "eps_beat_pct": 15.2
        },
        {
            "earnings_id": "ern_002",
            "ticker": "TECH",
            "quarter": "Q1 2026",
            "report_date": "2026-04-28",
            "revenue_actual": 2650000000,
            "revenue_estimate": 2800000000,
            "revenue_beat": False,
            "revenue_beat_pct": -5.36,
            "eps_actual": 0.94,
            "eps_estimate": 1.05,
            "eps_beat": False,
            "eps_beat_pct": -10.5
        },
        {
            "earnings_id": "ern_003",
            "ticker": "HLTH",
            "quarter": "Q2 2026",
            "report_date": "2026-07-08",
            "revenue_actual": 980000000,
            "revenue_estimate": 950000000,
            "revenue_beat": True,
            "revenue_beat_pct": 3.16,
            "eps_actual": 2.10,
            "eps_estimate": 2.00,
            "eps_beat": True,
            "eps_beat_pct": 5.0
        },
        {
            "earnings_id": "ern_004",
            "ticker": "MFST",
            "quarter": "Q1 2026",
            "report_date": "2026-04-15",
            "revenue_actual": 5500000000,
            "revenue_estimate": 5400000000,
            "revenue_beat": True,
            "revenue_beat_pct": 1.85,
            "eps_actual": 0.72,
            "eps_estimate": 0.69,
            "eps_beat": True,
            "eps_beat_pct": 4.3
        }
    ]
    with open(os.path.join(base, "data", "earnings", "earnings.json"), "w") as f:
        json.dump(earnings, f, indent=2)

    # ---------- data/news/news.json ----------
    os.makedirs(os.path.join(base, "data", "news"), exist_ok=True)
    news = [
        {
            "news_id": "nws_001",
            "headline": "Nexa Technologies Partners with Global AI Leader on Edge Computing",
            "summary": "NXTC announced a strategic partnership to deploy edge AI solutions, seen as major growth catalyst.",
            "category": "partnership",
            "source": "TechCrunch",
            "published_at": "2026-07-12",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["NXTC"]
        },
        {
            "news_id": "nws_002",
            "headline": "TechVentures Faces SEC Investigation Over Revenue Recognition",
            "summary": "The SEC has opened an inquiry into TECH's accounting practices; stock drops 4% in after-hours.",
            "category": "regulatory",
            "source": "WSJ",
            "published_at": "2026-07-14",
            "sentiment": "bearish",
            "impact": "high",
            "related_tickers": ["TECH"]
        },
        {
            "news_id": "nws_003",
            "headline": "Healthcare M&A Heats Up: HealthLink in Talks",
            "summary": "HLTH is reportedly in early acquisition discussions, lifting sector sentiment.",
            "category": "sector",
            "source": "Bloomberg",
            "published_at": "2026-07-11",
            "sentiment": "bullish",
            "impact": "medium",
            "related_tickers": ["HLTH"]
        },
        {
            "news_id": "nws_004",
            "headline": "MegaFast Shipping Q1 Results Meet Expectations",
            "summary": "MFST delivered inline quarterly results; management reiterated guidance.",
            "category": "earnings",
            "source": "CNBC",
            "published_at": "2026-04-16",
            "sentiment": "neutral",
            "impact": "medium",
            "related_tickers": ["MFST"]
        },
        {
            "news_id": "nws_005",
            "headline": "ConsumerFirst Brands Expands into Organic Segment",
            "summary": "CONS acquires small organic food company, stock rises modestly.",
            "category": "product",
            "source": "Reuters",
            "published_at": "2026-07-09",
            "sentiment": "bullish",
            "impact": "low",
            "related_tickers": ["CONS"]
        }
    ]
    with open(os.path.join(base, "data", "news", "news.json"), "w") as f:
        json.dump(news, f, indent=2)

    # ---------- data/briefs/tech_brief.json (旧简报) ----------
    os.makedirs(os.path.join(base, "data", "briefs"), exist_ok=True)
    old_brief = {
        "brief_id": "brf_tech_v1",
        "title": "Technology Sector Brief - Initial View",
        "tickers": ["TECH", "NXTC"],
        "created_at": "2026-07-05",
        "updated_at": "2026-07-05",
        "status": "draft",
        "summary": "Initial overview of Technology sector. Both companies show moderate growth potential.",
        "recommendations": [
            {"ticker": "TECH", "action": "Hold", "confidence": "Medium"},
            {"ticker": "NXTC", "action": "Hold", "confidence": "Medium"}
        ]
    }
    with open(os.path.join(base, "data", "briefs", "tech_brief.json"), "w") as f:
        json.dump(old_brief, f, indent=2)

    # ---------- 干扰文件 ----------
    # 一个无关的 txt 文件
    with open(os.path.join(base, "data", "readme.txt"), "w") as f:
        f.write("Don't touch this.\n")
    # 一个旧的备份目录
    os.makedirs(os.path.join(base, "data", "backup"), exist_ok=True)
    with open(os.path.join(base, "data", "backup", "stocks_2026_06.json"), "w") as f:
        json.dump({"dummy": True}, f)

    # 确保 reports/ 目录存在（但为空）
    os.makedirs(os.path.join(base, "reports"), exist_ok=True)

if __name__ == "__main__":
    build_env()
