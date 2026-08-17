import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # accounts.json
    accounts = [
        {
            "account_id": "acc_001",
            "display_name": "Li Gong",
            "department": "IT Security",
            "email": "li@company.com",
            "permissions": ["open", "restricted"]
        },
        {
            "account_id": "acc_002",
            "display_name": "Admin Zhang",
            "department": "Architecture Office",
            "email": "zhang@company.com",
            "permissions": ["open", "restricted", "confidential"]
        },
        {
            "account_id": "acc_003",
            "display_name": "Guest Wang",
            "department": "Sales",
            "email": "wang@company.com",
            "permissions": ["open"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # assets.json
    assets = [
        {
            "asset_id": "ast_01",
            "asset_name": "Customer DB",
            "asset_type": "customer_data",
            "classification": "public",
            "read_policy": "open",
            "owner_team": "CRM Platform"
        },
        {
            "asset_id": "ast_02",
            "asset_name": "Architecture Blueprint",
            "asset_type": "architecture_data",
            "classification": "confidential",
            "read_policy": "confidential",
            "owner_team": "Architecture Office"
        },
        {
            "asset_id": "ast_03",
            "asset_name": "Sales Reports",
            "asset_type": "customer_data",
            "classification": "internal",
            "read_policy": "restricted",
            "owner_team": "Sales"
        },
        {
            "asset_id": "ast_04",
            "asset_name": "Secret Project",
            "asset_type": "architecture_data",
            "classification": "secret",
            "read_policy": "confidential",
            "owner_team": "Architecture Office"
        },
        {
            "asset_id": "ast_05",
            "asset_name": "Public Docs",
            "asset_type": "customer_data",
            "classification": "public",
            "read_policy": "open",
            "owner_team": "Marketing"
        }
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

    # requests.json
    requests = [
        {
            "request_id": "req_001",
            "channel": "web",
            "request_type": "bulk_export",
            "risk_level": "low",
            "risk_type": "data_leak",
            "target_asset_id": "ast_01",
            "actor_name": "Alice",
            "claimed_role": "analyst",
            "message": "Need customer list for campaign",
            "status": "pending"
        },
        {
            "request_id": "req_002",
            "channel": "api",
            "request_type": "bulk_export",
            "risk_level": "high",
            "risk_type": "unauthorized_access",
            "target_asset_id": "ast_02",
            "actor_name": "Bob",
            "claimed_role": "architect",
            "message": "Export architecture blueprint for review",
            "status": "pending"
        },
        {
            "request_id": "req_003",
            "channel": "web",
            "request_type": "bulk_export",
            "risk_level": "medium",
            "risk_type": "data_leak",
            "target_asset_id": "ast_03",
            "actor_name": "Charlie",
            "claimed_role": "manager",
            "message": "Sales data for Q3 analysis",
            "status": "pending"
        },
        {
            "request_id": "req_004",
            "channel": "web",
            "request_type": "bulk_export",
            "risk_level": "critical",
            "risk_type": "data_leak",
            "target_asset_id": "ast_04",
            "actor_name": "Dave",
            "claimed_role": "engineer",
            "message": "Secret project baseline export",
            "status": "pending"
        },
        {
            "request_id": "req_005",
            "channel": "web",
            "request_type": "bulk_export",
            "risk_level": "low",
            "risk_type": "data_leak",
            "target_asset_id": "ast_01",
            "actor_name": "Eve",
            "claimed_role": "intern",
            "message": "Test export (already approved)",
            "status": "approved"
        },
        {
            "request_id": "req_006",
            "channel": "api",
            "request_type": "bulk_export",
            "risk_level": "medium",
            "risk_type": "unknown_asset",
            "target_asset_id": "ast_99",
            "actor_name": "Frank",
            "claimed_role": "admin",
            "message": "Export from nonexistent asset",
            "status": "pending"
        }
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # attachments.json (干扰项)
    attachments = [
        {
            "path": "attachments/export_policy_v2.pdf",
            "title": "Export Policy v2",
            "kind": "policy",
            "description": "Company-wide data export policy"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # contacts.json (干扰项)
    contacts = [
        {
            "contact_id": "cnt_001",
            "name": "Alice",
            "role": "analyst",
            "email": "alice@company.com"
        },
        {
            "contact_id": "cnt_002",
            "name": "Bob",
            "role": "architect",
            "email": "bob@company.com"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
