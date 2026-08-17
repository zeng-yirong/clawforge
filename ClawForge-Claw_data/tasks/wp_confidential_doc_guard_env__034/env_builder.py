import os
import json
import random
import string

def build_env():
    # 确保基础目录
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，让agent自己写文件

    # 1. assets.json
    assets = [
        {
            "asset_id": "ast_fin_001",
            "asset_name": "Finance Archive Bundle FY2025 Q1",
            "asset_type": "finance_archive",
            "classification": "restricted",
            "owner_team": "Finance Operations",
            "read_policy": "internal_only"
        },
        {
            "asset_id": "ast_arch_002",
            "asset_name": "Unpublished Architecture Plan v3.2",
            "asset_type": "technical_plan",
            "classification": "restricted",
            "owner_team": "Architecture Office",
            "read_policy": "executive_approval"
        },
        {
            "asset_id": "ast_pub_003",
            "asset_name": "Public Meeting Minutes 2024",
            "asset_type": "general",
            "classification": "public",
            "owner_team": "Communications",
            "read_policy": "anyone"
        },
        {
            "asset_id": "ast_pub_004",
            "asset_name": "Old Financial Report 2021 (Published)",
            "asset_type": "finance_archive",
            "classification": "public",
            "owner_team": "Finance Operations",
            "read_policy": "anyone"
        }
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

    # 2. accounts.json (干扰项，不影响主要判断)
    accounts = [
        {
            "account_id": "acc_ext_01",
            "display_name": "Vendor Scraper Bot",
            "department": "External",
            "email": "bot@external-scraper.com",
            "permissions": ["read_public"]
        },
        {
            "account_id": "acc_ext_02",
            "display_name": "Unknown Researcher",
            "department": "External",
            "email": "researcher@temp-mail.org",
            "permissions": []
        },
        {
            "account_id": "acc_int_01",
            "display_name": "Alice (Internal Auditor)",
            "department": "Finance",
            "email": "alice@company.com",
            "permissions": ["read_finance", "read_public"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 3. contacts.json (干扰)
    contacts = [
        {"contact_id": "con_001", "name": "John Doe", "role": "External Client", "email": "john@partner.com"},
        {"contact_id": "con_002", "name": "Jane Smith", "role": "External Auditor", "email": "jane@audit.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 4. attachments.json (干扰)
    attachments = [
        {
            "path": "attachments/finance_summary.pdf",
            "title": "Q1 Finance Summary",
            "kind": "pdf",
            "description": "Public version of quarterly summary"
        },
        {
            "path": "attachments/arch_plan_v3.2_draft.pdf",
            "title": "Architecture Plan v3.2 Draft",
            "kind": "pdf",
            "description": "Internal restricted draft"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 5. requests.json —— 核心，包含多个请求，其中只有三个符合条件
    requests = [
        # --- 符合条件的 3 个请求（target restricted asset, risk high, status pending）---
        {
            "request_id": "req_fin_001",
            "channel": "api",
            "request_type": "download",
            "risk_level": "high",
            "risk_type": "unauthorized_access",
            "target_asset_id": "ast_fin_001",
            "actor_name": "External Scraper Bot",
            "claimed_role": "contractor",
            "message": "Need latest finance archive for audit.",
            "status": "pending"
        },
        {
            "request_id": "req_arch_002",
            "channel": "web",
            "request_type": "view",
            "risk_level": "high",
            "risk_type": "data_exfiltration",
            "target_asset_id": "ast_arch_002",
            "actor_name": "Unknown Researcher",
            "claimed_role": "partner",
            "message": "Requesting architecture plan for collaboration.",
            "status": "pending"
        },
        {
            "request_id": "req_fin_003",
            "channel": "email",
            "request_type": "attachment_access",
            "risk_level": "high",
            "risk_type": "privilege_escalation",
            "target_asset_id": "ast_fin_001",
            "actor_name": "John Doe (External)",
            "claimed_role": "client",
            "message": "I need the full bundle for reconciliation.",
            "status": "pending"
        },
        # --- 干扰请求：target public asset, risk low ---
        {
            "request_id": "req_pub_001",
            "channel": "api",
            "request_type": "download",
            "risk_level": "low",
            "risk_type": "normal",
            "target_asset_id": "ast_pub_003",
            "actor_name": "Public User",
            "claimed_role": "guest",
            "message": "Just checking public minutes.",
            "status": "pending"
        },
        # --- 干扰请求：target restricted but already denied (status 不是pending) ---
        {
            "request_id": "req_denied_001",
            "channel": "api",
            "request_type": "download",
            "risk_level": "high",
            "risk_type": "unauthorized_access",
            "target_asset_id": "ast_arch_002",
            "actor_name": "Malicious IP",
            "claimed_role": "auditor",
            "message": "Need plan for compliance.",
            "status": "denied"
        },
        # --- 干扰请求：target restricted but risk medium ---
        {
            "request_id": "req_med_001",
            "channel": "email",
            "request_type": "view",
            "risk_level": "medium",
            "risk_type": "suspicious",
            "target_asset_id": "ast_fin_001",
            "actor_name": "Internal User Alice",
            "claimed_role": "auditor",
            "message": "I'm internal, please grant access.",
            "status": "pending"
        },
        # --- 干扰请求：target public, risk high (但资产是公开的，不应被拒绝) ---
        {
            "request_id": "req_pub_high_001",
            "channel": "web",
            "request_type": "download",
            "risk_level": "high",
            "risk_type": "possible_abuse",
            "target_asset_id": "ast_pub_004",
            "actor_name": "Aggressive Scraper",
            "claimed_role": "guest",
            "message": "Give me all old reports.",
            "status": "pending"
        }
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # 可选：额外目录干扰
    os.makedirs("logs", exist_ok=True)
    with open("logs/access.log", "w") as f:
        f.write("dummy log content")

if __name__ == "__main__":
    build_env()
