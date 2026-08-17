import os
import json

def build_env():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # ---- stocks.json ----
    stocks = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 150.0,
            "open_price": 145.0,
            "change_pct": 3.45,
            "volume": 5000000,
            "market_cap": 15000000000,
            "pe_ratio": 25.0,
            "revenue_growth_yoy": 0.15,
            "eps_growth_yoy": 0.08,
            "dividend_yield": 0.0
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Healthcare",
            "current_price": 80.0,
            "open_price": 78.0,
            "change_pct": 2.5,
            "volume": 3000000,
            "market_cap": 8000000000,
            "pe_ratio": 30.0,
            "revenue_growth_yoy": 0.10,
            "eps_growth_yoy": 0.05,
            "dividend_yield": 0.02
        },
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Industrials",
            "current_price": 200.0,
            "open_price": 195.0,
            "change_pct": 2.56,
            "volume": 10000000,
            "market_cap": 50000000000,
            "pe_ratio": 22.5,
            "revenue_growth_yoy": 0.08,
            "eps_growth_yoy": 0.04,
            "dividend_yield": 1.5
        },
        {
            "ticker": "TEC",
            "company_name": "Tech Edge Corp",
            "sector": "Industrials",
            "current_price": 55.0,
            "open_price": 54.0,
            "change_pct": 1.85,
            "volume": 2000000,
            "market_cap": 3000000000,
            "pe_ratio": 35.0,
            "revenue_growth_yoy": 0.05,
            "eps_growth_yoy": 0.02,
            "dividend_yield": 0.8
        }
    ]
    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ---- earnings.json ----
    earnings = [
        {
            "earnings_id": "e001",
            "ticker": "TECH",
            "quarter": "Q2 2026",
            "report_date": "2026-08-15",
            "revenue_actual": 1200000000,
            "revenue_estimate": 1150000000,
            "revenue_beat": True,
            "revenue_beat_pct": 4.35,
            "eps_actual": 2.10,
            "eps_estimate": 2.00,
            "eps_beat": True,
            "eps_beat_pct": 5.0
        },
        {
            "earnings_id": "e002",
            "ticker": "NXTC",
            "quarter": "Q2 2026",
            "report_date": "2026-08-12",
            "revenue_actual": 80000000,
            "revenue_estimate": 85000000,
            "revenue_beat": False,
            "revenue_beat_pct": -5.88,
            "eps_actual": 0.55,
            "eps_estimate": 0.60,
            "eps_beat": False,
            "eps_beat_pct": -8.33
        },
        {
            "earnings_id": "e003",
            "ticker": "MFST",
            "quarter": "Q2 2026",
            "report_date": "2026-08-10",
            "revenue_actual": 5000000000,
            "revenue_estimate": 4800000000,
            "revenue_beat": True,
            "revenue_beat_pct": 4.17,
            "eps_actual": 3.50,
            "eps_estimate": 3.40,
            "eps_beat": True,
            "eps_beat_pct": 2.94
        },
        {
            "earnings_id": "e004",
            "ticker": "TECH",
            "quarter": "Q1 2026",
            "report_date": "2026-05-10",
            "revenue_actual": 1100000000,
            "revenue_estimate": 1120000000,
            "revenue_beat": False,
            "revenue_beat_pct": -1.79,
            "eps_actual": 1.95,
            "eps_estimate": 2.00,
            "eps_beat": False,
            "eps_beat_pct": -2.5
        },
        {
            "earnings_id": "e005",
            "ticker": "TECH",
            "quarter": "Q2 2026",
            "report_date": "2026-08-15",
            "revenue_actual": 1190000000,
            "revenue_estimate": 1150000000,
            "revenue_beat": True,
            "revenue_beat_pct": 3.48,
            "eps_actual": 2.05,
            "eps_estimate": 2.00,
            "eps_beat": False,
            "eps_beat_pct": 2.5
        }
    ]
    with open("data/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # ---- news.json ----
    news = [
        {
            "news_id": "n001",
            "headline": "TechVentures Reports Strong Q2 Earnings Beat",
            "summary": "TechVentures Inc (TECH) posted Q2 earnings that exceeded analyst estimates on both revenue and EPS.",
            "category": "earnings",
            "source": "Bloomberg",
            "published_at": "2026-08-16T08:00:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TECH"]
        },
        {
            "news_id": "n002",
            "headline": "Nexa Tech Faces Regulatory Hurdle",
            "summary": "Nexa Technologies (NXTC) is under investigation for compliance issues.",
            "category": "regulatory",
            "source": "Reuters",
            "published_at": "2026-08-14T10:00:00Z",
            "sentiment": "bearish",
            "impact": "medium",
            "related_tickers": ["NXTC"]
        },
        {
            "news_id": "n003",
            "headline": "TechVentures Launches New AI Platform",
            "summary": "TechVentures Inc (TECH) announced its new AI-powered analytics platform for financial services.",
            "category": "product",
            "source": "TechCrunch",
            "published_at": "2026-07-25T09:00:00Z",
            "sentiment": "neutral",
            "impact": "medium",
            "related_tickers": ["TECH"]
        },
        {
            "news_id": "n004",
            "headline": "MegaFast Shipping Earnings in Line",
            "summary": "MFST reported Q2 results that matched estimates.",
            "category": "earnings",
            "source": "CNBC",
            "published_at": "2026-08-11T06:00:00Z",
            "sentiment": "neutral",
            "impact": "low",
            "related_tickers": ["MFST"]
        }
    ]
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

if __name__ == "__main__":
    build_env()
