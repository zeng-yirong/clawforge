import os
import json
import random
random.seed(42)

def build_env():
    # ---- data/ ----
    os.makedirs("data", exist_ok=True)

    # stocks.json
    stocks = [
        {"ticker": "TECH", "company_name": "TechVentures Inc", "sector": "Technology", "current_price": 145.2, "open_price": 143.8, "change_pct": 0.97, "volume": 3200000, "market_cap": 58000000000, "pe_ratio": 28.5, "revenue_growth_yoy": 22.3, "eps_growth_yoy": 18.7, "dividend_yield": 0.5},
        {"ticker": "NXTC", "company_name": "Nexa Technologies", "sector": "Technology", "current_price": 78.4, "open_price": 77.9, "change_pct": 0.64, "volume": 1800000, "market_cap": 24000000000, "pe_ratio": 35.2, "revenue_growth_yoy": 11.8, "eps_growth_yoy": 6.2, "dividend_yield": 0.0},
        {"ticker": "MFST", "company_name": "MegaFast Shipping", "sector": "Industrials", "current_price": 92.1, "open_price": 91.5, "change_pct": 0.66, "volume": 4100000, "market_cap": 72000000000, "pe_ratio": 18.3, "revenue_growth_yoy": 5.1, "eps_growth_yoy": 4.0, "dividend_yield": 1.2},
        {"ticker": "CONS", "company_name": "ConsumerFirst Brands", "sector": "Consumer Defensive", "current_price": 55.0, "open_price": 55.3, "change_pct": -0.54, "volume": 1500000, "market_cap": 18000000000, "pe_ratio": 22.7, "revenue_growth_yoy": 3.2, "eps_growth_yoy": 2.9, "dividend_yield": 2.1},
        {"ticker": "FNS", "company_name": "FinServe Corp", "sector": "Financial Services", "current_price": 212.0, "open_price": 210.5, "change_pct": 0.71, "volume": 980000, "market_cap": 105000000000, "pe_ratio": 15.4, "revenue_growth_yoy": 8.7, "eps_growth_yoy": 9.1, "dividend_yield": 1.8},
        {"ticker": "HLTH", "company_name": "HealthLink Systems", "sector": "Healthcare", "current_price": 134.6, "open_price": 133.2, "change_pct": 1.05, "volume": 2100000, "market_cap": 46000000000, "pe_ratio": 42.1, "revenue_growth_yoy": 14.3, "eps_growth_yoy": 12.5, "dividend_yield": 0.3},
    ]
    with open("data/stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    # news.json
    news = [
        {"news_id": "news_001", "headline": "TECH Partners with Global AI Leader", "summary": "TechVentures announced a strategic partnership with a leading AI firm to integrate GenAI into its cloud platform.", "category": "partnership", "source": "TechCrunch", "published_at": "2026-06-15T08:00:00Z", "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "news_002", "headline": "NXTC Faces Regulatory Delay in EU Launch", "summary": "Nexa Technologies received a setback as EU regulators postponed approval for its new product line.", "category": "regulatory", "source": "Reuters", "published_at": "2026-06-10T14:30:00Z", "sentiment": "bearish", "impact": "medium", "related_tickers": ["NXTC"]},
        {"news_id": "news_003", "headline": "Fed Holds Rates Steady, Markets React", "summary": "The Federal Reserve kept interest rates unchanged, sparking mixed reactions across sectors.", "category": "macro", "source": "CNBC", "published_at": "2026-06-14T19:00:00Z", "sentiment": "neutral", "impact": "medium", "related_tickers": []},
        {"news_id": "news_004", "headline": "TECH Reports Record Cloud Revenue", "summary": "TechVentures posted record quarterly cloud revenue, exceeding analyst expectations.", "category": "earnings", "source": "Bloomberg", "published_at": "2026-06-12T10:15:00Z", "sentiment": "bullish", "impact": "high", "related_tickers": ["TECH"]},
        {"news_id": "news_005", "headline": "NXTC Hires New CFO from Competitor", "summary": "Nexa Technologies appointed a former financial officer from a rival firm to strengthen its finance team.", "category": "product", "source": "WSJ", "published_at": "2026-06-08T09:45:00Z", "sentiment": "neutral", "impact": "low", "related_tickers": ["NXTC"]},
    ]
    with open("data/news.json", "w") as f:
        json.dump(news, f, indent=2)

    # earnings.json
    earnings = [
        {"earnings_id": "earn_001", "ticker": "TECH", "quarter": "Q2 2026", "report_date": "2026-06-20", "revenue_actual": 3850000000, "revenue_estimate": 3500000000, "revenue_beat": True, "revenue_beat_pct": 10.0, "eps_actual": 2.34, "eps_estimate": 2.03, "eps_beat": True, "eps_beat_pct": 15.27},
        {"earnings_id": "earn_002", "ticker": "NXTC", "quarter": "Q2 2026", "report_date": "2026-06-18", "revenue_actual": 1200000000, "revenue_estimate": 1150000000, "revenue_beat": True, "revenue_beat_pct": 4.35, "eps_actual": 0.88, "eps_estimate": 0.84, "eps_beat": True, "eps_beat_pct": 4.76},
        {"earnings_id": "earn_003", "ticker": "TECH", "quarter": "Q1 2026", "report_date": "2026-03-25", "revenue_actual": 3400000000, "revenue_estimate": 3300000000, "revenue_beat": True, "revenue_beat_pct": 3.03, "eps_actual": 2.01, "eps_estimate": 1.95, "eps_beat": True, "eps_beat_pct": 3.08},
        {"earnings_id": "earn_004", "ticker": "NXTC", "quarter": "Q1 2026", "report_date": "2026-03-20", "revenue_actual": 1050000000, "revenue_estimate": 1020000000, "revenue_beat": True, "revenue_beat_pct": 2.94, "eps_actual": 0.76, "eps_estimate": 0.73, "eps_beat": True, "eps_beat_pct": 4.11},
        {"earnings_id": "earn_005", "ticker": "MFST", "quarter": "Q2 2026", "report_date": "2026-06-22", "revenue_actual": 8700000000, "revenue_estimate": 8800000000, "revenue_beat": False, "revenue_beat_pct": -1.14, "eps_actual": 1.52, "eps_estimate": 1.60, "eps_beat": False, "eps_beat_pct": -5.0},
        {"earnings_id": "earn_006", "ticker": "CONS", "quarter": "Q2 2026", "report_date": "2026-06-16", "revenue_actual": 2100000000, "revenue_estimate": 2150000000, "revenue_beat": False, "revenue_beat_pct": -2.33, "eps_actual": 1.11, "eps_estimate": 1.14, "eps_beat": False, "eps_beat_pct": -2.63},
    ]
    with open("data/earnings.json", "w") as f:
        json.dump(earnings, f, indent=2)

    # analysts.json (distractor, not used in prompt)
    analysts = [
        {"analyst_id": "a001", "name": "Sarah Chen", "firm": "InvestWise Research", "coverage": ["TECH", "NXTC"], "rating": "Senior"},
        {"analyst_id": "a002", "name": "Mike Johnson", "firm": "Capital Markets", "coverage": ["MFST", "HLTH"], "rating": "Analyst"},
        {"analyst_id": "a003", "name": "Emily Brown", "firm": "Global Equities", "coverage": ["CONS", "FNS"], "rating": "Associate"},
    ]
    with open("data/analysts.json", "w") as f:
        json.dump(analysts, f, indent=2)

    # contacts.json (distractor)
    contacts = [
        {"contact_id": "c001", "name": "James Smith", "email": "james.smith@investwise.example.com", "role": "IR Director", "team": "Investor Relations"},
        {"contact_id": "c002", "name": "Lisa Wang", "email": "lisa.wang@techventures.example.com", "role": "Editor", "team": "Editorial"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # briefs.json empty (distractor)
    with open("data/briefs.json", "w") as f:
        json.dump([], f, indent=2)

    # ---- ops/ (empty, agent will create file here) ----
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
