import os
import csv
import json

def build_env():
    # Ensure base directories
    os.makedirs("data/ledgers/archive", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # --- Correct ledger: customer_ledger.csv ---
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024-Q1", "active_customers", 1000])
        writer.writerow(["2024-Q1", "active_customers", 500])
        writer.writerow(["2024-Q1", "new_customers", 150])
        writer.writerow(["2024-Q1", "new_customers", 50])
        writer.writerow(["2024-Q1", "churned_customers", 20])
        writer.writerow(["2024-Q1", "churned_customers", 10])
        writer.writerow(["2024-Q2", "active_customers", 1200])  # decoy period

    # --- Correct ledger: ops_ledger.csv ---
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024-Q1", "uptime", 99.8])
        writer.writerow(["2024-Q1", "incidents", 5])
        writer.writerow(["2024-Q1", "response_time", 2.5])

    # --- Correct ledger: product_ledger.csv ---
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024-Q1", "total_products", 450])
        writer.writerow(["2024-Q1", "defects", 12])
        writer.writerow(["2024-Q1", "returned", 5])

    # --- Decoy / interference files ---
    # Old customer ledger with different Q1 values
    with open("data/ledgers/customer_ledger_old.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2023-Q4", "active_customers", 800])
        writer.writerow(["2024-Q1", "active_customers", 999])   # misleading
        writer.writerow(["2023-Q4", "new_customers", 100])

    # Backup ops ledger (duplicate but with different values)
    with open("data/ledgers/ops_ledger_backup.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024-Q1", "uptime", 97.5])   # wrong

    # Broken product ledger (missing header, extra column)
    with open("data/ledgers/product_ledger_broken.csv", "w") as f:
        f.write("2024-Q1,total_products,999,extra\nbroken")

    # Archived ledger copy
    with open("data/ledgers/archive/customer_ledger_2023.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2023-Q4", "active_customers", 700])

    # --- Distractor JSON files (accounts and contacts) ---
    accounts = [
        {"account_id": "acc001", "display_name": "Alice", "department": "Engineering", "email": "alice@co.com", "permissions": ["read"]},
        {"account_id": "acc002", "display_name": "Bob", "department": "Finance", "email": "bob@co.com", "permissions": ["read","write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "cnt001", "name": "Charlie", "role": "Manager", "email": "charlie@co.com"},
        {"contact_id": "cnt002", "name": "Diana", "role": "Analyst", "email": "diana@co.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
