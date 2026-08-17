import os
import json
import shutil
from datetime import datetime

def build_env():
    # 清理已有内容（从头构建）
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("ops"):
        shutil.rmtree("ops")
    
    # 创建目录结构
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/social", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ====== 联系人 ======
    contacts = [
        {
            "contact_id": "mira_chen",
            "name": "Mira Chen",
            "email": "mira.chen@auroralabs.com",
            "role": "Legal Counsel",
            "team": "Legal",
            "social_handle": "@mirachen_legal"
        },
        {
            "contact_id": "priya_dev",
            "name": "Priya Dev",
            "email": "priya.dev@auroralabs.com",
            "role": "Support Manager",
            "team": "Support",
            "social_handle": "@priyadev_ops"
        },
        {
            "contact_id": "jon_bell",
            "name": "Jon Bell",
            "email": "jon@example.com",
            "role": "Creator",
            "team": "External",
            "social_handle": "@jonbellops"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ====== 账号 ======
    accounts = [
        {
            "account_id": "auroralabs",
            "display_name": "Aurora Labs",
            "brand_name": "Aurora Launch Systems",
            "x_handle": "@AuroraLabs",
            "reddit_profile": "u/AuroraLabs_Official",
            "default_reddit_community": "r/spacelaunch",
            "voice": ["professional", "enthusiastic"],
            "cta": "🚀 Learn more at auroralabs.com",
            "compliance_notes": ["No unverified milestones", "Include legal disclaimer"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ====== 邮件（干扰项 + 目标） ======
    emails = [
        {
            "id": "em_001",
            "thread_id": "thr_week001",
            "folder": "inbox",
            "sender_id": "jon_bell",
            "subject": "Weekly Sync - Feb 10",
            "timestamp": "2025-02-10T09:00:00Z",
            "importance": "low",
            "labels": ["internal"],
            "body": "Hey folks, just a quick sync on this week's progress. Nothing urgent.",
            "attachments": []
        },
        {
            "id": "em_002",
            "thread_id": "thr_orbital_v3",
            "folder": "inbox",
            "sender_id": "mira_chen",
            "subject": "Orbital Launch Brief v3 - Draft",
            "timestamp": "2025-02-08T14:30:00Z",
            "importance": "high",
            "labels": ["legal", "draft"],
            "body": "Please review the draft brief for the orbital launch. Attached is v3. We still need CEO sign-off on the date.",
            "attachments": [
                {
                    "attachment_id": "att_orbital_brief_v3",
                    "filename": "orbital_brief_v3.json",
                    "mime_type": "application/json"
                }
            ]
        },
        {
            "id": "em_003",
            "thread_id": "thr_orbital_approved",
            "folder": "inbox",
            "sender_id": "mira_chen",
            "subject": "Re: Orbital Launch Brief – Approved",
            "timestamp": "2025-02-11T08:15:00Z",
            "importance": "high",
            "labels": ["legal", "approved", "urgent"],
            "body": "Final approval obtained. The date and product name are in the attached v5 brief. Proceed with official announcement.",
            "attachments": [
                {
                    "attachment_id": "att_orbital_brief_v5",
                    "filename": "orbital_brief_v5.json",
                    "mime_type": "application/json"
                }
            ]
        },
        {
            "id": "em_004",
            "thread_id": "thr_budget_q1",
            "folder": "inbox",
            "sender_id": "priya_dev",
            "subject": "Q1 Budget Review",
            "timestamp": "2025-02-09T11:00:00Z",
            "importance": "medium",
            "labels": ["finance"],
            "body": "Please check the Q1 budget allocation for the launch campaign. Some items need adjustment.",
            "attachments": []
        }
    ]
    for em in emails:
        with open(f"data/emails/{em['id']}.json", "w") as f:
            json.dump(em, f, indent=2)

    # ====== 附件 ======
    # 干扰附件 v3
    att_v3 = {
        "attachment_id": "att_orbital_brief_v3",
        "brief_version": "v3",
        "launch_date": "2025-07-09",      # 错误版本
        "product_name": "Aurora LV-7",     # 旧产品名
        "payload_mass_kg": 4500,
        "orbit": "LEO"
    }
    with open("data/attachments/att_orbital_brief_v3.json", "w") as f:
        json.dump(att_v3, f, indent=2)

    # 正确附件 v5
    att_v5 = {
        "attachment_id": "att_orbital_brief_v5",
        "brief_version": "v5",
        "launch_date": "2025-07-16",      # 正确日期
        "product_name": "Aurora LV-9",     # 正确产品名
        "payload_mass_kg": 5200,
        "orbit": "GTO"
    }
    with open("data/attachments/att_orbital_brief_v5.json", "w") as f:
        json.dump(att_v5, f, indent=2)

    # ====== 社交帖子 ======
    social_posts = [
        {
            "post_id": "post_001",
            "platform": "reddit",
            "author_id": "spacefan42",
            "title": "Launch date??",
            "community": "r/spacelaunch",
            "content": "Does anyone know when Aurora Labs is planning their next launch? I heard rumors about July.",
            "timestamp": "2025-02-11T12:00:00Z",
            "tags": ["question", "launch"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "post_002",
            "platform": "x",
            "author_id": "techreview",
            "title": "Excited about the launch!",
            "community": "twitter",
            "content": "Can't wait for the Aurora LV-9 launch! Any hints on the date?",
            "timestamp": "2025-02-10T20:30:00Z",
            "tags": ["excitement", "rocket"],
            "needs_response": False,
            "replies": []
        },
        {
            "post_id": "post_003",
            "platform": "reddit",
            "author_id": "rocketjunkie",
            "title": "Any news from Aurora?",
            "community": "r/space",
            "content": "Their website hasn't updated in weeks. Is the program still alive?",
            "timestamp": "2025-02-09T18:45:00Z",
            "tags": ["inquiry"],
            "needs_response": False,
            "replies": []
        }
    ]
    for sp in social_posts:
        with open(f"data/social/{sp['post_id']}.json", "w") as f:
            json.dump(sp, f, indent=2)

if __name__ == "__main__":
    build_env()
