import os
import csv
from datetime import datetime

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # 主数据文件 sales_data.csv
    rows = [
        # (transaction_id, date, product, category, quantity, sales_amount, discount)
        ("T001", "2024-01-05", "Widget A", "Hardware", 2, 50.00, ""),
        ("T002", "2024-01-15", "Widget B", "Software", 1, 120.00, "10"),
        ("T003", "2024-01-20", "Widget A", "Hardware", 3, 50.00, ""),
        # 完全重复行（与T001重复）
        ("T001", "2024-01-05", "Widget A", "Hardware", 2, 50.00, ""),
        # 另一对重复（T004）
        ("T004", "2024-02-10", "Widget C", "Service", 5, 30.00, "20"),
        ("T004", "2024-02-10", "Widget C", "Service", 5, 30.00, "20"),
        ("T005", "2024-02-18", "Widget B", "Software", 1, 120.00, ""),
        ("T006", "2024-03-01", "Widget A", "Hardware", 4, 50.00, "5"),
        ("T007", "2024-03-12", "Widget C", "Service", 2, 30.00, "15"),
        ("T008", "2024-03-25", "Widget B", "Software", 3, 120.00, ""),
        # 额外孤立行，无重复
        ("T009", "2024-01-28", "Widget D", "Hardware", 1, 200.00, "10"),
    ]
    with open("data/sales_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "date", "product", "category", "quantity", "sales_amount", "discount"])
        for row in rows:
            writer.writerow(row)

    # 干扰文件：旧版本数据（类似但不同）
    old_rows = [
        ("T101", "2023-12-01", "Widget X", "Legacy", 1, 100.00, "0"),
        ("T102", "2023-12-15", "Widget Y", "Legacy", 2, 80.00, ""),
    ]
    with open("data/old_sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "date", "product", "category", "quantity", "sales_amount", "discount"])
        for row in old_rows:
            writer.writerow(row)

    # 干扰文件：测试数据（只有一行且字段不全）
    with open("data/test_sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "info"])
        writer.writerow(["test", "ignore"])

    # 干扰文件：无关笔记
    with open("data/notes.txt", "w") as f:
        f.write("这是旧备份的说明，不要删除。\n")

if __name__ == "__main__":
    build_env()
