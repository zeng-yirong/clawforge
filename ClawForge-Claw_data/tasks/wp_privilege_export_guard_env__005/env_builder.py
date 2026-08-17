import os
import json
import random
import string

def build_env():
    # 确保目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)  # 干扰目录

    # 1. 账户数据 (accounts.json)
    accounts = {
        "accounts": [
            {
                "account_id": "acc_001",
                "display_name": "Alice",
                "department": "Engineering",
                "email": "alice@corp.com",
                "permissions": ["customer_data_read", "architecture_data_read"]   # 完全权限
            },
            {
                "account_id": "acc_002",
                "display_name": "Bob",
                "department": "Support",
                "email": "bob@corp.com",
                "permissions": ["customer_data_read"]   # 只能看客户数据
            },
            {
                "account_id": "acc_003",
                "display_name": "Carol",
                "department": "Marketing",
                "email": "carol@corp.com",
                "permissions": ["architecture_data_read"]   # 只能看架构数据
            },
            {
                "account_id": "acc_004",
                "display_name": "Dave",
                "department": "Finance",
                "email": "dave@corp.com",
                "permissions": []   # 无权限
            },
            {
                "account_id": "acc_005",
                "display_name": "Eve",
                "department": "HR",
                "email": "eve@corp.com",
                "permissions": ["customer_data_read", "architecture_data_read"]   # 完全权限
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 2. 资产数据 (assets/assets.json)
    assets_data = {
        "assets": [
            {
                "asset_id": "ast_001",
                "asset_name": "Architecture Memory Repository",
                "asset_type": "architecture_data",
                "classification": "Confidential",
                "owner_team": "Architecture Office",
                "read_policy": "architecture_data_read"
            },
            {
                "asset_id": "ast_002",
                "asset_name": "Customer Master Ledger",
                "asset_type": "customer_data",
                "classification": "Highly Confidential",
                "owner_team": "CRM Platform",
                "read_policy": "customer_data_read"
            },
            {
                "asset_id": "ast_003",
                "asset_name": "Internal Wiki",
                "asset_type": "general",
                "classification": "Internal",
                "owner_team": "IT",
                "read_policy": "general_read"
            }
        ]
    }
    os.makedirs("data/assets", exist_ok=True)
    with open("data/assets/assets.json", "w") as f:
        json.dump(assets_data, f, indent=2)

    # 3. 请求数据 (requests/requests.json)
    requests_list = [
        # 正常请求（权限匹配）
        {"request_id": "req_001", "channel": "api", "request_type": "bulk_export", 
         "risk_level": "high", "risk_type": "data_leak", "target_asset_id": "ast_002",
         "actor_name": "Alice", "claimed_role": "Engineer", 
         "message": "Export customer records for Q3 analysis", "status": "pending"},
        {"request_id": "req_002", "channel": "ui", "request_type": "bulk_export",
         "risk_level": "medium", "risk_type": "unauthorized_access", "target_asset_id": "ast_001",
         "actor_name": "Alice", "claimed_role": "Engineer",
         "message": "Pull architecture diagrams for review", "status": "pending"},
        # 越权请求（Bob请求架构资产，但他只有客户权限）
        {"request_id": "req_003", "channel": "api", "request_type": "bulk_export",
         "risk_level": "critical", "risk_type": "privilege_escalation", "target_asset_id": "ast_001",
         "actor_name": "Bob", "claimed_role": "Support",
         "message": "Need all architecture models for support case", "status": "pending"},
        # 越权请求（Carol请求客户资产，但她只有架构权限）
        {"request_id": "req_004", "channel": "ui", "request_type": "bulk_export",
         "risk_level": "critical", "risk_type": "privilege_escalation", "target_asset_id": "ast_002",
         "actor_name": "Carol", "claimed_role": "Marketing",
         "message": "Export customer list for campaign", "status": "pending"},
        # 越权请求（Dave无任何权限，却请求架构资产）
        {"request_id": "req_005", "channel": "api", "request_type": "bulk_export",
         "risk_level": "critical", "risk_type": "privilege_escalation", "target_asset_id": "ast_001",
         "actor_name": "Dave", "claimed_role": "Finance",
         "message": "Need architecture for budgeting", "status": "pending"},
        # 干扰项：已拒绝的请求（不需要再处理）
        {"request_id": "req_006", "channel": "api", "request_type": "bulk_export",
         "risk_level": "high", "risk_type": "unauthorized_access", "target_asset_id": "ast_002",
         "actor_name": "Bob", "claimed_role": "Support",
         "message": "Export customer emails", "status": "denied"},
        # 干扰项：正常请求（Eve有完全权限）
        {"request_id": "req_007", "channel": "ui", "request_type": "bulk_export",
         "risk_level": "low", "risk_type": "data_backup", "target_asset_id": "ast_001",
         "actor_name": "Eve", "claimed_role": "HR Coordinator",
         "message": "Backup architecture repository", "status": "pending"},
        # 干扰项：目标资产不存在（需要跳过或单独处理，但越权判断仅基于权限，资产存在性不纳入当前任务）
        {"request_id": "req_008", "channel": "api", "request_type": "bulk_export",
         "risk_level": "high", "risk_type": "data_leak", "target_asset_id": "ast_999",
         "actor_name": "Alice", "claimed_role": "Engineer",
         "message": "Unknown asset", "status": "pending"},
    ]
    os.makedirs("data/requests", exist_ok=True)
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests_list}, f, indent=2)

    # 4. 干扰文件：无用的附件和联系人
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": []}, f, indent=2)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f, indent=2)

    # 5. 干扰日志文件（大量无关记录）
    log_dir = "logs"
    for i in range(5):
        log_data = [f"line {j} info request req_{j:03d}" for j in range(20)]
        with open(os.path.join(log_dir, f"audit_{i}.log"), "w") as f:
            f.write("\n".join(log_data))

    # 6. 在ops下放置一个旧版本的干扰文件，模拟历史记录
    with open("ops/deny_requests.json", "w") as f:
        json.dump(["req_old"], f, indent=2)

if __name__ == "__main__":
    build_env()
