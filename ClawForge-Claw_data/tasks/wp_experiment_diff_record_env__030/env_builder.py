import os
import csv
import json

def build_env():
    # 创建目录
    os.makedirs("data/experiments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # target dir for agent output
    os.makedirs("data", exist_ok=True)  # for decoy files

    # 生成实验数据 CSV（包含干扰批次和脏数据）
    rows = [
        # 目标批次 batch-001 （3个组）
        ["batch-001", "group-A", "0.85", "120", "0.23"],
        ["batch-001", "group-B", "0.90", "110", "0.18"],
        ["batch-001", "group-C", "0.88", "125", "0.21"],
        # 目标批次 batch-002 （3个组，注意group-C有下降）
        ["batch-002", "group-A", "0.87", "115", "0.24"],
        ["batch-002", "group-B", "0.92", "105", "0.17"],
        ["batch-002", "group-C", "0.84", "130", "0.22"],
        # 干扰批次 batch-003 （3个组，但和batch-001/002无关）
        ["batch-003", "group-X", "0.91", "95", "0.15"],
        ["batch-003", "group-Y", "0.78", "140", "0.30"],
        ["batch-003", "group-Z", "0.86", "118", "0.19"],
        # 干扰批次 batch-004 （只有1个组，缺少对应）
        ["batch-004", "group-A", "0.82", "132", "0.27"],
        # 脏数据：缺少 accuracy
        ["batch-001", "group-D", "", "999", "0.99"],
        # 重复行（相同batch+group，后出现的应被视为有效？按常规agent应去重？但为了答案唯一，这里故意让重复行数值与第一行相同，避免歧义）
        ["batch-001", "group-A", "0.85", "120", "0.23"],
        # 脏数据：latency_ms为负数（业务上不合理，但agent应忽略）
        ["batch-002", "group-E", "0.95", "-1", "0.01"],
        # 孤立组（只出现在batch-002，不应被纳入）
        ["batch-002", "group-F", "0.93", "108", "0.20"],
    ]
    header = ["batch_id", "group_id", "accuracy", "latency_ms", "cost_usd"]
    with open("data/experiments/experiment_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    # 诱饵文件：accounts.json 和 contacts.json（内容随意）
    accounts = [
        {"account_id": "acc-001", "display_name": "Alice", "department": "ML", "email": "alice@co.com", "permissions": ["read"]},
        {"account_id": "acc-002", "display_name": "Bob", "department": "Infra", "email": "bob@co.com", "permissions": ["write"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    contacts = [
        {"contact_id": "ct-001", "name": "Charlie", "role": "researcher", "email": "charlie@co.com"},
        {"contact_id": "ct-002", "name": "Diana", "role": "engineer", "email": "diana@co.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

if __name__ == "__main__":
    build_env()
