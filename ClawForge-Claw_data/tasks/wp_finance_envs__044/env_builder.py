import os
import json
from datetime import datetime, timezone

def build_env():
    # Create directories
    os.makedirs("data/stocks", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("data/earnings", exist_ok=True)
    os.makedirs("data/analysts", exist_ok=True)
    os.makedirs("briefs", exist_ok=True)

    # --- stocks.json ---
    stocks = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 245.75,
            "open_price": 240.00,
            "change_pct": 2.4,
            "volume": 1500000,
            "market_cap": 85000000000,
            "pe_ratio": 28.5,
            "revenue_growth_yoy": 0.18,
            "eps_growth_yoy": 0.22,
            "dividend_yield": 0.5
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "current_price": 112.30,
            "open_price": 110.00,
            "change_pct": 2.1,
            "volume": 800000,
            "market_cap": 22000000000,
            "pe_ratio": 22.1,
            "revenue_growth_yoy": 0.12,
            "eps_growth_yoy": 0.09,
            "dividend_yield": 1.2
        },
        {
            "ticker": "HLTH",
            "company_name": "HealthLink Systems",
            "sector": "Healthcare",
            "current_price": 89.40,
            "open_price": 90.00,
            "change_pct": -0.67,
            "volume": 1200000,
            "market_cap": 45000000000,
            "pe_ratio": 35.2,
            "revenue_growth_yoy": 0.05,
            "eps_growth_yoy": 0.03,
            "dividend_yield": 0.8
        },
        {
            "ticker": "PRXY",
            "company_name": "Proxima Robotics",
            "sector": "Technology",
            "current_price": 68.25,
            "open_price": 67.50,
            "change_pct": 1.11,
            "volume": 300000,
            "market_cap": 12000000000,
            "pe_ratio": 45.0,
            "revenue_growth_yoy": 0.35,
            "eps_growth_yoy": 0.42,
            "dividend_yield": 0.0
        }
    ]
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # --- news.json ---
    news = [
        {
            "news_id": "news_001",
            "headline": "TechVentures announces new AI partnership with GlobalTech",
            "summary": "TECH partners with GlobalTech to develop next-gen AI chips.",
            "category": "partnership",
            "source": "TechCrunch",
            "published_at": "2026-08-15T10:30:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TECH", "GLBL"]
        },
        {
            "news_id": "news_002",
            "headline": "TechVentures earnings beat estimates, stock surges",
            "summary": "TECH reported strong Q2 earnings, exceeding EPS expectations.",
            "category": "earnings",
            "source": "CNBC",
            "published_at": "2026-07-28T14:00:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TECH"]
        },
        {
            "news_id": "news_003",
            "headline": "TechVentures faces regulatory scrutiny over data privacy",
            "summary": "Old news from last year about potential fine.",
            "category": "regulatory",
            "source": "Reuters",
            "published_at": "2025-11-10T08:00:00Z",
            "sentiment": "bearish",
            "impact": "medium",
            "related_tickers": ["TECH"]
        },
        {
            "news_id": "news_004",
            "headline": "Nexa Technologies launches new cloud platform",
            "summary": "NXTC's cloud platform sees early adoption.",
            "category": "product",
            "source": "Bloomberg",
            "published_at": "2026-08-12T09:15:00Z",
            "sentiment": "bullish",
            "impact": "medium",
            "related_tickers": ["NXTC"]
        },
        {
            "news_id": "news_005",
            "headline": "HealthLink Systems acquires MedData",
            "summary": "HLTH expands into health analytics.",
            "category": "sector",
            "source": "WSJ",
            "published_at": "2026-08-10T11:45:00Z",
            "sentiment": "neutral",
            "impact": "medium",
            "related_tickers": ["HLTH"]
        }
    ]
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # --- earnings.json ---
    earnings = [
        {
            "earnings_id": "er_001",
            "ticker": "TECH",
            "quarter": "Q2 2026",
            "report_date": "2026-07-25",
            "revenue_actual": 5200000000,
            "revenue_estimate": 4800000000,
            "revenue_beat": True,
            "revenue_beat_pct": 8.33,
            "eps_actual": 1.35,
            "eps_estimate": 1.20,
            "eps_beat": True,
            "eps_beat_pct": 12.5
        },
        {
            "earnings_id": "er_002",
            "ticker": "TECH",
            "quarter": "Q1 2026",
            "report_date": "2026-04-20",
            "revenue_actual": 4700000000,
            "revenue_estimate": 4600000000,
            "revenue_beat": True,
            "revenue_beat_pct": 2.17,
            "eps_actual": 1.05,
            "eps_estimate": 1.02,
            "eps_beat": True,
            "eps_beat_pct": 2.94
        },
        {
            "earnings_id": "er_003",
            "ticker": "NXTC",
            "quarter": "Q2 2026",
            "report_date": "2026-07-30",
            "revenue_actual": 1900000000,
            "revenue_estimate": 1850000000,
            "revenue_beat": True,
            "revenue_beat_pct": 2.70,
            "eps_actual": 0.88,
            "eps_estimate": 0.82,
            "eps_beat": True,
            "eps_beat_pct": 7.32
        },
        {
            "earnings_id": "er_004",
            "ticker": "HLTH",
            "quarter": "Q2 2026",
            "report_date": "2026-08-01",
            "revenue_actual": 3200000000,
            "revenue_estimate": 3300000000,
            "revenue_beat": False,
            "revenue_beat_pct": -3.03,
            "eps_actual": 1.50,
            "eps_estimate": 1.55,
            "eps_beat": False,
            "eps_beat_pct": -3.23
        }
    ]
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # --- analysts.json (distraction) ---
    analysts = [
        {
            "analyst_id": "a001",
            "name": "Emily Brown",
            "firm": "InvestWise Research",
            "coverage": ["TECH", "NXTC"],
            "rating": "Senior"
        },
        {
            "analyst_id": "a002",
            "name": "Mike Johnson",
            "firm": "Capital Markets",
            "coverage": ["HLTH", "PRXY"],
            "rating": "Analyst"
        },
        {
            "analyst_id": "a003",
            "name": "Sarah Chen",
            "firm": "Global Equities",
            "coverage": ["TECH", "MFST"],
            "rating": "Associate"
        }
    ]
    with open("data/analysts/analysts.json", "w") as f:
        json.dump(analysts, f, indent=2)

if __name__ == "__main__":
    build_env()
