import os
import json
import random

random.seed(42)

def build_env():
    # data directory
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # stocks
    stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology",
         "current_price": 150.0, "open_price": 148.2, "change_pct": 1.21,
         "volume": 3400000, "market_cap": 45000000000, "pe_ratio": 22.5,
         "revenue_growth_yoy": 0.18, "eps_growth_yoy": 0.25, "dividend_yield": 0.0},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology",
         "current_price": 88.5, "open_price": 87.9, "change_pct": 0.68,
         "volume": 2100000, "market_cap": 28000000000, "pe_ratio": 35.2,
         "revenue_growth_yoy": 0.12, "eps_growth_yoy": 0.08, "dividend_yield": 0.5},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials",
         "current_price": 234.0, "open_price": 235.5, "change_pct": -0.64,
         "volume": 5100000, "market_cap": 82000000000, "pe_ratio": 18.7,
         "revenue_growth_yoy": 0.05, "eps_growth_yoy": 0.03, "dividend_yield": 1.2},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare",
         "current_price": 312.0, "open_price": 308.5, "change_pct": 1.13,
         "volume": 1800000, "market_cap": 94000000000, "pe_ratio": 40.1,
         "revenue_growth_yoy": 0.21, "eps_growth_yoy": 0.30, "dividend_yield": 0.3}
    ]
    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # earnings
    earnings = [
        # TECH latest quarter
        {"earnings_id": "earn_tech_q2_2026", "ticker": "TECH", "quarter": "Q2 2026",
         "report_date": "2026-05-20", "revenue_actual": 1250000000, "revenue_estimate": 1180000000,
         "revenue_beat": True, "revenue_beat_pct": 5.93,
         "eps_actual": 2.45, "eps_estimate": 2.12,
         "eps_beat": True, "eps_beat_pct": 15.7},
        # TECH old quarter (distractor)
        {"earnings_id": "earn_tech_q1_2026", "ticker": "TECH", "quarter": "Q1 2026",
         "report_date": "2026-02-15", "revenue_actual": 1100000000, "revenue_estimate": 1090000000,
         "revenue_beat": True, "revenue_beat_pct": 0.92,
         "eps_actual": 2.10, "eps_estimate": 1.98,
         "eps_beat": True, "eps_beat_pct": 6.06},
        # NXTC earnings
        {"earnings_id": "earn_nxtc_q2_2026", "ticker": "NXTC", "quarter": "Q2 2026",
         "report_date": "2026-05-18", "revenue_actual": 680000000, "revenue_estimate": 650000000,
         "revenue_beat": True, "revenue_beat_pct": 4.62,
         "eps_actual": 1.88, "eps_estimate": 1.75,
         "eps_beat": True, "eps_beat_pct": 7.43},
        {"earnings_id": "earn_nxtc_q1_2026", "ticker": "NXTC", "quarter": "Q1 2026",
         "report_date": "2026-02-10", "revenue_actual": 630000000, "revenue_estimate": 620000000,
         "revenue_beat": True, "revenue_beat_pct": 1.61,
         "eps_actual": 1.65, "eps_estimate": 1.60,
         "eps_beat": True, "eps_beat_pct": 3.12},
        # MFST earnings
        {"earnings_id": "earn_mfst_q2_2026", "ticker": "MFST", "quarter": "Q2 2026",
         "report_date": "2026-05-22", "revenue_actual": 5200000000, "revenue_estimate": 5100000000,
         "revenue_beat": True, "revenue_beat_pct": 1.96,
         "eps_actual": 5.10, "eps_estimate": 4.95,
         "eps_beat": True, "eps_beat_pct": 3.03}
    ]
    with open("data/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # news
    news = [
        {"news_id": "news_001", "headline": "TechVentures unveils next-gen AI platform",
         "summary": "TECH launches new AI platform expected to boost Q3 revenue",
         "category": "product", "source": "TechCrunch", "published_at": "2026-05-22T08:00:00Z",
         "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "news_002", "headline": "TECH beats Q2 estimates by a wide margin",
         "summary": "TechVentures reports strong earnings, shares jump pre-market",
         "category": "earnings", "source": "CNBC", "published_at": "2026-05-21T14:30:00Z",
         "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "news_003", "headline": "TECH faces DOJ antitrust inquiry",
         "summary": "Regulatory probe could impact TECH's expansion plans",
         "category": "regulatory", "source": "WSJ", "published_at": "2026-05-19T10:15:00Z",
         "sentiment": "bearish", "impact": "medium", "related_tickers": ["TECH", "NXTC"]},
        {"news_id": "news_004", "headline": "Market rally boosts tech sector",
         "summary": "Broad market rally lifts tech stocks amid Fed dovish signals",
         "category": "macro", "source": "Bloomberg", "published_at": "2026-05-20T09:00:00Z",
         "sentiment": "bullish", "impact": "medium", "related_tickers": ["NXTC", "MFST"]},
        {"news_id": "news_005", "headline": "HealthLink Systems acquisition approved",
         "summary": "HLTH received regulatory approval for merger, shares rise",
         "category": "regulatory", "source": "Reuters", "published_at": "2026-05-18T16:00:00Z",
         "sentiment": "bullish", "impact": "high", "related_tickers": ["HLTH"]}
    ]
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # create an old version of the target file to test overwriting
    old_content = {"ticker": "TECH", "latest_quarter": "Q1 2026", "eps_beat_pct": 6.06,
                   "bullish_high_impact_news": 0, "pe_ratio": 99.9}
    with open("reports/tech_analysis_old.json", "w") as f:
        json.dump(old_content, f, indent=2)

    # extra dummy file
    os.makedirs("logs", exist_ok=True)
    with open("logs/placeholder.txt", "w") as f:
        f.write("interference")

if __name__ == "__main__":
    build_env()
