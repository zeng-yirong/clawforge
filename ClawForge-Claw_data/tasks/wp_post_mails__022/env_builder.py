import os
import json
import datetime

def build_env():
    # ----- 目录结构 -----
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/social", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # agent 输出目录，初始空

    # ----- 联系人 -----
    contacts = [
        {"contact_id": "c001", "name": "Mia Hart", "email": "mia.hart@auroralabs.com", "role": "Community Lead", "team": "Community", "social_handle": "mia_hart"},
        {"contact_id": "c002", "name": "Mira Chen", "email": "mira.chen@auroralabs.com", "role": "Product Marketing Lead", "team": "Marketing", "social_handle": "@mira_chen"},
        {"contact_id": "c003", "name": "Ava Price", "email": "ava@example.com", "role": "Creator", "team": "External", "social_handle": "@avapractical"},
        {"contact_id": "c004", "name": "Jon Bell", "email": "jon@example.com", "role": "Support Manager", "team": "Support", "social_handle": "@jonbellops"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ----- 账户 -----
    accounts = [
        {
            "account_id": "ax_2024",
            "display_name": "AuroraX Official",
            "brand_name": "AuroraX",
            "x_handle": "@AuroraX",
            "reddit_profile": "u/AuroraX_Team",
            "default_reddit_community": "r/aurora",
            "voice": ["professional", "excited"],
            "cta": "Join the waitlist at aurorax.io/waitlist",
            "compliance_notes": ["no false claims", "include launch date"]
        },
        {
            "account_id": "legacy_2023",
            "display_name": "Aurora Legacy",
            "brand_name": "Aurora",
            "x_handle": "@AuroraLegacy",
            "reddit_profile": "u/aurora_legacy",
            "default_reddit_community": "r/oldAurora",
            "voice": ["casual"],
            "cta": "Check our blog",
            "compliance_notes": []
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ----- 附件：真正的批准简报 -----
    brief_final = """# AuroraX Launch Brief (FINAL)
Project: AuroraX
Launch Date: 2025-04-01
Mission Statement: Beyond the Horizon
Core Message: AuroraX is the next generation of orbital logistics. We are launching on 2025-04-01 with a mission to deliver payloads beyond Earth's orbit.
Key Features: • 30% faster delivery • 95% on-time rate • global coverage
Hashtags: #AuroraX #SpaceLogistics #Apr2025
"""
    with open("data/attachments/brief_v3.md", "w") as f:
        f.write(brief_final)

    # 干扰附件
    brief_draft = """# AuroraX Launch Brief (DRAFT v2)
Project: AuroraX
Launch Date: 2025-05-15
Mission: Reach for the Stars
"""
    with open("data/attachments/brief_v2_draft.md", "w") as f:
        f.write(brief_draft)

    old_brief = """# AuroraX Launch Brief (old)
Project: AuroraX
Launch Date: 2024-12-01
Mission: First Light
"""
    with open("data/attachments/brief_old.md", "w") as f:
        f.write(old_brief)

    # ----- 邮件 -----
    # 正确邮件：来自 Mira Chen，附件为 brief_v3.md
    correct_email = {
        "id": "em_022",
        "thread_id": "th_aurora_launch",
        "folder": "inbox",
        "sender_id": "c002",
        "subject": "FINAL APPROVED BRIEF – AuroraX Launch",
        "timestamp": "2025-03-28T09:00:00Z",
        "importance": "high",
        "labels": ["approved", "launch", "urgent"],
        "body": "Hi Mia, attaching the final approved brief. Please use this for all official communications. - Mira",
        "attachments": [{"attachment_id": "att_brief_v3", "filename": "brief_v3.md", "path": "data/attachments/brief_v3.md"}]
    }
    with open("data/emails/em_022.json", "w") as f:
        json.dump(correct_email, f, indent=2)

    # 干扰邮件1：旧版附件
    email_draft = {
        "id": "em_023",
        "thread_id": "th_aurora_launch",
        "folder": "inbox",
        "sender_id": "c002",
        "subject": "Re: Brief draft v2 for review",
        "timestamp": "2025-03-25T14:30:00Z",
        "importance": "medium",
        "labels": ["draft", "review"],
        "body": "Please review v2 draft attached.",
        "attachments": [{"attachment_id": "att_brief_v2", "filename": "brief_v2_draft.md", "path": "data/attachments/brief_v2_draft.md"}]
    }
    with open("data/emails/em_023.json", "w") as f:
        json.dump(email_draft, f, indent=2)

    # 干扰邮件2：来自其他人，主题相似但无附件
    email_fake = {
        "id": "em_024",
        "thread_id": "th_aurora_launch",
        "folder": "inbox",
        "sender_id": "c001",  # 来自 Mia 自己（干扰）
        "subject": "FYI: AuroraX press release draft",
        "timestamp": "2025-03-27T16:00:00Z",
        "importance": "low",
        "labels": ["draft"],
        "body": "Here's a press release draft I wrote earlier, but it's outdated.",
        "attachments": []
    }
    with open("data/emails/em_024.json", "w") as f:
        json.dump(email_fake, f, indent=2)

    # 干扰邮件3：来自外部，包含另一个附件（无关）
    email_spam = {
        "id": "em_025",
        "thread_id": "th_spam",
        "folder": "inbox",
        "sender_id": "c003",  # Ava Price
        "subject": "Exciting partnership opportunity",
        "timestamp": "2025-03-28T08:00:00Z",
        "importance": "low",
        "labels": ["spam"],
        "body": "Check out this offer!",
        "attachments": [{"attachment_id": "att_brochure", "filename": "partner_brochure.pdf", "path": "data/attachments/partner_brochure.pdf"}]
    }
    with open("data/emails/em_025.json", "w") as f:
        json.dump(email_spam, f, indent=2)
    # 创建干扰附件占位（非md，但agent应忽略）
    with open("data/attachments/partner_brochure.pdf", "w") as f:
        f.write("fake pdf content\n")

    # ----- 社交帖子（仅干扰，不用于任务） -----
    social_posts = [
        {
            "post_id": "sp_001",
            "platform": "reddit",
            "author_id": "ax_2024",
            "title": "We are excited to announce...",
            "community": "r/aurora",
            "content": "Stay tuned!",
            "timestamp": "2025-03-20T10:00:00Z",
            "tags": ["teaser"],
            "needs_response": False,
            "replies": []
        },
        {
            "post_id": "sp_002",
            "platform": "x",
            "author_id": "legacy_2023",
            "title": "",
            "community": "",
            "content": "Old news",
            "timestamp": "2025-03-15T08:00:00Z",
            "tags": [],
            "needs_response": False,
            "replies": []
        }
    ]
    for sp in social_posts:
        with open(f"data/social/{sp['post_id']}.json", "w") as f:
            json.dump(sp, f, indent=2)

if __name__ == "__main__":
    build_env()
