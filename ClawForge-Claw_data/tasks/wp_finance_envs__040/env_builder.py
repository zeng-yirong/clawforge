import json
import os

def build_env():
    # ---- stocks ----
    stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 245.0, "open_price": 240.0, "change_pct": 2.08, "volume": 1200000, "market_cap": 49000000000, "pe_ratio": 35.2, "revenue_growth_yoy": 0.18, "eps_growth_yoy": 0.22, "dividend_yield": 0.0},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 87.5, "open_price": 85.0, "change_pct": 2.94, "volume": 800000, "market_cap": 17500000000, "pe_ratio": 28.4, "revenue_growth_yoy": 0.25, "eps_growth_yoy": 0.30, "dividend_yield": 0.5},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials", "current_price": 152.0, "open_price": 150.0, "change_pct": 1.33, "volume": 2000000, "market_cap": 76000000000, "pe_ratio": 20.1, "revenue_growth_yoy": 0.08, "eps_growth_yoy": 0.05, "dividend_yield": 1.2},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare", "current_price": 310.0, "open_price": 305.0, "change_pct": 1.64, "volume": 900000, "market_cap": 62000000000, "pe_ratio": 42.0, "revenue_growth_yoy": 0.12, "eps_growth_yoy": 0.15, "dividend_yield": 0.8},
        {"ticker": "CONS", "company_name": "ConsumerFirst Brands", "sector": "Consumer Cyclical", "current_price": 78.0, "open_price": 79.0, "change_pct": -1.27, "volume": 1500000, "market_cap": 39000000000, "pe_ratio": 18.5, "revenue_growth_yoy": 0.03, "eps_growth_yoy": 0.01, "dividend_yield": 2.5}
    ]
    os.makedirs("data/stocks", exist_ok=True)
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ---- earnings ----
    earnings = [
        {"earnings_id": "E_TECH_Q2_2026", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-08-10", "revenue_actual": 5000, "revenue_estimate": 4600, "revenue_beat": True, "revenue_beat_pct": 8.5, "eps_actual": 2.45, "eps_estimate": 2.20, "eps_beat": True, "eps_beat_pct": 11.36},
        {"earnings_id": "E_NXTC_Q2_2026", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-08-12", "revenue_actual": 3200, "revenue_estimate": 2800, "revenue_beat": True, "revenue_beat_pct": 12.0, "eps_actual": 1.80, "eps_estimate": 1.60, "eps_beat": True, "eps_beat_pct": 12.5},
        {"earnings_id": "E_TECH_Q1_2026", "ticker": "TECH", "quarter": "Q1 2026", "report_date": "2026-05-05", "revenue_actual": 4800, "revenue_estimate": 4500, "revenue_beat": True, "revenue_beat_pct": 6.67, "eps_actual": 2.30, "eps_estimate": 2.15, "eps_beat": True, "eps_beat_pct": 6.98},
        {"earnings_id": "E_MFST_Q2_2026", "ticker": "MFST", "quarter": "Q2 2026", "report_date": "2026-08-08", "revenue_actual": 12000, "revenue_estimate": 11500, "revenue_beat": True, "revenue_beat_pct": 4.35, "eps_actual": 3.10, "eps_estimate": 2.95, "eps_beat": True, "eps_beat_pct": 5.08}
    ]
    os.makedirs("data/earnings", exist_ok=True)
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # ---- news ----
    news = [
        {"news_id": "news_001", "headline": "TECH launches revolutionary AI chip", "summary": "New chip expected to double data center performance.", "category": "product", "source": "TechCrunch", "published_at": "2026-09-01T08:30:00Z", "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "news_002", "headline": "NXTC partners with leading cloud provider", "summary": "Strategic partnership to expand edge computing reach.", "category": "partnership", "source": "Reuters", "published_at": "2026-08-28T14:00:00Z", "sentiment": "bullish", "impact": "medium", "related_tickers": ["NXTC"]},
        {"news_id": "news_003", "headline": "TECH faces regulatory probe in Europe", "summary": "Antitrust investigation announced.", "category": "regulatory", "source": "Reuters", "published_at": "2026-08-25T10:00:00Z", "sentiment": "bearish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "news_004", "headline": "MFST beats Q2 expectations", "summary": "Strong delivery volume drives revenue.", "category": "earnings", "source": "Bloomberg", "published_at": "2026-08-09T12:00:00Z", "sentiment": "bullish", "impact": "medium", "related_tickers": ["MFST"]}
    ]
    os.makedirs("data/news", exist_ok=True)
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # ---- additional noise files ----
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/access.log", "w") as f:
        f.write("2026-09-01 00:00:01 GET /stocks\n2026-09-01 00:01:23 GET /earnings\n")
    os.makedirs("temp", exist_ok=True)
    with open("temp/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
