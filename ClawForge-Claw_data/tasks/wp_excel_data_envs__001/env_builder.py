import os
import csv

def build_env():
    os.makedirs("data", exist_ok=True)
    with open("data/raw_sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "transaction_id", "date", "product", "category",
            "sales_amount", "discount", "salesperson", "region"
        ])
        # 有效记录
        writer.writerow(["T001", "2024-01-01", "Laptop", "Electronics", "1000.0", "10", "Alice", "North"])
        writer.writerow(["T002", "2024-01-02", "Shirt", "Clothing", "50.0", "5", "Bob", "South"])
        writer.writerow(["T003", "2024-01-03", "Phone", "Electronics", "800.0", "15", "Alice", "North"])
        writer.writerow(["T004", "2024-01-04", "Shoes", "Clothing", "80.0", "0", "Bob", "East"])
        writer.writerow(["T005", "2024-01-05", "Table", "Home", "200.0", "20", "Carol", "West"])
        # 完全重复的行（内容完全一样，包括 transaction_id）
        writer.writerow(["T001", "2024-01-01", "Laptop", "Electronics", "1000.0", "10", "Alice", "North"])
        writer.writerow(["T003", "2024-01-03", "Phone", "Electronics", "800.0", "15", "Alice", "North"])
        # 无效行：负数金额
        writer.writerow(["T008", "2024-01-08", "Blank", "Home", "-100.0", "5", "Dave", "North"])
        # 无效行：空金额
        writer.writerow(["T009", "2024-01-09", "Chair", "Home", "", "10", "Eve", "South"])
        # 另一有效记录
        writer.writerow(["T010", "2024-01-10", "Lamp", "Home", "60.0", "10", "Frank", "East"])
