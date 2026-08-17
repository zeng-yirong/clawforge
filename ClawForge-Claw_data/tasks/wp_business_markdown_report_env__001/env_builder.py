import os
import csv
import json

def build_env():
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # customer_ledger.csv
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024-04", "revenue", 12000])
        writer.writerow(["2024-04", "cost", 5000])
        writer.writerow(["2024-03", "revenue", 15000])
        writer.writerow(["", "", ""])
        writer.writerow(["2024-04", "revenue", 12000])   # 重复行
        writer.writerow(["2024-04", "revenue", "abc"])   # 脏数据

    # product_ledger.csv
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024-04", "revenue", 8000])
        writer.writerow(["2024-04", "profit", 3000])
        writer.writerow(["2024-04", "cost", 2000])
        writer.writerow(["2024-04", "other", "N/A"])

    # ops_ledger.csv
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024-04", "revenue", 5000])
        writer.writerow(["2024-03", "revenue", 7000])
        writer.writerow(["2024-04", "revenue", 5000])   # 重复行
        writer.writerow(["2024-04", "expenses", 4000])

    # 干扰文件
    accounts = [
        {"account_id": "A001", "department": "sales", "email": "s@c.com"},
        {"account_id": "A002", "department": "ops"}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

if __name__ == "__main__":
    build_env()
