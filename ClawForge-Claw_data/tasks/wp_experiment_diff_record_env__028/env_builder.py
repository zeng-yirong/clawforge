import os
import csv
import json

def build_env():
    # 创建实验数据目录
    os.makedirs("data/experiments", exist_ok=True)
    
    # 包含脏数据的CSV
    rows = [
        # 正常数据
        ["batch_001", "A", "0.80", "100", "0.10"],
        ["batch_001", "B", "0.75", "150", "0.15"],
        ["batch_001", "C", "0.90", "80",  "0.05"],
        # 脏数据：accuracy > 1
        ["batch_001", "D", "1.20", "200", "0.20"],
        # 脏数据：latency 负数
        ["batch_001", "E", "0.70", "-10", "0.08"],
        # batch_002 正常数据
        ["batch_002", "A", "0.87", "95",  "0.12"],
        ["batch_002", "B", "0.76", "145", "0.14"],
        ["batch_002", "C", "0.91", "78",  "0.04"],
        # 脏数据：cost 为空
        ["batch_002", "F", "0.65", "120", ""],
    ]
    csv_path = "data/experiments/experiment_results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        writer.writerows(rows)

    # 干扰文件（业务无关，但存在）
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)

if __name__ == "__main__":
    build_env()
