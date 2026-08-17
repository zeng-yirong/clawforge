import os
import json

def build_env():
    os.makedirs("data", exist_ok=True)
    os.makedirs("briefs", exist_ok=True)

    # ---------- stocks.json (authoritative) ----------
    stocks = [
        {"ticker": "CONS", "company_name": "ConsumerFirst Brands", "sector": "Consumer Cyclical", "revenue_growth_yoy": 8.2},
        {"ticker": "ENGY", "company_name": "PowerGrid Energy", "sector": "Utilities", "revenue_growth_yoy": 12.5},
        {"ticker": "FNS", "company_name": "FinServe Corp", "sector": "Financial Services", "revenue_growth_yoy": 3.0},
        {"ticker": "GLBL", "company_name": "Global Retail Inc", "sector": "Consumer Defensive", "revenue_growth_yoy": 4.1},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare", "revenue_growth_yoy": 10.3},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Technology", "revenue_growth_yoy": 15.0},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "revenue_growth_yoy": 18.0},
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "revenue_growth_yoy": 22.5}
    ]
    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ---------- stocks_backup.json (misleading, old data) ----------
    stocks_backup = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "revenue_growth_yoy": 30.0}
    ]
    with open("data/stocks_backup.json", "w") as f:
        json.dump(stocks_backup, f, indent=2)

    # ---------- earnings.json (latest quarterly data) ----------
    earnings = [
        {"earnings_id": "E001", "ticker": "MFST", "quarter": "Q2 2026", "report_date": "2026-08-15",
         "revenue_actual": 500, "revenue_estimate": 490, "revenue_beat": True,
         "revenue_beat_pct": round((500 - 490) / 490 * 100, 2),
         "eps_actual": 1.2, "eps_estimate": 1.1, "eps_beat": True,
         "eps_beat_pct": round((1.2 - 1.1) / 1.1 * 100, 2)},
        {"earnings_id": "E002", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-08-20",
         "revenue_actual": 300, "revenue_estimate": 290, "revenue_beat": True,
         "revenue_beat_pct": round((300 - 290) / 290 * 100, 2),
         "eps_actual": 0.8, "eps_estimate": 0.75, "eps_beat": True,
         "eps_beat_pct": round((0.8 - 0.75) / 0.75 * 100, 2)},
        {"earnings_id": "E003", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-08-25",
         "revenue_actual": 1000, "revenue_estimate": 950, "revenue_beat": True,
         "revenue_beat_pct": round((1000 - 950) / 950 * 100, 2),
         "eps_actual": 2.5, "eps_estimate": 2.4, "eps_beat": True,
         "eps_beat_pct": round((2.5 - 2.4) / 2.4 * 100, 2)}
    ]
    with open("data/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # ---------- earnings_backup.json (old data, misleading) ----------
    earnings_backup = [
        {"earnings_id": "E003_old", "ticker": "TECH", "quarter": "Q1 2026", "report_date": "2026-05-10",
         "revenue_actual": 900, "revenue_estimate": 920, "revenue_beat": False,
         "revenue_beat_pct": round((900 - 920) / 920 * 100, 2),
         "eps_actual": 2.2, "eps_estimate": 2.3, "eps_beat": False,
         "eps_beat_pct": round((2.2 - 2.3) / 2.3 * 100, 2)}
    ]
    with open("data/earnings_backup.json", "w") as f:
        json.dump(earnings_backup, f, indent=2)

    # ---------- news.json ----------
    news = [
        {"news_id": "N001", "headline": "MegaFast Shipping gains on logistics deal",
         "summary": "...", "category": "sector", "source": "WSJ",
         "published_at": "2026-08-26T10:00:00Z", "sentiment": "bullish",
         "related_tickers": ["MFST"]},
        {"news_id": "N002", "headline": "Nexa Technologies reports strong earnings",
         "summary": "...", "category": "earnings", "source": "Bloomberg",
         "published_at": "2026-08-21T08:00:00Z", "sentiment": "bullish",
         "related_tickers": ["NXTC"]},
        {"news_id": "N003", "headline": "TechVentures launches new AI platform",
         "summary": "...", "category": "product", "source": "TechCrunch",
         "published_at": "2026-08-27T09:00:00Z", "sentiment": "bullish",
         "related_tickers": ["TECH"]},
        {"news_id": "N004", "headline": "TechVentures faces regulatory scrutiny",
         "summary": "...", "category": "regulatory", "source": "WSJ",
         "published_at": "2026-08-20T14:00:00Z", "sentiment": "bearish",
         "related_tickers": ["TECH"]}
    ]
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # ---------- distractor CSV ----------
    with open("data/tech_stocks_2025.csv", "w") as f:
        f.write("ticker,revenue_growth\nTECH,25.0\nNXTC,20.0\n")

if __name__ == "__main__":
    build_env()
