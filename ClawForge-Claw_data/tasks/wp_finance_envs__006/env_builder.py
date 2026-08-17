import os
import json
import random

def build_env():
    # Create directory structure
    os.makedirs("data/stocks", exist_ok=True)
    os.makedirs("data/earnings", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)  # decoy directory

    # --- Stocks ---
    stocks = [
        # Technology sector
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 145.20, "open_price": 143.80, "change_pct": 0.97, "volume": 1234567, "market_cap": 14500000000, "pe_ratio": 28.4, "revenue_growth_yoy": 15.2, "eps_growth_yoy": 12.1, "dividend_yield": 0.0},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 78.50, "open_price": 79.10, "change_pct": -0.76, "volume": 890123, "market_cap": 7800000000, "pe_ratio": 35.1, "revenue_growth_yoy": 22.4, "eps_growth_yoy": 18.7, "dividend_yield": 0.5},
        # Other sectors (decoy)
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare", "current_price": 210.30, "open_price": 208.90, "change_pct": 0.67, "volume": 654321, "market_cap": 21000000000, "pe_ratio": 32.6, "revenue_growth_yoy": 11.8, "eps_growth_yoy": 9.3, "dividend_yield": 1.2},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials", "current_price": 92.10, "open_price": 93.40, "change_pct": -1.39, "volume": 234567, "market_cap": 9200000000, "pe_ratio": 19.8, "revenue_growth_yoy": 5.1, "eps_growth_yoy": 4.5, "dividend_yield": 2.8},
        {"ticker": "CONS", "company_name": "ConsumerFirst Brands", "sector": "Consumer Defensive", "current_price": 55.40, "open_price": 55.00, "change_pct": 0.73, "volume": 345678, "market_cap": 5500000000, "pe_ratio": 22.3, "revenue_growth_yoy": 3.2, "eps_growth_yoy": 2.1, "dividend_yield": 3.5},
        {"ticker": "GLBL", "company_name": "Global Retail Inc", "sector": "Consumer Cyclical", "current_price": 175.80, "open_price": 176.20, "change_pct": -0.23, "volume": 567890, "market_cap": 17500000000, "pe_ratio": 25.7, "revenue_growth_yoy": 8.9, "eps_growth_yoy": 7.4, "dividend_yield": 1.5},
        # Duplicate tickers (decoy – not valid in real data, but can mislead)
        {"ticker": "TECH", "company_name": "TechVentures Inc (DUPLICATE)", "sector": "Technology", "current_price": 999.99, "open_price": 1000.0, "change_pct": 0.0, "volume": 0, "market_cap": 0, "pe_ratio": 0.0, "revenue_growth_yoy": 0.0, "eps_growth_yoy": 0.0, "dividend_yield": 0.0},
    ]
    # Write stocks with duplicate entry – the agent should handle duplicates (first occurrence or dedup)
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # --- Earnings ---
    earnings = [
        # TECH – Q2 2026 (most recent)
        {"earnings_id": "earn_001", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-08-10", "revenue_actual": 1250000, "revenue_estimate": 1050000, "revenue_beat": True, "revenue_beat_pct": 19.05, "eps_actual": 2.45, "eps_estimate": 2.10, "eps_beat": True, "eps_beat_pct": 16.67},
        # TECH – Q1 2026 (older)
        {"earnings_id": "earn_002", "ticker": "TECH", "quarter": "Q1 2026", "report_date": "2026-05-05", "revenue_actual": 980000, "revenue_estimate": 950000, "revenue_beat": True, "revenue_beat_pct": 3.16, "eps_actual": 1.90, "eps_estimate": 1.85, "eps_beat": True, "eps_beat_pct": 2.70},
        # NXTC – Q2 2026 (most recent)
        {"earnings_id": "earn_003", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-08-15", "revenue_actual": 780000, "revenue_estimate": 700000, "revenue_beat": True, "revenue_beat_pct": 11.43, "eps_actual": 1.52, "eps_estimate": 1.40, "eps_beat": True, "eps_beat_pct": 8.57},
        # NXTC – Q1 2026 (older)
        {"earnings_id": "earn_004", "ticker": "NXTC", "quarter": "Q1 2026", "report_date": "2026-04-20", "revenue_actual": 620000, "revenue_estimate": 600000, "revenue_beat": True, "revenue_beat_pct": 3.33, "eps_actual": 1.10, "eps_estimate": 1.08, "eps_beat": True, "eps_beat_pct": 1.85},
        # HLTH (Healthcare) – very high beat but wrong sector
        {"earnings_id": "earn_005", "ticker": "HLTH", "quarter": "Q2 2026", "report_date": "2026-08-12", "revenue_actual": 3500000, "revenue_estimate": 2800000, "revenue_beat": True, "revenue_beat_pct": 25.00, "eps_actual": 4.20, "eps_estimate": 3.80, "eps_beat": True, "eps_beat_pct": 10.53},
        # MFST (Industrials) – moderate beat
        {"earnings_id": "earn_006", "ticker": "MFST", "quarter": "Q2 2026", "report_date": "2026-08-08", "revenue_actual": 2100000, "revenue_estimate": 2000000, "revenue_beat": True, "revenue_beat_pct": 5.00, "eps_actual": 3.10, "eps_estimate": 3.05, "eps_beat": True, "eps_beat_pct": 1.64},
        # CONSUMER (decoy, extra quarters to confuse)
        {"earnings_id": "earn_007", "ticker": "TECH", "quarter": "Q4 2025", "report_date": "2026-02-10", "revenue_actual": 900000, "revenue_estimate": 880000, "revenue_beat": True, "revenue_beat_pct": 2.27, "eps_actual": 1.75, "eps_estimate": 1.70, "eps_beat": True, "eps_beat_pct": 2.94},
    ]
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # --- Decoy news (empty, just to add noise) ---
    news = []
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # Optional: extra empty dir to simulate a messy workspace
    os.makedirs("temp_old", exist_ok=True)

if __name__ == "__main__":
    build_env()
