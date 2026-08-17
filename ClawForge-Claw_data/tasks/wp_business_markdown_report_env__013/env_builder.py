import os
import csv

def build_env():
    # 创建目录结构
    dirs = [
        "data/ledgers",
        "data",
        "old_reports",
        "reports"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    # ========= 干扰文件 =========
    # accounts.json (无用)
    with open("data/accounts.json", "w") as f:
        f.write('{"accounts": []}')
    # contacts.json (无用)
    with open("data/contacts.json", "w") as f:
        f.write('{"contacts": []}')
    # old_reports 里的旧报告
    with open("old_reports/2023_q4.md", "w") as f:
        f.write("# Old report\nNothing useful here.")
    
    # ========= 主分类账 =========
    # 1. customer_ledger.csv
    customer_rows = [
        ["period", "metric_code", "metric_value"],
        ["2024-Q1", "revenue", "15000"],
        ["2024-Q1", "cost", "8000"],
        # 干扰：非当季
        ["2024-Q2", "revenue", "12000"],
        # 干扰：数值非法
        ["2024-Q1", "revenue", "missing"],
        # 干扰：metric_code 拼写错误 (应忽略)
        ["2024-Q1", "revnue", "6000"],
        # 干扰：重复行 (不同值，但应视为正确数据？我们故意让此行为有效但重复？实际上我们期望只取有效行，
        # 但为了避免歧义，我们让重复行metric_code错误，所以忽略)
        # 再增加一个有效行？不行，会使结果不唯一。所以只保留上面两条有效行。
        # 明确：只有 period=2024-Q1, metric_code in (revenue,cost) 且 value 数字才有效。
        # 所以有效行只有 revenue=15000, cost=8000。
    ]
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(customer_rows)
    
    # 2. ops_ledger.csv
    ops_rows = [
        ["period", "metric_code", "metric_value"],
        ["2024-Q1", "revenue", "5000"],
        ["2024-Q1", "cost", "3000"],
        # 干扰：数值带空格（应可转数字）
        ["2024-Q1", "cost", " 3000 "],
        # 干扰：period 带前缀
        ["period_2024-Q1", "revenue", "2000"],
        # 干扰：空行？（csv自动忽略）
    ]
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(ops_rows)
    
    # 3. product_ledger.csv
    product_rows = [
        ["period", "metric_code", "metric_value"],
        ["2024-Q1", "revenue", "20000"],
        ["2024-Q1", "cost", "12000"],
        # 干扰：period 为 total
        ["total", "revenue", "50000"],
        # 干扰：metric_code 错误
        ["2024-Q1", "profit", "8000"],
    ]
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(product_rows)
    
    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
