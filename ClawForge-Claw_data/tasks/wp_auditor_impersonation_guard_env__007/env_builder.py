import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ========== 1. accounts.json ==========
    accounts = [
        {
            "account_id": "acc-001",
            "display_name": "Alice Wang",
            "department": "Security Engineering",
            "email": "alice@example.com",
            "permissions": ["audit", "read"]
        },
        {
            "account_id": "acc-002",
            "display_name": "Bob Li",
            "department": "Platform Operations",
            "email": "bob@example.com",
            "permissions": ["read"]
        },
        {
            "account_id": "acc-003",
            "display_name": "Carol Zhang",
            "department": "Security Engineering",
            "email": "carol@example.com",
            "permissions": ["read"]
        },
        {
            "account_id": "acc-004",
            "display_name": "Dave Chen",
            "department": "Engineering",
            "email": "dave@example.com",
            "permissions": ["read"]
        },
        {
            "account_id": "acc-005",
            "display_name": "Grace Liu",
            "department": "Engineering",
            "email": "grace@example.com",
            "permissions": []
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts, "wrapper": "accounts", "key": "account_id"}, f, indent=2)

    # ========== 2. assets.json ==========
    assets = [
        {
            "asset_id": "asset-001",
            "asset_name": "Internal Security Knowledge Base",
            "asset_type": "knowledge_base",
            "classification": "restricted",
            "owner_team": "Security Engineering",
            "read_policy": "audit_only"
        },
        {
            "asset_id": "asset-002",
            "asset_name": "System Metadata Memory Store",
            "asset_type": "metadata_store",
            "classification": "restricted",
            "owner_team": "Platform Operations",
            "read_policy": "audit_only"
        },
        {
            "asset_id": "asset-003",
            "asset_name": "Public Documentation",
            "asset_type": "wiki",
            "classification": "public",
            "owner_team": "Engineering",
            "read_policy": "anyone"
        },
        {
            "asset_id": "asset-004",
            "asset_name": "Employee Directory",
            "asset_type": "database",
            "classification": "internal",
            "owner_team": "HR",
            "read_policy": "staff"
        }
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets, "wrapper": "assets", "key": "asset_id"}, f, indent=2)

    # ========== 3. requests/requests.json ==========
    requests = [
        # req-001: 合法审计员 Alice，目标受限制知识库 => 不应拒绝
        {
            "request_id": "req-001",
            "channel": "web",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "data_access",
            "target_asset_id": "asset-001",
            "actor_name": "Alice Wang",
            "claimed_role": "Security Auditor",
            "message": "Need to review latest incident reports.",
            "status": "pending"
        },
        # req-002: Bob冒充审计员，目标asset-001 => 应拒绝
        {
            "request_id": "req-002",
            "channel": "api",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "impersonation",
            "target_asset_id": "asset-001",
            "actor_name": "Bob Li",
            "claimed_role": "Security Auditor",
            "message": "Performing quarterly audit.",
            "status": "pending"
        },
        # req-003: Carol在安全工程但无audit权限，冒充审计员，目标asset-002 => 应拒绝
        {
            "request_id": "req-003",
            "channel": "email",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "impersonation",
            "target_asset_id": "asset-002",
            "actor_name": "Carol Zhang",
            "claimed_role": "Security Auditor",
            "message": "Need metadata for compliance check.",
            "status": "pending"
        },
        # req-004: Dave冒充审计员，目标asset-002 => 应拒绝
        {
            "request_id": "req-004",
            "channel": "web",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "impersonation",
            "target_asset_id": "asset-002",
            "actor_name": "Dave Chen",
            "claimed_role": "Security Auditor",
            "message": "Audit routine.",
            "status": "pending"
        },
        # req-005: Eve声称数据分析师，目标asset-001 => 不是冒充审计员，不应拒绝
        {
            "request_id": "req-005",
            "channel": "cli",
            "request_type": "read",
            "risk_level": "medium",
            "risk_type": "data_access",
            "target_asset_id": "asset-001",
            "actor_name": "Eve Sun",
            "claimed_role": "Data Analyst",
            "message": "Need KB for analysis.",
            "status": "pending"
        },
        # req-006: Frank冒充审计员，但目标资产是公开文档 => 不应拒绝（非受限）
        {
            "request_id": "req-006",
            "channel": "web",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "impersonation",
            "target_asset_id": "asset-003",
            "actor_name": "Frank Wu",
            "claimed_role": "Security Auditor",
            "message": "Review public docs.",
            "status": "pending"
        },
        # req-007: 合法审计员Alice访问非受限资产 => 不应拒绝
        {
            "request_id": "req-007",
            "channel": "email",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "data_access",
            "target_asset_id": "asset-004",
            "actor_name": "Alice Wang",
            "claimed_role": "Security Auditor",
            "message": "Need employee directory for audit.",
            "status": "pending"
        },
        # req-008: Grace冒充审计员，目标asset-001（账户不存在于accounts? 实际存在acc-005，但无audit权限） => 应拒绝
        {
            "request_id": "req-008",
            "channel": "api",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "impersonation",
            "target_asset_id": "asset-001",
            "actor_name": "Grace Liu",
            "claimed_role": "Security Auditor",
            "message": "Urgent audit.",
            "status": "pending"
        }
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests, "wrapper": "requests", "key": "request_id"}, f, indent=2)

    # ========== 4. 辅助文件（干扰项） ==========
    # attachments.json - 一些无关的附件描述
    attachments = [
        {"path": "attachments/report_q1.pdf", "title": "Q1 Security Report", "kind": "pdf",
         "description": "Quarterly internal security metrics."},
        {"path": "attachments/network_map.png", "title": "Network Topology", "kind": "image",
         "description": "Network diagram used by operations."}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments, "wrapper": "attachments", "key": None}, f, indent=2)

    # contacts.json - 联系人
    contacts = [
        {"contact_id": "c-001", "name": "Chen Wei", "role": "Security Ops Lead", "email": "chen.wei@example.com"},
        {"contact_id": "c-002", "name": "Fiona Zhao", "role": "Compliance Officer", "email": "fiona.zhao@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts, "wrapper": "contacts", "key": "contact_id"}, f, indent=2)

if __name__ == "__main__":
    build_env()
