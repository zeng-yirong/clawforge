import csv
import os

def build_env():
    # Create experiment data directory
    os.makedirs("experiments", exist_ok=True)
    
    # Define batches and groups with metrics
    rows = [
        ["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"],
        # batch_20250301
        ["batch_20250301", "control",    "0.80", "100.0", "0.10"],
        ["batch_20250301", "variant_a",  "0.85", "120.0", "0.15"],
        ["batch_20250301", "variant_b",  "0.90", "110.0", "0.12"],
        # batch_20250315
        ["batch_20250315", "control",    "0.82", "102.0", "0.11"],
        ["batch_20250315", "variant_a",  "0.88", "130.0", "0.16"],
        ["batch_20250315", "variant_b",  "0.95", "115.0", "0.13"],
        # --- 干扰脏数据 ---
        # 空行（实际是跳过）
        [],
        # 缺失字段的行（少一个值）
        ["batch_20250301", "control", "0.80", "100.0"],
        # 无效 batch_id（不属于这两个批次）
        ["batch_20250201", "control", "0.75", "95.0", "0.09"],
        # 重复行（与上面某行相同，但保留）
        ["batch_20250315", "variant_b", "0.95", "115.0", "0.13"],
        # 非数值字段的行
        ["batch_20250301", "variant_a", "high", "120.0", "0.15"],
    ]
    
    with open("experiments/batch_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            if row:  # 跳过空行
                writer.writerow(row)

if __name__ == "__main__":
    build_env()
