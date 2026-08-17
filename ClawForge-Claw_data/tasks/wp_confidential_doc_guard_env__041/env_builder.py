import os
import json
import random

def build_env():
    # Create required directories
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # Add a decoy file
    os.makedirs("raw_logs", exist_ok=True)
    with open("raw_logs/audit.log", "w") as f:
        f.write("2025-03-10 03:14:15, ALERT, high_io_usage\n2025-03-10 03:16:22, INFO, session_opened\n")
    with open("ops/placeholder.txt", "w") as f:
        f.write("This file can be removed.\n")

    # Accounts
    accounts = [
        {"account_id": "acc-001", "display_name": "Alice", "department": "Engineering", "email": "alice@corp.com", "permissions": ["read", "write"]},
        {"account_id": "acc-002", "display_name": "Bob", "department": "Finance", "email": "bob@corp.com", "permissions": ["read"]},
        {"account_id": "acc-003", "display_name": "Charlie", "department": "External", "email": "charlie@external.com", "permissions": ["read"]},
        {"account_id": "acc-004", "display_name": "Diana", "department": "Architecture", "email": "diana@corp.com", "permissions": ["read", "write"]},
        {"account_id": "acc-005", "display_name": "Eve", "department": "External", "email": "eve@external.com", "permissions": []},
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # Assets – mix of confidential and non-confidential
    assets = [
        {"asset_id": "asset-001", "asset_name": "Unpublished Architecture Plan", "asset_type": "technical_plan", "classification": "confidential", "owner_team": "Architecture Office", "read_policy": "strict"},
        {"asset_id": "asset-002", "asset_name": "Finance Archive Bundle", "asset_type": "finance_archive", "classification": "confidential", "owner_team": "Finance Operations", "read_policy": "strict"},
        {"asset_id": "asset-003", "asset_name": "Internal Design Spec", "asset_type": "technical_plan", "classification": "internal", "owner_team": "Engineering", "read_policy": "moderate"},
        {"asset_id": "asset-004", "asset_name": "Public Quarterly Report", "asset_type": "finance_archive", "classification": "public", "owner_team": "Finance Operations", "read_policy": "open"},
        {"asset_id": "asset-005", "asset_name": "Next-Gen Blueprint", "asset_type": "technical_plan", "classification": "confidential", "owner_team": "Architecture Office", "read_policy": "strict"},
        {"asset_id": "asset-006", "asset_name": "Marketing Brochure", "asset_type": "finance_archive", "classification": "public", "owner_team": "Marketing", "read_policy": "open"},
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

    # Requests – many decoys, only a few truly match the deny rule
    requests = [
        {"request_id": "req-001", "channel": "external_api", "request_type": "read", "risk_level": "high", "risk_type": "unauthorized", "target_asset_id": "asset-001", "actor_name": "Charlie", "claimed_role": "external_partner", "message": "Need latest architecture plan for integration", "status": "pending"},
        {"request_id": "req-002", "channel": "external_api", "request_type": "read", "risk_level": "high", "risk_type": "data_exfiltration", "target_asset_id": "asset-002", "actor_name": "Eve", "claimed_role": "external_auditor", "message": "Audit required finance archive", "status": "pending"},
        {"request_id": "req-003", "channel": "internal", "request_type": "read", "risk_level": "high", "risk_type": "normal", "target_asset_id": "asset-003", "actor_name": "Alice", "claimed_role": "engineer", "message": "Need internal spec", "status": "pending"},   # internal asset, not confidential
        {"request_id": "req-004", "channel": "external_api", "request_type": "read", "risk_level": "medium", "risk_type": "suspicious", "target_asset_id": "asset-001", "actor_name": "Bob", "claimed_role": "external_support", "message": "Support request", "status": "pending"},  # medium risk
        {"request_id": "req-005", "channel": "external_api", "request_type": "read", "risk_level": "high", "risk_type": "unauthorized", "target_asset_id": "asset-004", "actor_name": "Charlie", "claimed_role": "external_partner", "message": "Public data access", "status": "pending"},  # public asset
        {"request_id": "req-006", "channel": "internal", "request_type": "read", "risk_level": "low", "risk_type": "normal", "target_asset_id": "asset-001", "actor_name": "Diana", "claimed_role": "architect", "message": "Legitimate review", "status": "pending"},  # low risk
        {"request_id": "req-007", "channel": "external_api", "request_type": "read", "risk_level": "high", "risk_type": "data_exfiltration", "target_asset_id": "asset-005", "actor_name": "Eve", "claimed_role": "external_auditor", "message": "Audit blueprint", "status": "pending"},  # high + confidential
        {"request_id": "req-008", "channel": "external_api", "request_type": "write", "risk_level": "high", "risk_type": "malicious", "target_asset_id": "asset-002", "actor_name": "Unknown", "claimed_role": "none", "message": "Attempt to upload malicious payload", "status": "pending"},  # high risk but write request? still count as request; but rule only cares risk_level and classification, so yes
        {"request_id": "req-009", "channel": "internal", "request_type": "read", "risk_level": "high", "risk_type": "normal", "target_asset_id": "asset-002", "actor_name": "Alice", "claimed_role": "engineer", "message": "Internal finance review", "status": "pending"},  # high + confidential (asset-002)
        {"request_id": "req-010", "channel": "external_api", "request_type": "read", "risk_level": "low", "risk_type": "scan", "target_asset_id": "asset-005", "actor_name": "Scanner", "claimed_role": "security_tool", "message": "Vulnerability scan", "status": "pending"},  # low risk
        {"request_id": "req-011", "channel": "external_api", "request_type": "read", "risk_level": "high", "risk_type": "unauthorized", "target_asset_id": "asset-006", "actor_name": "Charlie", "claimed_role": "external_partner", "message": "Marketing data", "status": "pending"},  # public asset
        {"request_id": "req-012", "channel": "internal", "request_type": "read", "risk_level": "medium", "risk_type": "normal", "target_asset_id": "asset-003", "actor_name": "Diana", "claimed_role": "architect", "message": "Cross-team review", "status": "pending"},
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # Contacts – optional, for flavor
    contacts = [
        {"contact_id": "con-001", "name": "Alice", "role": "Engineer", "email": "alice@corp.com"},
        {"contact_id": "con-002", "name": "Bob", "role": "Analyst", "email": "bob@corp.com"},
        {"contact_id": "con-003", "name": "Charlie", "role": "External Partner", "email": "charlie@external.com"},
        {"contact_id": "con-004", "name": "Diana", "role": "Architect", "email": "diana@corp.com"},
        {"contact_id": "con-005", "name": "Eve", "role": "External Auditor", "email": "eve@external.com"},
    ]
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
    # Expected answer for verification (not exposed to agent):
    # req-001, req-002, req-007, req-008, req-009  (since asset-001,002,005 are confidential; req-008 targets asset-002 high risk)
    # Actually check: asset-002 is confidential, so req-008 qualifies; req-009 also qualifies. So final set: {"req-001","req-002","req-007","req-008","req-009"}
