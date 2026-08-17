import json
import os

def build_env():
    # 确保 data 目录存在
    os.makedirs("data", exist_ok=True)

    # ---------- stocks.json ----------
    stocks = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 45.6,
            "open_price": 44.8,
            "change_pct": 1.79,
            "volume": 1230000,
            "market_cap": 3200000000,
            "pe_ratio": 18.2,
            "revenue_growth_yoy": 17.5,
            "eps_growth_yoy": 12.3,
            "dividend_yield": 0.0
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "current_price": 28.4,
            "open_price": 27.9,
            "change_pct": 1.79,
            "volume": 890000,
            "market_cap": 1100000000,
            "pe_ratio": 14.7,
            "revenue_growth_yoy": 22.1,
            "eps_growth_yoy": 18.5,
            "dividend_yield": 0.5
        },
        # 干扰项：Technology 行业但 PE太高
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Technology",
            "current_price": 78.2,
            "open_price": 77.5,
            "change_pct": 0.9,
            "volume": 4500000,
            "market_cap": 18000000000,
            "pe_ratio": 32.1,
            "revenue_growth_yoy": 8.2,
            "eps_growth_yoy": 5.1,
            "dividend_yield": 1.2
        },
        # 干扰项：Technology 行业但营收增长不足
        {
            "ticker": "FNS",
            "company_name": "FinServe Corp",
            "sector": "Technology",
            "current_price": 22.0,
            "open_price": 21.8,
            "change_pct": 0.92,
            "volume": 2100000,
            "market_cap": 950000000,
            "pe_ratio": 16.3,
            "revenue_growth_yoy": 9.8,
            "eps_growth_yoy": 7.2,
            "dividend_yield": 0.3
        },
        # 干扰项：非 Technology 行业，但其他条件可能满足
        {
            "ticker": "HLTH",
            "company_name": "HealthLink Systems",
            "sector": "Healthcare",
            "current_price": 33.1,
            "open_price": 32.5,
            "change_pct": 1.85,
            "volume": 1800000,
            "market_cap": 4100000000,
            "pe_ratio": 17.5,
            "revenue_growth_yoy": 19.2,
            "eps_growth_yoy": 14.0,
            "dividend_yield": 0.8
        },
        {
            "ticker": "CONS",
            "company_name": "ConsumerFirst Brands",
            "sector": "Consumer Defensive",
            "current_price": 55.3,
            "open_price": 54.9,
            "change_pct": 0.73,
            "volume": 980000,
            "market_cap": 6700000000,
            "pe_ratio": 19.8,
            "revenue_growth_yoy": 16.3,
            "eps_growth_yoy": 11.2,
            "dividend_yield": 1.5
        },
        # 完全无关的
        {
            "ticker": "ENGY",
            "company_name": "PowerGrid Energy",
            "sector": "Utilities",
            "current_price": 62.0,
            "open_price": 61.2,
            "change_pct": 1.31,
            "volume": 3500000,
            "market_cap": 22000000000,
            "pe_ratio": 22.5,
            "revenue_growth_yoy": 6.1,
            "eps_growth_yoy": 4.8,
            "dividend_yield": 3.2
        }
    ]

    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ---------- news.json ----------
    news = [
        {
            "news_id": "n001",
            "headline": "TechVentures announces breakthrough AI chip",
            "summary": "New chip promises 40% performance gain.",
            "category": "product",
            "source": "TechCrunch",
            "published_at": "2025-02-10T08:30:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TECH"]
        },
        {
            "news_id": "n002",
            "headline": "Nexa Technologies wins major defense contract",
            "summary": "Contract valued at $200M over 5 years.",
            "category": "partnership",
            "source": "Reuters",
            "published_at": "2025-02-11T14:15:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["NXTC"]
        },
        # 干扰：TECH 的负面新闻（sentiment 不是 bullish）
        {
            "news_id": "n003",
            "headline": "TechVentures faces class-action lawsuit",
            "summary": "Shareholders allege misleading revenue projections.",
            "category": "regulatory",
            "source": "WSJ",
            "published_at": "2025-02-09T10:00:00Z",
            "sentiment": "bearish",
            "impact": "high",
            "related_tickers": ["TECH"]
        },
        # 干扰：NXTC 的新闻但 impact 为 low
        {
            "news_id": "n004",
            "headline": "Nexa Technologies updates website",
            "summary": "Cosmetic changes only.",
            "category": "product",
            "source": "CNBC",
            "published_at": "2025-02-08T09:45:00Z",
            "sentiment": "bullish",
            "impact": "low",
            "related_tickers": ["NXTC"]
        },
        # 干扰：其他股票正面新闻，但行业不对
        {
            "news_id": "n005",
            "headline": "HealthLink Systems receives FDA approval",
            "summary": "New device cleared for market.",
            "category": "regulatory",
            "source": "Modern Healthcare",
            "published_at": "2025-02-12T11:00:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["HLTH"]
        },
        # 干扰：无关新闻
        {
            "news_id": "n006",
            "headline": "Federal Reserve holds rates steady",
            "summary": "Market reacts positively.",
            "category": "macro",
            "source": "Bloomberg",
            "published_at": "2025-02-07T16:30:00Z",
            "sentiment": "neutral",
            "impact": "medium",
            "related_tickers": []
        }
    ]

    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

    print("Environment built: data/stocks.json and data/news.json with competitive distractors.")

if __name__ == "__main__":
    build_env()
