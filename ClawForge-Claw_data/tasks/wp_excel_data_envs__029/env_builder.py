import csv
import os

def build_env():
    # 创建主数据目录和干扰目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("backup", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    # 干扰文件：旧的销售数据
    old_rows = [
        ("T001", "2024-01-01", "P001", "Widget A", "Electronics", "Gadgets", "North", "NYC", "C001", "Alice", 100.0, 2, 0, "Card", "S001", "John", "Online"),
        ("T002", "2024-01-02", "P002", "Widget B", "Electronics", "Gadgets", "South", "LA", "C002", "Bob", 200.0, 1, 5, "Cash", "S002", "Jane", "Retail"),
    ]
    with open("data/old_sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"])
        writer.writerows(old_rows)

    # 干扰文件：账户信息
    with open("data/accounts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["account_id","display_name","role","email"])
        writer.writerows([
            ("A001","Alice","Sales","alice@corp.com"),
            ("A002","Bob","Sales","bob@corp.com"),
        ])

    # 干扰文件：备份
    with open("backup/sales_backup.csv", "w", newline="") as f:
        f.write("empty\n")

    # 主数据：sales_raw.csv —— 包含重复、负数、缺失等脏数据
    raw_rows = [
        # 正常记录
        ("T001", "2024-01-01", "P001", "Widget A", "Electronics", "Gadgets", "North", "NYC", "C001", "Alice", 100.0, 2, 0, "Card", "S001", "John", "Online"),
        ("T002", "2024-01-02", "P002", "Widget B", "Electronics", "Gadgets", "South", "LA", "C002", "Bob", 200.0, 1, 5, "Cash", "S002", "Jane", "Retail"),
        # 完全重复 (与T001完全一样)
        ("T001", "2024-01-01", "P001", "Widget A", "Electronics", "Gadgets", "North", "NYC", "C001", "Alice", 100.0, 2, 0, "Card", "S001", "John", "Online"),
        # T003 重复，保留日期较新的 (2024-01-03)
        ("T003", "2024-01-02", "P003", "Widget C", "Home", "Kitchen", "East", "Boston", "C003", "Charlie", 50.0, 5, 10, "Cash", "S003", "Mike", "Online"),
        ("T003", "2024-01-03", "P003", "Widget C", "Home", "Kitchen", "East", "Boston", "C003", "Charlie", 60.0, 3, 10, "Card", "S003", "Mike", "Online"),
        # T004 重复，保留日期较新的 (2024-01-05)
        ("T004", "2024-01-04", "P004", "Widget D", "Sport", "Outdoor", "West", "SF", "C004", "Diana", 150.0, 1, 0, "Card", "S004", "Eve", "Retail"),
        ("T004", "2024-01-05", "P004", "Widget D", "Sport", "Outdoor", "West", "SF", "C004", "Diana", 180.0, 2, 0, "Cash", "S004", "Eve", "Retail"),
        # 负数金额记录（应被删除）
        ("T005", "2024-01-06", "P005", "Widget E", "Food", "Snacks", "Central", "Chicago", "C005", "Eve", -20.0, 1, 0, "Card", "S005", "Frank", "Online"),
        # 缺失 salesperson_name（应填充“未分配”）
        ("T006", "2024-01-07", "P006", "Widget F", "Clothing", "Men", "South", "Miami", "C006", "Frank", 300.0, 4, 15, "Cash", "S006", "", "Retail"),
        # 另一条正常记录
        ("T007", "2024-01-10", "P007", "Widget G", "Books", "Fiction", "North", "Seattle", "C007", "Grace", 45.0, 3, 5, "Card", "S007", "Helen", "Online"),
        # 另一条缺失销售人员名字 (需填充)
        ("T008", "2024-01-11", "P008", "Widget H", "Electronics", "Wearables", "South", "Dallas", "C008", "Henry", 250.0, 2, 0, "Cash", "S008", "", "Retail"),
        # 负数金额且缺失销售员 (双重脏)
        ("T009", "2024-01-12", "P009", "Widget I", "Sport", "Fitness", "West", "Denver", "C009", "Iris", -5.0, 1, 0, "Card", "S009", "", "Online"),
        # 正常记录
        ("T010", "2024-01-15", "P010", "Widget J", "Home", "Decor", "East", "NYC", "C010", "Jack", 120.0, 2, 0, "Card", "S010", "Kate", "Retail"),
    ]

    with open("data/sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id","date","product_id","product_name","category","subcategory","region","city","customer_id","customer_name","sales_amount","quantity","discount","payment_method","salesperson_id","salesperson_name","channel"])
        writer.writerows(raw_rows)

if __name__ == "__main__":
    build_env()
