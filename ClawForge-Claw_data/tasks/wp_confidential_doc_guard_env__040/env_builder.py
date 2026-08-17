import os
import json

def build_env():
    # Ensure base directories
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty dir, agent will write the deny list here

    # Assets
    assets = [
        {
            "asset_id": "asset_001",
            "asset_name": "Finance Archive Bundle",
            "asset_type": "finance_archive",
            "classification": "published",
            "owner_team": "Finance Operations",
            "read_policy": "open"
        },
        {
            "asset_id": "asset_002",
            "asset_name": "Unpublished Architecture Plan",
            "asset_type": "technical_plan",
            "classification": "unpublished",
            "owner_team": "Architecture Office",
            "read_policy": "strict"
        },
        {
            "asset_id": "asset_003",
            "asset_name": "Q3 Financial Draft",
            "asset_type": "finance_archive",
            "classification": "unpublished",
            "owner_team": "Finance Operations",
            "read_policy": "internal"
        },
        {
            "asset_id": "asset_004",
            "asset_name": "Old Marketing Plan",
            "asset_type": "technical_plan",
            "classification": "published",
            "owner_team": "Architecture Office",
            "read_policy": "open"
        }
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

    # Requests
    requests = [
        {
            "request_id": "req_001",
            "channel": "email",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "info_gathering",
            "target_asset_id": "asset_001",
            "actor_name": "Alice",
            "claimed_role": "Internal Analyst",
            "message": "Please send me the finance archive for review.",
            "status": "pending"
        },
        {
            "request_id": "req_002",
            "channel": "portal",
            "request_type": "read",
            "risk_level": "medium",
            "risk_type": "data_leak",
            "target_asset_id": "asset_002",
            "actor_name": "Bob",
            "claimed_role": "Internal Engineer",
            "message": "Need access to architecture plan for sprint planning.",
            "status": "pending"
        },
        {
            "request_id": "req_003",
            "channel": "email",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "unauthorized_access",
            "target_asset_id": "asset_002",
            "actor_name": "Charlie",
            "claimed_role": "External Contractor",
            "message": "Please provide the latest architecture blueprint.",
            "status": "pending"
        },
        {
            "request_id": "req_004",
            "channel": "api",
            "request_type": "download",
            "risk_level": "critical",
            "risk_type": "unauthorized_access",
            "target_asset_id": "asset_001",
            "actor_name": "Diana",
            "claimed_role": "External Contractor",
            "message": "Need finance bundle for audit.",
            "status": "pending"
        },
        {
            "request_id": "req_005",
            "channel": "email",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "unauthorized_access",
            "target_asset_id": "asset_003",
            "actor_name": "Eve",
            "claimed_role": "Vendor",
            "message": "Send me the Q3 draft for integration work.",
            "status": "pending"
        },
        {
            "request_id": "req_006",
            "channel": "portal",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "unauthorized_access",
            "target_asset_id": "asset_004",
            "actor_name": "Frank",
            "claimed_role": "External Contractor",
            "message": "Access to marketing plan required for campaign.",
            "status": "pending"
        },
        {
            "request_id": "req_007",
            "channel": "email",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "unauthorized_access",
            "target_asset_id": "asset_002",
            "actor_name": "Grace",
            "claimed_role": "Vendor",
            "message": "Architecture plan needed for compliance review.",
            "status": "pending"
        },
        {
            "request_id": "req_008",
            "channel": "api",
            "request_type": "read",
            "risk_level": "medium",
            "risk_type": "data_leak",
            "target_asset_id": "asset_003",
            "actor_name": "Heidi",
            "claimed_role": "Internal Auditor",
            "message": "Internal audit request for Q3 draft.",
            "status": "denied"  # already denied, should not appear
        },
        {
            "request_id": "req_009",
            "channel": "email",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "unauthorized_access",
            "target_asset_id": "asset_002",
            "actor_name": "Ivan",
            "claimed_role": "Internal Manager",
            "message": "I need the plan for my team.",
            "status": "pending"
        }
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # Accounts (interference)
    accounts = [
        {"account_id": "acc_001", "display_name": "Alice", "department": "Finance", "email": "alice@internal.com", "permissions": ["read"]},
        {"account_id": "acc_002", "display_name": "Bob", "department": "Engineering", "email": "bob@internal.com", "permissions": ["read", "write"]},
        {"account_id": "acc_003", "display_name": "Charlie", "department": "External", "email": "charlie@vendor.com", "permissions": []}
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # Contacts (interference)
    contacts = [
        {"contact_id": "con_001", "name": "Charlie Vendor", "role": "External Contractor", "email": "charlie@vendor.com"},
        {"contact_id": "con_002", "name": "Eve Vendor", "role": "Vendor", "email": "eve@vendor.com"}
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # Attachments (interference – dummy files)
    attachment_meta = [
        {"path": "data/attachments/req_003_attachment.pdf", "title": "Blueprint v2.1", "kind": "pdf", "description": "Unpublished architecture diagrams"},
        {"path": "data/attachments/req_005_attachment.xlsx", "title": "Q3 Draft Figures", "kind": "xlsx", "description": "Draft financial tables"},
        {"path": "data/attachments/req_008_attachment.txt", "title": "Audit Notes", "kind": "txt", "description": "Internal notes – already denied"}
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachment_meta}, f, indent=2)

    # Create actual dummy attachment files (empty for simplicity)
    for att in attachment_meta:
        open(att["path"], "a").close()

if __name__ == "__main__":
    build_env()
