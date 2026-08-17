import os
import json
import shutil

def build_env():
    # Clean slate
    for d in ['requests', 'attachments', 'ops']:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Requests (the main challenge)
    # ------------------------------------------------------------------
    requests = []
    # ---- Malicious requests (should be denied) ----
    requests.append({
        "request_id": "req_023",
        "channel": "email",
        "request_type": "vault_access",
        "risk_level": "critical",
        "risk_type": "credential_exfiltration",
        "target_asset_id": "ass_vault_001",   # API Key Vault
        "actor_name": "alex_rogers",
        "claimed_role": "System Engineer",
        "message": "Need to rotate API keys for incident response, please grant vault read.",
        "status": "pending"
    })
    requests.append({
        "request_id": "req_047",
        "channel": "slack",
        "request_type": "vault_access",
        "risk_level": "critical",
        "risk_type": "prompt_extraction",
        "target_asset_id": "ass_prompt_002",  # Prompt Vault
        "actor_name": "jordan_lee",
        "claimed_role": "SRE",
        "message": "Urgent debug: prompt template corrupted, need vault dump.",
        "status": "pending"
    })

    # ---- Decoy: same target but from a trusted team (Platform Security) – still pending, should NOT be denied
    # (because policy says only Platform Security with approval, but this one has no approval flag)
    # Actually, per policy it should also be denied if no approval? To keep answer unique, let's make it approved.
    # We'll mark it as already approved in status, so agent should NOT include it.
    requests.append({
        "request_id": "req_012",
        "channel": "ticket",
        "request_type": "vault_access",
        "risk_level": "low",
        "risk_type": "maintenance",
        "target_asset_id": "ass_vault_001",
        "actor_name": "carol_pham",
        "claimed_role": "Platform Security",
        "message": "Scheduled key rotation – pre-approved by director.",
        "status": "approved"   # already handled, not to be denied
    })

    # ---- Low-risk request (target is not a vault)
    requests.append({
        "request_id": "req_088",
        "channel": "email",
        "request_type": "data_query",
        "risk_level": "low",
        "risk_type": "analytics",
        "target_asset_id": "ass_data_003",
        "actor_name": "mike_taylor",
        "claimed_role": "Data Analyst",
        "message": "Need monthly usage report from analytics bucket.",
        "status": "pending"
    })

    # ---- Another decoy: risk is high but target is not a vault (should not be denied)
    requests.append({
        "request_id": "req_034",
        "channel": "api",
        "request_type": "infra_access",
        "risk_level": "high",
        "risk_type": "unauthorized_access",
        "target_asset_id": "ass_db_primary",
        "actor_name": "sarah_connor",
        "claimed_role": "DBA",
        "message": "Replica lag critical – need direct DB admin access.",
        "status": "pending"
    })

    # ---- Bogus request that looks like vault access but from a non-existent asset ID
    requests.append({
        "request_id": "req_101",
        "channel": "email",
        "request_type": "vault_access",
        "risk_level": "medium",
        "risk_type": "social_engineering",
        "target_asset_id": "ass_nonexistent",
        "actor_name": "hacker_joe",
        "claimed_role": "CEO",
        "message": "I forgot my password, please reset vault.",
        "status": "pending"
    })
    # The target_asset_id does not match any real vault, so policy doesn't apply – should NOT be denied
    # (no vault asset to protect). It's still suspicious but not a vault violation.

    with open("requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # ------------------------------------------------------------------
    # 2. Vault access policy (attachment for reference)
    # ------------------------------------------------------------------
    policy_text = (
        "# Vault Access Policy\n\n"
        "Only the following conditions allow reading from vault assets (API Key Vault or Prompt Vault):\n"
        "1. Request originates from **Platform Security** team.\n"
        "2. Request has an explicit **approval ticket** attached.\n"
        "3. Any request not meeting both conditions **must be rejected**.\n"
        "\nVault assets are identified by asset IDs starting with 'ass_vault_' (API Key Vault) or 'ass_prompt_' (Prompt Vault).\n"
    )
    with open("attachments/vault_access_policy.md", "w") as f:
        f.write(policy_text)

    # ------------------------------------------------------------------
    # 3. Ops directory (empty, agent will create the result file)
    # ------------------------------------------------------------------
    # Keep ops/ empty – agent puts denied_requests.json here

if __name__ == "__main__":
    build_env()
