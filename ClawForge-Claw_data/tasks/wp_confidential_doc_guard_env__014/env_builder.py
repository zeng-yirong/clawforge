import os
import json

def build_env():
    # data/requests.json
    requests = [
        {"request_id": "req-01", "channel": "web", "request_type": "read", "risk_level": "low", "risk_type": "internal", "target_asset_id": "ast-tech-001", "actor_name": "Alice", "claimed_role": "Architecture Office", "message": "Need latest plan for review", "status": "pending"},
        {"request_id": "req-02", "channel": "email", "request_type": "read", "risk_level": "high", "risk_type": "external", "target_asset_id": "ast-tech-001", "actor_name": "Bob", "claimed_role": "External Consultant", "message": "Requesting architectural blueprint", "status": "pending"},
        {"request_id": "req-03", "channel": "api", "request_type": "download", "risk_level": "low", "risk_type": "internal", "target_asset_id": "ast-fin-001", "actor_name": "Charlie", "claimed_role": "Finance Operations", "message": "Need Q2 archive", "status": "pending"},
        {"request_id": "req-04", "channel": "email", "request_type": "read", "risk_level": "high", "risk_type": "external", "target_asset_id": "ast-fin-001", "actor_name": "Dave", "claimed_role": "External Auditor", "message": "Requesting financial records", "status": "pending"},
        {"request_id": "req-05", "channel": "web", "request_type": "read", "risk_level": "low", "risk_type": "external", "target_asset_id": "ast-pub-001", "actor_name": "Eve", "claimed_role": "External", "message": "Public report access", "status": "pending"},
        {"request_id": "req-06", "channel": "cli", "request_type": "read", "risk_level": "medium", "risk_type": "internal", "target_asset_id": "ast-tech-001", "actor_name": "Frank", "claimed_role": "Architecture Office", "message": "Update dependency diagram", "status": "pending"},
        {"request_id": "req-07", "channel": "email", "request_type": "download", "risk_level": "high", "risk_type": "external", "target_asset_id": "ast-fin-001", "actor_name": "Grace", "claimed_role": "Marketing", "message": "Need financial data for campaign", "status": "pending"},
        {"request_id": "req-08", "channel": "web", "request_type": "read", "risk_level": "high", "risk_type": "external", "target_asset_id": "ast-tech-001", "actor_name": "Henry", "claimed_role": "Finance Operations", "message": "Cross-department request", "status": "pending"}
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # data/assets.json
    assets = [
        {"asset_id": "ast-tech-001", "asset_name": "Unpublished Architecture Plan", "asset_type": "technical_plan", "classification": "confidential", "owner_team": "Architecture Office", "read_policy": "restricted"},
        {"asset_id": "ast-fin-001", "asset_name": "Finance Archive Bundle", "asset_type": "finance_archive", "classification": "confidential", "owner_team": "Finance Operations", "read_policy": "restricted"},
        {"asset_id": "ast-pub-001", "asset_name": "Public Report", "asset_type": "public_report", "classification": "public", "owner_team": "General", "read_policy": "open"}
    ]
    with open("data/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

    # Optionally create a dummy ops directory to avoid accidental existence (not required)
    # We leave ops/ creation to the agent.

if __name__ == "__main__":
    build_env()
