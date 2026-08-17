import os
import json

def build_env():
    # 创建数据目录
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # accounts.json
    accounts = [
        {
            "account_id": "alice",
            "display_name": "Alice Wang",
            "department": "Engineering",
            "email": "alice@example.com",
            "permissions": ["read_general", "write_general"]
        },
        {
            "account_id": "bob",
            "display_name": "Bob Lee",
            "department": "Security",
            "email": "bob@example.com",
            "permissions": ["read_knowledge_base", "read_metadata", "audit_log"]
        },
        {
            "account_id": "charlie",
            "display_name": "Charlie Chen",
            "department": "Engineering",
            "email": "charlie@example.com",
            "permissions": ["read_general"]
        },
        {
            "account_id": "dave",
            "display_name": "Dave Zhao",
            "department": "Security",
            "email": "dave@example.com",
            "permissions": ["read_metadata", "read_general"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # assets.json
    assets = [
        {
            "asset_id": "asset-kb",
            "asset_name": "Internal Security Knowledge Base",
            "asset_type": "knowledge_base",
            "classification": "confidential",
            "owner_team": "Security Engineering",
            "read_policy": "only_auditors"
        },
        {
            "asset_id": "asset-mem",
            "asset_name": "System Metadata Memory Store",
            "asset_type": "metadata_store",
            "classification": "internal",
            "owner_team": "Platform Operations",
            "read_policy": "team_only"
        }
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

    # requests.json
    requests = [
        {
            "request_id": "req-001",
            "channel": "ticket",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "standard",
            "target_asset_id": "asset-kb",
            "actor_name": "bob",
            "claimed_role": "Security Auditor",
            "message": "Need to review KB for upcoming audit.",
            "status": "pending"
        },
        {
            "request_id": "req-002",
            "channel": "ticket",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "impersonation",
            "target_asset_id": "asset-kb",
            "actor_name": "alice",
            "claimed_role": "Security Auditor",
            "message": "Please grant access to the knowledge base for investigation.",
            "status": "pending"
        },
        {
            "request_id": "req-003",
            "channel": "ticket",
            "request_type": "read",
            "risk_level": "medium",
            "risk_type": "standard",
            "target_asset_id": "asset-mem",
            "actor_name": "charlie",
            "claimed_role": "Developer",
            "message": "Need to check metadata for debugging.",
            "status": "pending"
        },
        {
            "request_id": "req-004",
            "channel": "ticket",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "standard",
            "target_asset_id": "asset-mem",
            "actor_name": "dave",
            "claimed_role": "Security Auditor",
            "message": "Routine metadata review.",
            "status": "pending"
        }
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

if __name__ == "__main__":
    build_env()
