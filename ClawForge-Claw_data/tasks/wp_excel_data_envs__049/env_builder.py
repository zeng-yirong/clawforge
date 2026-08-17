import os
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # 创建数据目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("reference", exist_ok=True)

    # 定义原始数据字段
    headers = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "subcategory", "region", "city", "customer_id", "customer_name",
        "sales_amount", "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]

    # 生成基础数据（15个正常订单）
    base_rows = []
    regions = ["East", "West", "Central"]
    cities = {
        "East": ["New York", "Boston"],
        "West": ["Los Angeles", "San Francisco"],
        "Central": ["Chicago", "Dallas"]
    }
    products = [
        ("P001", "Widget A", "Widgets", "Standard"),
        ("P002", "Gadget B", "Gadgets", "Premium"),
        ("P003", "Thingamajig C", "Thingamajigs", "Standard"),
        ("P004", "Doodad D", "Doodads", "Premium")
    ]
    customers = [
        ("C001", "Alice Corp"),
        ("C002", "Beta Inc"),
        ("C003", "Gamma LLC"),
        ("C004", "Delta Co"),
        ("C005", "Epsilon Ltd")
    ]
    salespeople = [
        ("S001", "John Smith"),
        ("S002", "Jane Doe"),
        ("S003", "Bob Johnson")
    ]
    payment_methods = ["Credit Card", "Debit Card", "Cash", "Bank Transfer"]
    channels = ["Online", "In-Store", "Phone"]

    for i in range(15):
        tid = f"T{i+100:03d}"
        date = (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
        region = random.choice(regions)
        city = random.choice(cities[region])
        prod = random.choice(products)
        cust = random.choice(customers)
        sp = random.choice(salespeople)
        amount = round(random.uniform(100, 2000), 2)
        qty = random.randint(1, 10)
        discount = random.choice([0, 5, 10, 15, 20])
        pm = random.choice(payment_methods)
        ch = random.choice(channels)
        row = [tid, date, prod[0], prod[1], prod[2], prod[3], region, city,
               cust[0], cust[1], amount, qty, discount, pm, sp[0], sp[1], ch]
        base_rows.append(row)

    # 添加重复记录（transaction_id 重复，但其他字段略有不同）
    dup_tids = ["T101", "T105", "T112"]  # 选取三个存在的tid（假设它们在base_rows中索引为0,4,11）
    # 确保这些tid存在，如果不存在则调整
    # 我们手动构建这三个重复
    # 重复1：T101 重复，但salesperson_name缺失
    dup1 = ["T101", "2023-02-15", "P001", "Widget A", "Widgets", "Standard",
            "East", "New York", "C001", "Alice Corp", 1500.00, 5, 10,
            "Credit Card", "S001", "", "Online"]
    # 重复2：T105 重复，discount缺失（空字符串）
    dup2 = ["T105", "2023-03-20", "P002", "Gadget B", "Gadgets", "Premium",
            "West", "Los Angeles", "C002", "Beta Inc", 800.00, 3, "",
            "Debit Card", "S002", "Jane Doe", "In-Store"]
    # 重复3：T112 重复，完全重复行（与原始一模一样，但作为诱饵）
    # 先找到原始T112的行
    orig_t112 = None
    for row in base_rows:
        if row[0] == "T112":
            orig_t112 = row
            break
    if orig_t112:
        dup3 = orig_t112[:]  # 复制

    rows = base_rows + [dup1, dup2, dup3]

    # 写入 sales_raw.csv
    with open("data/sales_raw.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    # 创建干扰文件：旧备份
    old_headers = headers[:]
    old_rows = [
        ["T201", "2022-11-01", "P005", "Old Widget", "Widgets", "Standard",
         "East", "New York", "C010", "Old Corp", 500.00, 2, 0,
         "Cash", "S010", "Old Sales", "Phone"]
    ]
    with open("data/old_sales_backup.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(old_headers)
        writer.writerows(old_rows)

    # 创建无关文件
    with open("reference/notes.txt", "w") as f:
        f.write("These are reference notes.\n")

    # 创建空目录
    os.makedirs("archive", exist_ok=True)

if __name__ == "__main__":
    build_env()
