import os
import json

def build_env():
    # data/assets/assets.json
    assets = [
        {
            "asset_id": "ast-001",
            "asset_name": "Unpublished Architecture Plan v2",
            "asset_type": "technical_plan",
            "classification": "highly_confidential",
            "owner_team": "Architecture Office",
            "read_policy": "restrict"
        },
        {
            "asset_id": "ast-002",
            "asset_name": "Finance Archive Bundle Q1",
            "asset_type": "finance_archive",
            "classification": "highly_confidential",
            "owner_team": "Finance Operations",
            "read_policy": "restrict"
        },
        {
            "asset_id": "ast-003",
            "asset_name": "Public Marketing Brochure",
            "asset_type": "marketing",
            "classification": "public",
            "owner_team": "Marketing",
            "read_policy": "open"
        },
        {
            "asset_id": "ast-004",
            "asset_name": "Old Technical Draft (2019)",
            "asset_type": "technical_plan",
            "classification": "internal",
            "owner_team": "Architecture Office",
            "read_policy": "internal"
        }
    ]
    os.makedirs("data/assets", exist_ok=True)
    with open("data/assets/assets.json", "w") as f:
        json.dump(assets, f, indent=2)

    # data/requests/requests.json
    requests = [
        {
            "request_id": "req-101",
            "channel": "email",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "external_access",
            "target_asset_id": "ast-001",
            "actor_name": "James Smith",
            "claimed_role": "External Auditor",
            "message": "Need to review architecture plan",
            "status": "pending"
        },
        {
            "request_id": "req-102",
            "channel": "portal",
            "request_type": "read",
            "risk_level": "medium",
            "risk_type": "internal_curiosity",
            "target_asset_id": "ast-002",
            "actor_name": "Jane Doe",
            "claimed_role": "Finance Intern",
            "message": "Looking for financial data",
            "status": "pending"
        },
        {
            "request_id": "req-103",
            "channel": "email",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "routine",
            "target_asset_id": "ast-003",
            "actor_name": "Bob Lee",
            "claimed_role": "Marketing Partner",
            "message": "Need brochure for campaign",
            "status": "approved"
        },
        {
            "request_id": "req-104",
            "channel": "phone",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "external_access",
            "target_asset_id": "ast-001",
            "actor_name": "Alice Wang",
            "claimed_role": "Consultant",
            "message": "Urgent access to plan",
            "status": "denied"
        },
        {
            "request_id": "req-105",
            "channel": "email",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "external_access",
            "target_asset_id": "ast-004",
            "actor_name": "Eve Chen",
            "claimed_role": "Partner",
            "message": "Need old draft",
            "status": "pending"
        },
        {
            "request_id": "req-106",
            "channel": "api",
            "request_type": "read",
            "risk_level": "medium",
            "risk_type": "external_access",
            "target_asset_id": "ast-002",
            "actor_name": "System Bot",
            "claimed_role": "Automated Service",
            "message": "Scheduled fetch",
            "status": "pending"
        }
    ]
    os.makedirs("data/requests", exist_ok=True)
    with open("data/requests/requests.json", "w") as f:
        json.dump(requests, f, indent=2)

    # 干扰文件
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump([{"account_id": "acc-01", "display_name": "James Smith", "department": "External", "email": "james@ext.com", "permissions": ["read"]}], f, indent=2)
    with open("data/attachments.json", "w") as f:
        json.dump([{"path": "attachments/plan_v2.pdf", "title": "Architecture Plan v2", "kind": "pdf", "description": "Unpublished technical blueprint"}], f, indent=2)
    os.makedirs("ops", exist_ok=True)  # 让目录存在，但初始为空

if __name__ == "__main__":
    build_env()
