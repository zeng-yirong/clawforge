import os
import json
import csv

def build_env():
    # Create directory structure
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # --- Customer Ledger ---
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period","metric_code","metric_value"])
        # Valid Q3 rows
        writer.writerow(["2023-Q3","cust_new","120"])
        writer.writerow(["2023-Q3","cust_churn","5"])
        writer.writerow(["2023-Q3","cust_retention","85.5"])
        # Other periods
        writer.writerow(["2023-Q2","cust_new","100"])
        writer.writerow(["2023-Q2","cust_churn","4"])
        writer.writerow(["2024-Q1","cust_new","130"])
        # Dirty data: empty value
        writer.writerow(["2023-Q3","cust_new",""])
        # Dirty data: non-numeric
        writer.writerow(["2023-Q3","cust_new","invalid"])
        # Extra duplicate Q2
        writer.writerow(["2023-Q2","cust_retention","82.0"])

    # --- Ops Ledger ---
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period","metric_code","metric_value"])
        writer.writerow(["2023-Q3","ops_uptime","99.8"])
        writer.writerow(["2023-Q3","ops_response","45"])
        writer.writerow(["2023-Q3","ops_errors","2"])
        # Other period
        writer.writerow(["2023-Q2","ops_uptime","99.5"])
        # Dirty: missing value
        writer.writerow(["2023-Q3","ops_uptime",""])
        # Dirty: non-numeric
        writer.writerow(["2023-Q3","ops_response","slow"])
        # Extra Q2 duplicate
        writer.writerow(["2023-Q2","ops_errors","1"])

    # --- Product Ledger ---
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period","metric_code","metric_value"])
        writer.writerow(["2023-Q3","prod_revenue","500000"])
        writer.writerow(["2023-Q3","prod_cost","350000"])
        writer.writerow(["2023-Q3","prod_profit","150000"])
        # Other period
        writer.writerow(["2023-Q2","prod_revenue","480000"])
        writer.writerow(["2023-Q2","prod_cost","320000"])
        # Dirty: empty
        writer.writerow(["2023-Q3","prod_revenue",""])
        # Dirty: non-numeric
        writer.writerow(["2023-Q3","prod_cost","three fifty"])
        # Duplicate Q3 (same value, but still valid – agent must not double count if same metric_code appears multiple times? 
        # We'll add a second valid entry for prod_cost to test handling of duplicates.)
        # Actually we want unique answer: best to avoid exact duplicate. Let's add a second distinct but different metric.
        writer.writerow(["2023-Q3","prod_units","2500"])

    # --- Interference files ---
    # accounts.json
    accounts = [
        {"account_id": "a1", "display_name": "Kim Lee", "department": "Operations", "email": "kim@example.com", "permissions": ["read_ledgers"]},
        {"account_id": "a2", "display_name": "John Smith", "department": "Finance", "email": "john@example.com", "permissions": ["read_all"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # contacts.json
    contacts = [
        {"contact_id": "c1", "name": "BI Team", "role": "Analyst", "email": "bi@example.com"},
        {"contact_id": "c2", "name": "IT Support", "role": "Admin", "email": "it@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # Old report (distraction)
    with open("reports/q2_brief.md", "w") as f:
        f.write("# Q2 Market Brief\n\n```json\n{\"period\":\"2023-Q2\",\"customer\":{\"new\":100,\"churn\":4},\"ops\":{\"uptime\":99.5},\"product\":{\"revenue\":480000,\"cost\":320000}}\n```\n")

if __name__ == "__main__":
    build_env()
