import os
import csv
import json

def build_env():
    # Create directory structure
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("data/ledgers/archive", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 干扰目录

    # ---- 正常账本数据 ----
    # customer_ledger.csv (指标: revenue, cost, profit)
    customer_rows = [
        # 2024-Q1 正常数据
        ("2024-Q1", "revenue", 1000),
        ("2024-Q1", "revenue", 500),   # 同一指标有两行，应求和
        ("2024-Q1", "cost", 400),
        ("2024-Q1", "profit", 1100),
        # 2023-Q4 旧数据（应被忽略）
        ("2023-Q4", "revenue", 800),
        ("2023-Q4", "cost", 300),
        ("2023-Q4", "profit", 500),
    ]
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerows(customer_rows)

    # product_ledger.csv
    product_rows = [
        ("2024-Q1", "revenue", 2500),
        ("2024-Q1", "cost", 1200),
        ("2024-Q1", "profit", 1300),
        # 脏数据：非数字 metric_value
        ("2024-Q1", "revenue", "7k"),
        ("2024-Q1", "profit", 1300),   # 重复？保持唯一答案，此处是额外行
        # 过期
        ("2023-Q4", "revenue", 2000),
        ("2023-Q4", "cost", 900),
        ("2023-Q4", "profit", 1100),
    ]
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerows(product_rows)

    # ops_ledger.csv
    ops_rows = [
        ("2024-Q1", "revenue", 3000),
        ("2024-Q1", "cost", 1800),
        ("2024-Q1", "profit", 1200),
        # 拼写错误：revenu（应被过滤）
        ("2024-Q1", "revenu", 500),
        # 空 period
        ("", "cost", 100),
        # 脏数据：非整数
        ("2024-Q1", "cost", "1,200"),
        ("2024-Q1", "revenue", 3000),  # 重复行？不重复，但故意多一行
        # 过期
        ("2023-Q4", "revenue", 2200),
        ("2023-Q4", "cost", 1000),
        ("2023-Q4", "profit", 1200),
    ]
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerows(ops_rows)

    # ---- 干扰文件 ----
    # 备份账本（内容不同，不应被使用）
    backup_rows = [
        ("2024-Q1", "revenue", 9999),
        ("2024-Q1", "cost", 9999),
        ("2024-Q1", "profit", 9999),
    ]
    with open("data/ledgers/archive/backup_customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerows(backup_rows)

    # 其他干扰文件
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("ops/notes.txt", "w") as f:
        f.write("some random note\n")

if __name__ == "__main__":
    build_env()
