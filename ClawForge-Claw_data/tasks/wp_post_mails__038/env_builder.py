import os
import json
from datetime import datetime, timezone, timedelta

def build_env():
    # 创建目录
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 留空，agent会写

    # 创建干扰附件
    attachments = {
        "draft_v1.txt": "BRIEF_DRAFT_001",
        "old_brief.txt": "BRIEF_OLD_002",
        "final_brief.txt": "APPROVED_BRIEF_038",
        "rejected_brief.txt": "BRIEF_REJECT_004",
        "draft_v2.txt": "BRIEF_DRAFT_005"
    }
    for fname, content in attachments.items():
        with open(f"data/attachments/{fname}", "w") as f:
            f.write(content)

    # 邮件模板
    base_time = datetime(2025, 3, 29, 10, 0, 0, tzinfo=timezone.utc)

    emails = [
        {
            "id": "em_001",
            "folder": "inbox",
            "sender_id": "contact_003",
            "subject": "Draft Launch Brief v1",
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
            "importance": "low",
            "labels": ["draft"],
            "attachments": [{"attachment_id": "att_draft1", "filename": "draft_v1.txt"}],
            "body": "Early draft, please review."
        },
        {
            "id": "em_002",
            "folder": "inbox",
            "sender_id": "contact_002",
            "subject": "Approved Brief (old)",
            "timestamp": (base_time - timedelta(days=1)).isoformat(),
            "importance": "high",
            "labels": ["approved", "old"],
            "attachments": [{"attachment_id": "att_old", "filename": "old_brief.txt"}],
            "body": "This was approved last week, but superseded."
        },
        {
            "id": "em_003",
            "folder": "inbox",
            "sender_id": "contact_001",
            "subject": "[FINAL] Approved Launch Brief",
            "timestamp": base_time.isoformat(),
            "importance": "high",
            "labels": ["approved", "final"],
            "attachments": [{"attachment_id": "att_final", "filename": "final_brief.txt"}],
            "body": "Here is the final approved brief. Please use this."
        },
        {
            "id": "em_004",
            "folder": "inbox",
            "sender_id": "contact_004",
            "subject": "Rejected Brief",
            "timestamp": (base_time - timedelta(hours=3)).isoformat(),
            "importance": "medium",
            "labels": ["rejected"],
            "attachments": [{"attachment_id": "att_rejected", "filename": "rejected_brief.txt"}],
            "body": "This version was rejected by legal."
        },
        {
            "id": "em_005",
            "folder": "inbox",
            "sender_id": "contact_005",
            "subject": "Revised Draft",
            "timestamp": (base_time - timedelta(hours=1)).isoformat(),
            "importance": "low",
            "labels": ["draft", "revised"],
            "attachments": [{"attachment_id": "att_draft2", "filename": "draft_v2.txt"}],
            "body": "Another revision, not yet approved."
        }
    ]

    for email in emails:
        with open(f"data/emails/{email['id']}.json", "w") as f:
            json.dump(email, f, indent=2)

    # 可选的辅助文件（添加环境丰富度，但不影响答案）
    accounts = [
        {
            "account_id": "acct_001",
            "display_name": "Aurora Labs",
            "brand_name": "Aurora",
            "x_handle": "@aurora_ops",
            "reddit_profile": "u/aurora_official",
            "default_reddit_community": "r/aurora",
            "voice": ["professional", "enthusiastic"],
            "cta": "Check out our latest launch!",
            "compliance_notes": ["no forward-looking statements"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "contact_001", "name": "Mira Chen", "email": "mira.chen@auroralabs.com", "role": "Product Marketing Lead", "team": "Marketing", "social_handle": "@mirachen_legal"},
        {"contact_id": "contact_002", "name": "Jon Bell", "email": "jon@example.com", "role": "Creator", "team": "External", "social_handle": "@jonbellops"},
        {"contact_id": "contact_003", "name": "Priya Dev", "email": "priya.dev@auroralabs.com", "role": "Power User", "team": "External", "social_handle": "@priyadev_ops"},
        {"contact_id": "contact_004", "name": "Rafael Moore", "email": "rafael.moore@auroralabs.com", "role": "Legal Counsel", "team": "Legal", "social_handle": "@rafaelmoore"},
        {"contact_id": "contact_005", "name": "Owen Park", "email": "owen.park@auroralabs.com", "role": "Support Manager", "team": "Support", "social_handle": "@owen_builds"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 社交帖子干扰（可选）
    os.makedirs("data/social", exist_ok=True)
    posts = [
        {"post_id": "post_001", "platform": "x", "author_id": "acct_001", "title": "Old Announcement", "community": "general", "content": "We're launching soon...", "timestamp": (base_time - timedelta(days=10)).isoformat(), "tags": ["old"], "needs_response": False, "replies": []},
        {"post_id": "post_002", "platform": "reddit", "author_id": "acct_001", "title": "Draft Post", "community": "r/aurora", "content": "Draft content not final.", "timestamp": (base_time - timedelta(days=5)).isoformat(), "tags": ["draft"], "needs_response": False, "replies": []}
    ]
    for post in posts:
        with open(f"data/social/{post['post_id']}.json", "w") as f:
            json.dump(post, f, indent=2)

if __name__ == "__main__":
    build_env()
