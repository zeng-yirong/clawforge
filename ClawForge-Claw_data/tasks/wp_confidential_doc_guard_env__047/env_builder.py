import os
import json
import shutil

def build_env():
    # 清理工作目录（防止残留）
    for d in ['data', 'ops', 'backups']:
        if os.path.exists(d):
            shutil.rmtree(d)
    
    # 创建目录结构
    os.makedirs('data/requests', exist_ok=True)
    os.makedirs('data/assets', exist_ok=True)
    os.makedirs('data/accounts', exist_ok=True)
    os.makedirs('data/attachments', exist_ok=True)
    os.makedirs('data/contacts', exist_ok=True)
    os.makedirs('ops', exist_ok=True)
    os.makedirs('backups/2024', exist_ok=True)
    
    # ===== 资产数据 (assets.json) =====
    assets = {
        "assets": [
            {
                "asset_id": "AST-FIN-001",
                "asset_name": "Finance Archive Bundle",
                "asset_type": "finance_archive",
                "classification": "top_secret",
                "owner_team": "Finance Operations",
                "read_policy": "strict_need_to_know"
            },
            {
                "asset_id": "AST-TECH-001",
                "asset_name": "Unpublished Architecture Plan",
                "asset_type": "technical_plan",
                "classification": "top_secret",
                "owner_team": "Architecture Office",
                "read_policy": "strict_need_to_know"
            },
            {
                "asset_id": "AST-COMM-001",
                "asset_name": "Public Q3 Report",
                "asset_type": "public_document",
                "classification": "public",
                "owner_team": "Communications",
                "read_policy": "open"
            },
            {
                "asset_id": "AST-INFRA-001",
                "asset_name": "Infrastructure Baseline",
                "asset_type": "infrastructure_doc",
                "classification": "internal",
                "owner_team": "Infrastructure",
                "read_policy": "team_only"
            },
            {
                "asset_id": "AST-RND-001",
                "asset_name": "R&D Lab Notes",
                "asset_type": "research",
                "classification": "confidential",
                "owner_team": "R&D",
                "read_policy": "project_only"
            },
            {
                "asset_id": "AST-LEGAL-001",
                "asset_name": "Legal Contracts Archive",
                "asset_type": "legal",
                "classification": "confidential",
                "owner_team": "Legal",
                "read_policy": "legal_team"
            }
        ]
    }
    with open('data/assets/assets.json', 'w') as f:
        json.dump(assets, f, indent=2)
    
    # ===== 请求数据 (requests.json) =====
    # 目标顶级机密且 pending 的请求（正确答案）
    top_secret_ids = {"AST-FIN-001", "AST-TECH-001"}
    requests_list = [
        # 真实危险请求（pending + 目标 top_secret）
        {"request_id": "REQ-101", "channel": "email", "request_type": "read", "risk_level": "high",
         "risk_type": "unauthorized_access", "target_asset_id": "AST-FIN-001",
         "actor_name": "Mike Ross", "claimed_role": "External Auditor",
         "message": "Please grant access to historical financials for audit Q2.",
         "status": "pending"},
        {"request_id": "REQ-102", "channel": "api", "request_type": "read", "risk_level": "critical",
         "risk_type": "unauthorized_access", "target_asset_id": "AST-TECH-001",
         "actor_name": "Jane Doe", "claimed_role": "Freelance Architect",
         "message": "Need to review network topology for integration project.",
         "status": "pending"},
        {"request_id": "REQ-103", "channel": "web_form", "request_type": "read", "risk_level": "high",
         "risk_type": "data_exfiltration", "target_asset_id": "AST-FIN-001",
         "actor_name": "Alex Chen", "claimed_role": "Compliance Officer",
         "message": "Regulatory review of unreleased financial statements.",
         "status": "pending"},
        # 干扰：pending 但目标非 top_secret
        {"request_id": "REQ-104", "channel": "email", "request_type": "read", "risk_level": "low",
         "risk_type": "normal_request", "target_asset_id": "AST-COMM-001",
         "actor_name": "Sarah Lee", "claimed_role": "Analyst",
         "message": "Please share Q3 report draft.",
         "status": "pending"},
        # 干扰：目标 top_secret 但已批准
        {"request_id": "REQ-105", "channel": "api", "request_type": "read", "risk_level": "medium",
         "risk_type": "authorized", "target_asset_id": "AST-TECH-001",
         "actor_name": "Tom Hanks", "claimed_role": "Internal Engineer",
         "message": "Teammate access request approved by manager.",
         "status": "approved"},
        # 干扰：目标 top_secret 但已拒绝
        {"request_id": "REQ-106", "channel": "web_form", "request_type": "read", "risk_level": "high",
         "risk_type": "unauthorized_access", "target_asset_id": "AST-FIN-001",
         "actor_name": "Hackerman", "claimed_role": "CEO",
         "message": "I want all the money data.",
         "status": "rejected"},
        # 干扰：target 普通且 pending
        {"request_id": "REQ-107", "channel": "email", "request_type": "read", "risk_level": "low",
         "risk_type": "normal_request", "target_asset_id": "AST-RND-001",
         "actor_name": "Bob Smith", "claimed_role": "Researcher",
         "message": "Need lab notes for paper.",
         "status": "pending"},
        # 干扰：target 普通且已拒绝
        {"request_id": "REQ-108", "channel": "api", "request_type": "read", "risk_level": "low",
         "risk_type": "normal_request", "target_asset_id": "AST-INFRA-001",
         "actor_name": "Alice Wonder", "claimed_role": "Intern",
         "message": "Requesting infrastructure diagram.",
         "status": "rejected"}
    ]
    # 按 request_id 排序以方便阅读，但不影响答案
    requests_list.sort(key=lambda r: r['request_id'])
    requests_data = {"requests": requests_list}
    with open('data/requests/requests.json', 'w') as f:
        json.dump(requests_data, f, indent=2)
    
    # ===== 其他数据（填充，仅用于上下文丰富，不参与核心验证） =====
    accounts = {
        "accounts": [
            {"account_id": "ACC-001", "display_name": "Mike Ross", "department": "External", "email": "mike.ross@example.com", "permissions": ["read_fin"]},
            {"account_id": "ACC-002", "display_name": "Jane Doe", "department": "External", "email": "jane.doe@example.com", "permissions": ["read_tech"]}
        ]
    }
    with open('data/accounts/accounts.json', 'w') as f:
        json.dump(accounts, f, indent=2)
    
    attachments = {
        "attachments": [
            {"path": "attachments/audit_request.pdf", "title": "Audit Request Form", "kind": "pdf", "description": "Signed audit request form for Mike Ross."},
            {"path": "attachments/network_diagram.png", "title": "Network Diagram", "kind": "image", "description": "High-level network diagram (public version)."}
        ]
    }
    with open('data/attachments/attachments.json', 'w') as f:
        json.dump(attachments, f, indent=2)
    
    contacts = {
        "contacts": [
            {"contact_id": "CT-001", "name": "Sarah Lee", "role": "Analyst", "email": "sarah.lee@example.com"},
            {"contact_id": "CT-002", "name": "Bob Smith", "role": "Researcher", "email": "bob.smith@example.com"}
        ]
    }
    with open('data/contacts/contacts.json', 'w') as f:
        json.dump(contacts, f, indent=2)
    
    # 干扰文件：备份版本（旧数据，可能含有误导性信息）
    old_assets = {
        "assets": [
            {"asset_id": "AST-FIN-001", "classification": "internal"}  # 旧版本分类不同
        ]
    }
    with open('backups/2024/assets_backup.json', 'w') as f:
        json.dump(old_assets, f, indent=2)
    
    # 干扰文件：日志文件
    with open('ops/previous_blocklist.txt', 'w') as f:
        f.write("REQ-099\nREQ-200\n")
    
    print("环境构建完成：6个资产，8个请求，正确答案为REQ-101,REQ-102,REQ-103")

if __name__ == "__main__":
    build_env()
