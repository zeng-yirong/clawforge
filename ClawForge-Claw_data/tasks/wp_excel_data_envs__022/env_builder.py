import os
import csv
import json
import datetime

def build_env():
    # 确保所需目录存在
    for d in ["data", "analysis", "_meta"]:
        os.makedirs(d, exist_ok=True)

    # 构造 raw_sales.csv 数据（包含重复、缺失、负数、干扰）
    fieldnames = [
        "transaction_id", "date", "product_id", "product_name", "category",
        "subcategory", "region", "city", "customer_id", "customer_name",
        "sales_amount", "quantity", "discount", "payment_method",
        "salesperson_id", "salesperson_name", "channel"
    ]

    rows = [
        # 有效记录（Electronics）
        ["T001", "2024-01-10", "P100", "Wireless Mouse", "Electronics", "Accessories", "North", "NYC", "C001", "Alice", 25.99, 2, 0, "Credit", "S001", "Bob", "Online"],
        # 完全重复 (与上一条完全相同)
        ["T001", "2024-01-10", "P100", "Wireless Mouse", "Electronics", "Accessories", "North", "NYC", "C001", "Alice", 25.99, 2, 0, "Credit", "S001", "Bob", "Online"],
        # 有效记录（Electronics）
        ["T002", "2024-01-11", "P101", "Bluetooth Speaker", "Electronics", "Audio", "West", "LA", "C002", "Bob", 49.99, 1, 5, "Debit", "S002", "Charlie", "Retail"],
        # 有效记录（Clothing）
        ["T003", "2024-01-12", "P200", "Denim Jacket", "Clothing", "Outerwear", "South", "Houston", "C003", "Carol", 79.99, 1, 10, "Credit", "S003", "David", "Online"],
        # 缺失 sales_amount（应跳过）
        ["T004", "2024-01-13", "P201", "T-Shirt", "Clothing", "Tops", "East", "Boston", "C004", "Dan", "", 3, 0, "Cash", "S004", "Eve", "Online"],
        # 负数 sales_amount（应跳过）
        ["T005", "2024-01-14", "P202", "Jeans", "Clothing", "Bottoms", "North", "Chicago", "C005", "Eve", -5.00, 1, 0, "Credit", "S005", "Frank", "Retail"],
        # 有效记录（Clothing）
        ["T006", "2024-01-15", "P203", "Sweater", "Clothing", "Knits", "West", "Seattle", "C006", "Frank", 39.99, 1, 0, "Debit", "S006", "Grace", "Online"],
        # 有效记录（Home）
        ["T007", "2024-01-16", "P300", "Desk Lamp", "Home", "Lighting", "South", "Atlanta", "C007", "Grace", 34.50, 2, 0, "Credit", "S007", "Hank", "Retail"],
        # 有效记录（Home）
        ["T008", "2024-01-17", "P301", "Throw Pillow", "Home", "Decor", "East", "Miami", "C008", "Hank", 22.99, 4, 15, "Cash", "S008", "Ivy", "Online"],
        # 部分重复但 sales_amount 不同（视为两条不同记录，保留）
        ["T001", "2024-01-10", "P100", "Wireless Mouse", "Electronics", "Accessories", "North", "NYC", "C001", "Alice", 30.00, 2, 0, "Credit", "S001", "Bob", "Online"],
        # 有效记录（Electronics）
        ["T009", "2024-01-18", "P102", "USB Hub", "Electronics", "Accessories", "West", "SF", "C009", "Ivy", 15.99, 1, 0, "Debit", "S009", "Jack", "Online"],
        # 重复但仅 quantity 不同（完全重复定义：所有字段相同，所以不同）
        ["T002", "2024-01-11", "P101", "Bluetooth Speaker", "Electronics", "Audio", "West", "LA", "C002", "Bob", 49.99, 2, 5, "Debit", "S002", "Charlie", "Retail"],
    ]

    with open("data/raw_sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(rows)

    # 创建干扰文件（旧备份）
    old_rows = [
        ["T999", "2023-12-01", "P999", "Old Product", "Misc", "Junk", "North", "Nowhere", "C999", "Ghost", 9.99, 1, 0, "Cash", "S999", "Nobody", "Unknown"]
    ]
    with open("data/old_sales_backup.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(old_rows)

    # 另一个无关于扰
    with open("data/notes.txt", "w") as f:
        f.write("This is just a note, not a data file.\n")

    # 计算正确结果（去重、排除无效、按 category 汇总）
    # 1. 读入所有行
    all_rows = []
    with open("data/raw_sales.csv", "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_rows.append(row)

    # 2. 去重（第一遍：保留第一次出现的完全重复行）
    seen = set()
    unique_rows = []
    for row in all_rows:
        key = tuple(row.values())
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)

    # 3. 过滤无效
    valid_rows = []
    for row in unique_rows:
        try:
            amount = float(row["sales_amount"])
            if amount <= 0:
                continue
            valid_rows.append(row)
        except (ValueError, TypeError):
            continue

    # 4. 按 category 分组计算
    from collections import defaultdict
    groups = defaultdict(list)
    for row in valid_rows:
        groups[row["category"]].append(float(row["sales_amount"]))

    solution = []
    for cat in sorted(groups.keys()):
        amounts = groups[cat]
        total = round(sum(amounts), 2)
        avg = round(total / len(amounts), 2)
        solution.append({
            "category": cat,
            "total_sales": total,
            "average_order": avg
        })

    # 保存隐藏结果供 verify 使用
    with open("_meta/solution.json", "w") as f:
        json.dump(solution, f, indent=2)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
