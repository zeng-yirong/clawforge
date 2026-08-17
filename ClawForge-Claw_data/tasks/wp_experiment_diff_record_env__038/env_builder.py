import os
import csv
import json

def build_env():
    # 创建所需目录
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 写入 accounts.json（干扰项）
    accounts = [
        {"account_id": "a001", "display_name": "Alice", "department": "R&D", "email": "alice@lab.com", "permissions": ["read"]},
        {"account_id": "a002", "display_name": "Bob", "department": "QA", "email": "bob@lab.com", "permissions": ["read", "write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 写入 contacts.json（干扰项）
    contacts = [
        {"contact_id": "c001", "name": "Charlie", "role": "engineer", "email": "charlie@lab.com"},
        {"contact_id": "c002", "name": "Diana", "role": "data scientist", "email": "diana@lab.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 写入 experiment_results.csv（主数据，包含干扰）
    rows = [
        # 正常数据
        ["exp_v1", "control", "0.85", "120", "0.02"],
        ["exp_v1", "treatment_small", "0.87", "110", "0.03"],
        ["exp_v2", "control", "0.88", "100", "0.025"],
        ["exp_v2", "treatment_small", "0.91", "95", "0.035"],
        ["exp_v2", "treatment_large", "0.93", "90", "0.05"],
        ["exp_v3", "control", "0.89", "105", "0.028"],
        ["exp_v3", "treatment_small", "0.92", "98", "0.038"],
        ["exp_v3", "treatment_large", "0.94", "88", "0.055"],
        ["exp_v4", "control", "0.86", "115", "0.022"],
        ["exp_v4", "treatment_small", "0.90", "105", "0.04"],
        # 重复行（完全一致）
        ["exp_v2", "control", "0.88", "100", "0.025"],
        ["exp_v2", "control", "0.88", "100", "0.025"],
        ["exp_v3", "treatment_small", "0.92", "98", "0.038"],
        # 格式错误行（latency_ms 为字符串）
        ["exp_v2", "treatment_large", "0.93", "ninety", "0.05"],
        # 无关批次
        ["exp_v5", "treatment", "0.9", "80", "0.01"],
        # 其他干扰
        ["exp_v3", "control", "0.89", "105", "0.028"],  # 重复
    ]
    with open("data/experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        writer.writerows(rows)

if __name__ == "__main__":
    build_env()
