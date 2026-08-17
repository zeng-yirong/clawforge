import os
import json

def build_env():
    # 创建所需目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # ========== stocks.json ==========
    stocks = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 145.20,
            "open_price": 143.50,
            "change_pct": 1.18,
            "volume": 2500000,
            "market_cap": 145200000000,
            "pe_ratio": 28.5,
            "revenue_growth_yoy": 0.12,
            "eps_growth_yoy": 0.25,
            "dividend_yield": 0.0
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "current_price": 87.30,
            "open_price": 86.90,
            "change_pct": 0.46,
            "volume": 1800000,
            "market_cap": 87300000000,
            "pe_ratio": 22.1,
            "revenue_growth_yoy": 0.08,
            "eps_growth_yoy": 0.18,
            "dividend_yield": 0.5
        },
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Technology",
            "current_price": 210.00,
            "open_price": 208.00,
            "change_pct": 0.96,
            "volume": 3100000,
            "market_cap": 210000000000,
            "pe_ratio": 35.0,
            "revenue_growth_yoy": 0.05,
            "eps_growth_yoy": 0.05,
            "dividend_yield": 0.2
        },
        {
            "ticker": "CONS",
            "company_name": "ConsumerFirst Brands",
            "sector": "Consumer Defensive",
            "current_price": 65.40,
            "open_price": 65.10,
            "change_pct": 0.46,
            "volume": 1200000,
            "market_cap": 65400000000,
            "pe_ratio": 18.2,
            "revenue_growth_yoy": 0.03,
            "eps_growth_yoy": 0.06,
            "dividend_yield": 1.8
        },
        {
            "ticker": "ENGY",
            "company_name": "PowerGrid Energy",
            "sector": "Utilities",
            "current_price": 42.80,
            "open_price": 43.00,
            "change_pct": -0.47,
            "volume": 900000,
            "market_cap": 42800000000,
            "pe_ratio": 14.5,
            "revenue_growth_yoy": 0.04,
            "eps_growth_yoy": 0.02,
            "dividend_yield": 3.2
        },
        {
            "ticker": "GLBL",
            "company_name": "Global Retail Inc",
            "sector": "Consumer Cyclical",
            "current_price": 33.50,
            "open_price": 33.20,
            "change_pct": 0.90,
            "volume": 2100000,
            "market_cap": 33500000000,
            "pe_ratio": 12.8,
            "revenue_growth_yoy": 0.02,
            "eps_growth_yoy": -0.03,
            "dividend_yield": 4.5
        }
    ]
    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ========== earnings.json ==========
    earnings = [
        {
            "earnings_id": "E001",
            "ticker": "TECH",
            "quarter": "Q1 2026",
            "report_date": "2026-04-15",
            "revenue_actual": 5200000000,
            "revenue_estimate": 5000000000,
            "revenue_beat": True,
            "revenue_beat_pct": 4.0,
            "eps_actual": 1.20,
            "eps_estimate": 1.10,
            "eps_beat": True,
            "eps_beat_pct": 9.09
        },
        {
            "earnings_id": "E002",
            "ticker": "NXTC",
            "quarter": "Q1 2026",
            "report_date": "2026-04-12",
            "revenue_actual": 3100000000,
            "revenue_estimate": 3000000000,
            "revenue_beat": True,
            "revenue_beat_pct": 3.33,
            "eps_actual": 0.95,
            "eps_estimate": 0.88,
            "eps_beat": True,
            "eps_beat_pct": 7.95
        },
        {
            "earnings_id": "E003",
            "ticker": "MFST",
            "quarter": "Q1 2026",
            "report_date": "2026-04-18",
            "revenue_actual": 9800000000,
            "revenue_estimate": 10000000000,
            "revenue_beat": False,
            "revenue_beat_pct": -2.0,
            "eps_actual": 0.95,
            "eps_estimate": 1.00,
            "eps_beat": False,
            "eps_beat_pct": -5.0
        },
        # 干扰记录：非技术板块，而且有一个脏数据（eps_actual 字符串）
        {
            "earnings_id": "E004",
            "ticker": "CONS",
            "quarter": "Q1 2026",
            "report_date": "2026-04-10",
            "revenue_actual": 1200000000,
            "revenue_estimate": 1150000000,
            "revenue_beat": True,
            "revenue_beat_pct": 4.35,
            "eps_actual": "N/A",           # 脏数据
            "eps_estimate": 0.40,
            "eps_beat": False,
            "eps_beat_pct": 0.0
        },
        {
            "earnings_id": "E005",
            "ticker": "ENGY",
            "quarter": "Q1 2026",
            "report_date": "2026-04-08",
            "revenue_actual": 800000000,
            "revenue_estimate": 820000000,
            "revenue_beat": False,
            "revenue_beat_pct": -2.44,
            "eps_actual": 0.22,
            "eps_estimate": 0.25,
            "eps_beat": False,
            "eps_beat_pct": -12.0
        },
        # 另一个季度数据，但 technology 板块不需要
        {
            "earnings_id": "E006",
            "ticker": "TECH",
            "quarter": "Q4 2025",
            "report_date": "2026-01-20",
            "revenue_actual": 5100000000,
            "revenue_estimate": 5050000000,
            "revenue_beat": True,
            "revenue_beat_pct": 0.99,
            "eps_actual": 1.15,
            "eps_estimate": 1.12,
            "eps_beat": True,
            "eps_beat_pct": 2.68
        }
    ]
    with open("data/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # ========== news.json ==========
    news = [
        {
            "news_id": "N001",
            "headline": "TechVentures Reports Strong Q1, Upgrades Guidance",
            "summary": "TECH exceeded expectations on both revenue and EPS.",
            "category": "earnings",
            "source": "Reuters",
            "published_at": "2026-04-16",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TECH"]
        },
        {
            "news_id": "N002",
            "headline": "Nexa Technologies Gains on Partnership Announcement",
            "summary": "NXTC signs deal with major cloud provider.",
            "category": "partnership",
            "source": "CNBC",
            "published_at": "2026-04-14",
            "sentiment": "bullish",
            "impact": "medium",
            "related_tickers": ["NXTC"]
        },
        {
            "news_id": "N003",
            "headline": "MegaFast Shipping Faces Regulatory Probe",
            "summary": "MFST under investigation for accounting irregularities.",
            "category": "regulatory",
            "source": "WSJ",
            "published_at": "2026-04-20",
            "sentiment": "bearish",
            "impact": "high",
            "related_tickers": ["MFST"]
        },
        {
            "news_id": "N004",
            "headline": "ConsumerFirst Brands Dividend Announcement",
            "summary": "CONS increases dividend by 5%.",
            "category": "product",
            "source": "Bloomberg",
            "published_at": "2026-04-11",
            "sentiment": "bullish",
            "impact": "low",
            "related_tickers": ["CONS"]
        },
        {
            "news_id": "N005",
            "headline": "Global Retail Same-Store Sales Dip",
            "summary": "GLBL reports weaker than expected sales.",
            "category": "earnings",
            "source": "Modern Healthcare",
            "published_at": "2026-04-09",
            "sentiment": "bearish",
            "impact": "medium",
            "related_tickers": ["GLBL"]
        }
    ]
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # ========== 干扰文件 (分析师、简报等) ==========
    os.makedirs("data/analysts", exist_ok=True)
    analysts = [
        {"analyst_id": "A001", "name": "Sarah Chen", "firm": "InvestWise Research", "coverage": ["TECH", "NXTC"], "rating": "Senior"},
        {"analyst_id": "A002", "name": "Mike Johnson", "firm": "Capital Markets", "coverage": ["MFST", "CONS"], "rating": "Analyst"}
    ]
    with open("data/analysts/analysts.json", "w") as f:
        json.dump(analysts, f, indent=2)

    os.makedirs("data/briefs", exist_ok=True)
    briefs = [
        {"brief_id": "B001", "title": "TECH - Q1 Earnings Preview", "ticker": "TECH", "created_by": "A001", "created_at": "2026-04-10", "updated_at": "2026-04-10", "brief_type": "earnings_preview", "status": "draft", "summary": "Preview of Q1 results", "investment_rationale": ["Strong growth"], "risks": ["Competition"], "valuation_methodology": "DCF with 2027 projections"}
    ]
    with open("data/briefs/briefs.json", "w") as f:
        json.dump(briefs, f, indent=2)

if __name__ == "__main__":
    build_env()
