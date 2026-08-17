import os
import csv

def build_env():
    # 创建必要目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("backup", exist_ok=True)  # 干扰目录

    # 写 accounts.csv
    accounts = [
        {"account_id": "C001", "display_name": "Alice", "role": "sales", "email": "alice@example.com"},
        {"account_id": "C002", "display_name": "Bob", "role": "manager", "email": "bob@example.com"},
        {"account_id": "C003", "display_name": "Charlie", "role": "analyst", "email": "charlie@example.com"},
    ]
    with open("data/accounts.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["account_id", "display_name", "role", "email"])
        writer.writeheader()
        writer.writerows(accounts)

    # 写 sales_raw.csv（含重复行和缺失值）
    fields = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "subcategory", "region", "city", "customer_id", "customer_name",
        "sales_amount", "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]
    rows = [
        # 正常记录 T001
        ["T001", "2024-01-15", "P001", "Product A", "Category1", "Sub1",
         "North", "New York", "C001", "Alice", "100.0", "2", "10",
         "Credit", "SP001", "John", "Online"],
        # 正常记录 T002
        ["T002", "2024-01-20", "P002", "Product B", "Category1", "Sub2",
         "South", "Miami", "C002", "Bob", "200.0", "1", "0",
         "Cash", "SP002", "Jane", "Retail"],
        # T003 缺失 customer_name
        ["T003", "2024-02-10", "P001", "Product A", "Category1", "Sub1",
         "North", "New York", "C003", "", "150.0", "3", "5",
         "Credit", "SP001", "John", "Online"],
        # T004
        ["T004", "2024-02-15", "P003", "Product C", "Category2", "Sub3",
         "East", "Boston", "C001", "Alice", "300.0", "2", "20",
         "Debit", "SP003", "Mike", "Online"],
        # T005
        ["T005", "2024-03-05", "P002", "Product B", "Category1", "Sub2",
         "South", "Miami", "C002", "Bob", "250.0", "1", "0",
         "Cash", "SP002", "Jane", "Retail"],
        # T006 缺失 customer_name 和 sales_amount
        ["T006", "2024-03-20", "P004", "Product D", "Category2", "Sub3",
         "West", "Los Angeles", "C003", "", "", "5", "0",
         "Cash", "SP001", "John", "Online"],
        # 完全重复的 T001
        ["T001", "2024-01-15", "P001", "Product A", "Category1", "Sub1",
         "North", "New York", "C001", "Alice", "100.0", "2", "10",
         "Credit", "SP001", "John", "Online"],
    ]
    with open("data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(rows)

    # 干扰文件：data/old_sales_raw.csv
    old_rows = [
        ["O001", "2023-12-01", "P001", "Product A", "Category1", "Sub1",
         "North", "New York", "C001", "Alice", "80.0", "1", "5",
         "Credit", "SP001", "John", "Online"],
    ]
    with open("data/old_sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(old_rows)

    # 干扰文件：backup/sales_raw_old.csv
    with open("backup/sales_raw_old.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(old_rows)

if __name__ == "__main__":
    build_env()
