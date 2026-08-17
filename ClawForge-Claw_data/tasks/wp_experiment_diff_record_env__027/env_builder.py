import os
import csv
import random

def build_env():
    # --- 1. 目录结构 ---
    os.makedirs("experiments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # --- 2. 干扰文件 ---
    # 备份CSV（列名不同，不应使用）
    with open("experiments/experiment_results_backup.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["batch", "grp", "acc", "lat", "cst"])
        w.writerow(["batch_001", "A", 0.95, 120, 0.50])
        w.writerow(["batch_002", "B", 0.90, 140, 0.58])

    # 旧版CSV（列数少，不应使用）
    with open("experiments/old_results.csv", "w", newline="") as f:
        f.write("batch_id,score\nbatch_001,0.88\nbatch_002,0.91\n")

    # 无关目录 data/accounts.json
    import json
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [{"account_id":"admin","department":"ops"}]}, f)

    # 空日志目录
    open("logs/.gitkeep", "w").close()

    # --- 3. 主CSV（含异常行，需要清洗） ---
    rows = [
        # 标准行
        ["batch_001","A",0.95,120,0.50],
        ["batch_001","B",0.88,150,0.60],
        ["batch_001","C",0.92,130,0.55],
        ["batch_002","A",0.96,110,0.48],
        ["batch_002","B",0.90,140,0.58],
        ["batch_002","C",0.93,125,0.52],
        ["batch_003","A",0.94,130,0.55],
        ["batch_003","B",0.87,160,0.65],
        ["batch_003","C",0.91,140,0.60],
        ["batch_004","A",0.97,105,0.45],
        ["batch_004","B",0.89,145,0.62],
        ["batch_004","C",0.94,115,0.50],
        ["batch_005","A",0.93,135,0.58],
        ["batch_005","B",0.86,170,0.70],
        ["batch_005","C",0.90,150,0.65],
    ]
    # 插入干扰行
    rows.insert(3, [])                     # 空行
    rows.insert(7, "# this is a comment")  # 非CSV行
    rows.insert(12, ["batch_002","D"])     # 列数不足
    rows.insert(16, ["batch_003","A",0.94])# 缺失两列

    with open("experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["batch_id","group_id","accuracy","latency_ms","cost_usd"])
        for r in rows:
            if isinstance(r, list) and len(r) == 5:
                writer.writerow(r)
            else:
                # 异常行直接写入原样（会变成一行普通字符串，csv自动处理）
                if isinstance(r, str):
                    f.write(r + "\n")
                elif isinstance(r, list) and len(r) == 0:
                    f.write("\n")
                else:
                    # 列数不足的情况，直接用逗号分隔（但会缺少列）
                    f.write(",".join(str(x) for x in r) + "\n")

if __name__ == "__main__":
    build_env()
