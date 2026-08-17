import csv
import os

def build_env():
    # 创建目录结构
    os.makedirs("sales_data/archived", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # 主销售数据（含重复、缺失region、缺失sales_amount）
    sales_raw = [
        {"transaction_id": "T001", "product_id": "P01", "product_name": "Widget A", "category": "Home", "region": "", "city": "NY", "customer_id": "C01", "sales_amount": "120.50", "quantity": "2", "discount": "10"},
        {"transaction_id": "T002", "product_id": "P02", "product_name": "Widget B", "category": "Garden", "region": "West", "city": "LA", "customer_id": "C02", "sales_amount": "85.00", "quantity": "1", "discount": "5"},
        {"transaction_id": "T003", "product_id": "P03", "product_name": "Widget C", "category": "Electronics", "region": "", "city": "SF", "customer_id": "C03", "sales_amount": "300.00", "quantity": "3", "discount": "15"},
        {"transaction_id": "T004", "product_id": "P01", "product_name": "Widget A", "category": "Home", "region": "East", "city": "Boston", "customer_id": "C04", "sales_amount": "95.00", "quantity": "1", "discount": "0"},
        {"transaction_id": "T005", "product_id": "P02", "product_name": "Widget B", "category": "Garden", "region": "West", "city": "Seattle", "customer_id": "C05", "sales_amount": "", "quantity": "2", "discount": "5"},
        {"transaction_id": "T001", "product_id": "P01", "product_name": "Widget A", "category": "Home", "region": "East", "city": "NY", "customer_id": "C01", "sales_amount": "120.50", "quantity": "2", "discount": "10"},  # 重复T001
        {"transaction_id": "T006", "product_id": "P04", "product_name": "Widget D", "category": "Sports", "region": "North", "city": "Chicago", "customer_id": "C06", "sales_amount": "250.00", "quantity": "5", "discount": "20"},
        {"transaction_id": "T007", "product_id": "P03", "product_name": "Widget C", "category": "Electronics", "region": "South", "city": "Houston", "customer_id": "C07", "sales_amount": "180.00", "quantity": "2", "discount": "10"},
        {"transaction_id": "T008", "product_id": "P05", "product_name": "Widget E", "category": "Office", "region": "West", "city": "Denver", "customer_id": "C08", "sales_amount": "95.50", "quantity": "1", "discount": "0"},
        {"transaction_id": "T003", "product_id": "P03", "product_name": "Widget C", "category": "Electronics", "region": "South", "city": "SF", "customer_id": "C03", "sales_amount": "300.00", "quantity": "3", "discount": "15"},  # 重复T003
    ]

    with open("sales_data/sales_raw.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sales_raw[0].keys())
        writer.writeheader()
        writer.writerows(sales_raw)

    # 地区对照表（product_id -> region）
    lookup = [
        {"product_id": "P01", "region": "East"},
        {"product_id": "P02", "region": "West"},
        {"product_id": "P03", "region": "South"},
        {"product_id": "P04", "region": "North"},
        {"product_id": "P05", "region": "West"},
    ]
    with open("sales_data/region_lookup.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "region"])
        writer.writeheader()
        writer.writerows(lookup)

    # 干扰文件：旧版本存档
    old_data = [
        {"transaction_id": "T001", "product_id": "P01", "region": "East", "sales_amount": "100.00"},
        {"transaction_id": "T009", "product_id": "P06", "region": "Central", "sales_amount": "200.00"},
    ]
    with open("sales_data/archived/sales_old.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["transaction_id", "product_id", "region", "sales_amount"])
        writer.writeheader()
        writer.writerows(old_data)

    # 无关于扰文件
    with open("sales_data/notes.txt", "w") as f:
        f.write("This file is not relevant.\n")

if __name__ == "__main__":
    build_env()
