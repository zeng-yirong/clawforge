import os
import json

def build_env():
    # --- data/emails ---
    emails_dir = "data/emails"
    os.makedirs(emails_dir, exist_ok=True)

    # 干扰邮件
    distractor_emails = [
        {
            "id": "em_001",
            "thread_id": "th_001",
            "folder": "inbox",
            "sender_id": "mira.chen@auroralabs.com",
            "subject": "Draft Launch Brief v1",
            "timestamp": "2025-08-09T10:00:00Z",
            "importance": "medium",
            "labels": ["draft"],
            "body": "Here's the first draft of the brief.",
            "attachments": ["att_orbital_brief_v1"]
        },
        {
            "id": "em_002",
            "thread_id": "th_002",
            "folder": "inbox",
            "sender_id": "nina.santos@auroralabs.com",
            "subject": "Updated Brief – feedback applied",
            "timestamp": "2025-08-09T16:30:00Z",
            "importance": "high",
            "labels": ["review"],
            "body": "Incorporate legal feedback and resubmit.",
            "attachments": ["att_orbital_brief_v2"]
        },
        {
            "id": "em_003",
            "thread_id": "th_001",
            "folder": "sent",
            "sender_id": "support@auroralabs.com",
            "subject": "Re: Draft Launch Brief v1",
            "timestamp": "2025-08-09T11:00:00Z",
            "importance": "low",
            "labels": ["replied"],
            "body": "Looks good, minor changes needed.",
            "attachments": []
        },
        {
            "id": "em_004",
            "thread_id": "th_003",
            "folder": "inbox",
            "sender_id": "ceo@company.com",
            "subject": "Final Approved Brief – urgent",
            "timestamp": "2025-08-10T14:30:00Z",
            "importance": "high",
            "labels": ["approved", "urgent"],
            "body": "Please find the final approved brief attached. Proceed with launch preparation.",
            "attachments": ["att_orbital_brief_v3"]
        },
        {
            "id": "em_005",
            "thread_id": "th_004",
            "folder": "inbox",
            "sender_id": "jon.bell@auroralabs.com",
            "subject": "Old brief – ignore",
            "timestamp": "2025-08-08T08:15:00Z",
            "importance": "low",
            "labels": ["archived"],
            "body": "This is outdated.",
            "attachments": ["att_orbital_brief_v1"]
        }
    ]

    for mail in distractor_emails:
        # 把 CEO 那封的正确邮件映射到 em_004，这样只有一个满足条件
        # 这里我们把 em_004 作为正确邮件，其他都是干扰
        with open(os.path.join(emails_dir, f"{mail['id']}.json"), "w") as f:
            json.dump(mail, f, indent=2)

    # --- data/attachments ---
    att_dir = "data/attachments"
    os.makedirs(att_dir, exist_ok=True)

    # 附件内容（v3 是正确答案）
    attachments = {
        "att_orbital_brief_v1": {
            "mission_name": "Aurora Prime",
            "launch_date": "2025-08-20",
            "tagline": "Light the sky",
            "title": "Aurora Prime Launch",
            "post_content": "Aurora Prime is launching on August 20. Be there!"
        },
        "att_orbital_brief_v2": {
            "mission_name": "Nova Horizon",
            "launch_date": "2025-09-15",
            "tagline": "Beyond the horizon",
            "title": "Nova Horizon Mission",
            "post_content": "Nova Horizon will explore the unknown. Stay tuned."
        },
        "att_orbital_brief_v3": {
            "mission_name": "Orbital Dawn",
            "launch_date": "2025-09-01",
            "tagline": "Dawn of a new era",
            "title": "Orbital Dawn Launch Announcement",
            "post_content": "Join us for the launch of Orbital Dawn on September 1st, 2025. This mission marks a milestone in space exploration. #OrbitalDawn"
        }
    }

    for att_id, content in attachments.items():
        with open(os.path.join(att_dir, f"{att_id}.json"), "w") as f:
            json.dump(content, f, indent=2)

    # 额外干扰文件（accounts.json, contacts.json）— 可选，增加真实性
    accounts = [
        {
            "account_id": "acc_001",
            "display_name": "Aurora Labs",
            "brand_name": "Aurora Labs",
            "x_handle": "@auroralabs",
            "reddit_profile": "u/auroralabs",
            "default_reddit_community": "r/space",
            "voice": ["professional", "inspirational"],
            "cta": "Learn more at auroralabs.com",
            "compliance_notes": ["Approved by legal"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c_001", "name": "Ava Price", "email": "ava@example.com", "role": "Community Lead", "team": "Community", "social_handle": "@avapractical"},
        {"contact_id": "c_002", "name": "Jon Bell", "email": "jon@example.com", "role": "Creator", "team": "External", "social_handle": "@jonbellops"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
