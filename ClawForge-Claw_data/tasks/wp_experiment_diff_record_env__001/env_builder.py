import os
import csv
import json

def build_env():
    # 创建实验数据目录
    os.makedirs("experiments", exist_ok=True)
    os.makedirs("reports", exist_ok=True)  # 空目录，让agent去填
    os.makedirs("old_reports", exist_ok=True)  # 干扰目录

    # ---- 关键数据：batch_v1.csv ----
    v1_rows = [
        ["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"],
        ["batch_v1", "group_a", 0.85, 100, 10.0],
        ["batch_v1", "group_b", 0.90, 120, 12.0],
        ["batch_v1", "group_c", 0.86, 110, 11.0],
    ]
    with open("experiments/batch_v1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(v1_rows)

    # ---- 关键数据：batch_v2.csv ----
    v2_rows = [
        ["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"],
        ["batch_v2", "group_a", 0.88, 95, 11.0],
        ["batch_v2", "group_b", 0.91, 115, 13.0],
        ["batch_v2", "group_c", 0.88, 105, 12.0],
    ]
    with open("experiments/batch_v2.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(v2_rows)

    # ---- 干扰：其他批次数据 ----
    noise_rows = [
        ["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"],
        ["batch_v0", "group_x", 0.80, 130, 9.5],
        ["batch_v0", "group_y", 0.82, 140, 10.5],
        ["batch_v3", "group_m", 0.92, 80, 14.0],
        ["batch_v3", "group_n", 0.89, 90, 13.0],
    ]
    with open("experiments/extra_batches.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(noise_rows)

    # ---- 干扰：旧版本的差异报告 ----
    old_diff = {
        "batch_1": "batch_v0",
        "batch_2": "batch_v3",
        "metrics_diff": {"accuracy": 0.095, "latency_ms": -40.0, "cost_usd": 3.5}
    }
    with open("old_reports/diff_old.json", "w") as f:
        json.dump(old_diff, f)

    # ---- 干扰：accounts.json ----
    accounts = {
        "accounts": [
            {"account_id": "acc1", "display_name": "Alice", "department": "ML", "email": "alice@co.io", "permissions": ["read"]},
            {"account_id": "acc2", "display_name": "Bob", "department": "Platform", "email": "bob@co.io", "permissions": ["read","write"]}
        ]
    }
    with open("accounts.json", "w") as f:
        json.dump(accounts, f)

    # ---- 干扰：contacts.json ----
    contacts = {
        "contacts": [
            {"contact_id": "c1", "name": "Charlie", "role": "Engineer", "email": "charlie@co.io"},
            {"contact_id": "c2", "name": "Diana", "role": "PM", "email": "diana@co.io"}
        ]
    }
    with open("contacts.json", "w") as f:
        json.dump(contacts, f)

    # ---- 干扰：一个无关的文本文件 ----
    with open("README.txt", "w") as f:
        f.write("This directory holds experiment data and reports.\n")

if __name__ == "__main__":
    build_env()
