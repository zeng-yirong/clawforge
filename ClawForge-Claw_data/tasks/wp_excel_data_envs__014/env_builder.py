import os
import csv
import random
from decimal import Decimal, ROUND_HALF_UP

# 确保初始目录存在
os.makedirs("data", exist_ok=True)
os.makedirs("old_backups", exist_ok=True)
os.makedirs("temp", exist_ok=True)

# 生成销售原始数据（含干扰）
def write_sales_raw(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "date", "product_id", "product_name",
                         "category", "subcategory", "region", "city",
                         "customer_id", "customer_name", "sales_amount",
                         "quantity", "discount", "payment_method",
                         "salesperson_id", "salesperson_name", "channel"])
        for row in rows:
            writer.writerow(row)

# 正常数据
normal_rows = [
    ["T001", "2024-07-01", "P001", "Widget A", "Electronics", "Gadgets",
     "North", "New York", "C001", "Alice", "100.00", "2", "10",
     "Credit", "S001", "Bob", "Online"],
    ["T002", "2024-07-02", "P002", "Widget B", "Electronics", "Gadgets",
     "South", "Atlanta", "C002", "Bob", "200.00", "1", "0",
     "Cash", "S002", "Charlie", "Offline"],
    ["T003", "2024-07-03", "P003", "Gadget X", "Home", "Appliances",
     "East", "Boston", "C003", "Carol", "50.00", "5", "20",
     "Debit", "S003", "David", "Online"],
    ["T004", "2024-07-04", "P004", "Gadget Y", "Home", "Appliances",
     "West", "Los Angeles", "C004", "Dave", "300.00", "1", "15",
     "Credit", "S004", "Eve", "Offline"],
]

# 重复行（完全重复 T001）
duplicate_row = ["T001", "2024-07-01", "P001", "Widget A", "Electronics", "Gadgets",
                 "North", "New York", "C001", "Alice", "100.00", "2", "10",
                 "Credit", "S001", "Bob", "Online"]

# 缺失 region
missing_region = ["T005", "2024-07-05", "P005", "Tool Z", "Tools", "Hand",
                  "", "Chicago", "C005", "Eve", "150.00", "3", "5",
                  "Cash", "S005", "Frank", "Online"]

# 负数销售额
negative_amount = ["T006", "2024-07-06", "P006", "Bad item", "Misc", "Other",
                   "North", "Seattle", "C006", "Frank", "-50.00", "1", "0",
                   "Credit", "S006", "Grace", "Offline"]

# 负数数量
negative_qty = ["T007", "2024-07-07", "P007", "Defective", "Misc", "Other",
                "South", "Dallas", "C007", "Grace", "30.00", "-2", "10",
                "Debit", "S007", "Hank", "Online"]

# 构建完整列表，打乱顺序
all_rows = normal_rows + [duplicate_row] + [missing_region] + [negative_amount] + [negative_qty]
random.shuffle(all_rows)  # 增加迷惑性

# 写入主数据文件
write_sales_raw("data/sales_raw.csv", all_rows)

# 创建干扰文件：旧备份（格式相同但数据不同）
backup_rows = [
    ["B001", "2024-06-01", "P101", "Old Widget", "Electronics", "Gadgets",
     "North", "New York", "C101", "Old Alice", "80.00", "3", "0",
     "Credit", "S101", "Old Bob", "Online"],
]
write_sales_raw("old_backups/sales_2023.csv", backup_rows)

# 创建另一个干扰文件：temp 目录下的不完整文件
with open("temp/partial.csv", "w") as f:
    f.write("transaction_id,region,sales_amount\n")
    f.write("X001,North,200\n")

# 创建 accounts.csv 作为冗余数据（不会被用到）
with open("data/accounts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["account_id", "display_name", "role", "email"])
    writer.writerow(["A001", "Alice", "Manager", "alice@example.com"])
    writer.writerow(["A002", "Bob", "Sales", "bob@example.com"])
