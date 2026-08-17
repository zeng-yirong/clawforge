import os
import csv

def build_env():
    # 创建目录结构
    os.makedirs("data/ledgers", exist_ok=True)
    os.makedirs("cache", exist_ok=True)

    # 客户账本
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024Q3", "c_revenue", 1500])
        writer.writerow(["2024Q3", "c_count", 200])
        writer.writerow(["2024Q3", "c_avg_order", 75.5])
        # 干扰行（旧季度）
        writer.writerow(["2024Q2", "c_revenue", 1000])
        writer.writerow(["2024Q2", "c_count", 180])
        # 空行和注释（用一行备注模拟）
        # 实际csv不会写注释，我们通过额外行模拟干扰
        # 但为了符合csv规范，添加一行备注字段
        writer.writerow(["# This is old data, ignore", "", ""])

    # 运营账本
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024Q3", "o_cost", 800])
        writer.writerow(["2024Q3", "o_latency", 12.5])
        writer.writerow(["2024Q3", "o_uptime", 99.98])
        writer.writerow(["2024Q2", "o_cost", 750])

    # 产品账本
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024Q3", "p_sales", 3000])
        writer.writerow(["2024Q3", "p_units", 500])
        writer.writerow(["2024Q3", "p_returns", 30])
        writer.writerow(["2024Q2", "p_sales", 2800])

    # 干扰文件：备份账本（包含不同数值）
    with open("data/ledgers/ops_ledger_backup.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "metric_code", "metric_value"])
        writer.writerow(["2024Q3", "o_cost", 900])   # 不同值
        writer.writerow(["2024Q3", "o_latency", 11.0])

    # 无关文件
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        f.write('{"account_id": "acc1", "display_name": "Test"}')

if __name__ == "__main__":
    build_env()
