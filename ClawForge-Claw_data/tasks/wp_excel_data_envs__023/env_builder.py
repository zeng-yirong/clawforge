import os
import csv
import random

def build_env():
    # 保证工作区干净
    base = "."
    os.makedirs(base, exist_ok=True)

    # 构建原始销售数据（含重复、负数、缺失）
    rows = [
        ["T001", "2023-01-01", "Electronics", 1200.00, "North"],
        ["T002", "2023-01-02", "Clothing", 450.00, "South"],
        ["T003", "2023-01-03", "Electronics", 800.00, "East"],
        ["T003", "2023-01-03", "Electronics", 800.00, "West"],  # 重复
        ["T004", "2023-01-04", "Food", 250.00, "West"],
        ["T005", "2023-01-05", "Electronics", -50.00, "North"], # 负数
        ["T006", "2023-01-06", "Clothing", 600.00, "West"],
        ["T007", "2023-01-07", "Food", 150.00, ""],             # 地区缺失
        ["T008", "2023-01-08", "Electronics", 1100.00, "South"],
        ["T009", "2023-01-09", "Clothing", 320.00, "North"],
        ["T010", "2023-01-10", "Food", 200.00, "East"],
    ]
    # 打乱顺序增加迷惑性
    random.shuffle(rows)

    with open("raw_sales.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "date", "category", "sales_amount", "region"])
        writer.writerows(rows)

    # 干扰文件
    with open("old_backup.csv", "w", newline="") as f:
        f.write("id,value\n1,abc\n2,def\n")
    with open("notes.txt", "w") as f:
        f.write("These are just random notes.\n")

if __name__ == "__main__":
    build_env()
