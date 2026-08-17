import os
import csv
import json
import random

def build_env():
    # 创建数据目录
    os.makedirs("data/experiments", exist_ok=True)
    # 创建干扰目录
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 写入实验数据 CSV（包含干扰行、脏数据）
    csv_path = "data/experiments/experiment_results.csv"
    header = ["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"]
    rows = [
        # 目标批次有效行
        ["batch_2024Q1", "alpha", "0.95", "120.0", "0.05"],
        ["batch_2024Q1", "beta",  "0.88", "150.0", "0.08"],
        ["batch_2024Q1", "gamma", "0.92", "110.0", "0.06"],
        ["batch_2024Q2", "alpha", "0.97", "100.0", "0.04"],
        ["batch_2024Q2", "beta",  "0.85", "160.0", "0.09"],
        ["batch_2024Q2", "gamma", "0.93", "105.0", "0.055"],
        # 干扰批次
        ["batch_2023Q4", "alpha", "0.91", "130.0", "0.07"],
        ["batch_2023Q4", "beta",  "0.86", "145.0", "0.085"],
        ["batch_2023Q4", "gamma", "0.89", "115.0", "0.065"],
        # 脏数据：缺失关键字段
        ["batch_2024Q1", "alpha", "",     "120.0", "0.05"],
        ["batch_2024Q1", "beta",  "0.88", "",      "0.08"],
        ["batch_2024Q2", "gamma", "0.93", "105.0", ""],
        # 脏数据：非数值
        ["batch_2024Q1", "gamma", "null", "110.0", "0.06"],
        ["batch_2024Q2", "alpha", "0.97", "abc",   "0.04"],
        # 重复 group 但带错误值（确保每个 group 仅一行有效）
        ["batch_2024Q1", "alpha", "0.95", "120.0", "0.05"],  # 重复行，但无缺失
        # 但上面重复行与有效行完全一致，导致两个有效行？ 需要避免，改为一个有效行：
        # 重新设计：将上面的重复行改为无效（缺失一个字段）
    ]
    # 修正：上面第3行重复有效，需要去掉，改为无效行
    rows = [r for r in rows if not (r[0]=="batch_2024Q1" and r[1]=="alpha" and r[2]=="0.95" and r[3]=="120.0" and r[4]=="0.05")]
    # 注意上面循环删除了有效行本身？ 不，我们保留第一个有效行，删掉重复的那一行（最后一个元素）
    # 实际上 rows 里第一个 batch_2024Q1,alpha 是有效行，最后一个重复行也是有效，我们需要保留一个。
    # 简单做法：重新构建 rows：
    rows = [
        # 目标批次有效行
        ["batch_2024Q1", "alpha", "0.95", "120.0", "0.05"],
        ["batch_2024Q1", "beta",  "0.88", "150.0", "0.08"],
        ["batch_2024Q1", "gamma", "0.92", "110.0", "0.06"],
        ["batch_2024Q2", "alpha", "0.97", "100.0", "0.04"],
        ["batch_2024Q2", "beta",  "0.85", "160.0", "0.09"],
        ["batch_2024Q2", "gamma", "0.93", "105.0", "0.055"],
        # 干扰批次
        ["batch_2023Q4", "alpha", "0.91", "130.0", "0.07"],
        ["batch_2023Q4", "beta",  "0.86", "145.0", "0.085"],
        ["batch_2023Q4", "gamma", "0.89", "115.0", "0.065"],
        # 脏数据：缺失字段
        ["batch_2024Q1", "alpha", "",     "120.0", "0.05"],
        ["batch_2024Q1", "beta",  "0.88", "",      "0.08"],
        ["batch_2024Q2", "gamma", "0.93", "105.0", ""],
        # 脏数据：非数值
        ["batch_2024Q1", "gamma", "null", "110.0", "0.06"],
        ["batch_2024Q2", "alpha", "0.97", "abc",   "0.04"],
        # 重复 group 但带缺失字段（避免多个有效行）
        ["batch_2024Q1", "alpha", "0.95", "",      "0.05"],  # latency 缺失
        ["batch_2024Q2", "beta",  "",     "160.0", "0.09"],  # accuracy 缺失
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    # 创建干扰数据文件
    accounts = [
        {"account_id": "acc01", "display_name": "Alice", "department": "Engineering", "email": "alice@corp.com", "permissions": ["read", "write"]},
        {"account_id": "acc02", "display_name": "Bob", "department": "Marketing", "email": "bob@corp.com", "permissions": ["read"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts, "wrapper": "accounts", "key": "account_id"}, f)

    contacts = [
        {"contact_id": "c01", "name": "Charlie", "role": "Engineer", "email": "charlie@corp.com"},
        {"contact_id": "c02", "name": "Diana", "role": "Manager", "email": "diana@corp.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts, "wrapper": "contacts", "key": "contact_id"}, f)

    # 创建一个空的备份目录和日志文件（无明显作用）
    os.makedirs("logs/old", exist_ok=True)
    with open("logs/run.log", "w") as f:
        f.write("Experiment run completed at 2025-01-15\n")

if __name__ == "__main__":
    build_env()
