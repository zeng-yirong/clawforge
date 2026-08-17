import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 写入 accounts.json
    accounts = {
        "accounts": [
            {
                "account_id": "analyst_001",
                "display_name": "Alice",
                "department": "Data Science",
                "email": "alice@example.com",
                "permissions": ["read", "write"]
            },
            {
                "account_id": "analyst_002",
                "display_name": "Bob",
                "department": "Engineering",
                "email": "bob@example.com",
                "permissions": ["read"]
            },
            {
                "account_id": "analyst_003",
                "display_name": "Charlie",
                "department": "ML Ops",
                "email": "charlie@example.com",
                "permissions": ["read", "execute"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 写入 contacts.json（干扰项，不要求使用）
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Delta", "role": "PM", "email": "delta@example.com"},
            {"contact_id": "c002", "name": "Eve", "role": "QA", "email": "eve@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 写入 experiment_results.csv，包含正常行、脏数据、干扰批次
    csv_lines = [
        "batch_id,group_id,accuracy,latency_ms,cost_usd",
        # 目标批次 batch_001（3个 group）
        "batch_001,group_A,0.95,120.0,0.5",
        "batch_001,group_B,0.93,115.0,0.45",
        "batch_001,group_C,0.91,118.0,0.48",
        # 目标批次 batch_002（2个 group）
        "batch_002,group_A,0.88,135.0,0.6",
        "batch_002,group_B,0.85,130.0,0.55",
        # 干扰批次 batch_003（3个 group，但不要算进去）
        "batch_003,group_X,0.77,150.0,0.7",
        "batch_003,group_Y,0.79,145.0,0.68",
        "batch_003,group_Z,0.76,152.0,0.72",
        # 干扰批次 batch_004（1个 group）
        "batch_004,group_S,0.90,110.0,0.52",
        # 脏数据：非数字值（latency_ms 不是数字）
        "batch_001,group_D,0.89,abc,0.44",
        # 脏数据：缺失字段
        "batch_002,group_E,0.87,128.0",
        # 脏数据：完全乱行
        "this_is_garbage,0.5,0.3,0.2",
        # 脏数据：重复表头（应被忽略）
        "batch_id,group_id,accuracy,latency_ms,cost_usd",
        # 正常但无关批次 batch_005（1个 group）
        "batch_005,group_P,0.80,140.0,0.65",
    ]

    with open("data/experiments/experiment_results.csv", "w") as f:
        for line in csv_lines:
            f.write(line + "\n")

if __name__ == "__main__":
    build_env()
