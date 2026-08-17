import csv
import os

def build_env():
    # 确保目录存在（当前工作目录已是 ）
    # 写入 accounts.csv
    accounts = [
        ["customer_id", "display_name", "role", "email"],
        ["C001", "Alice Johnson", "Sales", "alice@example.com"],
        ["C002", "Bob Smith", "Sales", "bob@example.com"],
        ["C003", "Carol Davis", "Sales", "carol@example.com"],
        ["C004", "David Brown", "Sales", "david@example.com"],
    ]
    with open("accounts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(accounts)

    # 写入 sales_raw.csv，包含重复行和缺失值
    # 列顺序: transaction_id, date, product_id, product_name, category, subcategory, region, city,
    #         customer_id, customer_name, sales_amount, quantity, discount, payment_method,
    #         salesperson_id, salesperson_name, channel
    # 10条唯一记录，其中4条有缺失（customer_name 或 sales_amount）
    unique_rows = [
        # 1
        ["T001", "2024-01-10", "P001", "Widget A", "Electronics", "Widgets", "North", "New York",
         "C001", "Alice Johnson", "100.50", "2", "0", "Card", "SP01", "John Doe", "Online"],
        # 2
        ["T002", "2024-01-11", "P002", "Gadget B", "Electronics", "Gadgets", "South", "Miami",
         "C002", "Bob Smith", "250.00", "1", "10", "Cash", "SP02", "Jane Roe", "In-store"],
        # 3
        ["T003", "2024-01-12", "P003", "Device C", "Office", "Supplies", "East", "Boston",
         "C003", "Carol Davis", "45.00", "5", "0", "Card", "SP03", "Jim Beam", "Online"],
        # 4 (缺失 customer_name 和 sales_amount)
        ["T004", "2024-01-13", "P004", "Cable D", "Electronics", "Cables", "West", "Los Angeles",
         "C001", "", "", "3", "0", "Card", "SP01", "John Doe", "Online"],
        # 5 (缺失 customer_name 和 sales_amount)
        ["T005", "2024-01-14", "P005", "Adapter E", "Electronics", "Adapters", "North", "Chicago",
         "C002", "", "", "4", "5", "Card", "SP02", "Jane Roe", "In-store"],
        # 6 (缺失 sales_amount)
        ["T006", "2024-01-15", "P006", "Paper F", "Office", "Paper", "East", "Philadelphia",
         "C003", "Carol Davis", "", "6", "0", "Cash", "SP03", "Jim Beam", "Online"],
        # 7 (缺失 customer_name)
        ["T007", "2024-01-16", "P007", "Pen G", "Office", "Writing", "South", "Dallas",
         "C004", "", "12.00", "10", "0", "Card", "SP04", "Steve Jobs", "Online"],
        # 8
        ["T008", "2024-01-17", "P008", "Ink H", "Office", "Supplies", "West", "San Francisco",
         "C003", "Carol Davis", "30.00", "2", "0", "Card", "SP03", "Jim Beam", "Online"],
        # 9
        ["T009", "2024-01-18", "P009", "Board I", "Office", "Boards", "North", "Seattle",
         "C002", "Bob Smith", "200.00", "1", "10", "Card", "SP02", "Jane Roe", "In-store"],
        # 10
        ["T010", "2024-01-19", "P010", "Marker J", "Office", "Writing", "South", "Houston",
         "C001", "Alice Johnson", "15.00", "5", "0", "Cash", "SP01", "John Doe", "Online"],
    ]

    # 重复行：T001 完全重复一次，T002 完全重复一次，T003 完全重复两次
    duplicates = [
        unique_rows[0][:],  # T001
        unique_rows[1][:],  # T002
        unique_rows[2][:],  # T003 第一次重复
        unique_rows[2][:],  # T003 第二次重复
    ]

    all_rows = unique_rows + duplicates
    with open("sales_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        # 写入列头
        writer.writerow([
            "transaction_id", "date", "product_id", "product_name", "category", "subcategory",
            "region", "city", "customer_id", "customer_name", "sales_amount", "quantity",
            "discount", "payment_method", "salesperson_id", "salesperson_name", "channel"
        ])
        writer.writerows(all_rows)

    # 添加干扰文件（可选）
    with open("sales_old.csv", "w", newline="") as f:
        f.write("old data, not relevant\n")

if __name__ == "__main__":
    build_env()
