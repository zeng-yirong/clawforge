import os
import csv

def build_env():
    # 确保工作区干净
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # 干扰项 - 旧版本账本
    os.makedirs("raw_data/archive", exist_ok=True)
    with open("raw_data/archive/old_customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period","metric_code","metric_value"])
        writer.writerow(["2024-Q4","revenue","390000"])
        writer.writerow(["2024-Q4","active_users","4800"])
        writer.writerow(["2024-Q3","revenue","370000"])

    # 干扰项 - 临时文件
    with open("raw_data/temp_draft.txt", "w") as f:
        f.write("这是一份草稿，不是正式账本\n")

    # 客户账本
    with open("raw_data/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period","metric_code","metric_value"])
        writer.writerow(["2025-Q1","revenue","420000"])
        writer.writerow(["2025-Q2","revenue","450000"])       # 目标
        writer.writerow(["2025-Q3","revenue","480000"])
        writer.writerow(["2025-Q2","active_users","5200"])    # 干扰
        writer.writerow(["2025-Q2","churn_rate","3.5"])       # 干扰

    # 产品账本
    with open("raw_data/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period","metric_code","metric_value"])
        writer.writerow(["2025-Q1","revenue","350000"])
        writer.writerow(["2025-Q2","revenue","380000"])       # 目标
        writer.writerow(["2025-Q3","revenue","410000"])
        writer.writerow(["2025-Q2","units_sold","19000"])     # 干扰

    # 运营账本
    with open("raw_data/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period","metric_code","metric_value"])
        writer.writerow(["2025-Q1","cost","88000"])
        writer.writerow(["2025-Q2","cost","95000"])           # 目标
        writer.writerow(["2025-Q3","cost","102000"])
        writer.writerow(["2025-Q2","uptime_percent","99.8"])  # 干扰

    # 额外干扰 - 非账本 CSV（不同表头）
    with open("raw_data/employee_list.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name","department"])
        writer.writerow(["Alice","Engineering"])

    print("环境构建完成，初始文件树已就绪。")

if __name__ == "__main__":
    build_env()
