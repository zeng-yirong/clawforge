import os
import csv
import json

def build_env():
    # 创建 ops 输出目录
    os.makedirs("ops", exist_ok=True)

    # 创建 data/experiments 目录并写入实验数据
    os.makedirs("data/experiments", exist_ok=True)
    with open("data/experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        # 主批次 batch_001
        writer.writerow(["batch_001", "group_A", 0.95, 120.0, 0.05])
        writer.writerow(["batch_001", "group_B", 0.88, 150.0, 0.07])
        writer.writerow(["batch_001", "group_C", 0.91, 110.0, 0.06])
        # 主批次 batch_002
        writer.writerow(["batch_002", "group_A", 0.97, 115.0, 0.04])
        writer.writerow(["batch_002", "group_B", 0.85, 155.0, 0.08])
        writer.writerow(["batch_002", "group_C", 0.93, 105.0, 0.055])
        # 干扰批次 batch_003（不参与比较）
        writer.writerow(["batch_003", "group_A", 0.90, 130.0, 0.06])
        writer.writerow(["batch_003", "group_D", 0.92, 125.0, 0.065])
        # 重复行（干扰，应被忽略或去重？但为了简化，直接保留，agent 需要知道只取一次）
        writer.writerow(["batch_001", "group_A", 0.95, 120.0, 0.05])

    # 创建干扰的数据文件
    os.makedirs("data", exist_ok=True)
    accounts = [
        {"account_id": "acc001", "display_name": "Alice", "department": "Engineering", "email": "alice@ex.com", "permissions": ["read", "write"]},
        {"account_id": "acc002", "display_name": "Bob", "department": "Product", "email": "bob@ex.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    contacts = [
        {"contact_id": "c001", "name": "Charlie", "role": "Manager", "email": "charlie@ex.com"},
        {"contact_id": "c002", "name": "Diana", "role": "Engineer", "email": "diana@ex.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

if __name__ == "__main__":
    build_env()
