import os, json

def build_env():
    # Ensure directories
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Assets
    assets = [
        {"asset_id": "ast-001", "asset_name": "Unpublished Architecture Plan v3", "asset_type": "technical_plan", "classification": "highly_confidential", "owner_team": "Architecture Office"},
        {"asset_id": "ast-002", "asset_name": "Q3 Finance Forecast", "asset_type": "finance_archive", "classification": "confidential", "owner_team": "Finance Operations"},
        {"asset_id": "ast-003", "asset_name": "Public Roadmap", "asset_type": "technical_plan", "classification": "public", "owner_team": "Architecture Office"}
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

    # Requests (with distractors)
    requests = [
        {"request_id": "req-001", "channel": "email", "request_type": "read", "risk_level": "high", "risk_type": "external", "target_asset_id": "ast-001", "actor_name": "James Carter", "claimed_role": "External Auditor", "message": "Need access to architecture plan", "status": "pending"},
        {"request_id": "req-002", "channel": "web", "request_type": "read", "risk_level": "medium", "risk_type": "external", "target_asset_id": "ast-002", "actor_name": "Maria Lopez", "claimed_role": "Contractor", "message": "Need financial data", "status": "pending"},
        {"request_id": "req-003", "channel": "api", "request_type": "read", "risk_level": "low", "risk_type": "internal", "target_asset_id": "ast-001", "actor_name": "Alice Wang", "claimed_role": "Senior Architect", "message": "Review plan", "status": "pending"},
        {"request_id": "req-004", "channel": "email", "request_type": "read", "risk_level": "low", "risk_type": "external", "target_asset_id": "ast-003", "actor_name": "Bob Lee", "claimed_role": "Guest", "message": "Public roadmap", "status": "pending"},
        {"request_id": "req-005", "channel": "web", "request_type": "read", "risk_level": "high", "risk_type": "external", "target_asset_id": "ast-002", "actor_name": "Eve Smith", "claimed_role": "External Auditor", "message": "Audit finance", "status": "pending"},
        {"request_id": "req-006", "channel": "api", "request_type": "read", "risk_level": "critical", "risk_type": "internal", "target_asset_id": "ast-002", "actor_name": "David Chen", "claimed_role": "Financial Analyst", "message": "Q3 forecast", "status": "pending"},
        # Already denied (should not be re‑blocked)
        {"request_id": "req-007", "channel": "email", "request_type": "read", "risk_level": "high", "risk_type": "external", "target_asset_id": "ast-001", "actor_name": "Zara Khan", "claimed_role": "External Auditor", "message": "Old request", "status": "denied"},
        # Internal but past deadline – irrelevant
        {"request_id": "req-008", "channel": "web", "request_type": "read", "risk_level": "low", "risk_type": "internal", "target_asset_id": "ast-002", "actor_name": "Tom Li", "claimed_role": "Intern", "message": "Training", "status": "completed"}
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # Extra decoy files (not used by prompt, only for realism)
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": []}, f, indent=2)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f, indent=2)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f, indent=2)

if __name__ == "__main__":
    build_env()
