import os
import json
from datetime import datetime

def build_env():
    # Create main data directory
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # --- Stocks ---
    stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 145.80, "open_price": 142.10, "change_pct": 2.6, "volume": 3500000, "market_cap": 12000000000, "pe_ratio": 35.4, "revenue_growth_yoy": 0.22, "eps_growth_yoy": 0.18, "dividend_yield": 0.0},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 78.30, "open_price": 77.90, "change_pct": 0.5, "volume": 1200000, "market_cap": 4500000000, "pe_ratio": 28.1, "revenue_growth_yoy": 0.15, "eps_growth_yoy": 0.12, "dividend_yield": 0.5},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials", "current_price": 52.40, "open_price": 52.00, "change_pct": 0.8, "volume": 800000, "market_cap": 8300000000, "pe_ratio": 22.3, "revenue_growth_yoy": 0.05, "eps_growth_yoy": 0.03, "dividend_yield": 1.2},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare", "current_price": 203.10, "open_price": 201.50, "change_pct": 0.8, "volume": 2100000, "market_cap": 28000000000, "pe_ratio": 45.0, "revenue_growth_yoy": 0.11, "eps_growth_yoy": 0.09, "dividend_yield": 0.3}
    ]
    # Add a Technology stock that has beat but lacks bullish news – deliberate distractor
    stocks.append({"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 78.30, "open_price": 77.90, "change_pct": 0.5, "volume": 1200000, "market_cap": 4500000000, "pe_ratio": 28.1, "revenue_growth_yoy": 0.15, "eps_growth_yoy": 0.12, "dividend_yield": 0.5})
    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # --- Earnings ---
    earnings = [
        # TECH – Q1 2026 (miss), Q2 2026 (beat 15%)
        {"earnings_id": "er_tech_q1_2026", "ticker": "TECH", "quarter": "Q1 2026", "report_date": "2026-04-15", "revenue_actual": 2450000000, "revenue_estimate": 2500000000, "revenue_beat": False, "revenue_beat_pct": -0.02, "eps_actual": 1.85, "eps_estimate": 1.92, "eps_beat": False, "eps_beat_pct": -0.0365},
        {"earnings_id": "er_tech_q2_2026", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-07-20", "revenue_actual": 2700000000, "revenue_estimate": 2600000000, "revenue_beat": True, "revenue_beat_pct": 0.0385, "eps_actual": 2.10, "eps_estimate": 1.83, "eps_beat": True, "eps_beat_pct": 0.1475},
        # NXTC – Q2 2026 beat 8% (technology but no bullish high-impact news)
        {"earnings_id": "er_nxtc_q2_2026", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-07-18", "revenue_actual": 980000000, "revenue_estimate": 950000000, "revenue_beat": True, "revenue_beat_pct": 0.0316, "eps_actual": 0.92, "eps_estimate": 0.85, "eps_beat": True, "eps_beat_pct": 0.0824},
        # MFST – Q2 2026 beat but sector is Industrials
        {"earnings_id": "er_mfst_q2_2026", "ticker": "MFST", "quarter": "Q2 2026", "report_date": "2026-07-22", "revenue_actual": 3200000000, "revenue_estimate": 3100000000, "revenue_beat": True, "revenue_beat_pct": 0.0323, "eps_actual": 1.45, "eps_estimate": 1.38, "eps_beat": True, "eps_beat_pct": 0.0507},
        # HLTH – Q1 2026 beat but sector Healthcare, no news
        {"earnings_id": "er_hlth_q1_2026", "ticker": "HLTH", "quarter": "Q1 2026", "report_date": "2026-04-12", "revenue_actual": 5100000000, "revenue_estimate": 5000000000, "revenue_beat": True, "revenue_beat_pct": 0.02, "eps_actual": 3.10, "eps_estimate": 2.95, "eps_beat": True, "eps_beat_pct": 0.0508}
    ]
    # Add an old backup copy with stale data as distractor
    os.makedirs("data/backup", exist_ok=True)
    old_earnings = [
        {"earnings_id": "er_tech_q4_2025", "ticker": "TECH", "quarter": "Q4 2025", "report_date": "2026-01-15", "revenue_actual": 2300000000, "revenue_estimate": 2350000000, "revenue_beat": False, "revenue_beat_pct": -0.0213, "eps_actual": 1.60, "eps_estimate": 1.65, "eps_beat": False, "eps_beat_pct": -0.0303}
    ]
    with open("data/backup/earnings_old.json", "w") as f:
        json.dump(old_earnings, f, indent=2)

    with open("data/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # --- News ---
    news = [
        # TECH – bullish high-impact
        {"news_id": "n_tech_001", "headline": "TECH Launches AI-Driven Platform, Analysts Upgrade", "summary": "TechVentures unveiled a new AI platform expected to boost revenue by 15% in 2027.", "category": "product", "source": "TechCrunch", "published_at": "2026-07-21T09:30:00Z", "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH", "NXTC"]},
        # TECH – neutral low-impact (distractor)
        {"news_id": "n_tech_002", "headline": "TechVentures Announces Office Expansion", "summary": "New campus in Austin to accommodate 2000 employees.", "category": "product", "source": "Bloomberg", "published_at": "2026-07-19T14:00:00Z", "sentiment": "neutral", "impact": "low", "related_tickers": ["TECH"]},
        # NXTC – bullish but impact medium (not high)
        {"news_id": "n_nxtc_001", "headline": "Nexa Technologies Reports Strong Q2 Growth", "summary": "Revenue up 12% YoY, driven by cloud segment.", "category": "earnings", "source": "WSJ", "published_at": "2026-07-19T08:00:00Z", "sentiment": "bullish", "impact": "medium", "related_tickers": ["NXTC"]},
        # MFST – bearish high-impact (not bullish)
        {"news_id": "n_mfst_001", "headline": "MegaFast Shipping Faces Port Strike Delays", "summary": "Labor dispute threatens holiday deliveries.", "category": "sector", "source": "Reuters", "published_at": "2026-07-20T11:00:00Z", "sentiment": "bearish", "impact": "high", "related_tickers": ["MFST"]},
        # HLTH – bullish high-impact but not technology sector
        {"news_id": "n_hlth_001", "headline": "HealthLink Systems Gets FDA Approval for New Drug", "summary": "Breakthrough therapy for diabetes cleared.", "category": "regulatory", "source": "Modern Healthcare", "published_at": "2026-07-18T16:00:00Z", "sentiment": "bullish", "impact": "high", "related_tickers": ["HLTH"]}
    ]
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # Also leave a junk file in data/ to test focus
    with open("data/ignore_this.txt", "w") as f:
        f.write("Do not look at this file.")

if __name__ == "__main__":
    build_env()
