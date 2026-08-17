import os
import csv
import random
from decimal import Decimal, ROUND_HALF_UP

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("report", exist_ok=True)
    # 干扰文件：旧备份
    os.makedirs("backup", exist_ok=True)
    
    # ========== 产品目录 (product_catalog.csv) ==========
    products = {
        "P001": ("Wireless Mouse", "Electronics"),
        "P002": ("USB-C Hub", "Electronics"),
        "P003": ("Notebook", "Stationery"),
        "P004": ("Desk Lamp", "Furniture"),
        "P005": ("Coffee Mug", "Kitchen"),
        "P006": ("Headphones", "Electronics"),
        "P007": ("Backpack", "Accessories"),
    }
    with open("data/product_catalog.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "product_name", "category"])
        for pid, (pname, cat) in products.items():
            writer.writerow([pid, pname, cat])
    
    # ========== 原始销售数据 (sales_raw.csv) ==========
    # 包含3条重复记录（相同的transaction_id），部分缺失category（留空）
    sales_records = [
        ["T001", "2025-01-15", "P001", "Wireless Mouse", "", "North", "Beijing", "C001", "Alice", 120.50, 2, 5, "Credit", "S001", "Tom", "Online"],
        ["T001", "2025-01-15", "P001", "Wireless Mouse", "", "North", "Beijing", "C001", "Alice", 120.50, 2, 5, "Credit", "S001", "Tom", "Online"],  # 重复
        ["T002", "2025-01-16", "P003", "Notebook", "", "South", "Shanghai", "C002", "Bob", 85.00, 5, 10, "Cash", "S002", "Jerry", "Retail"],
        ["T003", "2025-01-17", "P002", "USB-C Hub", "", "East", "Hangzhou", "C003", "Charlie", 200.00, 1, 0, "WeChat", "S003", "Lucy", "Online"],
        ["T004", "2025-01-18", "P006", "Headphones", "", "West", "Chengdu", "C004", "Diana", 350.00, 3, 15, "Credit", "S001", "Tom", "Online"],
        ["T004", "2025-01-18", "P006", "Headphones", "", "West", "Chengdu", "C004", "Diana", 350.00, 3, 15, "Credit", "S001", "Tom", "Online"],  # 重复
        ["T005", "2025-01-19", "P004", "Desk Lamp", "", "North", "Beijing", "C005", "Eve", 75.50, 4, 5, "Cash", "S002", "Jerry", "Retail"],
        ["T006", "2025-01-20", "P005", "Coffee Mug", "", "South", "Shanghai", "C006", "Frank", 45.00, 10, 0, "WeChat", "S003", "Lucy", "Online"],
        ["T007", "2025-01-21", "P007", "Backpack", "", "East", "Hangzhou", "C007", "Grace", 180.00, 2, 20, "Credit", "S001", "Tom", "Online"],
        ["T007", "2025-01-21", "P007", "Backpack", "", "East", "Hangzhou", "C007", "Grace", 180.00, 2, 20, "Credit", "S001", "Tom", "Online"],  # 重复
        ["T008", "2025-01-22", "P001", "Wireless Mouse", "", "West", "Chengdu", "C008", "Hank", 110.00, 1, 0, "Cash", "S002", "Jerry", "Retail"],
    ]
    headers = ["transaction_id", "date", "product_id", "product_name", "category", "region", "city", "customer_id", "customer_name", "sales_amount", "quantity", "discount", "payment_method", "salesperson_id", "salesperson_name", "channel"]
    with open("data/sales_raw.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in sales_records:
            writer.writerow(row)
    
    # ========== 干扰文件：旧的备份（不同列，旧数据）==========
    with open("backup/old_sales.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "product", "amount", "region"])
        writer.writerow(["T009", "2024-12-01", "Mouse", 100.0, "North"])
        writer.writerow(["T010", "2024-12-02", "Keyboard", 200.0, "South"])
    
    # ========== 干扰文件：额外产品清单（无关）==========
    with open("data/extra_products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["code", "desc", "price"])
        writer.writerow(["X001", "Mouse Pad", 15.0])
        writer.writerow(["X002", "Cable", 8.0])
    
    # ========== 干扰文件：笔记==========
    with open("notes.txt", "w", encoding="utf-8") as f:
        f.write("待办：核对销售数据中的增值税。\n")

if __name__ == "__main__":
    build_env()
