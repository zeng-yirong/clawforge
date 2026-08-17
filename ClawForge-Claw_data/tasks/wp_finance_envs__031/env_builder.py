import os
import json
import random
from datetime import datetime

random.seed(42)


def create_stocks():
    stocks = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 150.25,
            "open_price": 148.10,
            "change_pct": 1.45,
            "volume": 2340000,
            "market_cap": 75000000000,
            "pe_ratio": 25.6,
            "revenue_growth_yoy": 18.2,
            "eps_growth_yoy": 22.0,
            "dividend_yield": 0.0,
        },
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Technology",
            "current_price": 310.80,
            "open_price": 315.00,
            "change_pct": -1.33,
            "volume": 1980000,
            "market_cap": 155000000000,
            "pe_ratio": 30.1,
            "revenue_growth_yoy": 5.7,
            "eps_growth_yoy": -3.2,
            "dividend_yield": 0.8,
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Healthcare",
            "current_price": 82.40,
            "open_price": 81.90,
            "change_pct": 0.61,
            "volume": 550000,
            "market_cap": 4100000000,
            "pe_ratio": 18.4,
            "revenue_growth_yoy": 12.1,
            "eps_growth_yoy": 15.0,
            "dividend_yield": 0.2,
        },
        {
            "ticker": "HLTH",
            "company_name": "HealthLink Systems",
            "sector": "Healthcare",
            "current_price": 210.50,
            "open_price": 209.80,
            "change_pct": 0.33,
            "volume": 890000,
            "market_cap": 42000000000,
            "pe_ratio": 22.8,
            "revenue_growth_yoy": 9.4,
            "eps_growth_yoy": 11.0,
            "dividend_yield": 0.15,
        },
        {
            "ticker": "FNS",
            "company_name": "FinServe Corp",
            "sector": "Financial Services",
            "current_price": 45.60,
            "open_price": 45.50,
            "change_pct": 0.22,
            "volume": 3200000,
            "market_cap": 22800000000,
            "pe_ratio": 12.4,
            "revenue_growth_yoy": 3.2,
            "eps_growth_yoy": 4.1,
            "dividend_yield": 2.5,
        },
    ]
    os.makedirs("data/stocks", exist_ok=True)
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)


def create_earnings():
    earnings = [
        {
            "earnings_id": "e_tech_q2_2026",
            "ticker": "TECH",
            "quarter": "Q2 2026",
            "report_date": "2026-07-15",
            "revenue_actual": 1200000,
            "revenue_estimate": 1100000,
            "revenue_beat": True,
            "revenue_beat_pct": 9.09,
            "eps_actual": 2.25,
            "eps_estimate": 2.00,
            "eps_beat": True,
            "eps_beat_pct": 12.5,
        },
        {
            "earnings_id": "e_mfst_q2_2026",
            "ticker": "MFST",
            "quarter": "Q2 2026",
            "report_date": "2026-07-20",
            "revenue_actual": 5000000,
            "revenue_estimate": 5200000,
            "revenue_beat": False,
            "revenue_beat_pct": -3.85,
            "eps_actual": 1.10,
            "eps_estimate": 1.20,
            "eps_beat": False,
            "eps_beat_pct": -8.33,
        },
        {
            "earnings_id": "e_nxtc_q2_2026",
            "ticker": "NXTC",
            "quarter": "Q2 2026",
            "report_date": "2026-07-10",
            "revenue_actual": 800000,
            "revenue_estimate": 750000,
            "revenue_beat": True,
            "revenue_beat_pct": 6.67,
            "eps_actual": 0.55,
            "eps_estimate": 0.50,
            "eps_beat": True,
            "eps_beat_pct": 10.0,
        },
    ]
    os.makedirs("data/earnings", exist_ok=True)
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)


def create_news():
    news = [
        {
            "news_id": "n_tech_001",
            "headline": "TechVentures Announces Strategic Partnership with AI Startup",
            "summary": "TechVentures partners with DeepMind AI to accelerate cloud product development.",
            "category": "partnership",
            "source": "TechCrunch",
            "published_at": "2026-07-16",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TECH"],
        },
        {
            "news_id": "n_mfst_001",
            "headline": "MegaFast Shipping Faces Regulatory Probe Over Delivery Delays",
            "summary": "The FTC opens an investigation into MegaFast's logistics practices.",
            "category": "regulatory",
            "source": "WSJ",
            "published_at": "2026-07-18",
            "sentiment": "bearish",
            "impact": "high",
            "related_tickers": ["MFST"],
        },
        {
            "news_id": "n_nxtc_001",
            "headline": "Nexa Technologies Reports Strong Q2 Earnings, Shares Gain",
            "summary": "Nexa beat EPS estimates but revenue growth was in line with expectations.",
            "category": "earnings",
            "source": "Bloomberg",
            "published_at": "2026-07-11",
            "sentiment": "neutral",
            "impact": "medium",
            "related_tickers": ["NXTC"],
        },
        {
            "news_id": "n_macro_001",
            "headline": "Fed Holds Rates Steady, Signals Possible Cut Later This Year",
            "summary": "Federal Reserve leaves interest rates unchanged, but hints at easing.",
            "category": "macro",
            "source": "Reuters",
            "published_at": "2026-07-14",
            "sentiment": "neutral",
            "impact": "medium",
            "related_tickers": [],
        },
        {
            "news_id": "n_tech_002",
            "headline": "TechVentures Wins $500M Cloud Contract from Government",
            "summary": "The 5-year deal boosts TechVentures' enterprise segment.",
            "category": "product",
            "source": "CNBC",
            "published_at": "2026-07-12",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TECH"],
        },
    ]
    os.makedirs("data/news", exist_ok=True)
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)


def main():
    create_stocks()
    create_earnings()
    create_news()
    # 创建干扰目录和文件（不会被任务使用）
    os.makedirs("data/old_backups", exist_ok=True)
    with open("data/old_backups/earnings_archive.json", "w") as f:
        f.write("[]")
    with open("data/notes.txt", "w") as f:
        f.write("Random thoughts about market trends...\n")


if __name__ == "__main__":
    main()
