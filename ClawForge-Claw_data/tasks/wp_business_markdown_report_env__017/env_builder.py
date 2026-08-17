import os
import csv

def build_env():
    # 确保目录存在
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # ===== customer_ledger.csv =====
    rows = [
        ["period", "metric_code", "metric_value"],
        ["2025-Q1", "revenue", "1000"],
        ["2025-Q1", "revenue", "1000"],         # 重复行
        ["2025-Q1", "cost", "500"],
        ["2025-Q1", "cost", "abc"],             # 无效值
        ["2025-01", "cost", "200"],             # 无关 period
        ["2025-Q1", "profit", "300"],
    ]
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    # ===== ops_ledger.csv =====
    rows = [
        ["period", "metric_code", "metric_value"],
        ["2025-Q1", "uptime", "99.9"],
        ["2025-Q1", "uptime", "99.9"],          # 重复行
        ["2025-Q2", "uptime", "98.0"],          # 无关 period
        ["2025-Q1", "errors", "5"],
    ]
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    # ===== product_ledger.csv =====
    rows = [
        ["period", "metric_code", "metric_value"],
        ["2025-Q1", "revenue", "2000"],
        ["2025-Q1", "units", "150"],
    ]
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    # ===== 干扰文件 =====
    with open("data/ledgers/old_customer_ledger.csv", "w") as f:
        f.write("period,metric_code,metric_value\n2024-Q4,revenue,800\n")
    with open("data/ledgers/notes.txt", "w") as f:
        f.write("ignore this file\n")
    
    # ===== accounts.json & contacts.json (无关) =====
    with open("data/accounts.json", "w") as f:
        f.write('{"accounts": [{"account_id": "a1", "display_name": "Alice", "department": "Sales", "email": "a@c.com", "permissions": ["read"]}]}')
    with open("data/contacts.json", "w") as f:
        f.write('{"contacts": [{"contact_id": "c1", "name": "Bob", "role": "Manager", "email": "b@c.com"}]}')

if __name__ == "__main__":
    build_env()
