import os
import csv
import random

def build_env():
    # 创建目录结构
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    # 干扰文件：旧版实验结果（格式相同但数值不同）
    old_rows = [
        ["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"],
        ["A", "g_old1", "0.80", "105", "0.48"],
        ["A", "g_old2", "0.83", "115", "0.55"],
        ["B", "g_old3", "0.87", "95", "0.42"],
    ]
    with open("data/experiments/old_experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(old_rows)
    
    # 干扰文件：无关笔记
    with open("docs/notes.txt", "w") as f:
        f.write("实验配置备忘：A/B 测试使用相同模型，仅采样率不同。\n")
    
    # 主实验数据，包含一些脏数据行
    rows = [
        ["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"],
        ["A", "g1", "0.85", "100", "0.5"],
        ["A", "g2", "0.9", "120", "0.6"],
        ["A", "g_dirty", "invalid", "110", "0.55"],   # accuracy 非数值
        ["B", "g3", "0.88", "90", "0.45"],
        ["B", "g4", "0.92", "80", "0.4"],
        ["B", "g5", "0.95", "70", "0.35"],
        ["B", "g_dirty2", "0.9", "", "0.42"],        # latency_ms 缺失
    ]
    with open("data/experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    # 额外干扰：accounts.json（无关数据）
    accounts = [
        {"account_id": "a1", "display_name": "Alice", "department": "ML", "email": "alice@co.io", "permissions": ["read"]},
        {"account_id": "a2", "display_name": "Bob", "department": "Infra", "email": "bob@co.io", "permissions": ["read", "write"]},
    ]
    with open("data/accounts.json", "w") as f:
        import json
        json.dump({"accounts": accounts}, f)

if __name__ == "__main__":
    build_env()
