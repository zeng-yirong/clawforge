import os
import json

def build_env():
    # Create data/stocks directory
    os.makedirs("data/stocks", exist_ok=True)

    # Main stock file - current version
    stocks_current = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "current_price": 150.0,
            "open_price": 148.0,
            "change_pct": 1.35,
            "volume": 2000000,
            "market_cap": 75000000000,
            "pe_ratio": 25.5,
            "revenue_growth_yoy": 0.15,
            "eps_growth_yoy": 0.12,
            "dividend_yield": 0.0
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "current_price": 88.0,
            "open_price": 87.0,
            "change_pct": 1.15,
            "volume": 1500000,
            "market_cap": 44000000000,
            "pe_ratio": 32.1,
            "revenue_growth_yoy": 0.22,
            "eps_growth_yoy": 0.18,
            "dividend_yield": 0.5
        },
        {
            "ticker": "MFST",
            "company_name": "MegaFast Shipping",
            "sector": "Industrials",
            "current_price": 45.0,
            "open_price": 44.5,
            "change_pct": 1.12,
            "volume": 5000000,
            "market_cap": 90000000000,
            "pe_ratio": 18.0,
            "revenue_growth_yoy": 0.05,
            "eps_growth_yoy": 0.03,
            "dividend_yield": 2.0
        },
        {
            "ticker": "HLTH",
            "company_name": "HealthLink Systems",
            "sector": "Healthcare",
            "current_price": 120.0,
            "open_price": 119.0,
            "change_pct": 0.84,
            "volume": 800000,
            "market_cap": 60000000000,
            "pe_ratio": 28.0,
            "revenue_growth_yoy": 0.10,
            "eps_growth_yoy": 0.08,
            "dividend_yield": 1.5
        },
        {
            "ticker": "CONS",
            "company_name": "ConsumerFirst Brands",
            "sector": "Consumer Defensive",
            "current_price": 200.0,
            "open_price": 199.0,
            "change_pct": 0.5,
            "volume": 3000000,
            "market_cap": 100000000000,
            "pe_ratio": 22.0,
            "revenue_growth_yoy": 0.03,
            "eps_growth_yoy": 0.02,
            "dividend_yield": 3.0
        }
    ]
    with open("data/stocks/stocks.json", "w") as f:
        json.dump(stocks_current, f, indent=2)

    # Decoy file – old version with different PE ratios for Technology stocks
    stocks_old = [
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "sector": "Technology",
            "pe_ratio": 24.0,
            "other_fields": "irrelevant"
        },
        {
            "ticker": "NXTC",
            "company_name": "Nexa Technologies",
            "sector": "Technology",
            "pe_ratio": 30.0,
            "other_fields": "irrelevant"
        }
    ]
    with open("data/stocks_old.json", "w") as f:
        json.dump(stocks_old, f, indent=2)

if __name__ == "__main__":
    build_env()
