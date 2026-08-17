import os
import json

def build_env():
    # Ensure directories exist
    os.makedirs("data/stocks", exist_ok=True)
    os.makedirs("data/earnings", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)

    # Write stocks.json
    stocks = {
        "stocks": [
            {
                "ticker": "TECH",
                "company_name": "TechVentures Inc",
                "sector": "Technology",
                "current_price": 150.0,
                "open_price": 148.5,
                "change_pct": 1.01,
                "volume": 2000000,
                "market_cap": 15000000000,
                "pe_ratio": 25.0,
                "revenue_growth_yoy": 0.15,
                "eps_growth_yoy": 0.12,
                "dividend_yield": 0.005
            },
            {
                "ticker": "NXTC",
                "company_name": "Nexa Technologies",
                "sector": "Technology",
                "current_price": 85.0,
                "open_price": 84.0,
                "change_pct": 1.19,
                "volume": 1500000,
                "market_cap": 8500000000,
                "pe_ratio": 18.0,
                "revenue_growth_yoy": 0.10,
                "eps_growth_yoy": 0.08,
                "dividend_yield": 0.01
            },
            {
                "ticker": "MFST",
                "company_name": "MegaFast Shipping",
                "sector": "Industrials",
                "current_price": 72.5,
                "open_price": 73.0,
                "change_pct": -0.68,
                "volume": 800000,
                "market_cap": 7200000000,
                "pe_ratio": 22.0,
                "revenue_growth_yoy": 0.06,
                "eps_growth_yoy": 0.04,
                "dividend_yield": 0.02
            }
        ]
    }
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # Write earnings.json (include TECH Q2 2026 (latest), Q1 2026, and an old Q1 2025 as interference)
    earnings = {
        "earnings": [
            {
                "earnings_id": "e001",
                "ticker": "TECH",
                "quarter": "Q1 2026",
                "report_date": "2026-04-15",
                "revenue_actual": 1000,
                "revenue_estimate": 950,
                "revenue_beat": True,
                "revenue_beat_pct": 5.26,
                "eps_actual": 1.20,
                "eps_estimate": 1.10,
                "eps_beat": True,
                "eps_beat_pct": 9.09
            },
            {
                "earnings_id": "e002",
                "ticker": "TECH",
                "quarter": "Q2 2026",
                "report_date": "2026-07-20",
                "revenue_actual": 1100,
                "revenue_estimate": 1050,
                "revenue_beat": True,
                "revenue_beat_pct": 4.76,
                "eps_actual": 1.35,
                "eps_estimate": 1.25,
                "eps_beat": True,
                "eps_beat_pct": 8.0
            },
            {
                "earnings_id": "e003",
                "ticker": "NXTC",
                "quarter": "Q1 2026",
                "report_date": "2026-04-10",
                "revenue_actual": 500,
                "revenue_estimate": 480,
                "revenue_beat": True,
                "revenue_beat_pct": 4.17,
                "eps_actual": 0.80,
                "eps_estimate": 0.75,
                "eps_beat": True,
                "eps_beat_pct": 6.67
            },
            {
                "earnings_id": "e004",
                "ticker": "TECH",
                "quarter": "Q1 2025",
                "report_date": "2025-04-15",
                "revenue_actual": 900,
                "revenue_estimate": 870,
                "revenue_beat": True,
                "revenue_beat_pct": 3.45,
                "eps_actual": 1.00,
                "eps_estimate": 0.95,
                "eps_beat": True,
                "eps_beat_pct": 5.26
            }
        ]
    }
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # Write news.json (two TECH-related, one other)
    news = {
        "news": [
            {
                "news_id": "n001",
                "headline": "TechVentures launches new product",
                "summary": "The company unveiled its next-gen AI platform.",
                "category": "product",
                "source": "TechCrunch",
                "published_at": "2026-07-23T10:00:00Z",
                "sentiment": "bullish",
                "impact": "medium",
                "related_tickers": ["TECH"]
            },
            {
                "news_id": "n002",
                "headline": "TechVentures Q2 earnings beat expectations",
                "summary": "Strong revenue growth driven by cloud segment.",
                "category": "earnings",
                "source": "WSJ",
                "published_at": "2026-07-21T14:00:00Z",
                "sentiment": "bullish",
                "impact": "high",
                "related_tickers": ["TECH", "NXTC"]
            },
            {
                "news_id": "n003",
                "headline": "NXTC announces new partnership",
                "summary": "Collaboration with major logistics provider.",
                "category": "partnership",
                "source": "Reuters",
                "published_at": "2026-07-22T08:00:00Z",
                "sentiment": "bullish",
                "impact": "medium",
                "related_tickers": ["NXTC"]
            }
        ]
    }
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

if __name__ == "__main__":
    build_env()
