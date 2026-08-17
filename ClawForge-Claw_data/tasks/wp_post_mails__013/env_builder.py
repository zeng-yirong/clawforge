import os
import json
import random

def build_env():
    # 确保基础目录存在
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/social", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 留空，由 agent 写入

    # ========== 附件 ==========
    # 正确的最新批准简报 v3
    att_brief_v3 = {
        "mission_name": "Orbital Dawn",
        "launch_window": "2025-06-15T04:30:00Z to 2025-06-15T06:30:00Z",
        "payload": "AuroraCom-2 communications satellite",
        "orbit": "LEO 550km",
        "version": 3,
        "status": "approved"
    }
    with open("data/attachments/att_brief_v3.json", "w") as f:
        json.dump(att_brief_v3, f, indent=2)

    # 干扰：同样版本但 draft 状态（时间更短）
    att_brief_v3_draft = {
        "mission_name": "Orbital Dawn",
        "launch_window": "2025-06-16T04:30:00Z to 2025-06-16T06:30:00Z",
        "payload": "AuroraCom-2 communications satellite",
        "orbit": "LEO 550km",
        "version": 3,
        "status": "draft"
    }
    with open("data/attachments/att_brief_v3_draft.json", "w") as f:
        json.dump(att_brief_v3_draft, f, indent=2)

    # 干扰：旧的批准简报 v2
    att_brief_v2 = {
        "mission_name": "Orbital Dawn",
        "launch_window": "2025-05-20T02:00:00Z to 2025-05-20T04:00:00Z",
        "payload": "AuroraCom-1 experimental",
        "orbit": "LEO 400km",
        "version": 2,
        "status": "approved"
    }
    with open("data/attachments/att_brief_v2.json", "w") as f:
        json.dump(att_brief_v2, f, indent=2)

    # 另一个无关附件（财务数据）
    att_finance = {
        "budget_quarter": "Q2 2025",
        "balance": 1250000.00,
        "currency": "USD"
    }
    with open("data/attachments/att_finance.json", "w") as f:
        json.dump(att_finance, f, indent=2)

    # ========== 邮件 ==========
    # 正确邮件（最新批准，标签含 "approved"）
    email_approved = {
        "id": "em_001",
        "thread_id": "t001",
        "folder": "inbox",
        "sender_id": "ceo@auroralabs.com",
        "subject": "Brief v3 – Approved",
        "timestamp": "2025-06-10T09:00:00Z",
        "importance": "high",
        "labels": ["approved", "urgent"],
        "body": "See attached.",
        "attachments": ["att_brief_v3"]
    }
    with open("data/emails/em_001.json", "w") as f:
        json.dump(email_approved, f, indent=2)

    # 干扰：draft 标签的 v3 邮件（更早时间）
    email_draft = {
        "id": "em_002",
        "thread_id": "t001",
        "folder": "inbox",
        "sender_id": "mission_planning@auroralabs.com",
        "subject": "Brief v3 – Draft for Review",
        "timestamp": "2025-06-09T12:00:00Z",
        "importance": "medium",
        "labels": ["draft"],
        "body": "Please review.",
        "attachments": ["att_brief_v3_draft"]
    }
    with open("data/emails/em_002.json", "w") as f:
        json.dump(email_draft, f, indent=2)

    # 干扰：旧批准 v2 邮件
    email_old_approved = {
        "id": "em_003",
        "thread_id": "t002",
        "folder": "inbox",
        "sender_id": "ceo@auroralabs.com",
        "subject": "Brief v2 – Approved",
        "timestamp": "2025-06-08T08:00:00Z",
        "importance": "high",
        "labels": ["approved"],
        "body": "Old version.",
        "attachments": ["att_brief_v2"]
    }
    with open("data/emails/em_003.json", "w") as f:
        json.dump(email_old_approved, f, indent=2)

    # 完全无关的邮件（财务）
    email_finance = {
        "id": "em_004",
        "thread_id": "t003",
        "folder": "inbox",
        "sender_id": "finance@auroralabs.com",
        "subject": "Q2 Budget Summary",
        "timestamp": "2025-06-07T14:30:00Z",
        "importance": "low",
        "labels": ["finance"],
        "body": "Attached.",
        "attachments": ["att_finance"]
    }
    with open("data/emails/em_004.json", "w") as f:
        json.dump(email_finance, f, indent=2)

    # ========== accounts.json ==========
    accounts = {
        "accounts": [
            {
                "account_id": "auroralabs",
                "display_name": "Aurora Labs",
                "brand_name": "Aurora Labs Inc.",
                "x_handle": "@auroralabs",
                "reddit_profile": "r/auroralabs",
                "default_reddit_community": "r/space",
                "voice": ["professional", "exciting"],
                "cta": "Join the mission!",
                "compliance_notes": ["No unverified claims"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ========== contacts.json（干扰） ==========
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Ava Price", "email": "ava@example.com", "role": "Community Lead", "team": "Community", "social_handle": "@avapractical"},
            {"contact_id": "c002", "name": "Jon Bell", "email": "jon@example.com", "role": "Creator", "team": "External", "social_handle": "@jonbellops"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ========== social/ 干扰帖子 ==========
    social_post = {
        "post_id": "p001",
        "platform": "x",
        "author_id": "community_bot",
        "title": "Countdown begins!",
        "community": "space",
        "content": "Preparing for launch...",
        "timestamp": "2025-06-11T10:00:00Z",
        "tags": ["launch", "countdown"],
        "needs_response": False,
        "replies": []
    }
    with open("data/social/post_001.json", "w") as f:
        json.dump(social_post, f, indent=2)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
