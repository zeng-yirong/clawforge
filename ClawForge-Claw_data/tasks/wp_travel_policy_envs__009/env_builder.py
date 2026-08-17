import os
import csv
import json
import random

random.seed(42)

def build_env():
    # Ensure directories exist
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # --- Create policy.json ---
    policy = {
        "policy_id": "acme_corp_2026",
        "name": "Acme Corp Business Travel Policy",
        "version": "3.1",
        "max_cost_per_booking": 1200,
        "max_single_booking_cost": 800,
        "allowed_cabin_classes": ["economy", "premium_economy"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 500,
        "preferred_vendors": ["SkyBook", "FlightPro"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("raw_data/policy.json", "w") as f:
        json.dump(policy, f, indent=2)

    # --- Create account.json (for reference, not used in scoring) ---
    account = {
        "account_id": "acme_001",
        "company_name": "Acme Corp",
        "travel_budget": 15000,
        "currency": "USD",
        "approvers": ["jamie@acme.com", "boss@acme.com"]
    }
    with open("raw_data/account.json", "w") as f:
        json.dump(account, f, indent=2)

    # --- Build flight offers CSV with intentional noise ---
    # Schema: flight_id, platform, origin, destination, departure_date, cabin_class, price, currency
    valid_offers = [
        # (flight_id, platform, origin, dest, date, cabin, price)
        ("FL001", "SkyBook", "JFK", "LHR", "2026-06-15", "economy", 520.00),
        ("FL002", "FlightPro", "JFK", "LHR", "2026-06-15", "premium_economy", 680.00),
        ("FL003", "AeroCheap", "JFK", "LHR", "2026-06-15", "economy", 490.00),
        ("FL004", "SkyBook", "JFK", "LHR", "2026-06-15", "business", 1200.00),   # not allowed
        ("FL005", "FlightPro", "JFK", "LHR", "2026-06-15", "economy", 1300.00),  # over max_cost_per_booking
        ("FL006", "SkyBook", "JFK", "LHR", "2026-06-15", "economy", 510.00),     # duplicate of FL001? Actually different price -> valid but not cheapest
        ("FL007", "AeroCheap", "JFK", "LHR", "2026-06-15", "first", 2000.00),    # not allowed
        ("FL008", "FlightPro", "JFK", "LHR", "2026-06-15", "premium_economy", 750.00),  # valid
    ]

    # Duplicate row (exact same as FL003) to test dedup
    duplicate = ("FL009", "AeroCheap", "JFK", "LHR", "2026-06-15", "economy", 490.00)

    # Invalid rows (corrupted)
    corrupted_rows = [
        ["FL010", "SkyBook", "JFK", "", "2026-06-15", "economy", 300.00],     # missing destination
        ["FL011", "UnknownPlat", "JFK", "LHR", "2026-06-15", "economy", 400.00], # platform not in known list? but not a policy rule
        # A row with non-numeric price
        ["FL012", "SkyBook", "JFK", "LHR", "2026-06-15", "economy", "FREE"],
        # Row with missing cabin class
        ["FL013", "SkyBook", "JFK", "LHR", "2026-06-15", "", 500.00],
    ]

    all_rows = [list(offer) for offer in valid_offers]
    all_rows.append(list(duplicate))
    all_rows.extend(corrupted_rows)

    # Shuffle to make it more realistic
    random.shuffle(all_rows)

    header = ["flight_id", "platform", "origin", "destination", "departure_date", "cabin_class", "price", "currency"]

    with open("raw_data/flight_offers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_rows)

    # --- Also create a fake directory for distraction ---
    os.makedirs("deprecated", exist_ok=True)
    with open("deprecated/old_policy.json", "w") as f:
        json.dump({"version": "2.0", "max_cost_per_booking": 500}, f)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
