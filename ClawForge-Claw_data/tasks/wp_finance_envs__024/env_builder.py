import os
import json

def build_env():
    # Ensure directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- stocks.json ----------
    stocks = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 150.0,
            "open_price": 148.2,
            "change_pct": 1.21,
            "volume": 2_500_000,
            "market_cap": 75_000_000_000,
            "pe_ratio": 28.5,
            "revenue_growth_yoy": 15.3,
            "eps_growth_yoy": 18.7,
            "dividend_yield": 0.0
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "current_price": 85.4,
            "open_price": 84.9,
            "change_pct": 0.59,
            "volume": 1_800_000,
            "market_cap": 42_000_000_000,
            "pe_ratio": 32.1,
            "revenue_growth_yoy": 22.0,
            "eps_growth_yoy": 25.4,
            "dividend_yield": 0.4
        },
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Industrials",
            "current_price": 210.3,
            "open_price": 209.0,
            "change_pct": 0.62,
            "volume": 3_100_000,
            "market_cap": 200_000_000_000,
            "pe_ratio": 22.8,
            "revenue_growth_yoy": 8.1,
            "eps_growth_yoy": 6.5,
            "dividend_yield": 1.2
        },
        {
            "ticker": "HLTH",
            "company_name": "HealthLink Systems",
            "sector": "Healthcare",
            "current_price": 175.0,
            "open_price": 174.2,
            "change_pct": 0.46,
            "volume": 900_000,
            "market_cap": 55_000_000_000,
            "pe_ratio": 35.4,
            "revenue_growth_yoy": 12.5,
            "eps_growth_yoy": 10.2,
            "dividend_yield": 0.8
        }
    ]
    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ---------- earnings.json (with noise and traps) ----------
    earnings = [
        # VALID – TECH beats both Q1 and Q2 2026
        {
            "earnings_id": "e1",
            "ticker": "TECH",
            "quarter": "Q1 2026",
            "report_date": "2026-04-15",
            "revenue_actual": 1200,
            "revenue_estimate": 1150,
            "revenue_beat": True,
            "revenue_beat_pct": 4.3478,
            "eps_actual": 1.50,
            "eps_estimate": 1.42,
            "eps_beat": True,
            "eps_beat_pct": 5.634
        },
        {
            "earnings_id": "e2",
            "ticker": "TECH",
            "quarter": "Q2 2026",
            "report_date": "2026-07-20",
            "revenue_actual": 1350,
            "revenue_estimate": 1280,
            "revenue_beat": True,
            "revenue_beat_pct": 5.4688,
            "eps_actual": 1.80,
            "eps_estimate": 1.69,
            "eps_beat": True,
            "eps_beat_pct": 6.508
        },
        # VALID Q1 for NXTC, but Q2 miss
        {
            "earnings_id": "e3",
            "ticker": "NXTC",
            "quarter": "Q1 2026",
            "report_date": "2026-04-10",
            "revenue_actual": 800,
            "revenue_estimate": 770,
            "revenue_beat": True,
            "revenue_beat_pct": 3.8961,
            "eps_actual": 0.90,
            "eps_estimate": 0.85,
            "eps_beat": True,
            "eps_beat_pct": 5.882
        },
        {
            "earnings_id": "e4",
            "ticker": "NXTC",
            "quarter": "Q2 2026",
            "report_date": "2026-07-15",
            "revenue_actual": 820,
            "revenue_estimate": 850,
            "revenue_beat": False,
            "revenue_beat_pct": -3.5294,
            "eps_actual": 1.00,
            "eps_estimate": 1.02,
            "eps_beat": False,
            "eps_beat_pct": -1.960
        },
        # Distractor – old quarter for TECH (should be excluded)
        {
            "earnings_id": "e5",
            "ticker": "TECH",
            "quarter": "Q1 2025",
            "report_date": "2025-04-12",
            "revenue_actual": 1000,
            "revenue_estimate": 980,
            "revenue_beat": True,
            "revenue_beat_pct": 2.0408,
            "eps_actual": 1.20,
            "eps_estimate": 1.18,
            "eps_beat": True,
            "eps_beat_pct": 1.695
        },
        # Distractor – missing eps_beat_pct field (dirty record)
        {
            "earnings_id": "e6",
            "ticker": "TECH",
            "quarter": "Q2 2025",
            "report_date": "2025-07-18",
            "revenue_actual": 1050,
            "revenue_estimate": 1020,
            "revenue_beat": True,
            "revenue_beat_pct": 2.9412,
            "eps_actual": 1.30,
            "eps_estimate": 1.28,
            "eps_beat": True,
            # no eps_beat_pct
        },
        # Distractor – non-Technology stock MFST (Q1 beat, Q2 beat but sector not Tech)
        {
            "earnings_id": "e7",
            "ticker": "MFST",
            "quarter": "Q1 2026",
            "report_date": "2026-04-05",
            "revenue_actual": 3200,
            "revenue_estimate": 3100,
            "revenue_beat": True,
            "revenue_beat_pct": 3.2258,
            "eps_actual": 2.50,
            "eps_estimate": 2.48,
            "eps_beat": True,
            "eps_beat_pct": 0.806
        },
        {
            "earnings_id": "e8",
            "ticker": "MFST",
            "quarter": "Q2 2026",
            "report_date": "2026-07-10",
            "revenue_actual": 3400,
            "revenue_estimate": 3300,
            "revenue_beat": True,
            "revenue_beat_pct": 3.0303,
            "eps_actual": 2.60,
            "eps_estimate": 2.55,
            "eps_beat": True,
            "eps_beat_pct": 1.961
        }
    ]
    with open("data/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # ---------- noise files (irrelevant) ----------
    news = [
        {"news_id": "n1", "headline": "TechVentures launches new AI platform", "category": "product",
         "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "n2", "headline": "Fed holds rates steady", "category": "macro",
         "sentiment": "neutral", "impact": "medium", "related_tickers": []}
    ]
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # old brief (trap – not in scope)
    briefs = [
        {"brief_id": "b1", "title": "TECH Initiating Coverage", "ticker": "TECH",
         "status": "draft", "summary": "Old summary",
         "investment_rationale": [], "risks": [], "valuation_methodology": "DCF"}
    ]
    with open("data/briefs.json", "w") as f:
        json.dump(briefs, f, indent=2)

if __name__ == "__main__":
    build_env()
