import csv
import os

def build_env():
    # 确保必要目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)  # 干扰目录

    # 主数据文件 raw_sales_2024.csv
    # 字段顺序: transaction_id, date, product_id, product_name, category, subcategory, region, city, customer_id, customer_name, sales_amount, quantity, discount, payment_method, salesperson_id, salesperson_name, channel
    header = [
        "transaction_id", "date", "product_id", "product_name",
        "category", "subcategory", "region", "city",
        "customer_id", "customer_name", "sales_amount", "quantity",
        "discount", "payment_method", "salesperson_id", "salesperson_name", "channel"
    ]
    rows = [
        # 有效行
        ["T001", "2024-06-01", "P01", "Widget A", "Electrical", "Widgets", "North", "New York", "C001", "John Doe", "1500.00", "10", "5", "Credit", "SP01", "Alice", "Online"],
        ["T002", "2024-06-02", "P02", "Gadget B", "Electronics", "Gadgets", "South", "Atlanta", "C002", "Jane Smith", "2500.00", "5", "10", "Debit", "SP02", "Bob", "Retail"],
        ["T003", "2024-06-03", "P03", "Widget A", "Electrical", "Widgets", "East", "Boston", "C003", "Jim Brown", "800.00", "4", "0", "PayPal", "SP01", "Alice", "Online"],
        # 重复行 (T001)
        ["T001", "2024-06-01", "P01", "Widget A", "Electrical", "Widgets", "North", "New York", "C001", "John Doe", "1500.00", "10", "5", "Credit", "SP01", "Alice", "Online"],
        ["T004", "2024-06-04", "P04", "Gadget C", "Electronics", "Gadgets", "West", "Los Angeles", "C004", "Sarah Lee", "3200.00", "8", "15", "Credit", "SP02", "Bob", "Retail"],
        ["T005", "2024-06-05", "P05", "Widget B", "Electrical", "Widgets", "North", "Chicago", "C005", "Tom Clark", "1200.00", "6", "0", "Debit", "SP03", "Charlie", "Online"],
        # 重复行 (T002)
        ["T002", "2024-06-02", "P02", "Gadget B", "Electronics", "Gadgets", "South", "Atlanta", "C002", "Jane Smith", "2500.00", "5", "10", "Debit", "SP02", "Bob", "Retail"],
        ["T006", "2024-06-06", "P01", "Widget A", "Electrical", "Widgets", "East", "New York", "C006", "Emma Wilson", "900.00", "3", "5", "Credit", "SP03", "Charlie", "Retail"],
        ["T007", "2024-06-07", "P06", "Widget C", "Electrical", "Widgets", "North", "New York", "C007", "David Kim", "2000.00", "7", "10", "PayPal", "SP01", "Alice", "Online"],
        ["T008", "2024-06-08", "P07", "Gadget D", "Electronics", "Gadgets", "South", "Miami", "C008", "Anna Torres", "1100.00", "2", "0", "Debit", "SP02", "Bob", "Retail"],
        # 重复行 (T003)
        ["T003", "2024-06-03", "P03", "Widget A", "Electrical", "Widgets", "East", "Boston", "C003", "Jim Brown", "800.00", "4", "0", "PayPal", "SP01", "Alice", "Online"],
        ["T009", "2024-06-09", "P01", "Widget A", "Electrical", "Widgets", "North", "New York", "C009", "Mike Davis", "1800.00", "9", "5", "Credit", "SP03", "Charlie", "Online"],
        # 空行 (用空列表表示)
        [],
        # 负数金额行
        ["T010", "2024-06-10", "P08", "Gadget E", "Electronics", "Gadgets", "West", "Seattle", "C010", "Lucy White", "-500.00", "1", "0", "Credit", "SP02", "Bob", "Retail"],
        # 数量为零行
        ["T011", "2024-06-11", "P09", "Widget D", "Electrical", "Widgets", "East", "Boston", "C011", "Sam Green", "600.00", "0", "10", "Debit", "SP01", "Alice", "Online"],
        # 产品名缺失行 (product_name 为空)
        ["T012", "2024-06-12", "P10", "", "Electrical", "Widgets", "North", "New York", "C012", "Kate Black", "2500.00", "10", "20", "PayPal", "SP03", "Charlie", "Online"],
        # 额外有效行
        ["T013", "2024-06-13", "P01", "Widget A", "Electrical", "Widgets", "North", "Chicago", "C013", "Ray Brown", "1300.00", "7", "5", "Credit", "SP02", "Bob", "Retail"],
        ["T014", "2024-06-14", "P02", "Gadget B", "Electronics", "Gadgets", "South", "Atlanta", "C014", "Nancy Green", "2200.00", "4", "10", "Debit", "SP01", "Alice", "Online"],
    ]

    with open("data/raw_sales_2024.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    # 干扰文件：旧的备份数据
    old_rows = [
        ["transaction_id", "product_name", "sales_amount"],
        ["T001", "Widget A", "1500"],
        ["T002", "Gadget B", "2500"],
    ]
    with open("data/sales_backup_old.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_rows)

    # 干扰文件：accounts.csv（无关）
    with open("data/accounts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["account_id", "display_name", "role", "email"])
        writer.writerow(["C001", "John Doe", "customer", "john@example.com"])
        writer.writerow(["C002", "Jane Smith", "customer", "jane@example.com"])

    # 其他干扰目录和文件
    with open("logs/access.log", "w") as f:
        f.write("2024-01-01 10:00:00 INFO startup\n")
    with open("logs/debug.log", "w") as f:
        f.write("[DEBUG] nothing important\n")


if __name__ == "__main__":
    build_env()
