import os
import csv
import json
import random

def build_env():
    # 需要的数据目录
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 目标是让agent创建ops/diff_record.json，但我们先空着

    # 主实验数据
    main_csv = "data/experiments/experiment_results.csv"
    with open(main_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        writer.writerow(["batch_001", "control", "0.8512", "12.3", "0.05"])
        writer.writerow(["batch_001", "variant", "0.9234", "8.7", "0.03"])
        writer.writerow(["batch_002", "control", "0.8321", "11.9", "0.06"])
        writer.writerow(["batch_002", "variant", "0.9456", "9.1", "0.04"])

    # 干扰项1：旧实验结果，包含不同的批次ID和格式混乱
    old_csv = "data/experiments/old_experiment_results.csv"
    with open(old_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["exp_id", "group", "acc", "lat", "cost"])
        writer.writerow(["batch_000", "control", "0.7000", "15.0", "0.10"])
        writer.writerow(["batch_000", "variant", "0.8000", "12.0", "0.08"])
        # 故意加一条和主文件相同的batch_id但不同数值，以迷惑
        writer.writerow(["batch_001", "control", "0.9000", "10.0", "0.02"])

    # 干扰项2：accounts.json（业务骨架数据）
    accounts = {
        "accounts": [
            {"account_id": "1", "display_name": "Alice", "department": "R&D", "email": "alice@corp.com", "permissions": ["read", "write"]},
            {"account_id": "2", "display_name": "Bob", "department": "R&D", "email": "bob@corp.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # 干扰项3：contacts.json
    contacts = {
        "contacts": [
            {"contact_id": "c1", "name": "Charlie", "role": "engineer", "email": "charlie@corp.com"},
            {"contact_id": "c2", "name": "Diana", "role": "manager", "email": "diana@corp.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    # 空ops目录（无初始文件）
    # 但保留目录以便agent写入

if __name__ == "__main__":
    build_env()
