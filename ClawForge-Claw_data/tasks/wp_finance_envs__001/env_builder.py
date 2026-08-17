import os
import json
import random

def build_env():
    # 创建数据目录
    os.makedirs("data/stocks", exist_ok=True)
    os.makedirs("data/earnings", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("temp", exist_ok=True)  # 干扰目录
    os.makedirs("backup", exist_ok=True)  # 干扰目录

    # 1. stocks.json
    stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 145.30, "open_price": 142.10, "change_pct": 2.25, "volume": 1234567, "market_cap": 20000000000, "pe_ratio": 25.4, "revenue_growth_yoy": 12.3, "eps_growth_yoy": 8.9, "dividend_yield": 0.5},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 87.50, "open_price": 85.00, "change_pct": 2.94, "volume": 2345678, "market_cap": 5000000000, "pe_ratio": 18.2, "revenue_growth_yoy": 28.4, "eps_growth_yoy": 35.1, "dividend_yield": 0.0},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials", "current_price": 62.80, "open_price": 63.10, "change_pct": -0.48, "volume": 890123, "market_cap": 8000000000, "pe_ratio": 14.6, "revenue_growth_yoy": 5.2, "eps_growth_yoy": 3.8, "dividend_yield": 1.2},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare", "current_price": 210.45, "open_price": 208.00, "change_pct": 1.18, "volume": 456789, "market_cap": 15000000000, "pe_ratio": 32.1, "revenue_growth_yoy": 9.7, "eps_growth_yoy": 11.5, "dividend_yield": 0.8}
    ]
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # 2. earnings.json (包含干扰项：其他股票、过期季度、格式不一致的旧版本)
    earnings = [
        {"earnings_id": "E-NXTC-Q1-2026", "ticker": "NXTC", "quarter": "Q1 2026", "report_date": "2026-04-15", "revenue_actual": 1100, "revenue_estimate": 1080, "revenue_beat": True, "revenue_beat_pct": 1.85, "eps_actual": 2.3, "eps_estimate": 2.1, "eps_beat": True, "eps_beat_pct": 9.52},
        {"earnings_id": "E-NXTC-Q2-2026", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-07-18", "revenue_actual": 1250, "revenue_estimate": 1200, "revenue_beat": True, "revenue_beat_pct": 4.17, "eps_actual": 2.8, "eps_estimate": 2.5, "eps_beat": True, "eps_beat_pct": 12.00},
        {"earnings_id": "E-TECH-Q2-2026", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-07-20", "revenue_actual": 3400, "revenue_estimate": 3300, "revenue_beat": True, "revenue_beat_pct": 3.03, "eps_actual": 4.5, "eps_estimate": 4.3, "eps_beat": True, "eps_beat_pct": 4.65},
        {"earnings_id": "E-MFST-Q2-2026", "ticker": "MFST", "quarter": "Q2 2026", "report_date": "2026-07-22", "revenue_actual": 900, "revenue_estimate": 920, "revenue_beat": False, "revenue_beat_pct": -2.17, "eps_actual": 1.8, "eps_estimate": 1.9, "eps_beat": False, "eps_beat_pct": -5.26},
        # 干扰：NXTC旧季度 (fake)
        {"earnings_id": "E-NXTC-Q2-2025", "ticker": "NXTC", "quarter": "Q2 2025", "report_date": "2025-07-15", "revenue_actual": 950, "revenue_estimate": 970, "revenue_beat": False, "revenue_beat_pct": -2.06, "eps_actual": 1.9, "eps_estimate": 2.0, "eps_beat": False, "eps_beat_pct": -5.00},
        # 干扰：其他股票
        {"earnings_id": "E-HLTH-Q2-2026", "ticker": "HLTH", "quarter": "Q2 2026", "report_date": "2026-07-25", "revenue_actual": 2800, "revenue_estimate": 2750, "revenue_beat": True, "revenue_beat_pct": 1.82, "eps_actual": 6.1, "eps_estimate": 5.9, "eps_beat": True, "eps_beat_pct": 3.39},
        # 干扰：格式错误的历史版本 (键名不同)
        {"earnings_id": "E-NXTC-Q2-2026-LEGACY", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-07-18", "total_revenue": 1250, "avg_estimate_revenue": 1200, "eps": 2.8, "eps_expected": 2.5}  # 键名不一致，应该忽略
    ]
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # 3. news.json (一些相关新闻，仅作环境丰富度)
    news = [
        {"news_id": "news_nxtc_001", "headline": "Nexa Technologies Q2 Revenue Beat Estimates", "summary": "Company reports $1.25B vs expected $1.2B", "category": "earnings", "source": "Reuters", "published_at": "2026-07-18T10:30:00Z", "sentiment": "bullish", "impact": "high", "related_tickers": ["NXTC"]},
        {"news_id": "news_nxtc_002", "headline": "Nexa Launches New AI Platform", "summary": "Next generation AI platform aims to disrupt market", "category": "product", "source": "TechCrunch", "published_at": "2026-07-10T08:00:00Z", "sentiment": "bullish", "impact": "medium", "related_tickers": ["NXTC", "TECH"]},
        {"news_id": "news_tech_001", "headline": "TechVentures Announces Partnership", "summary": "Strategic partnership with major cloud provider", "category": "partnership", "source": "CNBC", "published_at": "2026-07-15T14:00:00Z", "sentiment": "neutral", "impact": "medium", "related_tickers": ["TECH"]}
    ]
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # 4. 干扰文件：临时数据、旧备份等
    with open("temp/old_earnings.csv", "w") as f:
        f.write("ticker,quarter,revenue,eps\nNXTC,Q2 2026,1250,2.8\n")
    with open("backup/stocks_2025.json", "w") as f:
        json.dump([{"ticker": "NXTC", "price": 72.00}], f)

if __name__ == "__main__":
    build_env()
