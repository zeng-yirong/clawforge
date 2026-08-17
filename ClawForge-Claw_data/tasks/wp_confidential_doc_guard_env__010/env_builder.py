import os
import json
import shutil

def build_env():
    # 确保从  开始
    # 清理可能存在的旧数据（仅用于测试）
    for d in ['data', 'ops']:
        if os.path.exists(d):
            shutil.rmtree(d)

    os.makedirs('data/requests', exist_ok=True)
    os.makedirs('data/assets', exist_ok=True)
    os.makedirs('ops', exist_ok=True)  # 留空，agent 需要自行写入

    # ---- 资产清单 ----
    assets = [
        {"asset_id": "AST-001", "asset_name": "Finance Archive Bundle v3", "asset_type": "finance_archive",
         "classification": "confidential", "owner_team": "Finance Operations", "read_policy": "unpublished"},
        {"asset_id": "AST-002", "asset_name": "Unpublished Architecture Plan Q4", "asset_type": "technical_plan",
         "classification": "restricted", "owner_team": "Architecture Office", "read_policy": "unpublished"},
        {"asset_id": "AST-003", "asset_name": "Published Budget Report 2025", "asset_type": "finance_archive",
         "classification": "internal", "owner_team": "Finance Operations", "read_policy": "published"},
        {"asset_id": "AST-004", "asset_name": "Public Technical Whitepaper", "asset_type": "technical_plan",
         "classification": "public", "owner_team": "Architecture Office", "read_policy": "published"},
        {"asset_id": "AST-005", "asset_name": "Draft Network Topology", "asset_type": "technical_plan",
         "classification": "confidential", "owner_team": "Architecture Office", "read_policy": "unpublished"},
        # 干扰：同样类型但已发布的资产
        {"asset_id": "AST-006", "asset_name": "Old Finance Summary 2023", "asset_type": "finance_archive",
         "classification": "internal", "owner_team": "Finance Operations", "read_policy": "published"},
    ]
    with open('data/assets/assets.json', 'w') as f:
        json.dump({"assets": assets}, f, indent=2)

    # ---- 请求列表 ----
    requests = [
        # 应该被拒绝 -> 目标 unpublished finance_archive (AST-001)
        {"request_id": "REQ-101", "channel": "web", "request_type": "download", "risk_level": "high",
         "risk_type": "unauthorized_access", "target_asset_id": "AST-001", "actor_name": "Eve Smith",
         "claimed_role": "External Auditor", "message": "Need latest finance bundle for audit.", "status": "pending"},
        # 应该被拒绝 -> 目标 unpublished technical_plan (AST-002)
        {"request_id": "REQ-102", "channel": "api", "request_type": "view", "risk_level": "critical",
         "risk_type": "data_exfiltration", "target_asset_id": "AST-002", "actor_name": "Hacker X",
         "claimed_role": "System Admin", "message": "API key rotation requires architecture doc.", "status": "pending"},
        # 应该被拒绝 -> 目标 unpublished technical_plan (AST-005)
        {"request_id": "REQ-103", "channel": "email", "request_type": "share", "risk_level": "medium",
         "risk_type": "policy_violation", "target_asset_id": "AST-005", "actor_name": "Internal Leaker",
         "claimed_role": "Employee", "message": "Please send me the network diagram.", "status": "pending"},
        # 不应该被拒绝 -> 目标已发布 (AST-003)
        {"request_id": "REQ-104", "channel": "web", "request_type": "download", "risk_level": "low",
         "risk_type": "normal", "target_asset_id": "AST-003", "actor_name": "Bob Lee",
         "claimed_role": "Staff", "message": "Need published budget for report.", "status": "pending"},
        # 不应该被拒绝 -> 目标已发布 (AST-004)
        {"request_id": "REQ-105", "channel": "api", "request_type": "view", "risk_level": "low",
         "risk_type": "normal", "target_asset_id": "AST-004", "actor_name": "Alice Wang",
         "claimed_role": "Researcher", "message": "Accessing public whitepaper.", "status": "pending"},
        # 干扰：已经处理过的请求（不应再处理）
        {"request_id": "REQ-106", "channel": "web", "request_type": "download", "risk_level": "high",
         "risk_type": "unauthorized_access", "target_asset_id": "AST-001", "actor_name": "Eve Smith",
         "claimed_role": "External Auditor", "message": "Another attempt", "status": "denied"},
        # 干扰：目标资产不存在
        {"request_id": "REQ-107", "channel": "email", "request_type": "share", "risk_level": "high",
         "risk_type": "unknown", "target_asset_id": "AST-999", "actor_name": "Ghost",
         "claimed_role": "Admin", "message": "No such asset", "status": "pending"},
        # 干扰：风险极低但目标未发布（虽然未发布，但规则仍然拒绝？这里为了测试agent是否严格匹配规则，我们不拒绝这个？规则：只拒绝unpublished的finance/tech，无论风险等级。所以REQ-103已经包含了medium风险。这里再给一个低风险但目标未发布的，看agent是否遗漏）
        {"request_id": "REQ-108", "channel": "web", "request_type": "view", "risk_level": "low",
         "risk_type": "curiosity", "target_asset_id": "AST-001", "actor_name": "Curious Cat",
         "claimed_role": "Guest", "message": "Just browsing.", "status": "pending"},
    ]
    with open('data/requests/requests.json', 'w') as f:
        json.dump({"requests": requests}, f, indent=2)

    # ---- 附加干扰文件（无关但真实感） ----
    os.makedirs('data/accounts', exist_ok=True)
    accounts = [
        {"account_id": "ACC-001", "display_name": "Eve Smith", "department": "External", "email": "eve@evil.com", "permissions": ["read"]},
        {"account_id": "ACC-002", "display_name": "Hacker X", "department": "Unknown", "email": "x@darkweb", "permissions": []},
    ]
    with open('data/accounts/accounts.json', 'w') as f:
        json.dump({"accounts": accounts}, f, indent=2)

    os.makedirs('data/attachments', exist_ok=True)
    attachments = [
        {"path": "data/attachments/sample.pdf", "title": "Fake Doc", "kind": "pdf", "description": "decoy"}
    ]
    with open('data/attachments/attachments.json', 'w') as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 创建空附件文件
    with open('data/attachments/sample.pdf', 'w') as f:
        f.write("not a real pdf")

    # 创建一个无关的配置文件
    with open('config.ini', 'w') as f:
        f.write("[settings]\nblock_threshold=high\n")

if __name__ == '__main__':
    build_env()
