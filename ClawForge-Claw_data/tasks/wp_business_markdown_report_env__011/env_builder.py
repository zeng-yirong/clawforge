import os
import csv
import json

def build_env():
    # Create directory structure
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/old", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # ---- Customer ledger ----
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2025-01", "active_customers", 125])
        writer.writerow(["2025-01", "new_signups", 45])
        writer.writerow(["2024-12", "active_customers", 100])
        writer.writerow(["2024-12", "new_signups", 30])

    # ---- Ops ledger ----
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2025-01", "revenue", 45000])
        writer.writerow(["2025-01", "expenses", 32000])
        writer.writerow(["2024-12", "revenue", 38000])

    # ---- Product ledger ----
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2025-01", "product_count", 80])
        writer.writerow(["2025-01", "returns", 5])
        writer.writerow(["2024-12", "product_count", 75])

    # ---- Distractor: old copy with wrong values ----
    with open("data/old/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2025-01", "active_customers", 200])  # wrong
        writer.writerow(["2024-12", "active_customers", 100])

    # ---- Distractor: accounts.json (not used in answer) ----
    accounts = [
        {
            "account_id": "a1",
            "display_name": "Acme Corp",
            "department": "Sales",
            "email": "acme@test.com",
            "permissions": ["read", "write"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # ---- Distractor: contacts.json (not used in answer) ----
    contacts = [
        {
            "contact_id": "c1",
            "name": "John Doe",
            "role": "Manager",
            "email": "jdoe@test.com"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

if __name__ == "__main__":
    build_env()
