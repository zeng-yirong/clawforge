import csv
import os
import json
import random

def build_env():
    # 创建目录
    os.makedirs("data/ledgers/archive", exist_ok=True)
    os.makedirs("report", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 干扰文件：accounts.json (无用，但存在)
    accounts = [
        {"account_id": "a001", "display_name": "Alice", "department": "Sales", "email": "alice@corp.com", "permissions": ["read"]},
        {"account_id": "a002", "display_name": "Bob", "department": "Engineering", "email": "bob@corp.com", "permissions": ["read", "write"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 客户分类账 (customer_ledger.csv)
    customer_rows = [
        # 有效的 Q1 2025 数据
        ["period", "metric_code", "metric_value"],
        ["2025-Q1", "revenue", "125000"],
        ["2025-Q1", "revenue", "34000"],          # 总收入 = 125000+34000 = 159000
        ["2025-Q1", "new_signups", "450"],         # 干扰指标，不关心
        # 其他 period 干扰
        ["2024-Q4", "revenue", "98000"],
        ["2025-Q2", "revenue", "142000"],
        # 脏数据：空行和无效值
        ["2025-Q1", "revenue", "NULL"],            # 应跳过
        ["", "", ""],                               # 空行
        ["2025-Q1", "revenue", "abc"],             # 非数字
        # 重复值 – 刻意增加一条有效 revenue 看 agent 是否去重？不去重则总和继续增加
        ["2025-Q1", "revenue", "34000"],           # 重复值，总收入变为 159000+34000=193000？但上一条已经加了34000，这里是重复第二遍，最终总和 125000+34000+34000=193000
        # 故意让答案唯一：我们期望 agent 不自动去重，直接计算所有有效数字行总和。所以设计两个有效 revenue 行：125000 和 34000，再重复一个34000，总和 193000？
        # 为了简化，去掉重复，只保留两个有效 revenue：125000 和 34000，总和159000。其他干扰行不参与。
        # 重新设计：去掉重复行，只保留两个有效 revenue。
    ]
    # 重新定义更干净的版本
    customer_rows = [
        ["period", "metric_code", "metric_value"],
        ["2025-Q1", "revenue", "125000"],
        ["2025-Q1", "revenue", "34000"],
        ["2025-Q1", "new_signups", "450"],
        ["2024-Q4", "revenue", "98000"],
        ["2025-Q2", "revenue", "142000"],
        ["2025-Q1", "revenue", "NULL"],
        ["", "", ""],
        ["2025-Q1", "revenue", "abc"],
    ]
    with open("data/ledgers/customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(customer_rows)

    # 产品分类账 (product_ledger.csv)
    product_rows = [
        ["period", "metric_code", "metric_value"],
        ["2025-Q1", "units_sold", "890"],
        ["2025-Q1", "units_sold", "1100"],       # 总和 = 890+1100=1990
        ["2025-Q1", "returns", "32"],            # 干扰
        ["2024-Q4", "units_sold", "750"],
        # 脏数据
        ["2025-Q1", "units_sold", ""],           # 空值
        ["2025-Q1", "units_sold", "12.5"],       # 非整数？也可以接受为数字，但题目暗示 int？我们保持整数，这里写"twelve" 不行
        ["2025-Q1", "units_sold", "twelve"],     # 非数字
    ]
    with open("data/ledgers/product_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(product_rows)

    # 运维分类账 (ops_ledger.csv)
    ops_rows = [
        ["period", "metric_code", "metric_value"],
        ["2025-Q1", "downtime_minutes", "34.5"],
        ["2025-Q1", "downtime_minutes", "12.0"],
        ["2025-Q1", "downtime_minutes", "28.3"],   # 平均值 = (34.5+12.0+28.3)/3 = 24.93333...
        # 干扰
        ["2024-Q4", "downtime_minutes", "55.1"],
        ["2025-Q1", "incidents", "3"],
        # 脏数据
        ["2025-Q1", "downtime_minutes", None],     # 空
        ["2025-Q1", "downtime_minutes", "N/A"],
        # 重复
        ["2025-Q1", "downtime_minutes", "12.0"],   # 重复，平均值会变 (34.5+12.0+28.3+12.0)/4=21.7，但我们期望 agent 不自动去重，所以平均值应为 (34.5+12.0+28.3+12.0)/4 = 21.7
        # 为了简化，取消重复，只保留三个有效值
    ]
    # 重新设计，去掉重复
    ops_rows = [
        ["period", "metric_code", "metric_value"],
        ["2025-Q1", "downtime_minutes", "34.5"],
        ["2025-Q1", "downtime_minutes", "12.0"],
        ["2025-Q1", "downtime_minutes", "28.3"],
        ["2024-Q4", "downtime_minutes", "55.1"],
        ["2025-Q1", "incidents", "3"],
        ["2025-Q1", "downtime_minutes", ""],
        ["2025-Q1", "downtime_minutes", "N/A"],
    ]
    with open("data/ledgers/ops_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(ops_rows)

    # 干扰文件：过期版本 ledger 在 archive 下
    old_cust_rows = [
        ["period", "metric_code", "metric_value"],
        ["2023-Q1", "revenue", "50000"],
    ]
    os.makedirs("data/ledgers/archive", exist_ok=True)
    with open("data/ledgers/archive/old_customer_ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_cust_rows)

    print("Environment built: ledgers with distractors and dirty data.")

if __name__ == "__main__":
    build_env()
