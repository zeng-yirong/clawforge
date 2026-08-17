import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/earnings", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- 主数据文件 ----------
    stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 150.0, "open_price": 148.0, "change_pct": 1.35, "volume": 2000000, "market_cap": 50000000000, "pe_ratio": 25.0, "revenue_growth_yoy": 0.15, "eps_growth_yoy": 0.20, "dividend_yield": 0.01},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Technology", "current_price": 80.0, "open_price": 79.5, "change_pct": 0.63, "volume": 1500000, "market_cap": 30000000000, "pe_ratio": 30.0, "revenue_growth_yoy": 0.10, "eps_growth_yoy": 0.05, "dividend_yield": 0.02},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare", "current_price": 120.0, "open_price": 118.5, "change_pct": 1.27, "volume": 1000000, "market_cap": 20000000000, "pe_ratio": 20.0, "revenue_growth_yoy": 0.12, "eps_growth_yoy": 0.18, "dividend_yield": 0.0},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 90.0, "open_price": 91.0, "change_pct": -1.10, "volume": 800000, "market_cap": 15000000000, "pe_ratio": 35.0, "revenue_growth_yoy": 0.08, "eps_growth_yoy": 0.03, "dividend_yield": 0.005},
        {"ticker": "CONS", "company_name": "ConsumerFirst Brands", "sector": "Consumer Defensive", "current_price": 60.0, "open_price": 59.8, "change_pct": 0.33, "volume": 3000000, "market_cap": 40000000000, "pe_ratio": 18.0, "revenue_growth_yoy": 0.05, "eps_growth_yoy": 0.04, "dividend_yield": 0.03}
    ]
    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    earnings = [
        {"earnings_id": "earn_001", "ticker": "TECH", "quarter": "Q1 2026", "report_date": "2026-04-20", "revenue_actual": 1200, "revenue_estimate": 1100, "revenue_beat": True, "revenue_beat_pct": 9.09, "eps_actual": 2.5, "eps_estimate": 2.2, "eps_beat": True, "eps_beat_pct": 13.64},
        {"earnings_id": "earn_002", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-07-10", "revenue_actual": 1300, "revenue_estimate": 1150, "revenue_beat": True, "revenue_beat_pct": 13.04, "eps_actual": 2.8, "eps_estimate": 2.5, "eps_beat": True, "eps_beat_pct": 12.0},
        {"earnings_id": "earn_003", "ticker": "MFST", "quarter": "Q1 2026", "report_date": "2026-04-18", "revenue_actual": 800, "revenue_estimate": 750, "revenue_beat": True, "revenue_beat_pct": 6.67, "eps_actual": 1.5, "eps_estimate": 1.4, "eps_beat": True, "eps_beat_pct": 7.14},
        {"earnings_id": "earn_004", "ticker": "MFST", "quarter": "Q2 2026", "report_date": "2026-07-09", "revenue_actual": 850, "revenue_estimate": 800, "revenue_beat": True, "revenue_beat_pct": 6.25, "eps_actual": 1.6, "eps_estimate": 1.7, "eps_beat": False, "eps_beat_pct": -5.88},
        {"earnings_id": "earn_005", "ticker": "HLTH", "quarter": "Q1 2026", "report_date": "2026-04-22", "revenue_actual": 600, "revenue_estimate": 550, "revenue_beat": True, "revenue_beat_pct": 9.09, "eps_actual": 1.2, "eps_estimate": 1.0, "eps_beat": True, "eps_beat_pct": 20.0},
        {"earnings_id": "earn_006", "ticker": "HLTH", "quarter": "Q2 2026", "report_date": "2026-07-11", "revenue_actual": 650, "revenue_estimate": 600, "revenue_beat": True, "revenue_beat_pct": 8.33, "eps_actual": 1.3, "eps_estimate": 1.1, "eps_beat": True, "eps_beat_pct": 18.18},
        {"earnings_id": "earn_007", "ticker": "NXTC", "quarter": "Q1 2026", "report_date": "2026-04-19", "revenue_actual": 400, "revenue_estimate": 380, "revenue_beat": True, "revenue_beat_pct": 5.26, "eps_actual": 0.9, "eps_estimate": 0.8, "eps_beat": True, "eps_beat_pct": 12.5},
        {"earnings_id": "earn_008", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-07-08", "revenue_actual": 420, "revenue_estimate": 430, "revenue_beat": False, "revenue_beat_pct": -2.33, "eps_actual": 0.85, "eps_estimate": 0.9, "eps_beat": False, "eps_beat_pct": -5.56},
        {"earnings_id": "earn_009", "ticker": "CONS", "quarter": "Q1 2026", "report_date": "2026-04-21", "revenue_actual": 2000, "revenue_estimate": 1900, "revenue_beat": True, "revenue_beat_pct": 5.26, "eps_actual": 3.0, "eps_estimate": 2.9, "eps_beat": True, "eps_beat_pct": 3.45},
        {"earnings_id": "earn_010", "ticker": "CONS", "quarter": "Q2 2026", "report_date": "2026-07-12", "revenue_actual": 2100, "revenue_estimate": 2000, "revenue_beat": True, "revenue_beat_pct": 5.0, "eps_actual": 3.2, "eps_estimate": 3.1, "eps_beat": True, "eps_beat_pct": 3.23}
    ]
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    news = [
        {"news_id": "news_001", "headline": "TechVentures unveils new AI platform", "summary": "TECH announced a breakthrough AI product.", "category": "product", "source": "TechCrunch", "published_at": "2026-07-14", "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "news_002", "headline": "MegaFast Shipping expands fleet", "summary": "MFST invests in new logistics.", "category": "product", "source": "Reuters", "published_at": "2026-07-01", "sentiment": "bullish", "impact": "medium", "related_tickers": ["MFST"]},
        {"news_id": "news_003", "headline": "HealthLink Systems reports steady growth", "summary": "HLTH maintains outlook.", "category": "earnings", "source": "Bloomberg", "published_at": "2026-07-14", "sentiment": "neutral", "impact": "medium", "related_tickers": ["HLTH"]},
        {"news_id": "news_004", "headline": "Nexa Technologies faces regulatory hurdle", "summary": "NXTC stock dips on news.", "category": "regulatory", "source": "WSJ", "published_at": "2026-07-13", "sentiment": "bearish", "impact": "high", "related_tickers": ["NXTC"]},
        {"news_id": "news_005", "headline": "ConsumerFirst Brands launches new product line", "summary": "CONS enters new market.", "category": "product", "source": "CNBC", "published_at": "2026-07-14", "sentiment": "bullish", "impact": "medium", "related_tickers": ["CONS"]}
    ]
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # ---------- 干扰文件 ----------
    old_earnings = [
        {"earnings_id": "earn_old_001", "ticker": "TECH", "quarter": "Q1 2026", "report_date": "2026-04-20", "revenue_actual": 1200, "revenue_estimate": 1100, "revenue_beat": True, "revenue_beat_pct": 9.09, "eps_actual": 2.5, "eps_estimate": 2.2, "eps_beat": True, "eps_beat_pct": 13.64},
        {"earnings_id": "earn_old_002", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-07-10", "revenue_actual": 1100, "revenue_estimate": 1150, "revenue_beat": False, "revenue_beat_pct": -4.35, "eps_actual": 2.4, "eps_estimate": 2.5, "eps_beat": False, "eps_beat_pct": -4.0}
    ]
    with open("data/earnings/earnings_old.json", "w") as f:
        json.dump(old_earnings, f, indent=2)

    old_stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Healthcare", "current_price": 150.0, "open_price": 148.0, "change_pct": 1.35, "volume": 2000000, "market_cap": 50000000000, "pe_ratio": 25.0, "revenue_growth_yoy": 0.15, "eps_growth_yoy": 0.20, "dividend_yield": 0.01}
    ]
    with open("data/stocks_backup.json", "w") as f:
        json.dump(old_stocks, f, indent=2)

if __name__ == "__main__":
    build_env()
