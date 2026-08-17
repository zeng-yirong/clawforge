import os
import csv
import json
import random

def build_env():
    # 创建数据目录
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 只建目录，不建结果文件
    # 干扰目录
    os.makedirs("backup", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # --- experiment_results.csv ---
    groups = ["ctrl", "variant_a", "variant_b", "feature_x"]
    # 批次 alpha (baseline)
    alpha_data = {
        "ctrl":     (0.874, 45.2, 0.012),
        "variant_a": (0.891, 42.7, 0.015),
        "variant_b": (0.865, 48.1, 0.010),
        "feature_x": (0.903, 38.4, 0.018),
    }
    # 批次 beta (new)
    beta_data = {
        "ctrl":     (0.881, 44.8, 0.011),
        "variant_a": (0.895, 40.2, 0.017),
        "variant_b": (0.862, 49.0, 0.009),
        "feature_x": (0.910, 36.7, 0.020),
    }
    # 干扰批次 gamma (不应被使用)
    gamma_data = {
        "ctrl":     (0.870, 45.5, 0.013),
        "variant_a": (0.888, 43.0, 0.014),
    }

    with open("data/experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        for batch, data in [("batch_alpha", alpha_data), ("batch_beta", beta_data), ("batch_gamma", gamma_data)]:
            for gid, (acc, lat, cost) in data.items():
                writer.writerow([batch, gid, acc, lat, cost])
        # 加入脏数据行：空行、列数错误、非数字
        writer.writerow(["batch_alpha", "broken", "n/a", 45.0, 0.01])  # accuracy 非数字
        writer.writerow(["batch_beta", "extra", 0.9, 44.0])            # 缺少一列
        writer.writerow([])                                              # 空行

    # --- 干扰文件 ---
    # 无关的 accounts.json
    accounts = [
        {"account_id": "a1", "display_name": "Alice", "department": "eng", "email": "a@example.com", "permissions": ["read"]},
        {"account_id": "a2", "display_name": "Bob", "department": "ops", "email": "b@example.com", "permissions": ["read", "write"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # 旧版 CSV（诱饵）
    with open("backup/experiment_results_old.csv", "w") as f:
        f.write("batch_id,group_id,accuracy\nbatch_alpha,ctrl,0.87\n")  # 格式不同

    # 日志文件（无意义）
    with open("logs/system.log", "w") as f:
        f.write("INFO: experiment completed at 2025-04-01 02:00\n")

if __name__ == "__main__":
    build_env()
