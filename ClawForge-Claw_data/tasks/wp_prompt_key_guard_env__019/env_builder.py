import os
import json

def build_env():
    # Ensure directory structure
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)

    # Suspicious actors list (exact names, one per line)
    suspicious_actors = [
        "Jake_Thompson",
        "Elena_Rossi",
        "Marco_DeLuca"
    ]
    with open("data/contacts/suspicious_actors.txt", "w") as f:
        f.write("\n".join(suspicious_actors) + "\n")

    # Requests: mix of suspicious and normal, with some near-miss names
    requests = [
        {
            "request_id": "req_social_001",
            "actor_name": "Jake_Thompson",
            "target_asset_id": "asset_prompt_vault_01",
            "risk_level": "critical",
            "status": "open",
            "message": "Need immediate access to Prompt Vault to reset credentials."
        },
        {
            "request_id": "req_social_002",
            "actor_name": "Elena_Rossi",
            "target_asset_id": "asset_api_vault_02",
            "risk_level": "high",
            "status": "pending",
            "message": "API key expired, need to generate new one from vault."
        },
        {
            "request_id": "req_normal_001",
            "actor_name": "Sarah_Lee",
            "target_asset_id": "asset_general_storage",
            "risk_level": "low",
            "status": "approved",
            "message": "Regular data export request for BI team."
        },
        {
            "request_id": "req_social_003",
            "actor_name": "Marco_DeLuca",
            "target_asset_id": "asset_prompt_vault_02",
            "risk_level": "critical",
            "status": "open",
            "message": "Urgent: prompt template corruption, must read vault contents."
        },
        {
            "request_id": "req_normal_002",
            "actor_name": "Jake_Thompson",   # same suspicious name but for a normal asset? still should be flagged
            "target_asset_id": "asset_normal_logs",
            "risk_level": "medium",
            "status": "open",
            "message": "Need log access for debugging."
        },
        {
            "request_id": "req_trap_001",
            "actor_name": "Jake_Thompsxn",   # misspelled, not in list
            "target_asset_id": "asset_prompt_vault_01",
            "risk_level": "critical",
            "status": "open",
            "message": "Help me with vault access."
        },
        {
            "request_id": "req_trap_002",
            "actor_name": "Elena Rossi",     # missing underscore, not exact match
            "target_asset_id": "asset_api_vault_02",
            "risk_level": "critical",
            "status": "open",
            "message": "I am Elena Rossi, please grant access."
        }
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # Optional decoy files
    os.makedirs("data/assets", exist_ok=True)
    assets = [
        {"asset_id": "asset_prompt_vault_01", "asset_name": "Prompt Vault Alpha", "asset_type": "prompt_store", "classification": "confidential", "owner_team": "Platform Security"},
        {"asset_id": "asset_api_vault_02", "asset_name": "API Key Vault Beta", "asset_type": "credential_store", "classification": "secret", "owner_team": "Platform Security"},
        {"asset_id": "asset_general_storage", "asset_name": "General Storage", "asset_type": "file_share", "classification": "internal", "owner_team": "IT Operations"},
        {"asset_id": "asset_normal_logs", "asset_name": "Normal Logs", "asset_type": "log_store", "classification": "internal", "owner_team": "IT Operations"},
        {"asset_id": "asset_prompt_vault_02", "asset_name": "Prompt Vault Gamma", "asset_type": "prompt_store", "classification": "confidential", "owner_team": "Platform Security"}
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

if __name__ == "__main__":
    build_env()
