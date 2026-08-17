import os
import csv
import json

def build_env():
    # Ensure base directories
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # decoy directory

    # --- Customer ledger ---
    cust_rows = [
        ["period", "metric_code", "metric_value"],
        # valid Q4 rows
        ["2024-Q4", "new_customers", "150"],
        ["2024-Q4", "churned_customers", "23"],
        ["2024-Q4", "total_customers", "5000"],
        # duplicate row (exact copy of new_customers)
        ["2024-Q4", "new_customers", "150"],
        # malformed row (missing metric_code)
        ["2024-Q4", "", "50"],
        # other periods (noise)
        ["2024-Q3", "new_customers", "120"],
        ["2025-Q1", "new_customers", "100"],
    ]
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(cust_rows)

    # --- Product ledger ---
    prod_rows = [
        ["period", "metric_code", "metric_value"],
        ["2024-Q4", "units_sold", "1200"],
        ["2024-Q4", "returns", "45"],
        ["2024-Q4", "avg_price", "24"],
        # duplicate row (exact copy of units_sold)
        ["2024-Q4", "units_sold", "1200"],
        # noise
        ["2024-Q3", "units_sold", "1100"],
        ["2025-Q1", "units_sold", "1300"],
    ]
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(prod_rows)

    # --- Ops ledger ---
    ops_rows = [
        ["period", "metric_code", "metric_value"],
        ["2024-Q4", "uptime_pct", "99"],
        ["2024-Q4", "incidents", "3"],
        ["2024-Q4", "response_time_avg_ms", "2400"],
        # noise
        ["2024-Q3", "uptime_pct", "99"],
        ["2025-Q1", "incidents", "1"],
    ]
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(ops_rows)

    # --- Decoy JSON files (not used by the task) ---
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Ana", "department": "Finance", "email": "ana@fin.local", "permissions": ["read"]},
            {"account_id": "A002", "display_name": "Bob", "department": "Ops", "email": "bob@ops.local", "permissions": ["read", "write"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "CFO Office", "role": "Executive", "email": "cfo@fin.local"},
            {"contact_id": "C002", "name": "Data Support", "role": "Tech", "email": "support@fin.local"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    # --- A dummy readme in data (noise) ---
    with open("data/README.md", "w") as f:
        f.write("# Dump directory\nThese are raw exports from the accounting system.\n")

if __name__ == "__main__":
    build_env()
