import os
import csv
import json
import random

def build_env():
    base = os.getcwd()
    # 创建目录
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("backup", exist_ok=True)  # 干扰目录

    # 真实的两个批次数据
    batch1_id = "batch_20250301"
    batch2_id = "batch_20250315"

    # 共同组数据 (g1,g2,g3,g4) 和单批次组 (g5只在batch1, g6只在batch2)
    groups = {
        "g1": (0.92, 120.5, 1.23),
        "g2": (0.88, 95.3, 0.98),
        "g3": (0.95, 78.2, 1.45),
        "g4": (0.79, 150.1, 2.01),
    }
    batch1_only = {"g5": (0.85, 110.0, 1.10)}
    batch2_only = {"g6": (0.91, 88.4, 0.76)}

    def write_csv(filename, batch_id, groups_dict):
        filepath = os.path.join("data/experiments", filename)
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
            for gid, (acc, lat, cost) in groups_dict.items():
                writer.writerow([batch_id, gid, acc, lat, cost])

    write_csv("batch_20250301.csv", batch1_id, {**groups, **batch1_only})
    write_csv("batch_20250315.csv", batch2_id, {**groups, **batch2_only})

    # 干扰项：无关文件
    with open("data/experiments/old_batch_20250201.csv", "w") as f:
        f.write("batch_id,group_id,accuracy,latency_ms,cost_usd\na,g1,0.7,200,0.5")
    with open("data/experiments/export_summary.txt", "w") as f:
        f.write("some notes")
    # 干扰项：错误格式的空文件
    with open("data/experiments/empty.csv", "w") as f:
        pass
    # 干扰项：备份目录里也有类似数据
    with open("backup/batch_20250301.csv", "w") as f:
        f.write("batch_id,group_id,accuracy\nv1,g1,0.5")

    # 另外可能存在的 accounts/contacts 数据（不影响任务）
    os.makedirs("data", exist_ok=True)
    json.dump({"accounts": []}, open("data/accounts.json", "w"))
    json.dump({"contacts": []}, open("data/contacts.json", "w"))

if __name__ == "__main__":
    build_env()
