import os
import csv
import json
import random

random.seed(42)

def build_env():
    # 创建目录
    os.makedirs("experiments", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 留空供 agent 写入

    # 1. 构造实验结果 CSV
    csv_path = "experiments/experiment_results.csv"
    rows = [
        # batch_v1 - 正常数据
        ("batch_v1", "group_a", 0.85, 120, 0.05),
        ("batch_v1", "group_a", 0.86, 125, 0.06),
        ("batch_v1", "group_a", 0.84, 130, 0.05),
        ("batch_v1", "group_b", 0.75, 200, 0.10),
        ("batch_v1", "group_b", 0.76, 210, 0.11),
        ("batch_v1", "group_c", 0.90, 80,  0.03),
        ("batch_v1", "group_c", 0.91, 85,  0.03),
        # batch_v1 - 故意插入的重复行（内容与上面某行完全一致）
        ("batch_v1", "group_a", 0.86, 125, 0.06),
        ("batch_v1", "group_a", 0.86, 125, 0.06),  # 重复两次
        ("batch_v1", "group_b", 0.75, 200, 0.10),
        # batch_v2
        ("batch_v2", "group_a", 0.88, 110, 0.04),
        ("batch_v2", "group_a", 0.89, 115, 0.04),
        ("batch_v2", "group_a", 0.87, 108, 0.05),
        ("batch_v2", "group_b", 0.78, 190, 0.09),
        ("batch_v2", "group_b", 0.79, 195, 0.09),
        ("batch_v2", "group_c", 0.92, 75,  0.02),
        ("batch_v2", "group_c", 0.93, 78,  0.02),
        # 干扰批次 batch_old（格式一致但组不同）
        ("batch_old", "group_d", 0.60, 300, 0.20),
        ("batch_old", "group_e", 0.70, 250, 0.15),
    ]

    # 打乱顺序增加迷惑性
    random.shuffle(rows)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        writer.writerows(rows)

    # 2. 构造干扰 CSV（不同列名，旧格式）
    old_csv = "experiments/old_results.csv"
    old_rows = [
        ["batch", "group", "score", "time_ms", "expense"],
        ["old1", "x", 0.5, 400, 0.3],
        ["old2", "y", 0.6, 350, 0.25],
    ]
    with open(old_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_rows)

    # 3. 构造 accounts.json (干扰项)
    accounts = {
        "accounts": [
            {"account_id": "a001", "display_name": "Alice", "department": "AI", "email": "alice@lab.com", "permissions": ["read", "write"]},
            {"account_id": "a002", "display_name": "Bob", "department": "Ops", "email": "bob@lab.com", "permissions": ["read"]},
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 4. 构造 contacts.json (干扰项)
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Charlie", "role": "researcher", "email": "charlie@lab.com"},
            {"contact_id": "c002", "name": "Diana", "role": "engineer", "email": "diana@lab.com"},
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

if __name__ == "__main__":
    build_env()
