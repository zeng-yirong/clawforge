import os
import csv
import random
import json

def build_env():
    # 创建目录
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # 创建干扰文件
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump({
            "accounts": [
                {"account_id": "a001", "display_name": "Alice", "department": "ML", "email": "alice@co.io", "permissions": ["read", "write"]},
                {"account_id": "a002", "display_name": "Bob", "department": "Infra", "email": "bob@co.io", "permissions": ["read"]}
            ]
        }, f)
    with open("data/contacts.json", "w") as f:
        json.dump({
            "contacts": [
                {"contact_id": "c001", "name": "Charlie", "role": "researcher", "email": "charlie@co.io"},
                {"contact_id": "c002", "name": "Diana", "role": "engineer", "email": "diana@co.io"}
            ]
        }, f)

    # 生成实验数据
    # 真实批次 batch_A 和 batch_B，各三个组
    batch_A_data = {
        "group_1": (0.85, 120.0, 0.05),
        "group_2": (0.92, 100.0, 0.04),
        "group_3": (0.78, 150.0, 0.06)
    }
    batch_B_data = {
        "group_1": (0.88, 115.0, 0.055),
        "group_2": (0.91, 102.0, 0.042),
        "group_3": (0.82, 140.0, 0.058)
    }
    # 干扰批次
    batch_C_data = {
        "group_1": (0.75, 130.0, 0.07),
        "group_2": (0.89, 110.0, 0.045),
        "group_4": (0.80, 125.0, 0.06)
    }
    batch_D_data = {
        "group_1": (0.90, 105.0, 0.048),
        "group_2": (0.87, 118.0, 0.052),
        "group_3": (0.79, 145.0, 0.065)
    }

    rows = []
    # 注释行
    rows.append("# This is a comment line, ignore it")
    # 空行（用空字符串表示）
    rows.append("")
    # 合法数据
    def add_batch(batch_id, data):
        for gid, (acc, lat, cost) in data.items():
            rows.append(f"{batch_id},{gid},{acc},{lat},{cost}")
    add_batch("batch_A", batch_A_data)
    add_batch("batch_B", batch_B_data)
    add_batch("batch_C", batch_C_data)
    add_batch("batch_D", batch_D_data)
    # 再添加一条格式错误行（缺少列）
    rows.append("batch_E,group_1,0.91,110.0")
    # 再添加一条重复行（但组内唯一，batch_A 的 group_1 再写一次，干扰）
    rows.append("batch_A,group_1,0.86,121.0,0.051")
    # 最后空行
    rows.append("")

    with open("data/experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(["batch_id","group_id","accuracy","latency_ms","cost_usd"])
        for row in rows:
            if row == "":
                f.write("\n")
            elif row.startswith("#"):
                f.write(row + "\n")
            else:
                f.write(row + "\n")

if __name__ == "__main__":
    build_env()
