import os
import csv
import random

def build_env():
    # 确保目录存在
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)

    # 标准记录模板
    base_records = [
        {"transaction_id": "T001", "date": "2024-01-15", "product_id": "P001", "product_name": "Wireless Mouse", "category": "Electronics", "subcategory": "Peripherals", "region": "North", "city": "New York", "customer_id": "C001", "customer_name": "Alice", "sales_amount": "45.00", "quantity": "2", "discount": "10", "payment_method": "Credit Card", "salesperson_id": "S001", "salesperson_name": "John", "channel": "Online"},
        {"transaction_id": "T002", "date": "2024-01-16", "product_id": "P002", "product_name": "Desk Lamp", "category": "Home", "subcategory": "Lighting", "region": "South", "city": "Atlanta", "customer_id": "C002", "customer_name": "Bob", "sales_amount": "120.00", "quantity": "1", "discount": "0", "payment_method": "Cash", "salesperson_id": "S002", "salesperson_name": "Jane", "channel": "Retail"},
        {"transaction_id": "T003", "date": "2024-01-17", "product_id": "P003", "product_name": "Notebook", "category": "Stationery", "subcategory": "Paper", "region": "East", "city": "Boston", "customer_id": "C003", "customer_name": "Charlie", "sales_amount": "25.50", "quantity": "5", "discount": "5", "payment_method": "Debit Card", "salesperson_id": "S003", "salesperson_name": "Mike", "channel": "Online"},
        {"transaction_id": "T004", "date": "2024-01-18", "product_id": "P004", "product_name": "Coffee Maker", "category": "Kitchen", "subcategory": "Appliances", "region": "West", "city": "Los Angeles", "customer_id": "C004", "customer_name": "David", "sales_amount": "89.99", "quantity": "1", "discount": "20", "payment_method": "Credit Card", "salesperson_id": "S004", "salesperson_name": "Sarah", "channel": "Retail"},
        {"transaction_id": "T005", "date": "2024-01-19", "product_id": "P005", "product_name": "Yoga Mat", "category": "Sports", "subcategory": "Fitness", "region": "North", "city": "Chicago", "customer_id": "C005", "customer_name": "Eve", "sales_amount": "35.00", "quantity": "3", "discount": "0", "payment_method": "Cash", "salesperson_id": "S005", "salesperson_name": "Tom", "channel": "Online"},
    ]

    # 添加重复记录：T002 完全重复一次，T004 完全重复一次
    duplicate_records = [
        {"transaction_id": "T002", "date": "2024-01-16", "product_id": "P002", "product_name": "Desk Lamp", "category": "Home", "subcategory": "Lighting", "region": "South", "city": "Atlanta", "customer_id": "C002", "customer_name": "Bob", "sales_amount": "120.00", "quantity": "1", "discount": "0", "payment_method": "Cash", "salesperson_id": "S002", "salesperson_name": "Jane", "channel": "Retail"},
        {"transaction_id": "T004", "date": "2024-01-18", "product_id": "P004", "product_name": "Coffee Maker", "category": "Kitchen", "subcategory": "Appliances", "region": "West", "city": "Los Angeles", "customer_id": "C004", "customer_name": "David", "sales_amount": "89.99", "quantity": "1", "discount": "20", "payment_method": "Credit Card", "salesperson_id": "S004", "salesperson_name": "Sarah", "channel": "Retail"},
    ]

    # 添加包含缺失值的记录：T006 缺 sales_amount，T007 缺 product_name
    missing_records = [
        {"transaction_id": "T006", "date": "2024-01-20", "product_id": "P006", "product_name": "Pen Set", "category": "Stationery", "subcategory": "Writing", "region": "South", "city": "Houston", "customer_id": "C006", "customer_name": "Frank", "sales_amount": "", "quantity": "10", "discount": "0", "payment_method": "Cash", "salesperson_id": "S006", "salesperson_name": "Lisa", "channel": "Retail"},
        {"transaction_id": "T007", "date": "2024-01-21", "product_id": "P007", "product_name": "", "category": "Electronics", "subcategory": "Accessories", "region": "East", "city": "Miami", "customer_id": "C007", "customer_name": "Grace", "sales_amount": "67.50", "quantity": "2", "discount": "15", "payment_method": "Debit Card", "salesperson_id": "S007", "salesperson_name": "Paul", "channel": "Online"},
    ]

    # 干扰文件：old_sales.csv 内容稍有不同，故意包含一些额外记录
    old_records = [
        {"transaction_id": "T001", "date": "2023-12-20", "product_id": "P001", "product_name": "Wireless Mouse", "category": "Electronics", "subcategory": "Peripherals", "region": "North", "city": "New York", "customer_id": "C001", "customer_name": "Alice", "sales_amount": "45.00", "quantity": "2", "discount": "10", "payment_method": "Credit Card", "salesperson_id": "S001", "salesperson_name": "John", "channel": "Online"},
        {"transaction_id": "T008", "date": "2024-01-10", "product_id": "P008", "product_name": "Bluetooth Speaker", "category": "Electronics", "subcategory": "Audio", "region": "West", "city": "San Francisco", "customer_id": "C008", "customer_name": "Hank", "sales_amount": "150.00", "quantity": "1", "discount": "5", "payment_method": "Credit Card", "salesperson_id": "S008", "salesperson_name": "Nina", "channel": "Online"},
    ]

    # 写入 sales_raw.csv
    fieldnames = list(base_records[0].keys())
    with open("data/sales_raw.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # 先写入基本记录
        for r in base_records:
            writer.writerow(r)
        # 插入重复记录（故意打乱顺序增加迷惑性）
        for r in duplicate_records:
            writer.writerow(r)
        # 插入缺失记录
        for r in missing_records:
            writer.writerow(r)

    # 写入干扰文件 old_sales.csv
    with open("data/backup/old_sales.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in old_records:
            writer.writerow(r)

    # 写入一个无用的 readme.txt
    with open("data/readme.txt", "w") as f:
        f.write("This directory contains sales export files. Do not modify directly.\n")

if __name__ == "__main__":
    build_env()
