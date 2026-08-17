import os
import csv
import random

def build_env():
    # Create directories
    os.makedirs("ledgers", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    # Create a dummy accounts.json (distraction)
    with open("accounts.json", "w") as f:
        f.write('{"accounts": []}')
    
    # Helper to write CSV with a given filename and list of rows
    def write_csv(filename, rows):
        with open(f"ledgers/{filename}", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["period", "metric_code", "metric_value"])
            writer.writerows(rows)
    
    # Customer ledger: some 2024-Q1 rows and noise
    customer_rows = [
        ("2024-Q1", "new_customers", 42),
        ("2024-Q1", "active_customers", 315),
        ("2024-Q1", "churned_customers", 11),
        ("2023-Q4", "new_customers", 38),
        ("2023-Q4", "active_customers", 290),
        ("2023-Q3", "new_customers", 35),
    ]
    write_csv("customer_ledger.csv", customer_rows)
    
    # Product ledger
    product_rows = [
        ("2024-Q1", "units_sold", 1280),
        ("2024-Q1", "returns", 47),
        ("2024-Q1", "new_products", 5),
        ("2023-Q4", "units_sold", 1150),
        ("2023-Q4", "returns", 52),
    ]
    write_csv("product_ledger.csv", product_rows)
    
    # Ops ledger
    ops_rows = [
        ("2024-Q1", "server_uptime", 99.7),
        ("2024-Q1", "incidents_resolved", 89),
        ("2024-Q1", "avg_response_time", 1.2),
        ("2023-Q4", "server_uptime", 99.5),
        ("2023-Q4", "incidents_resolved", 82),
    ]
    write_csv("ops_ledger.csv", ops_rows)

if __name__ == "__main__":
    build_env()
