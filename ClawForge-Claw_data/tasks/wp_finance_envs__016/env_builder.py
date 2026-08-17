import os
import json
import shutil

def build_env():
    # Ensure base directories
    os.makedirs("data/earnings", exist_ok=True)
    os.makedirs("data/analysts", exist_ok=True)
    os.makedirs("data/briefs", exist_ok=True)
    os.makedirs("data/news", exist_ok=True)
    os.makedirs("data/stocks", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("archived", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    # Stocks data
    stocks = [
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "current_price": 124.57,
            "open_price": 122.30,
            "change_pct": 1.85,
            "volume": 3450000,
            "market_cap": 89500000000,
            "pe_ratio": 28.4,
            "revenue_growth_yoy": 15.2,
            "eps_growth_yoy": 22.1,
            "dividend_yield": 0.0
        },
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 89.12,
            "open_price": 88.75,
            "change_pct": 0.42,
            "volume": 1200000,
            "market_cap": 32000000000,
            "pe_ratio": 35.6,
            "revenue_growth_yoy": 8.9,
            "eps_growth_yoy": 12.3,
            "dividend_yield": 1.2
        },
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Industrials",
            "current_price": 215.30,
            "open_price": 213.00,
            "change_pct": 1.08,
            "volume": 2100000,
            "market_cap": 128000000000,
            "pe_ratio": 22.1,
            "revenue_growth_yoy": 11.4,
            "eps_growth_yoy": 10.8,
            "dividend_yield": 1.8
        }
    ]
    # NXTC missing dividend_yield? No, it has 0.0. We'll add a dirty stock missing a field
    dirty_stock = {
        "ticker": "DISC",
        "company_name": "Discovery Corp",
        "sector": "Consumer Cyclical",
        "current_price": 45.67,
        "open_price": 46.00,
        "change_pct": -0.72,
        # missing volume, market_cap, pe_ratio etc. – intentional dirty
    }
    stocks.append(dirty_stock)
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # Earnings data
    earnings = [
        {
            "earnings_id": "earn_001",
            "ticker": "NXTC",
            "quarter": "Q1 2026",
            "report_date": "2026-04-15",
            "revenue_actual": 185000000,
            "revenue_estimate": 180000000,
            "revenue_beat": True,
            "revenue_beat_pct": 2.78,
            "eps_actual": 1.25,
            "eps_estimate": 1.20,
            "eps_beat": True,
            "eps_beat_pct": 4.17
        },
        {
            "earnings_id": "earn_002",
            "ticker": "NXTC",
            "quarter": "Q2 2026",
            "report_date": "2026-07-15",
            "revenue_actual": 210000000,
            "revenue_estimate": 200000000,
            "revenue_beat": True,
            "revenue_beat_pct": 5.00,
            "eps_actual": 1.45,
            "eps_estimate": 1.35,
            "eps_beat": True,
            "eps_beat_pct": 7.41
        },
        {
            "earnings_id": "earn_003",
            "ticker": "TECH",
            "quarter": "Q1 2026",
            "report_date": "2026-04-20",
            "revenue_actual": 95000000,
            "revenue_estimate": 100000000,
            "revenue_beat": False,
            "revenue_beat_pct": -5.00,
            "eps_actual": 0.78,
            "eps_estimate": 0.85,
            "eps_beat": False,
            "eps_beat_pct": -8.24
        },
        {
            "earnings_id": "earn_004",
            "ticker": "TECH",
            "quarter": "Q2 2026",
            "report_date": "2026-07-22",
            "revenue_actual": 105000000,
            "revenue_estimate": 102000000,
            "revenue_beat": True,
            "revenue_beat_pct": 2.94,
            "eps_actual": 0.92,
            "eps_estimate": 0.88,
            "eps_beat": True,
            "eps_beat_pct": 4.55
        }
    ]
    # Dirty record: missing eps_beat_pct
    dirty_earn = {
        "earnings_id": "earn_dirty",
        "ticker": "MFST",
        "quarter": "Q1 2026",
        "report_date": "2026-04-10",
        "revenue_actual": 320000000,
        "revenue_estimate": 315000000,
        "revenue_beat": True,
        "revenue_beat_pct": 1.59,
        "eps_actual": 2.10,
        "eps_estimate": 2.05,
        "eps_beat": True,
        # eps_beat_pct missing intentionally
    }
    earnings.append(dirty_earn)
    with open("data/earnings/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # News data
    news = [
        {
            "news_id": "news_001",
            "headline": "Nexa Technologies Partners with Cloud Giant",
            "summary": "Nexa signs strategic partnership with major cloud provider.",
            "category": "partnership",
            "source": "TechCrunch",
            "published_at": "2026-07-20T09:30:00Z",
            "sentiment": "bullish",
            "impact": "high",
            "related_tickers": ["NXTC", "TECH"]
        },
        {
            "news_id": "news_002",
            "headline": "Nexa Q2 Revenue Beats Estimates",
            "summary": "Nexa Technologies reports strong Q2 revenue growth.",
            "category": "earnings",
            "source": "Bloomberg",
            "published_at": "2026-07-16T14:00:00Z",
            "sentiment": "bullish",
            "impact": "medium",
            "related_tickers": ["NXTC"]
        },
        {
            "news_id": "news_003",
            "headline": "Regulatory Scrutiny on Nexa's New Product",
            "summary": "Regulators raise questions about Nexa's upcoming AI platform.",
            "category": "regulatory",
            "source": "Reuters",
            "published_at": "2026-07-18T11:15:00Z",
            "sentiment": "bearish",
            "impact": "high",
            "related_tickers": ["NXTC"]
        },
        {
            "news_id": "news_004",
            "headline": "TechVentures Announces New CFO",
            "summary": "TECH appoints new CFO effective next month.",
            "category": "product",
            "source": "CNBC",
            "published_at": "2026-07-12T08:00:00Z",
            "sentiment": "neutral",
            "impact": "low",
            "related_tickers": ["TECH"]
        }
    ]
    with open("data/news/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # Analysts data
    analysts = [
        {
            "analyst_id": "ana_001",
            "name": "Sarah Chen",
            "firm": "InvestWise Research",
            "coverage": ["NXTC", "TECH"],
            "rating": "Senior"
        },
        {
            "analyst_id": "ana_002",
            "name": "Tom Davis",
            "firm": "Capital Markets",
            "coverage": ["MFST", "GLBL"],
            "rating": "Analyst"
        },
        {
            "analyst_id": "ana_003",
            "name": "Emily Brown",
            "firm": "Global Equities",
            "coverage": ["CONS", "HLTH"],
            "rating": "Associate"
        }
    ]
    with open("data/analysts/analysts.json", "w") as f:
        json.dump(analysts, f, indent=2)

    # Briefs (existing, for distraction)
    briefs = [
        {
            "brief_id": "brf_001",
            "title": "NXTC - Q2 Earnings Preview",
            "ticker": "NXTC",
            "created_by": "Sarah Chen",
            "created_at": "2026-07-10T10:00:00Z",
            "updated_at": "2026-07-11T15:30:00Z",
            "brief_type": "earnings_preview",
            "status": "draft",
            "summary": "Preview of NXTC Q2 earnings expectations.",
            "investment_rationale": ["Expect revenue beat", "EPS growth story"],
            "risks": ["Valuation stretched", "Competition"],
            "valuation_methodology": "DCF with 2027 projections"
        }
    ]
    with open("data/briefs/briefs.json", "w") as f:
        json.dump(briefs, f, indent=2)

    # Risk model rules (the only correct one)
    risk_md = """# Risk Score Calculation
To compute the risk score for a ticker:
1. Find all earnings records for that ticker in data/earnings/earnings.json.
2. Calculate the average of the 'eps_beat_pct' values across all records (ignore records with missing 'eps_beat_pct').
3. From data/news/news.json, find all news items where the 'related_tickers' list includes the ticker.
   - For each news, if sentiment is 'bullish', add +1; if 'bearish', add -1; if 'neutral', add 0.
4. Sum the average eps_beat_pct (as a number, not percentage) and the sum of news sentiment scores.
   Example: if average eps_beat_pct is 5.0 and there are 2 bullish and 1 bearish news, risk score = 5.0 + (2 - 1) = 6.0.
5. The risk score is a floating-point number. Output it in the 'risk_score' field.
"""
    with open("data/risk_model.md", "w") as f:
        f.write(risk_md)

    # Distraction: old risk rule in docs/
    old_risk = """# Old Risk Rule (deprecated)
Average revenue beat percentage + 0.5 * number of news.
"""
    with open("docs/old_risk_rule.txt", "w") as f:
        f.write(old_risk)

    # Distraction: archived earnings (older version, incomplete)
    archived_earnings = [
        {"earnings_id": "earn_old", "ticker": "NXTC", "quarter": "Q4 2025", "report_date":"2026-01-20",
         "eps_actual": 1.10, "eps_estimate": 1.05, "eps_beat": True, "eps_beat_pct": 4.76}
    ]
    with open("archived/earnings_backup.json", "w") as f:
        json.dump(archived_earnings, f, indent=2)

    # Distraction: a random note file
    with open("data/notes.txt", "w") as f:
        f.write("Meeting notes: NXTC discussion postponed.\n")

if __name__ == "__main__":
    build_env()
