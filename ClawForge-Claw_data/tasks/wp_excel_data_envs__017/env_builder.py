import os
import csv
import random

def build_env():
    # 确保基础目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)  # 空目录，agent 会覆盖

    # 设置随机种子保证可复现
    random.seed(42)

    # 定义列名
    fieldnames = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "subcategory", "region", "city", "customer_id", "customer_name",
        "sales_amount", "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]

    # 基础数据行（含重复、缺失、干扰）
    rows = [
        # transaction_id, date, product_id, product_name, category, subcategory, region, city, customer_id, customer_name, sales_amount, quantity, discount, payment_method, salesperson_id, salesperson_name, channel
        # 重复 T001
        ["T001", "2025-01-01", "P001", "Widget A", "Widgets", "Standard", "East", "New York", "C001", "Alice", "100.0", "2", "0", "Credit", "S001", "John", "Online"],
        ["T001", "2025-01-03", "P001", "Widget A", "Widgets", "Standard", "East", "New York", "C001", "Alice", "110.0", "2", "0", "Credit", "S001", "John", "Online"],
        # 重复 T002（最后一条缺失 sales_amount）
        ["T002", "2025-01-02", "P001", "Widget A", "Widgets", "Standard", "East", "Boston", "C002", "Bob", "200.0", "3", "5", "Cash", "S002", "Jane", "Retail"],
        ["T002", "2025-01-04", "P001", "Widget A", "Widgets", "Standard", "East", "Boston", "C002", "Bob", "210.0", "3", "5", "Cash", "S002", "Jane", "Retail"],
        ["T002", "2025-01-05", "P001", "Widget A", "Widgets", "Standard", "East", "Boston", "C002", "Bob", "", "3", "5", "Cash", "S002", "Jane", "Retail"],
        # 重复 T003
        ["T003", "2025-01-02", "P002", "Widget B", "Widgets", "Premium", "West", "Los Angeles", "C003", "Charlie", "300.0", "1", "0", "Debit", "S003", "Mike", "Online"],
        ["T003", "2025-01-04", "P002", "Widget B", "Widgets", "Premium", "West", "Los Angeles", "C003", "Charlie", "300.0", "1", "0", "Debit", "S003", "Mike", "Online"],
        # 单行无重复但有缺失
        ["T004", "2025-01-06", "P003", "Gadget X", "Gadgets", "Basic", "North", "Chicago", "C004", "Diana", "150.0", "4", "10", "Credit", "S004", "Emma", "Retail"],
        ["T005", "2025-01-07", "P002", "Widget B", "Widgets", "Premium", "West", "San Francisco", "C005", "Eve", "", "2", "0", "Cash", "S005", "Tom", "Online"],
        # 另外一些正常行（用于填充平均值）
        ["T006", "2025-01-08", "P001", "Widget A", "Widgets", "Standard", "South", "Houston", "C006", "Frank", "120.0", "3", "0", "Credit", "S001", "John", "Online"],
        ["T007", "2025-01-09", "P002", "Widget B", "Widgets", "Premium", "North", "Seattle", "C007", "Grace", "250.0", "1", "5", "Debit", "S003", "Mike", "Retail"],
        ["T008", "2025-01-10", "P004", "Gadget Y", "Gadgets", "Advanced", "East", "Philadelphia", "C008", "Heidi", "180.0", "2", "0", "Credit", "S006", "Lisa", "Online"],
        ["T009", "2025-01-11", "P003", "Gadget X", "Gadgets", "Basic", "South", "Miami", "C009", "Ivan", "160.0", "5", "10", "Cash", "S007", "Nina", "Retail"],
        # 干扰项：重复但更旧，应该被丢弃
        ["T010", "2024-12-31", "P005", "Legacy Item", "Legacy", "Old", "East", "New York", "C010", "Judy", "500.0", "1", "0", "Credit", "S008", "Paul", "Online"],
        ["T010", "2025-01-01", "P005", "Legacy Item", "Legacy", "Old", "East", "New York", "C010", "Judy", "550.0", "1", "0", "Credit", "S008", "Paul", "Online"],
        # 干扰：完全不同的旧备份数据（不应被 agent 处理）
        ["T011", "2024-06-01", "P006", "Old Widget", "Widgets", "Standard", "West", "Denver", "C011", "Ken", "999.0", "10", "20", "Check", "S009", "Kim", "Offline"],
    ]

    # 写入 sales_raw.csv
    with open("data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(rows)

    # 创建干扰文件
    # 1. 旧备份
    old_rows = [
        ["TX01", "2025-01-01", "P001", "Widget A", "Widgets", "Standard", "East", "New York", "C001", "Alice", "100.0", "2", "0", "Credit", "S001", "John", "Online"],
        ["TX02", "2025-01-02", "P002", "Widget B", "Widgets", "Premium", "West", "LA", "C003", "Charlie", "300.0", "1", "0", "Debit", "S003", "Mike", "Online"],
    ]
    os.makedirs("data/backup", exist_ok=True)
    with open("data/backup/old_sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(old_rows)

    # 2. 客户信息文件
    accounts = [
        ["C001", "Alice", "Manager", "alice@example.com"],
        ["C002", "Bob", "Staff", "bob@example.com"],
    ]
    with open("data/accounts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["account_id", "display_name", "role", "email"])
        writer.writerows(accounts)

    # 3. 日志目录（空的）
    os.makedirs("logs", exist_ok=True)

    # 4. 诱饵：一个不完整的 CSV
    with open("data/incomplete.csv", "w") as f:
        f.write("header1,header2\nvalue1\n")

if __name__ == "__main__":
    build_env()
