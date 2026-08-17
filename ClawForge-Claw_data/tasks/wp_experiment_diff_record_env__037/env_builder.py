import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 预置空目录，agent 后续写入
    os.makedirs("data", exist_ok=True)

    # ===== 核心实验数据 (含脏数据) =====
    csv_lines = [
        "batch_id,group_id,accuracy,latency_ms,cost_usd",
        # 标准行 – batch_001
        "batch_001,group_A,0.95,120,0.05",
        "batch_001,group_B,0.88,150,0.06",
        "batch_001,group_C,0.76,200,0.04",
        "batch_001,group_D,0.93,100,0.03",
        "batch_001,group_E,0.82,180,0.07",
        # 标准行 – batch_002
        "batch_002,group_A,0.90,125,0.06",
        "batch_002,group_B,0.85,155,0.05",
        "batch_002,group_C,0.78,195,0.05",
        "batch_002,group_D,0.89,105,0.04",
        "batch_002,group_E,0.81,178,0.08",
        # 干扰批次 batch_003 (不应被比较)
        "batch_003,group_A,0.92,118,0.04",
        "batch_003,group_B,0.87,148,0.05",
        # 脏数据：仅在一个批次中出现的组
        "batch_001,group_F,0.90,100,0.02",   # batch_002 无 group_F
        "batch_002,group_G,0.80,90,0.01",    # batch_001 无 group_G
        # 脏数据：格式错误（accuracy 不可解析）
        "batch_001,group_H,abc,120,0.03",
        "batch_002,group_H,0.85,abc,0.02",
        # 脏数据：空行（csv 跳过即可）
        "",
        # 脏数据：重复的 batch_id 但数值相同（无害重复）
        "batch_001,group_A,0.95,120,0.05",
    ]
    with open("data/experiments/experiment_results.csv", "w", newline="") as f:
        f.write("\n".join(csv_lines))

    # ===== 干扰数据文件 =====
    accounts = [
        {"account_id": "a001", "display_name": "Alice", "department": "Eng", "email": "alice@example.com", "permissions": ["read"]},
        {"account_id": "a002", "display_name": "Bob", "department": "Ops", "email": "bob@example.com", "permissions": ["admin"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    contacts = [
        {"contact_id": "c001", "name": "Charlie", "role": "PM", "email": "charlie@example.com"},
        {"contact_id": "c002", "name": "Dave", "role": "QA", "email": "dave@example.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

if __name__ == "__main__":
    build_env()
