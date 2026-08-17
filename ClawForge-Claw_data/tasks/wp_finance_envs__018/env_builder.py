import os
import json
from datetime import datetime, timedelta

def build_env():
    # 目录结构
    os.makedirs("data/stocks", exist_ok=True)
    os.makedirs("data/earnings", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("data/analysts", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # 1. stocks.json – 包含两个技术股 + 多个干扰股
    stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology",
         "current_price": 150.25, "open_price": 148.0, "change_pct": 1.52,
         "volume": 5000000, "market_cap": 5000000000, "pe_ratio": 25.5,
         "revenue_growth_yoy": 0.15, "eps_growth_yoy": 0.22, "dividend_yield": 0.01},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology",
         "current_price": 85.5, "open_price": 84.0, "change_pct": 1.79,
         "volume": 3000000, "market_cap": 2500000000, "pe_ratio": 20.1,
         "revenue_growth_yoy": 0.12, "eps_growth_yoy": 0.18, "dividend_yield": 0.02},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials",
         "current_price": 75.0, "open_price": 74.2, "change_pct": 1.08,
         "volume": 1200000, "market_cap": 3000000000, "pe_ratio": 18.0,
         "revenue_growth_yoy": 0.08, "eps_growth_yoy": 0.06, "dividend_yield": 0.03},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare",
         "current_price": 220.0, "open_price": 218.5, "change_pct": 0.68,
         "volume": 800000, "market_cap": 12000000000, "pe_ratio": 32.0,
         "revenue_growth_yoy": 0.05, "eps_growth_yoy": 0.04, "dividend_yield": 0.0},
        # 干扰：重复的 TECH（旧价格）
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology",
         "current_price": 148.0, "open_price": 147.0, "change_pct": 0.68,
         "volume": 4000000, "market_cap": 4950000000, "pe_ratio": 26.0,
         "revenue_growth_yoy": 0.14, "eps_growth_yoy": 0.21, "dividend_yield": 0.01},
    ]
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # 2. earnings.json – 只保留 TECH 和 NXTC 的 Q2 2026，其他季度和股票为干扰
    earnings = [
        {"earnings_id": "E_TECH_Q2_2026", "ticker": "TECH", "quarter": "Q2 2026",
         "report_date": "2026-04-10", "revenue_actual": 1200000000,
         "revenue_estimate": 1150000000, "revenue_beat": True, "revenue_beat_pct": 4.35,
         "eps_actual": 1.52, "eps_estimate": 1.40, "eps_beat": True, "eps_beat_pct": 8.57},
        {"earnings_id": "E_NXTC_Q2_2026", "ticker": "NXTC", "quarter": "Q2 2026",
         "report_date": "2026-04-12", "revenue_actual": 600000000,
         "revenue_estimate": 580000000, "revenue_beat": True, "revenue_beat_pct": 3.45,
         "eps_actual": 0.95, "eps_estimate": 0.90, "eps_beat": True, "eps_beat_pct": 5.56},
        # 干扰：旧季度
        {"earnings_id": "E_TECH_Q1_2026", "ticker": "TECH", "quarter": "Q1 2026",
         "report_date": "2026-01-15", "revenue_actual": 1100000000,
         "revenue_estimate": 1080000000, "revenue_beat": True, "revenue_beat_pct": 1.85,
         "eps_actual": 1.35, "eps_estimate": 1.30, "eps_beat": True, "eps_beat_pct": 3.85},
        {"earnings_id": "E_MFST_Q2_2026", "ticker": "MFST", "quarter": "Q2 2026",
         "report_date": "2026-04-08", "revenue_actual": 800000000,
         "revenue_estimate": 810000000, "revenue_beat": False, "revenue_beat_pct": -1.23,
         "eps_actual": 0.60, "eps_estimate": 0.62, "eps_beat": False, "eps_beat_pct": -3.23},
    ]
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # 3. news.json – 最近一周的新闻，以及一些旧新闻
    now = datetime(2026, 4, 15)
    week_ago = now - timedelta(days=7)  # 2026-04-08
    news = [
        {"news_id": "n1", "headline": "TechVentures beats Q2 estimates",
         "summary": "Strong revenue growth driven by cloud segment",
         "category": "earnings", "source": "Bloomberg",
         "published_at": "2026-04-12T10:30:00Z",
         "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "n2", "headline": "Nexa announces new chip partnership",
         "summary": "Partnership with global automaker for autonomous driving",
         "category": "partnership", "source": "TechCrunch",
         "published_at": "2026-04-14T08:00:00Z",
         "sentiment": "bullish", "impact": "high", "related_tickers": ["NXTC"]},
        {"news_id": "n3", "headline": "Regulatory scrutiny on TechVentures",
         "summary": "FTC investigates data privacy practices",
         "category": "regulatory", "source": "Reuters",
         "published_at": "2026-04-10T14:00:00Z",
         "sentiment": "bearish", "impact": "medium", "related_tickers": ["TECH"]},
        {"news_id": "n4", "headline": "Nexa product launch delayed",
         "summary": "Supply chain issues push next-gen device to Q3",
         "category": "product", "source": "CNBC",
         "published_at": "2026-04-09T09:00:00Z",
         "sentiment": "bearish", "impact": "medium", "related_tickers": ["NXTC"]},
        {"news_id": "n5", "headline": "TechVentures executive resignation",
         "summary": "CFO steps down amid internal restructuring",
         "category": "product", "source": "WSJ",
         "published_at": "2026-04-08T16:00:00Z",
         "sentiment": "bearish", "impact": "medium", "related_tickers": ["TECH"]},
        # 干扰：旧新闻（一周前）
        {"news_id": "n6", "headline": "TechVentures old news",
         "summary": "Last year's report",
         "category": "earnings", "source": "Bloomberg",
         "published_at": "2026-03-20T10:00:00Z",
         "sentiment": "neutral", "impact": "low", "related_tickers": ["TECH"]},
        # 干扰：不相关股票新闻
        {"news_id": "n7", "headline": "MegaFast Shipping expands fleet",
         "summary": "New routes",
         "category": "product", "source": "Reuters",
         "published_at": "2026-04-13T11:00:00Z",
         "sentiment": "bullish", "impact": "medium", "related_tickers": ["MFST"]},
    ]
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # 4. analysts.json – 覆盖 TECH 和 NXTC 的分析师，以及干扰
    analysts = [
        {"analyst_id": "A1", "name": "Emily Brown", "firm": "Capital Markets",
         "coverage": ["TECH"], "rating": "Senior"},
        {"analyst_id": "A2", "name": "Mike Johnson", "firm": "Global Equities",
         "coverage": ["TECH", "NXTC"], "rating": "Analyst"},
        {"analyst_id": "A3", "name": "Sarah Chen", "firm": "InvestWise Research",
         "coverage": ["NXTC"], "rating": "Senior"},
        {"analyst_id": "A4", "name": "Tom Davis", "firm": "Capital Markets",
         "coverage": ["MFST"], "rating": "Associate"},  # 干扰
        {"analyst_id": "A5", "name": "Lisa Wang", "firm": "Global Equities",
         "coverage": ["HLTH"], "rating": "Analyst"},  # 干扰
    ]
    with open("data/analysts/analysts.json", "w") as f:
        json.dump(analysts, f, indent=2)

if __name__ == "__main__":
    build_env()
