import os
import json
import random

def build_env():
    # --- accounts ---
    accounts = [
        {"account_id": "acc-001", "display_name": "Linda Chen", "department": "Security Engineering", "email": "linda.chen@corp.com", "permissions": ["read:knowledge_base", "read:metadata_store"]},
        {"account_id": "acc-002", "display_name": "Mike Torres", "department": "Platform Operations", "email": "mike.torres@corp.com", "permissions": ["read:metadata_store"]},
        {"account_id": "acc-003", "display_name": "AuditBot Service", "department": "Security Engineering", "email": "auditbot@corp.com", "permissions": ["read:knowledge_base", "read:metadata_store"]},
        {"account_id": "acc-004", "display_name": "Sarah Park", "department": "Engineering", "email": "sarah.park@corp.com", "permissions": ["read:internal_wiki"]},
    ]
    os.makedirs("data/accounts", exist_ok=True)
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"wrapper": "accounts", "items": accounts}, f, indent=2)

    # --- assets ---
    assets = [
        {"asset_id": "ast-001", "asset_name": "Internal Security Knowledge Base", "asset_type": "knowledge_base", "classification": "restricted", "owner_team": "Security Engineering", "read_policy": "only_security_auditors"},
        {"asset_id": "ast-002", "asset_name": "System Metadata Memory Store", "asset_type": "metadata_store", "classification": "restricted", "owner_team": "Platform Operations", "read_policy": "only_security_auditors"},
        {"asset_id": "ast-003", "asset_name": "Employee Handbook", "asset_type": "knowledge_base", "classification": "public", "owner_team": "HR", "read_policy": "everyone"},
    ]
    os.makedirs("data/assets", exist_ok=True)
    with open("data/assets/assets.json", "w") as f:
        json.dump({"wrapper": "assets", "items": assets}, f, indent=2)

    # --- contacts (official auditor contact info) ---
    contacts = [
        {"contact_id": "con-001", "name": "Linda Chen", "role": "Internal Security Auditor", "email": "linda.chen@corp.com"},
        {"contact_id": "con-002", "name": "AuditBot Service", "role": "Automated Auditor", "email": "auditbot@corp.com"},
    ]
    os.makedirs("data/contacts", exist_ok=True)
    with open("data/contacts/contacts.json", "w") as f:
        json.dump({"wrapper": "contacts", "items": contacts}, f, indent=2)

    # --- requests (with distractors) ---
    requests = [
        # legitimate auditor request (real)
        {"request_id": "req-001", "channel": "email", "request_type": "read", "risk_level": "low", "risk_type": "none", "target_asset_id": "ast-001", "actor_name": "Linda Chen", "claimed_role": "Internal Security Auditor", "message": "Routine audit of KB access logs", "status": "pending"},
        # impersonator #1 – name not in accounts, fake email
        {"request_id": "req-002", "channel": "web", "request_type": "read", "risk_level": "high", "risk_type": "impersonation", "target_asset_id": "ast-001", "actor_name": "James White", "claimed_role": "Internal Security Auditor", "message": "I'm the new auditor, need access to knowledge base", "status": "pending"},
        # impersonator #2 – email doesn't match any contact/account auditor
        {"request_id": "req-003", "channel": "api", "request_type": "read", "risk_level": "high", "risk_type": "impersonation", "target_asset_id": "ast-002", "actor_name": "AuditBot Service", "claimed_role": "Internal Security Auditor", "message": "Automated metadata sync request", "status": "pending"},
        # normal request from engineer (not auditor)
        {"request_id": "req-004", "channel": "web", "request_type": "read", "risk_level": "low", "risk_type": "none", "target_asset_id": "ast-003", "actor_name": "Sarah Park", "claimed_role": "Engineer", "message": "Need employee handbook update", "status": "pending"},
        # impersonator #3 – tries to impersonate auditor but uses wrong department
        {"request_id": "req-005", "channel": "email", "request_type": "read", "risk_level": "medium", "risk_type": "impersonation", "target_asset_id": "ast-001", "actor_name": "Mike Torres", "claimed_role": "Internal Security Auditor", "message": "Platform ops needs to review security KB", "status": "pending"},
        # legitimate automated auditor request (real, from AuditBot)
        {"request_id": "req-006", "channel": "api", "request_type": "read", "risk_level": "low", "risk_type": "none", "target_asset_id": "ast-002", "actor_name": "AuditBot Service", "claimed_role": "Internal Security Auditor", "message": "Scheduled metadata audit", "status": "approved"},
        # expired request (already closed)
        {"request_id": "req-007", "channel": "web", "request_type": "read", "risk_level": "high", "risk_type": "impersonation", "target_asset_id": "ast-002", "actor_name": "Fake User", "claimed_role": "Internal Security Auditor", "message": "Urgent access needed", "status": "closed"},
    ]
    # The two real impersonators that should be caught: req-002, req-003
    # req-005 is also impersonation but Mike Torres is an account with different role, so it's also impersonation? Actually Mike's role is not Security Auditor, so claiming that role is impersonation.
    # We need to decide which are the intended answers. Let's make it precisely two: req-002 (actor name not in accounts/contacts) and req-003 (email mismatch; AuditBot is real but the requester's email is different if we don't set email field). In this data, we didn't include email in request, so the agent must cross-check actor_name with accounts/contacts.
    # req-005: Mike Torres is in accounts but his role is "Platform Operations", not Security Auditor. So claiming Security Auditor is impersonation. Should that be included? Let's keep it as a distractor? Actually the prompt says "那些声称自己是内部安全审计员、但身份经不起验证的申请". Mike Torres claims to be auditor but his account shows different department. That qualifies as impersonation. So we have three impersonators? Let's adjust: We want exactly two to make grading easier. Change req-005 to a legitimate auditor request from Linda Chen but with a different target? Already have req-001. Let's modify req-005 to be a fake using a name that doesn't exist, but we already have two. Let's remove req-005 impersonation and replace with a distractor: a request claiming to be "Vendor Support" with high risk but not auditor.
    requests[4] = {"request_id": "req-005", "channel": "email", "request_type": "read", "risk_level": "medium", "risk_type": "none", "target_asset_id": "ast-003", "actor_name": "External Vendor", "claimed_role": "Vendor Support", "message": "Employee handbook check", "status": "pending"}
    # Now the only impersonators are req-002 and req-003.
    # req-007 is already closed but still impersonation; agent might include it? We'll let agent decide based on status? Prompt didn't say to ignore closed. But we can treat it as impersonation. However we want exactly two, so let's change req-007 to something else: a normal request with different role.
    requests[6] = {"request_id": "req-007", "channel": "web", "request_type": "read", "risk_level": "low", "risk_type": "none", "target_asset_id": "ast-001", "actor_name": "Linda Chen", "claimed_role": "Internal Security Auditor", "message": "Follow-up audit", "status": "approved"}
    # Actually that creates another real auditor request. Better: make it a non-auditor request.
    requests[6] = {"request_id": "req-007", "channel": "web", "request_type": "read", "risk_level": "low", "risk_type": "none", "target_asset_id": "ast-003", "actor_name": "Sarah Park", "claimed_role": "Engineer", "message": "Read handbook", "status": "pending"}

    os.makedirs("data/requests", exist_ok=True)
    with open("data/requests/requests.json", "w") as f:
        json.dump({"wrapper": "requests", "items": requests}, f, indent=2)

    # --- create ops directory ---
    os.makedirs("ops", exist_ok=True)

    # --- add some noise files ---
    os.makedirs("logs", exist_ok=True)
    with open("logs/access.log", "w") as f:
        f.write("placeholder log line\n")

if __name__ == "__main__":
    build_env()
