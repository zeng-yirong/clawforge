import os
import csv
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data/experiments/archive", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 定义真实数据：两个批次，每组多行测试记录
    # 批次1: batch_001, 批次2: batch_002
    # 组: control, variant_a, variant_b
    # 每个组有 3~5 条记录
    real_data = [
        # batch_001
        {"batch_id": "batch_001", "group_id": "control", "accuracy": 0.85, "latency_ms": 120.0, "cost_usd": 0.012},
        {"batch_id": "batch_001", "group_id": "control", "accuracy": 0.87, "latency_ms": 115.0, "cost_usd": 0.011},
        {"batch_id": "batch_001", "group_id": "control", "accuracy": 0.86, "latency_ms": 118.0, "cost_usd": 0.013},
        {"batch_id": "batch_001", "group_id": "control", "accuracy": 0.84, "latency_ms": 122.0, "cost_usd": 0.012},
        {"batch_id": "batch_001", "group_id": "variant_a", "accuracy": 0.91, "latency_ms": 95.0, "cost_usd": 0.015},
        {"batch_id": "batch_001", "group_id": "variant_a", "accuracy": 0.93, "latency_ms": 90.0, "cost_usd": 0.014},
        {"batch_id": "batch_001", "group_id": "variant_a", "accuracy": 0.92, "latency_ms": 92.0, "cost_usd": 0.016},
        {"batch_id": "batch_001", "group_id": "variant_b", "accuracy": 0.78, "latency_ms": 150.0, "cost_usd": 0.010},
        {"batch_id": "batch_001", "group_id": "variant_b", "accuracy": 0.80, "latency_ms": 145.0, "cost_usd": 0.009},
        {"batch_id": "batch_001", "group_id": "variant_b", "accuracy": 0.79, "latency_ms": 148.0, "cost_usd": 0.011},
        # batch_002
        {"batch_id": "batch_002", "group_id": "control", "accuracy": 0.88, "latency_ms": 105.0, "cost_usd": 0.010},
        {"batch_id": "batch_002", "group_id": "control", "accuracy": 0.89, "latency_ms": 108.0, "cost_usd": 0.009},
        {"batch_id": "batch_002", "group_id": "control", "accuracy": 0.87, "latency_ms": 110.0, "cost_usd": 0.011},
        {"batch_id": "batch_002", "group_id": "variant_a", "accuracy": 0.94, "latency_ms": 82.0, "cost_usd": 0.013},
        {"batch_id": "batch_002", "group_id": "variant_a", "accuracy": 0.95, "latency_ms": 80.0, "cost_usd": 0.012},
        {"batch_id": "batch_002", "group_id": "variant_a", "accuracy": 0.96, "latency_ms": 85.0, "cost_usd": 0.014},
        {"batch_id": "batch_002", "group_id": "variant_a", "accuracy": 0.93, "latency_ms": 84.0, "cost_usd": 0.013},
        {"batch_id": "batch_002", "group_id": "variant_b", "accuracy": 0.82, "latency_ms": 130.0, "cost_usd": 0.008},
        {"batch_id": "batch_002", "group_id": "variant_b", "accuracy": 0.83, "latency_ms": 128.0, "cost_usd": 0.009},
        {"batch_id": "batch_002", "group_id": "variant_b", "accuracy": 0.81, "latency_ms": 132.0, "cost_usd": 0.007},
    ]

    # 干扰数据：无效记录（accuracy>1或<0, latency<0等），以及旧批次副本
    noisy_data = [
        {"batch_id": "batch_001", "group_id": "control", "accuracy": 1.5, "latency_ms": 100.0, "cost_usd": 0.02},  # accuracy > 1
        {"batch_id": "batch_002", "group_id": "variant_a", "accuracy": -0.1, "latency_ms": 90.0, "cost_usd": 0.015}, # accuracy < 0
        {"batch_id": "batch_001", "group_id": "variant_b", "accuracy": 0.77, "latency_ms": -10.0, "cost_usd": 0.01},  # latency negative
        {"batch_id": "batch_002", "group_id": "control", "accuracy": 0.9, "latency_ms": 0.0, "cost_usd": 0.005},     # latency 0 (视为无效)
        {"batch_id": "batch_001", "group_id": "control", "accuracy": 0.86, "latency_ms": 120.0, "cost_usd": 0.012}, # duplicate row (but not exactly same values? Actually duplicate record is acceptable if it's a real test, but we'll keep it for noise)
        {"batch_id": "batch_001", "group_id": "control", "accuracy": 0.86, "latency_ms": 120.0, "cost_usd": 0.012}, # exactly duplicate
        {"batch_id": "batch_900", "group_id": "group_x", "accuracy": 0.7, "latency_ms": 200.0, "cost_usd": 0.02},   # different batch (should be ignored)
    ]

    # 写入主文件：包含真实数据和干扰数据，随机混合
    all_rows = real_data + noisy_data
    random.shuffle(all_rows)

    main_csv_path = "data/experiments/experiment_results.csv"
    with open(main_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        writer.writeheader()
        writer.writerows(all_rows)

    # 创建干扰文件：旧版本（只有一部分数据）
    old_csv_path = "data/experiments/archive/experiment_results_old.csv"
    old_rows = [
        {"batch_id": "batch_000", "group_id": "control", "accuracy": 0.80, "latency_ms": 130.0, "cost_usd": 0.015},
        {"batch_id": "batch_000", "group_id": "variant_a", "accuracy": 0.88, "latency_ms": 100.0, "cost_usd": 0.018},
    ]
    with open(old_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"])
        writer.writeheader()
        writer.writerows(old_rows)

    # 创建备份文件（缺少字段）
    backup_csv_path = "data/experiments/experiment_results_backup.csv"
    with open(backup_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id", "group_id", "accuracy"])  # 缺少 latency, cost
        writer.writerow(["batch_001", "control", 0.85])

    # 创建空目录作为干扰
    os.makedirs("data/experiments/empty_dir", exist_ok=True)

    # 计算预期答案（用于后续验证不泄露，但这里只铺环境）
    # 注意：我们后续 verify 脚本会重新计算，这里不写答案文件
    print("Env built successfully.")
