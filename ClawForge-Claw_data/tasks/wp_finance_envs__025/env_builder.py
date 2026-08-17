import os
import json
import shutil
from datetime import datetime, timedelta

def build_env():
    # Ensure cwd is already 
    base = "."

    # Clean slate
    for d in ["data", "ops", "outputs"]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    # ──── data/accounts.json ────
    accounts = [
        {
            "account_id": "acc_001",
            "display_name": "Sarah Chen",
            "department": "Technology",
            "email": "sarah.chen@investwise.example.com",
            "permissions": ["read", "write", "admin"],
            "default_universe": ["TECH", "NXTC", "MFST"],
            "voice": ["brief"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ──── data/analysts/analysts.json ────
    analysts = [
        {"analyst_id": "an_001", "name": "Sarah Chen", "firm": "InvestWise Research",
         "coverage": ["TECH"], "rating": "Senior"},
        {"analyst_id": "an_002", "name": "Mike Johnson", "firm": "Global Equities",
         "coverage": ["NXTC", "MFST"], "rating": "Analyst"}
    ]
    os.makedirs("data/analysts", exist_ok=True)
    with open("data/analysts/analysts.json", "w") as f:
        json.dump(analysts, f, indent=2)

    # ──── data/contacts.json ────
    contacts = [
        {"contact_id": "c_001", "name": "Sarah Chen", "email": "sarah.chen@investwise.example.com",
         "role": "Senior Analyst", "team": "Technology"},
        {"contact_id": "c_002", "name": "Lisa Wang", "email": "lisa.wang@techventures.example.com",
         "role": "IR Director", "team": "Investor Relations"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ──── data/stocks/stocks.json ────
    # TECH is the only Technology stock; we give it specific values
    stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology",
         "current_price": 245.30, "open_price": 240.10, "change_pct": 2.17,
         "volume": 3200000, "market_cap": 49060000000, "pe_ratio": 28.45,
         "revenue_growth_yoy": 15.2, "eps_growth_yoy": 22.4, "dividend_yield": 0.65},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology",
         "current_price": 87.50, "open_price": 85.90, "change_pct": 1.86,
         "volume": 1500000, "market_cap": 17500000000, "pe_ratio": 35.2,
         "revenue_growth_yoy": 8.1, "eps_growth_yoy": 12.3, "dividend_yield": 0.0},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials",
         "current_price": 128.00, "open_price": 127.50, "change_pct": 0.39,
         "volume": 890000, "market_cap": 25600000000, "pe_ratio": 18.7,
         "revenue_growth_yoy": 4.5, "eps_growth_yoy": 3.2, "dividend_yield": 2.1}
    ]
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ──── data/earnings/earnings.json ────
    # TECH has two earnings: Q1 2026 (old) and Q2 2026 (new). Q2 beat revenue by 8.5%.
    # Also a duplicate (fake) entry for Q2 with wrong numbers to mislead.
    earnings = [
        # TECH Q1 2026 (old date)
        {"earnings_id": "ern_001", "ticker": "TECH", "quarter": "Q1 2026",
         "report_date": "2026-04-15", "revenue_actual": 820000000, "revenue_estimate": 800000000,
         "revenue_beat": True, "revenue_beat_pct": 2.5,
         "eps_actual": 1.82, "eps_estimate": 1.75, "eps_beat": True, "eps_beat_pct": 4.0},
        # TECH Q2 2026 (new, correct)
        {"earnings_id": "ern_002", "ticker": "TECH", "quarter": "Q2 2026",
         "report_date": "2026-07-20", "revenue_actual": 890000000, "revenue_estimate": 820000000,
         "revenue_beat": True, "revenue_beat_pct": 8.5,
         "eps_actual": 2.10, "eps_estimate": 1.95, "eps_beat": True, "eps_beat_pct": 7.7},
        # TECH Q2 2026 duplicate with wrong numbers (trap)
        {"earnings_id": "ern_003", "ticker": "TECH", "quarter": "Q2 2026",
         "report_date": "2026-07-20", "revenue_actual": 880000000, "revenue_estimate": 830000000,
         "revenue_beat": True, "revenue_beat_pct": 6.0,
         "eps_actual": 2.05, "eps_estimate": 1.98, "eps_beat": True, "eps_beat_pct": 3.5},
        # NXTC earnings (distraction)
        {"earnings_id": "ern_004", "ticker": "NXTC", "quarter": "Q2 2026",
         "report_date": "2026-07-18", "revenue_actual": 315000000, "revenue_estimate": 310000000,
         "revenue_beat": True, "revenue_beat_pct": 1.6,
         "eps_actual": 0.95, "eps_estimate": 0.92, "eps_beat": True, "eps_beat_pct": 3.3}
    ]
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # ──── data/news/news.json ────
    news = [
        {"news_id": "n_001", "headline": "TechVentures Q2 beats expectations",
         "summary": "Revenue surged on cloud deals", "category": "earnings",
         "source": "Bloomberg", "published_at": "2026-07-21T10:30:00Z",
         "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "n_002", "headline": "Analyst raises price target on TECH",
         "summary": "New product pipeline promising", "category": "product",
         "source": "CNBC", "published_at": "2026-07-22T08:15:00Z",
         "sentiment": "bullish", "impact": "medium", "related_tickers": ["TECH"]},
        {"news_id": "n_003", "headline": "Macro headwinds hit tech sector",
         "summary": "Interest rate fears weigh", "category": "macro",
         "source": "WSJ", "published_at": "2026-07-19T14:00:00Z",
         "sentiment": "bearish", "impact": "high", "related_tickers": ["TECH", "NXTC"]},
        {"news_id": "n_004", "headline": "NXTC partnership with health giant",
         "summary": "Expansion into AI diagnostics", "category": "partnership",
         "source": "TechCrunch", "published_at": "2026-07-20T12:00:00Z",
         "sentiment": "bullish", "impact": "medium", "related_tickers": ["NXTC"]}
    ]
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # ──── data/briefs/briefs.json ────
    briefs = [
        {"brief_id": "brf_001", "title": "TECH - Q2 Earnings Preview",
         "ticker": "TECH", "created_by": "Sarah Chen",
         "created_at": "2026-07-10T09:00:00Z",
         "updated_at": "2026-07-15T11:30:00Z",
         "brief_type": "earnings_preview", "status": "draft",
         "summary": "Expect modest beat due to cloud growth.",
         "investment_rationale": ["Cloud expansion", "Cost controls"],
         "risks": ["Macro slowdown", "Competition"],
         "valuation_methodology": "DCF with 2027 projections"}
    ]
    with open("data/briefs/briefs.json", "w") as f:
        json.dump(briefs, f, indent=2)

    # ──── ops/old_brief.json (stale draft with wrong numbers) ────
    old_brief = {
        "ticker": "TECH",
        "company_name": "TechVentures Inc",
        "sector": "Technology",
        "current_price": 239.00,
        "pe_ratio": 29.1,
        "revenue_growth_yoy": 14.0,
        "eps_growth_yoy": 20.5,
        "dividend_yield": 0.62,
        "latest_earnings": {
            "quarter": "Q1 2026",
            "revenue_actual": 820000000,
            "eps_actual": 1.82,
            "revenue_beat_pct": 2.5,
            "eps_beat_pct": 4.0
        },
        "bullish_news_count": 1,
        "combined_score": 0.1234   # bogus
    }
    with open("ops/old_brief.json", "w") as f:
        json.dump(old_brief, f, indent=2)

    # ──── ops/earnings_summary.csv (trap: malformed) ────
    csv_content = "ticker,quarter,revenue\nTECH,Q2 2026,890000000\nTECH,Q1 2026,820000000\n"
    with open("ops/earnings_summary.csv", "w") as f:
        f.write(csv_content)

    # ──── ops/notes.txt (irrelevant) ────
    with open("ops/notes.txt", "w") as f:
        f.write("Reminder: check forward P/E after print.\n")

    # ──── Create outputs directory (empty initially) ────
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

if __name__ == "__main__":
    build_env()
