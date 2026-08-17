import os
import json
from datetime import datetime

def build_env():
    # 创建目录结构
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/social", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 账户信息
    accounts = {
        "auroralabs": {
            "account_id": "auroralabs",
            "display_name": "Aurora Labs",
            "brand_name": "Aurora Labs",
            "x_handle": "@AuroraLabs",
            "reddit_profile": "u/auroralabs_official",
            "default_reddit_community": "r/SpaceX",
            "voice": ["professional", "excited", "innovative", "visionary"],
            "cta": "Join the future of space.",
            "compliance_notes": [
                "Do not mention unapproved payload mass figures",
                "Use only version 4 approved facts"
            ]
        }
    }
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 联系人（作为干扰，简化只写部分）
    contacts = [
        {"contact_id": "c001", "name": "Mia Hart", "email": "mia.hart@auroralabs.com", "role": "Product Marketing Lead", "team": "Marketing", "social_handle": "@mia_hart"},
        {"contact_id": "c002", "name": "Ava Price", "email": "ava@example.com", "role": "Community Lead", "team": "Community", "social_handle": "@avapractical"},
        {"contact_id": "c003", "name": "Jon Bell", "email": "jon@example.com", "role": "Creator", "team": "External", "social_handle": "@jonbellops"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ========== 邮件（包含干扰项） ==========
    # 真正的批准简报 v4 (最新，2025-04-10 14:30)
    emails = [
        {
            "id": "em_009",
            "thread_id": "th_orbital_launch",
            "folder": "inbox",
            "sender_id": "mia.hart@auroralabs.com",
            "subject": "Approved: Orbital Launch Brief v4 [FINAL]",
            "timestamp": "2025-04-10T14:30:00Z",
            "importance": "high",
            "labels": ["approved", "brief", "urgent"],
            "body": "Here is the final approved brief. All facts have been cleared by legal. Use this for the launch announcement. Attachment: att_brief_v4.json",
            "attachments": [
                {"id": "att_brief_v4", "filename": "orbital_launch_brief_v4.json", "mime_type": "application/json"}
            ]
        },
        {
            "id": "em_002",
            "thread_id": "th_orbital_launch",
            "folder": "inbox",
            "sender_id": "ava@example.com",
            "subject": "Draft Brief v2 – comments needed",
            "timestamp": "2025-03-28T09:15:00Z",
            "importance": "medium",
            "labels": ["draft", "brief"],
            "body": "Here is the v2 draft for review. Not yet approved.",
            "attachments": [
                {"id": "att_brief_v2_draft", "filename": "orbital_launch_brief_v2_draft.json", "mime_type": "application/json"}
            ]
        },
        {
            "id": "em_005",
            "thread_id": "th_orbital_launch",
            "folder": "inbox",
            "sender_id": "jon@example.com",
            "subject": "Review: Orbital Launch Brief v3",
            "timestamp": "2025-04-02T11:00:00Z",
            "importance": "medium",
            "labels": ["review", "brief"],
            "body": "Please review v3 before legal sign-off. Some numbers are outdated.",
            "attachments": [
                {"id": "att_brief_v3_review", "filename": "orbital_launch_brief_v3_review.json", "mime_type": "application/json"}
            ]
        },
        {
            "id": "em_007",
            "thread_id": "th_orbital_launch",
            "folder": "inbox",
            "sender_id": "priya.dev@auroralabs.com",
            "subject": "Approved Brief v2 (old) – reference only",
            "timestamp": "2025-03-20T16:45:00Z",
            "importance": "low",
            "labels": ["approved", "brief", "archive"],
            "body": "This is the old approved v2, superseded by v4. Do not use for new announcements.",
            "attachments": [
                {"id": "att_brief_v2_old", "filename": "orbital_launch_brief_v2_old.json", "mime_type": "application/json"}
            ]
        },
        # 其他无关邮件（干扰）
        {
            "id": "em_001",
            "thread_id": "th_team_sync",
            "folder": "inbox",
            "sender_id": "nina.santos@auroralabs.com",
            "subject": "Weekly marketing sync",
            "timestamp": "2025-04-08T08:00:00Z",
            "importance": "low",
            "labels": ["meeting", "internal"],
            "body": "Agenda attached.",
            "attachments": []
        },
        {
            "id": "em_003",
            "thread_id": "th_finance",
            "folder": "inbox",
            "sender_id": "owen.park@auroralabs.com",
            "subject": "Budget Q2 update",
            "timestamp": "2025-04-09T10:30:00Z",
            "importance": "high",
            "labels": ["finance"],
            "body": "See the spreadsheet.",
            "attachments": [{"id": "att_budget_q2", "filename": "budget_q2.xlsx", "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}]
        }
    ]
    for em in emails:
        with open(f"data/emails/{em['id']}.json", "w") as f:
            json.dump(em, f, indent=2)

    # ========== 附件（简报文件） ==========
    # 正确的 v4 简报
    brief_v4 = {
        "brief_id": "orbital_launch_v4",
        "version": 4,
        "approved": True,
        "mission_name": "Aurora Dawn",
        "launch_date": "2025-05-15",
        "launch_window": "14:00-16:00 UTC",
        "vehicle": "Aurora Heavy",
        "payload": "60 Starlink v2 satellites",
        "payload_mass_kg": 15600,
        "target_orbit": "LEO 550 km, 53° inclination",
        "booster_recovery": "ASDS (Just Read The Instructions)",
        "key_metrics": {
            "satellites_deployed": 60,
            "total_mass_to_orbit": 15600,
            "orbital_altitude_km": 550,
            "orbital_inclination_deg": 53
        },
        "approved_facts": [
            "First flight of Aurora Heavy with full payload fairing",
            "60 second-generation Starlink satellites",
            "Target orbit: 550 km, 53°",
            "Booster will attempt landing on ASDS 'Just Read The Instructions'",
            "Launch window opens at 14:00 UTC on May 15, 2025"
        ],
        "cta_approved": "Join the future of space.",
        "compliance_notes": ["Do not mention previous version payload mass of 17200 kg"],
        "attribution": "Aurora Labs"
    }
    with open("data/attachments/att_brief_v4.json", "w") as f:
        json.dump(brief_v4, f, indent=2)

    # 干扰：v2 draft
    brief_v2_draft = {
        "brief_id": "orbital_launch_v2_draft",
        "version": 2,
        "approved": False,
        "mission_name": "Aurora Dawn",
        "launch_date": "2025-05-15",
        "vehicle": "Aurora Heavy",
        "payload": "60 Starlink v2 satellites",
        "payload_mass_kg": 17200,  # 错误数据（未批准）
        "target_orbit": "LEO 550 km",
        "booster_recovery": "ASDS",
        "approved_facts": [
            "First flight of Aurora Heavy",
            "60 Starlink v2 satellites",
            "Target orbit: 550 km"
        ]
    }
    with open("data/attachments/att_brief_v2_draft.json", "w") as f:
        json.dump(brief_v2_draft, f, indent=2)

    # 干扰：v3 review
    brief_v3_review = {
        "brief_id": "orbital_launch_v3_review",
        "version": 3,
        "approved": False,
        "mission_name": "Aurora Dawn",
        "launch_date": "2025-05-16",  # 日期错误
        "vehicle": "Aurora Heavy",
        "payload": "60 Starlink v2 satellites",
        "payload_mass_kg": 16500,
        "target_orbit": "LEO 550 km, 53°",
        "booster_recovery": "ASDS 'Just Read The Instructions'"
    }
    with open("data/attachments/att_brief_v3_review.json", "w") as f:
        json.dump(brief_v3_review, f, indent=2)

    # 干扰：v2 old approved（已过时）
    brief_v2_old = {
        "brief_id": "orbital_launch_v2_old",
        "version": 2,
        "approved": True,
        "mission_name": "Aurora Dawn",
        "launch_date": "2025-05-10",  # 已过时
        "vehicle": "Aurora Heavy",
        "payload": "60 Starlink v1 satellites",  # 错误
        "payload_mass_kg": 17200,
        "target_orbit": "LEO 550 km",
        "booster_recovery": "ASDS",
        "approved_facts": [
            "First flight of Aurora Heavy",
            "60 Starlink v1 satellites"
        ]
    }
    with open("data/attachments/att_brief_v2_old.json", "w") as f:
        json.dump(brief_v2_old, f, indent=2)

    # ========== 社交帖子（干扰） ==========
    social_posts = [
        {
            "post_id": "sp_001",
            "platform": "x",
            "author_id": "user_excited_astronaut",
            "title": "",
            "community": "",
            "content": "Heard rumors about a major launch next month! Any details?",
            "timestamp": "2025-04-09T20:00:00Z",
            "tags": ["rumor", "launch"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "sp_002",
            "platform": "reddit",
            "author_id": "space_enthusiast42",
            "title": "Any news from Aurora Labs?",
            "community": "r/SpaceX",
            "content": "I saw some tweets about a new heavy lifter. When is the next launch?",
            "timestamp": "2025-04-10T08:00:00Z",
            "tags": ["question", "launch"],
            "needs_response": True,
            "replies": [
                {"author_id": "user_skeptical", "content": "Probably fake.", "timestamp": "2025-04-10T08:30:00Z"}
            ]
        },
        {
            "post_id": "sp_003",
            "platform": "x",
            "author_id": "rocket_watcher",
            "title": "",
            "community": "",
            "content": "Just saw a static fire test! Amazing.",
            "timestamp": "2025-04-08T12:00:00Z",
            "tags": ["static_fire"],
            "needs_response": False,
            "replies": []
        }
    ]
    for sp in social_posts:
        with open(f"data/social/{sp['post_id']}.json", "w") as f:
            json.dump(sp, f, indent=2)

if __name__ == "__main__":
    build_env()
