import os
import json

def build_env():
    os.makedirs("data", exist_ok=True)

    stocks = [
        # Technology sector
        {
            "ticker": "TEC1",
            "company_name": "TechOne Inc.",
            "sector": "Technology",
            "current_price": 145.20,
            "open_price": 143.80,
            "change_pct": 0.97,
            "volume": 2500000,
            "market_cap": 12000000000,
            "pe_ratio": 15.0,
            "revenue_growth_yoy": 18.0,
            "eps_growth_yoy": 22.5,
            "dividend_yield": 0.5
        },
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 287.50,
            "open_price": 285.00,
            "change_pct": 0.88,
            "volume": 1800000,
            "market_cap": 45000000000,
            "pe_ratio": 22.5,
            "revenue_growth_yoy": 12.3,
            "eps_growth_yoy": 10.1,
            "dividend_yield": 0.3
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "current_price": 67.80,
            "open_price": 68.20,
            "change_pct": -0.59,
            "volume": 3200000,
            "market_cap": 8900000000,
            "pe_ratio": 28.0,
            "revenue_growth_yoy": 9.5,
            "eps_growth_yoy": 5.2,
            "dividend_yield": 0.0
        },
        {
            "ticker": "TEC2",
            "company_name": "TechDynamics Corp.",
            "sector": "Technology",
            "current_price": 210.00,
            "open_price": 212.50,
            "change_pct": -1.18,
            "volume": 1100000,
            "market_cap": 22000000000,
            "pe_ratio": 40.0,
            "revenue_growth_yoy": 25.0,
            "eps_growth_yoy": 18.0,
            "dividend_yield": 0.2
        },
        # Other sectors (distractors)
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Industrials",
            "current_price": 98.40,
            "open_price": 97.90,
            "change_pct": 0.51,
            "volume": 5000000,
            "market_cap": 75000000000,
            "pe_ratio": 20.0,
            "revenue_growth_yoy": 5.0,
            "eps_growth_yoy": 3.5,
            "dividend_yield": 1.2
        },
        {
            "ticker": "HLTH",
            "company_name": "HealthLink Systems",
            "sector": "Healthcare",
            "current_price": 55.30,
            "open_price": 55.00,
            "change_pct": 0.55,
            "volume": 2200000,
            "market_cap": 8000000000,
            "pe_ratio": 18.0,
            "revenue_growth_yoy": 12.0,
            "eps_growth_yoy": 9.0,
            "dividend_yield": 0.8
        },
        {
            "ticker": "CONS",
            "company_name": "ConsumerFirst Brands",
            "sector": "Consumer Defensive",
            "current_price": 34.20,
            "open_price": 34.00,
            "change_pct": 0.59,
            "volume": 8000000,
            "market_cap": 15000000000,
            "pe_ratio": 12.0,
            "revenue_growth_yoy": 8.0,
            "eps_growth_yoy": 4.5,
            "dividend_yield": 2.5
        },
        {
            "ticker": "ENGY",
            "company_name": "PowerGrid Energy",
            "sector": "Utilities",
            "current_price": 72.10,
            "open_price": 72.50,
            "change_pct": -0.55,
            "volume": 1500000,
            "market_cap": 28000000000,
            "pe_ratio": 35.0,
            "revenue_growth_yoy": 10.0,
            "eps_growth_yoy": 7.0,
            "dividend_yield": 3.0
        },
        {
            "ticker": "FNS",
            "company_name": "FinServe Corp",
            "sector": "Financial Services",
            "current_price": 42.80,
            "open_price": 43.00,
            "change_pct": -0.47,
            "volume": 3000000,
            "market_cap": 50000000000,
            "pe_ratio": 15.0,
            "revenue_growth_yoy": 6.0,
            "eps_growth_yoy": 5.0,
            "dividend_yield": 1.5
        },
        {
            "ticker": "GLBL",
            "company_name": "Global Retail Inc",
            "sector": "Consumer Cyclical",
            "current_price": 89.60,
            "open_price": 90.00,
            "change_pct": -0.44,
            "volume": 4000000,
            "market_cap": 32000000000,
            "pe_ratio": 50.0,
            "revenue_growth_yoy": 2.0,
            "eps_growth_yoy": 1.0,
            "dividend_yield": 0.5
        }
    ]

    news = [
        {
            "news_id": "news_001",
            "headline": "TEC1 Announces Breakthrough Chip",
            "summary": "TechOne unveils next-gen AI processor, expects 40% performance boost.",
            "category": "product",
            "source": "TechCrunch",
            "published_at": "2025-04-10T08:00:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TEC1"]
        },
        {
            "news_id": "news_002",
            "headline": "TECH Partners with Global Leader",
            "summary": "TechVentures signs strategic partnership with a top cloud provider.",
            "category": "partnership",
            "source": "Bloomberg",
            "published_at": "2025-04-09T14:30:00Z",
            "sentiment": "bullish",
            "impact": "medium",
            "related_tickers": ["TECH"]
        },
        {
            "news_id": "news_003",
            "headline": "Nexa Technologies Reports Mixed Q1",
            "summary": "Revenue meets expectations but growth slows.",
            "category": "earnings",
            "source": "Reuters",
            "published_at": "2025-04-08T12:00:00Z",
            "sentiment": "neutral",
            "impact": "medium",
            "related_tickers": ["NXTC"]
        },
        {
            "news_id": "news_004",
            "headline": "TechDynamics Faces Regulatory Hurdle",
            "summary": "New compliance requirements may impact margins.",
            "category": "regulatory",
            "source": "WSJ",
            "published_at": "2025-04-07T09:45:00Z",
            "sentiment": "bearish",
            "impact": "high",
            "related_tickers": ["TEC2"]
        },
        {
            "news_id": "news_005",
            "headline": "MegaFast Shipping Expands Fleet",
            "summary": "New routes expected to boost revenue.",
            "category": "product",
            "source": "CNBC",
            "published_at": "2025-04-10T06:00:00Z",
            "sentiment": "bullish",
            "impact": "medium",
            "related_tickers": ["MFST"]
        },
        {
            "news_id": "news_006",
            "headline": "HealthLink Launches Remote Monitoring",
            "summary": "New platform targets chronic patients.",
            "category": "product",
            "source": "Modern Healthcare",
            "published_at": "2025-04-09T11:00:00Z",
            "sentiment": "bullish",
            "impact": "medium",
            "related_tickers": ["HLTH"]
        },
        {
            "news_id": "news_007",
            "headline": "ConsumerFirst Brands Recall",
            "summary": "Voluntary recall of snack products due to contamination.",
            "category": "regulatory",
            "source": "Bloomberg",
            "published_at": "2025-04-08T16:00:00Z",
            "sentiment": "bearish",
            "impact": "high",
            "related_tickers": ["CONS"]
        },
        {
            "news_id": "news_008",
            "headline": "PowerGrid Energy Rate Hike Approved",
            "summary": "Regulators approve 5% rate increase.",
            "category": "regulatory",
            "source": "Reuters",
            "published_at": "2025-04-07T13:00:00Z",
            "sentiment": "neutral",
            "impact": "medium",
            "related_tickers": ["ENGY"]
        },
        {
            "news_id": "news_009",
            "headline": "FinServe Corp AI Platform Launches",
            "summary": "New AI trading assistant gains early traction.",
            "category": "product",
            "source": "TechCrunch",
            "published_at": "2025-04-10T07:30:00Z",
            "sentiment": "bullish",
            "impact": "medium",
            "related_tickers": ["FNS"]
        },
        {
            "news_id": "news_010",
            "headline": "Global Retail Misses Earnings",
            "summary": "Q1 profits down 15% due to supply chain issues.",
            "category": "earnings",
            "source": "CNBC",
            "published_at": "2025-04-09T15:00:00Z",
            "sentiment": "bearish",
            "impact": "high",
            "related_tickers": ["GLBL"]
        }
    ]

    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

if __name__ == "__main__":
    build_env()
