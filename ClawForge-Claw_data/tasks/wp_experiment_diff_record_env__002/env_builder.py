import os
import csv

def build_env():
    # 创建目录结构
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    # 创建干扰文件：无用的 accounts.json
    with open("data/accounts.json", "w") as f:
        f.write('{"accounts": []}')
    # 主要实验数据
    csv_path = "data/experiments/experiment_results.csv"
    rows = [
        # 注释行（脏数据）
        "# 以下是两批实验的准确率记录",
        # 空行
        "",
        "batch_id,group_id,accuracy,latency_ms,cost_usd",
        "batch_001,A,0.80,12.3,0.05",
        "batch_001,B,0.85,15.1,0.06",
        "batch_001,C,0.90,11.8,0.04",
        "batch_001,D,0.70,9.5,0.03",   # D 只出现在 batch_001
        "batch_002,A,0.87,13.0,0.05",
        "batch_002,B,0.88,14.6,0.06",
        "batch_002,C,0.91,12.2,0.04",
        "batch_002,E,0.75,10.1,0.03",   # E 只出现在 batch_002
    ]
    with open(csv_path, "w", newline="") as f:
        for line in rows:
            if line.startswith("#") or line.strip() == "":
                f.write(line + "\n")
            else:
                f.write(line + "\n")
    # 干扰文件：历史备份（诱饵）
    with open("data/experiments/experiment_results_old.csv", "w") as f:
        f.write("batch_id,group_id,accuracy,latency_ms,cost_usd\n")
        f.write("batch_001,A,0.79,12.5,0.05\n")
        f.write("batch_002,A,0.86,13.2,0.05\n")

if __name__ == "__main__":
    build_env()
