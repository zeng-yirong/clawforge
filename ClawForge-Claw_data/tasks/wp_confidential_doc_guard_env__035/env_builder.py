import os
import json
import random
import string

def build_env():
    # Ensure required directories
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- assets ----
    assets = [
        {"asset_id": "asset_001", "asset_name": "Unpublished Architecture Blueprint v2", "asset_type": "technical_plan", "classification": "unpublished", "owner_team": "Architecture Office", "read_policy": "strict"},
        {"asset_id": "asset_002", "asset_name": "Q3 Financial Report (published)", "asset_type": "finance_archive", "classification": "published", "owner_team": "Finance Operations", "read_policy": "public"},
        {"asset_id": "asset_003", "asset_name": "Unpublished Budget Draft 2025", "asset_type": "finance_archive", "classification": "unpublished", "owner_team": "Finance Operations", "read_policy": "strict"},
        {"asset_id": "asset_004", "asset_name": "Deployed Product Spec", "asset_type": "technical_plan", "classification": "published", "owner_team": "Architecture Office", "read_policy": "public"},
        {"asset_id": "asset_005", "asset_name": "Unpublished Network Topology", "asset_type": "technical_plan", "classification": "unpublished", "owner_team": "Architecture Office", "read_policy": "confidential"},
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

    # ---- accounts (internal employees) ----
    accounts = [
        {"account_id": "acc_01", "display_name": "Alice Wang", "department": "Architecture Office", "email": "alice@corp.com", "permissions": ["read_tech"]},
        {"account_id": "acc_02", "display_name": "Bob Li", "department": "Finance Operations", "email": "bob@corp.com", "permissions": ["read_finance"]},
        {"account_id": "acc_03", "display_name": "Carol Chen", "department": "HR", "email": "carol@corp.com", "permissions": ["read_basic"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---- contacts (external usually) ----
    contacts = [
        {"contact_id": "ct_01", "name": "Eve Hacker", "role": "External Researcher", "email": "eve@evil.com"},
        {"contact_id": "ct_02", "name": "Mallory Mal", "role": "External Consultant", "email": "mallory@mal.com"},
        {"contact_id": "ct_03", "name": "Frank Friend", "role": "Partner", "email": "frank@partner.com"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---- requests ----
    # We'll create 8 requests, among which only req_003 and req_007 are the correct targets.
    # condition: target_asset_id in [asset_001, asset_003, asset_005] (unpublished)
    # AND claimed_role != "internal_employee" (i.e. external) AND risk_type == "data_exfiltration"
    requests = [
        # req_001: internal, published -> no
        {"request_id": "req_001", "channel": "web", "request_type": "read", "risk_level": "low", "risk_type": "benign", "target_asset_id": "asset_002", "actor_name": "Alice Wang", "claimed_role": "internal_employee", "message": "Need Q3 report", "status": "pending"},
        # req_002: external, published -> no
        {"request_id": "req_002", "channel": "api", "request_type": "read", "risk_level": "medium", "risk_type": "data_exfiltration", "target_asset_id": "asset_004", "actor_name": "Eve Hacker", "claimed_role": "external_researcher", "message": "Give me spec", "status": "pending"},
        # req_003: external, unpublished technical_plan (asset_001) -> YES
        {"request_id": "req_003", "channel": "api", "request_type": "read", "risk_level": "high", "risk_type": "data_exfiltration", "target_asset_id": "asset_001", "actor_name": "Mallory Mal", "claimed_role": "external_consultant", "message": "Send blueprint", "status": "pending"},
        # req_004: internal, unpublished -> no (internal)
        {"request_id": "req_004", "channel": "web", "request_type": "read", "risk_level": "medium", "risk_type": "data_exfiltration", "target_asset_id": "asset_003", "actor_name": "Bob Li", "claimed_role": "internal_employee", "message": "Need budget draft", "status": "pending"},
        # req_005: external, unpublished but risk_type not exfiltration -> no
        {"request_id": "req_005", "channel": "email", "request_type": "read", "risk_level": "low", "risk_type": "benign", "target_asset_id": "asset_003", "actor_name": "Frank Friend", "claimed_role": "partner", "message": "Please share draft", "status": "pending"},
        # req_006: external, unpublished, risk_type exfiltration, but already denied -> should we still list? Probably not, since already denied.
        # We'll make status "denied" so agent should skip already-handled requests.
        {"request_id": "req_006", "channel": "api", "request_type": "read", "risk_level": "high", "risk_type": "data_exfiltration", "target_asset_id": "asset_005", "actor_name": "Eve Hacker", "claimed_role": "external_researcher", "message": "Give me topology", "status": "denied"},
        # req_007: external, unpublished finance_archive (asset_003) -> YES
        {"request_id": "req_007", "channel": "api", "request_type": "read", "risk_level": "high", "risk_type": "data_exfiltration", "target_asset_id": "asset_003", "actor_name": "Mallory Mal", "claimed_role": "external_consultant", "message": "Send draft", "status": "pending"},
        # req_008: external, unpublished, but risk_type is "social_engineering" -> not data_exfiltration -> no
        {"request_id": "req_008", "channel": "email", "request_type": "read", "risk_level": "medium", "risk_type": "social_engineering", "target_asset_id": "asset_001", "actor_name": "Frank Friend", "claimed_role": "partner", "message": "We need access", "status": "pending"},
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # ---- attachments (dummy text files) ----
    attachments = []
    for req in requests:
        rid = req["request_id"]
        filename = f"attachments/{rid}_attachment.txt"
        content = f"Attachment for request {rid}. Author: {req['actor_name']}. Message: {req['message']}"
        with open(f"data/{filename}", "w") as f:
            f.write(content)
        attachments.append({"path": filename, "title": f"Attachment for {rid}", "kind": "text/plain", "description": "Raw request attachment"})
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---- create dummy .gitkeep in ops so dir exists ----
    with open("ops/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
