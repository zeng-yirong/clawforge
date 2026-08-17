import os
import csv
import json
import random

def build_env():
    # 创建目录
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，留给 agent 写结果

    # 主体：experiment_results.csv
    rows = []
    # 批次 A 和 B 的目标 group 数据
    # group1: acc差+0.07, lat差-5, cost差+0.05 -> 仅 accuracy 超过
    # group2: acc差-0.01, lat差-11, cost差+0.05 -> 仅 latency 超过
    # group3: acc差+0.06, lat差-9, cost差+0.15 -> accuracy 和 cost 超过
    # group4: acc差-0.01, lat差-2, cost差+0.01 -> 无超过
    # group5: acc差+0.01, lat差-5, cost差+0.05 -> 无超过
    batch_a = [
        ("batch_A", 1, 0.85, 100, 0.50),
        ("batch_A", 2, 0.90, 80, 0.30),
        ("batch_A", 3, 0.70, 120, 0.60),
        ("batch_A", 4, 0.95, 60, 0.20),
        ("batch_A", 5, 0.80, 90, 0.40),
    ]
    batch_b = [
        ("batch_B", 1, 0.92, 95, 0.55),
        ("batch_B", 2, 0.89, 69, 0.35),  # lat diff = -11
        ("batch_B", 3, 0.76, 111, 0.75), # acc diff +0.06, cost diff +0.15
        ("batch_B", 4, 0.94, 58, 0.21),  # 无显著变化
        ("batch_B", 5, 0.81, 85, 0.45),  # 无显著变化
    ]
    rows.extend(batch_a)
    rows.extend(batch_b)

    # 干扰批次 batch_C (只出现一次)
    rows.append(("batch_C", 1, 0.88, 102, 0.45))
    rows.append(("batch_C", 2, 0.91, 77, 0.32))

    # 只在一个批次出现的 group (诱饵)
    rows.append(("batch_A", 6, 0.78, 130, 0.55))   # 只在 A
    rows.append(("batch_B", 7, 0.82, 95, 0.42))    # 只在 B

    # 重复行（完全重复，不影响唯一结果）
    rows.append(("batch_A", 1, 0.85, 100, 0.50))

    # 缺失值行（干扰）
    rows.append(("batch_A", 8, None, 110, 0.48))    # accuracy 缺失
    rows.append(("batch_B", 8, 0.87, None, 0.50))   # latency 缺失

    # 写 CSV
    with open("data/experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        for row in rows:
            writer.writerow(row)

    # 干扰文件：accounts.json, contacts.json (为了更像真实环境)
    accounts = [
        {"account_id": "acc1", "display_name": "Alice", "department": "R&D", "email": "alice@example.com", "permissions": ["read"]},
        {"account_id": "acc2", "display_name": "Bob", "department": "Eng", "email": "bob@example.com", "permissions": ["write"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    contacts = [
        {"contact_id": "c1", "name": "Carol", "role": "PM", "email": "carol@example.com"},
        {"contact_id": "c2", "name": "Dave", "role": "QA", "email": "dave@example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

if __name__ == "__main__":
    build_env()
