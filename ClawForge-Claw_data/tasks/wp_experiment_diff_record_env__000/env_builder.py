import os

def build_env():
    os.makedirs("data/experiments", exist_ok=True)
    # 主数据文件（含干扰项、脏数据）
    csv_content = (
        "batch_id,group_id,accuracy,latency_ms,cost_usd\n"
        "\"batch_001\",\"control\",0.85,120,0.50\n"
        "\"batch_001\",\"treatment\",0.91,100,0.70\n"
        "\"batch_002\",\"control\",0.87,110,0.45\n"
        "\"batch_002\",\"treatment\",0.93,85,0.65\n"
        "\"batch_003\",\"control\",0.80,130,0.55\n"
        "batch_001,control,0.85,120\n"              # 缺少 cost 列（脏数据）
        "batch_004,test,0.90,105,x\n"               # cost 列非数字（脏数据）
    )
    with open("data/experiments/experiment_results.csv", "w") as f:
        f.write(csv_content)

    # 干扰文件：旧数据目录
    os.makedirs("data/experiments/archive", exist_ok=True)
    with open("data/experiments/old_results.csv", "w") as f:
        f.write("batch_id,group_id,accuracy,latency_ms,cost_usd\n")
        f.write("batch_001,control,0.80,130,0.55\n")

    # 无关目录
    os.makedirs("logs", exist_ok=True)
    with open("logs/readme.txt", "w") as f:
        f.write("This is a log directory.\n")
