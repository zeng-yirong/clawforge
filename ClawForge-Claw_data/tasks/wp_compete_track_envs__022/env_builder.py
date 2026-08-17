import os
import json

def build_env():
    # Ensure required directories exist
    os.makedirs("data/users", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Create a placeholder ops file (will be overwritten by agent)
    with open("ops/.gitkeep", "w") as f:
        f.write("")

    # Clean user data files
    users = [
        {
            "user_id": "u001",
            "name": "Alice Johnson",
            "email": "alice.j@enterprise.com",
            "competitor_id": "CloudMajor",
            "tier": "enterprise",
            "cohort": "cohort_q4_2025",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "spring_promo",
            "acquisition_date": "2025-11-15",
            "acquisition_cost": 500,
            "initial_channel": "google_ads",
            "lifetime_value": 8000
        },
        {
            "user_id": "u002",
            "name": "Bob Williams",
            "email": "bob.w@startup.io",
            "competitor_id": "CloudMajor",
            "tier": "premium",
            "cohort": "cohort_q4_2025",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "spring_promo",
            "acquisition_date": "2025-12-01",
            "acquisition_cost": 700,
            "initial_channel": "google_ads",
            "lifetime_value": 6000
        },
        {
            "user_id": "u003",
            "name": "Carol Martinez",
            "email": "carol.m@cloudco.com",
            "competitor_id": "DataFlow AI",
            "tier": "basic",
            "cohort": "cohort_q4_2025",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "brand_awareness",
            "acquisition_date": "2025-10-20",
            "acquisition_cost": 300,
            "initial_channel": "google_ads",
            "lifetime_value": 3000
        },
        {
            "user_id": "u004",
            "name": "David Lee",
            "email": "david.lee@retail.net",
            "competitor_id": "TechCorp",
            "tier": "enterprise",
            "cohort": "cohort_q4_2025",
            "acquisition_source": "organic",
            "acquisition_campaign": "content_marketing",
            "acquisition_date": "2025-11-30",
            "acquisition_cost": 0,
            "initial_channel": "blog",
            "lifetime_value": 5000
        },
        {
            "user_id": "u005",
            "name": "Emma Brown",
            "email": "emma.b@saas.co",
            "competitor_id": "SmartSaaS",
            "tier": "premium",
            "cohort": "cohort_q4_2025",
            "acquisition_source": "paid_ads",
            "acquisition_campaign": "linkedin_awareness",
            "acquisition_date": "2025-12-10",
            "acquisition_cost": 200,
            "initial_channel": "linkedin",
            "lifetime_value": 2000
        }
    ]

    for user in users:
        with open(f"data/users/{user['user_id']}.json", "w") as f:
            json.dump(user, f, indent=2)

    # Corrupt file (not valid JSON)
    with open("data/users/corrupt.json", "w") as f:
        f.write("this is not json")

    # Missing lifetime_value field
    incomplete = {
        "user_id": "u006",
        "name": "Fake User",
        "email": "fake@example.com",
        "competitor_id": "DataFlow AI",
        "tier": "basic",
        "cohort": "cohort_q4_2025",
        "acquisition_source": "paid_ads",
        "acquisition_campaign": "spring_promo",
        "acquisition_date": "2025-12-05",
        "acquisition_cost": 100,
        "initial_channel": "google_ads"
    }
    with open("data/users/incomplete.json", "w") as f:
        json.dump(incomplete, f, indent=2)

    # Extra decoy: user from a different cohort but same acquisition_source
    decoy = {
        "user_id": "u007",
        "name": "Grace Kim",
        "email": "grace@other.com",
        "competitor_id": "SmartSaaS",
        "tier": "basic",
        "cohort": "cohort_q2_2025",
        "acquisition_source": "paid_ads",
        "acquisition_campaign": "partner_program",
        "acquisition_date": "2025-06-15",
        "acquisition_cost": 150,
        "initial_channel": "partner",
        "lifetime_value": 9999
    }
    with open("data/users/decoy.json", "w") as f:
        json.dump(decoy, f, indent=2)

    # Placeholder for competitors and policies (not used in task but add realism)
    os.makedirs("data/competitors", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    # Write a dummy competitor
    comp = {
        "competitor_id": "CloudMajor",
        "name": "CloudMajor",
        "description": "Leading cloud provider",
        "sector": "Cloud Computing",
        "market_cap": 500000,
        "market_share": 0.25,
        "revenue": 200000,
        "user_count": 10000,
        "growth_rate": 0.15,
        "financials": {"quarter": "Q4_2025", "profit": 50000},
        "products": ["CloudEngine", "DataLake"],
        "news": ["New AI service launched"]
    }
    with open("data/competitors/CloudMajor.json", "w") as f:
        json.dump(comp, f, indent=2)
