import os
import json

def build_env():
    os.makedirs("data/stocks/stocks_archive", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/earnings", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 最新版股票数据
    stocks_current = {
        "last_updated": "2026-03-01T12:00:00Z",
        "stocks": [
            {"ticker": "CONS", "company_name": "ConsumerFirst Brands", "sector": "Consumer Defensive", "current_price": 45.2, "pe_ratio": 18.5, "revenue_growth_yoy": 3.2},
            {"ticker": "ENGY", "company_name": "PowerGrid Energy", "sector": "Utilities", "current_price": 67.8, "pe_ratio": 22.0, "revenue_growth_yoy": 5.1},
            {"ticker": "FNS", "company_name": "FinServe Corp", "sector": "Financial Services", "current_price": 120.0, "pe_ratio": 15.0, "revenue_growth_yoy": 8.7},
            {"ticker": "GLBL", "company_name": "Global Retail Inc", "sector": "Consumer Cyclical", "current_price": 88.5, "pe_ratio": 25.0, "revenue_growth_yoy": -1.2},
            {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare", "current_price": 210.0, "pe_ratio": 35.0, "revenue_growth_yoy": 12.0},
            {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials", "current_price": 55.0, "pe_ratio": 20.0, "revenue_growth_yoy": 6.5},
            {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 80.0, "pe_ratio": 20.0, "revenue_growth_yoy": 22.0},
            {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 150.0, "pe_ratio": 25.0, "revenue_growth_yoy": 15.5}
        ]
    }
    with open("data/stocks/stocks_current.json", "w") as f:
        json.dump(stocks_current, f, indent=2)

    # 旧版数据（2025年11月）
    stocks_old = {
        "last_updated": "2025-11-15T08:00:00Z",
        "stocks": [
            {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 140.0, "pe_ratio": 28.0, "revenue_growth_yoy": 12.0},
            {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials", "current_price": 52.0, "pe_ratio": 19.0, "revenue_growth_yoy": 5.0},
        ]
    }
    with open("data/stocks/stocks_old_2025.json", "w") as f:
        json.dump(stocks_old, f, indent=2)

    # 存档目录中的旧版（2026年2月）
    stocks_archive = {
        "last_updated": "2026-02-10T10:00:00Z",
        "stocks": [
            {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 78.0, "pe_ratio": 22.0, "revenue_growth_yoy": 18.0},
            {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 145.0, "pe_ratio": 24.0, "revenue_growth_yoy": 14.0},
        ]
    }
    with open("data/stocks/stocks_archive/v2.json", "w") as f:
        json.dump(stocks_archive, f, indent=2)

    # 干扰数据
    with open("logs/system.log", "w") as f:
        f.write("2026-03-01 10:00:00 INFO Data sync completed\n")
    earnings = {
        "earnings": [
            {"ticker": "NXTC", "quarter": "Q1 2026", "revenue_actual": 500, "eps_actual": 1.2}
        ]
    }
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)
    news = {"news": []}
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)
    with open("data/stocks/README.txt", "w") as f:
        f.write("This directory contains stock data files.\n")

if __name__ == "__main__":
    build_env()
