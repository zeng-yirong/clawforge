import os
import csv

def build_env():
    # 创建实验数据目录
    os.makedirs("experiments", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("old_logs", exist_ok=True)

    # 主实验数据 CSV（含干扰批次）
    rows = [
        ["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"],
        # 目标批次 batch_v2
        ["batch_v2", "control", "0.85", "120", "0.50"],
        ["batch_v2", "variant_a", "0.88", "115", "0.55"],
        ["batch_v2", "variant_b", "0.82", "125", "0.45"],
        # 目标批次 batch_v3
        ["batch_v3", "control", "0.89", "110", "0.52"],
        ["batch_v3", "variant_a", "0.92", "105", "0.58"],
        ["batch_v3", "variant_b", "0.86", "115", "0.46"],
        # 干扰历史批次
        ["batch_v1", "control", "0.80", "140", "0.42"],
        ["batch_v1", "variant_a", "0.78", "145", "0.40"],
        ["batch_v1", "variant_b", "0.76", "150", "0.38"],
        ["batch_v4", "control", "0.91", "108", "0.53"],
        ["batch_v4", "variant_a", "0.93", "102", "0.60"],
        ["batch_v4", "variant_b", "0.88", "118", "0.49"],
    ]
    with open("experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # 干扰数据文件
    accounts = [
        {"account_id": "acc_1", "display_name": "Alice", "department": "Engineering", "email": "alice@co.com", "permissions": ["read", "write"]},
    ]
    contacts = [
        {"contact_id": "ct_1", "name": "Bob", "role": "researcher", "email": "bob@co.com"},
    ]
    with open("data/accounts.json", "w") as f:
        import json
        json.dump({"accounts": accounts}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # 旧日志干扰
    with open("old_logs/experiment_v1.csv", "w") as f:
        f.write("batch_v1,0.80,0.78,0.76\n")

if __name__ == "__main__":
    build_env()
