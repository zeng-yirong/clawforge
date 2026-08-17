import os
import json

def build_env():
    # ---------- stocks ----------
    stocks = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 245.00,
            "open_price": 243.50,
            "change_pct": 0.62,
            "volume": 1234567,
            "market_cap": 50000000,
            "pe_ratio": 28.5,
            "revenue_growth_yoy": 0.18,
            "eps_growth_yoy": 0.15,
            "dividend_yield": 0.0
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "current_price": 78.25,
            "open_price": 77.90,
            "change_pct": 0.45,
            "volume": 987654,
            "market_cap": 12000000,
            "pe_ratio": 22.1,
            "revenue_growth_yoy": 0.10,
            "eps_growth_yoy": 0.08,
            "dividend_yield": 0.5
        },
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Industrials",
            "current_price": 152.30,
            "open_price": 151.80,
            "change_pct": 0.33,
            "volume": 654321,
            "market_cap": 80000000,
            "pe_ratio": 18.9,
            "revenue_growth_yoy": 0.06,
            "eps_growth_yoy": 0.04,
            "dividend_yield": 1.2
        },
        {
            "ticker": "GLBL",
            "company_name": "Global Retail Inc",
            "sector": "Consumer Cyclical",
            "current_price": 34.75,
            "open_price": 35.00,
            "change_pct": -0.71,
            "volume": 2109876,
            "market_cap": 35000000,
            "pe_ratio": 14.2,
            "revenue_growth_yoy": 0.02,
            "eps_growth_yoy": -0.01,
            "dividend_yield": 2.8
        }
    ]
    os.makedirs("data/stocks", exist_ok=True)
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # ---------- earnings ----------
    earnings = [
        {
            "earnings_id": "earn_001",
            "ticker": "TECH",
            "quarter": "Q2 2026",
            "report_date": "2026-07-15",
            "revenue_actual": 2500000,
            "revenue_estimate": 2400000,
            "revenue_beat": True,
            "revenue_beat_pct": 4.17,
            "eps_actual": 1.52,
            "eps_estimate": 1.45,
            "eps_beat": True,
            "eps_beat_pct": 4.83
        },
        {
            "earnings_id": "earn_002",
            "ticker": "TECH",
            "quarter": "Q1 2026",
            "report_date": "2026-04-20",
            "revenue_actual": 2300000,
            "revenue_estimate": 2250000,
            "revenue_beat": True,
            "revenue_beat_pct": 2.22,
            "eps_actual": 1.38,
            "eps_estimate": 1.35,
            "eps_beat": True,
            "eps_beat_pct": 2.22
        },
        {
            "earnings_id": "earn_003",
            "ticker": "NXTC",
            "quarter": "Q2 2026",
            "report_date": "2026-07-18",
            "revenue_actual": 1800000,
            "revenue_estimate": 1750000,
            "revenue_beat": True,
            "revenue_beat_pct": 2.86,
            "eps_actual": 0.95,
            "eps_estimate": 0.91,
            "eps_beat": True,
            "eps_beat_pct": 4.40
        },
        {
            "earnings_id": "earn_004",
            "ticker": "MFST",
            "quarter": "Q2 2026",
            "report_date": "2026-07-22",
            "revenue_actual": 3200000,
            "revenue_estimate": 3100000,
            "revenue_beat": True,
            "revenue_beat_pct": 3.23,
            "eps_actual": 2.10,
            "eps_estimate": 2.05,
            "eps_beat": True,
            "eps_beat_pct": 2.44
        }
    ]
    os.makedirs("data/earnings", exist_ok=True)
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # ---------- news ----------
    news = [
        {
            "news_id": "news_001",
            "headline": "TECH Beats Q2 Estimates on Cloud Growth",
            "summary": "TechVentures reported strong Q2 results driven by cloud services.",
            "category": "earnings",
            "source": "WSJ",
            "published_at": "2026-07-16T10:00:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TECH", "MFST"]
        },
        {
            "news_id": "news_002",
            "headline": "TECH Announces Strategic Partnership with Global Retail",
            "summary": "Partnership aims to expand tech retail presence.",
            "category": "partnership",
            "source": "TechCrunch",
            "published_at": "2026-07-14T08:30:00Z",
            "sentiment": "bullish",
            "impact": "medium",
            "related_tickers": ["TECH", "GLBL"]
        },
        {
            "news_id": "news_003",
            "headline": "Market Downturn Looms Amid Inflation Concerns",
            "summary": "Analysts warn of potential correction.",
            "category": "macro",
            "source": "Bloomberg",
            "published_at": "2026-07-17T12:00:00Z",
            "sentiment": "bearish",
            "impact": "high",
            "related_tickers": ["GLBL", "MFST"]
        },
        {
            "news_id": "news_004",
            "headline": "NXTC Product Launch Delayed",
            "summary": "Regulatory issues push launch to next quarter.",
            "category": "product",
            "source": "Reuters",
            "published_at": "2026-07-15T09:45:00Z",
            "sentiment": "bearish",
            "impact": "medium",
            "related_tickers": ["NXTC"]
        },
        {
            "news_id": "news_005",
            "headline": "TECH Wins Major Government Contract",
            "summary": "Deal valued at $150M over three years.",
            "category": "partnership",
            "source": "WSJ",
            "published_at": "2026-07-12T14:00:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["TECH"]
        }
    ]
    os.makedirs("data/news", exist_ok=True)
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # ---------- decoy data (accounts, analysts, briefs, contacts) ----------
    accounts = [
        {
            "account_id": "acc_001",
            "display_name": "Sarah Chen",
            "department": "Research",
            "email": "sarah.chen@investwise.example.com",
            "permissions": ["read", "write", "admin"],
            "default_universe": "Technology",
            "voice": ["en-US"]
        }
    ]
    os.makedirs("data/accounts", exist_ok=True)
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    analysts = [
        {
            "analyst_id": "ana_001",
            "name": "Sarah Chen",
            "firm": "InvestWise Research",
            "coverage": ["TECH", "NXTC"],
            "rating": "Senior"
        },
        {
            "analyst_id": "ana_002",
            "name": "Mike Johnson",
            "firm": "Global Equities",
            "coverage": ["MFST", "GLBL"],
            "rating": "Analyst"
        }
    ]
    os.makedirs("data/analysts", exist_ok=True)
    with open("data/analysts/analysts.json", "w") as f:
        json.dump(analysts, f, indent=2)

    briefs = [
        {
            "brief_id": "brief_001",
            "title": "NXTC - Q2 Earnings Preview",
            "ticker": "NXTC",
            "created_by": "Mike Johnson",
            "created_at": "2026-07-10T09:00:00Z",
            "updated_at": "2026-07-10T09:00:00Z",
            "brief_type": "earnings_preview",
            "status": "draft",
            "summary": "Preview of NXTC Q2 earnings.",
            "investment_rationale": ["Expects revenue beat"],
            "risks": ["Regulatory delay"],
            "valuation_methodology": "DCF with 2027 projections"
        }
    ]
    os.makedirs("data/briefs", exist_ok=True)
    with open("data/briefs/briefs.json", "w") as f:
        json.dump(briefs, f, indent=2)

    contacts = [
        {
            "contact_id": "cnt_001",
            "name": "Sarah Chen",
            "email": "sarah.chen@investwise.example.com",
            "role": "Senior Analyst",
            "team": "Technology"
        },
        {
            "contact_id": "cnt_002",
            "name": "Mike Johnson",
            "email": "mike.johnson@investwise.example.com",
            "role": "Analyst",
            "team": "Industrials"
        }
    ]
    os.makedirs("data/contacts", exist_ok=True)
    with open("data/contacts/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
