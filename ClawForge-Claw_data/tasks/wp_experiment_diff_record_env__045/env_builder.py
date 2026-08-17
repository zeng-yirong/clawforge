import os
import csv
import json
import random
import shutil

def build_env():
    # 清理可能残留的目录
    for d in ["data/experiments", "ops"]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    # 创建干净的实验数据 CSV（包含干扰项）
    rows = []
    # 正式批次 batch_001
    groups_001 = {
        "group_a": (0.923, 45.2, 0.35),
        "group_b": (0.887, 52.1, 0.41),
        "group_c": (0.951, 38.7, 0.29),
    }
    for gid, (acc, lat, cost) in groups_001.items():
        rows.append(["batch_001", gid, f"{acc}", f"{lat}", f"{cost}"])

    # 正式批次 batch_002
    groups_002 = {
        "group_a": (0.945, 42.8, 0.38),
        "group_b": (0.902, 49.5, 0.44),
        "group_c": (0.967, 36.2, 0.32),
    }
    for gid, (acc, lat, cost) in groups_002.items():
        rows.append(["batch_002", gid, f"{acc}", f"{lat}", f"{cost}"])

    # 干扰批次 batch_003 (不同组)
    rows.append(["batch_003", "group_x", "0.812", "67.3", "0.55"])
    rows.append(["batch_003", "group_y", "0.778", "71.9", "0.62"])

    # 干扰批次 batch_004 (旧数据)
    rows.append(["batch_004", "group_a", "0.901", "50.0", "0.33"])
    rows.append(["batch_004", "group_b", "0.865", "55.2", "0.39"])

    # 故意插入脏数据行：空行、标题行的偏移、注释
    rows.append(["", "", "", "", ""])                     # 空行
    rows.append(["batch_001", "group_a", "0.923", "45.2", "0.35"])  # 重复行 (期望 agent 去重？但指令没要求去重，可以作为干扰但合理处理)
    rows.append("# this is a comment line")               # 注释行（整行不是有效CSV，会引发解析错误，需要agent跳过）
    rows.append(["batch_002", "group_d", "0.910", "44.0", "0.36"])  # batch_002 多一个组（干扰，但最终答案不需要这个组）

    # 写入 CSV
    csv_path = "data/experiments/experiment_results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        # 不写表头，增加难度
        for row in rows:
            # 如果是注释行，写入字符串自身（会变成一行文本）
            if isinstance(row, str):
                f.write(row + "\n")
            else:
                writer.writerow(row)

    # 创建干扰文件 data/accounts.json (不被使用)
    accounts = [
        {"account_id": "acc_1", "display_name": "Alice", "department": "eng", "email": "a@x.com", "permissions": ["read"]},
        {"account_id": "acc_2", "display_name": "Bob", "department": "eng", "email": "b@x.com", "permissions": ["write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # 创建干扰目录 ops/tmp （空目录）
    os.makedirs("ops/tmp", exist_ok=True)

    # 创建干扰文件 ops/old_diff.json (模拟旧差异)
    fake_diff = {"batch_001_vs_batch_003": {"group_a": {"accuracy_diff": -0.022}}}
    with open("ops/old_diff.json", "w") as f:
        json.dump(fake_diff, f)

    # 创建干扰数据 data/experiments/old_results.csv
    old_rows = [["batch_000", "group_a", "0.850", "60.0", "0.50"]]
    with open("data/experiments/old_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_rows)

    # 确保 ops 目录存在（已创建）
    pass

if __name__ == "__main__":
    build_env()
