import os
import json
import shutil
from datetime import datetime, timedelta

def build_env():
    # 确保工作区干净
    for d in ['data/emails', 'data/social', 'output']:
        os.makedirs(d, exist_ok=True)
    
    # --- 联系人 (contacts) ---
    contacts = [
        {"contact_id": "c001", "name": "Mira Chen", "email": "mira.chen@auroralabs.com", "role": "Legal Counsel", "team": "Legal", "social_handle": "@mirachen_legal"},
        {"contact_id": "c002", "name": "Jon Bell", "email": "jon@example.com", "role": "Support Manager", "team": "Support", "social_handle": "@jonbellops"},
        {"contact_id": "c003", "name": "Ava Price", "email": "ava@example.com", "role": "Community Lead", "team": "Community", "social_handle": "@avapractical"},
        {"contact_id": "c004", "name": "Nina Santos", "email": "nina.santos@auroralabs.com", "role": "Product Marketing Lead", "team": "Marketing", "social_handle": "@ninasantos_pm"},
    ]
    with open('data/contacts.json', 'w') as f:
        json.dump({"contacts": contacts}, f, indent=2)
    
    # --- 品牌账号 (accounts) ---
    accounts = [
        {
            "account_id": "a001",
            "display_name": "Aurora Labs",
            "brand_name": "Aurora Labs",
            "x_handle": "@auroralabs",
            "reddit_profile": "u/auroralabs_official",
            "default_reddit_community": "r/AuroraSpace",
            "voice": ["professional", "excited", "forward-looking"],
            "cta": "🚀 Ready for liftoff? Follow us for updates.",
            "compliance_notes": ["Always use approved mission names", "No exact launch date until T-24h announcement"]
        }
    ]
    with open('data/accounts.json', 'w') as f:
        json.dump({"accounts": accounts}, f, indent=2)
    
    # --- 邮件 (emails) ---
    now = datetime(2025, 5, 15, 10, 0, 0)
    
    # 干扰邮件：旧版草稿
    emails = [
        {
            "id": "em_001",
            "thread_id": "th_01",
            "folder": "inbox",
            "sender_id": "c001",
            "subject": "Draft Launch Brief v1",
            "timestamp": (now - timedelta(days=7)).isoformat(),
            "importance": "low",
            "labels": ["draft"],
            "body": "Initial draft of the orbital launch brief. Still needs legal review.",
            "attachments": ["att_brief_v1.txt"]
        },
        {
            "id": "em_002",
            "thread_id": "th_01",
            "folder": "inbox",
            "sender_id": "c001",
            "subject": "Approved Launch Brief v2",
            "timestamp": (now - timedelta(days=3)).isoformat(),
            "importance": "high",
            "labels": ["approved", "old"],
            "body": "This version was approved but superseded by v3. Keep for reference.",
            "attachments": ["att_brief_v2.txt"]
        },
        {
            "id": "em_003",
            "thread_id": "th_01",
            "folder": "inbox",
            "sender_id": "c001",
            "subject": "Approved Launch Brief v3 (FINAL)",
            "timestamp": (now - timedelta(hours=2)).isoformat(),
            "importance": "high",
            "labels": ["approved", "final"],
            "body": "Legal and marketing have signed off. Use this version for all public materials.",
            "attachments": ["att_brief_v3.txt"]
        },
        {
            "id": "em_004",
            "thread_id": "th_02",
            "folder": "inbox",
            "sender_id": "c002",
            "subject": "Support ticket escalation",
            "timestamp": now.isoformat(),
            "importance": "medium",
            "labels": ["support"],
            "body": "Customer reported issues with pre-launch dashboard.",
            "attachments": []
        },
        {
            "id": "em_005",
            "thread_id": "th_03",
            "folder": "spam",
            "sender_id": "c003",
            "subject": "Re: [SPAM] Get rich quick",
            "timestamp": (now - timedelta(days=1)).isoformat(),
            "importance": "low",
            "labels": ["spam"],
            "body": "No thanks.",
            "attachments": []
        },
        {
            "id": "em_006",
            "thread_id": "th_04",
            "folder": "inbox",
            "sender_id": "c004",
            "subject": "Review of competitor launch",
            "timestamp": (now - timedelta(hours=5)).isoformat(),
            "importance": "low",
            "labels": ["research"],
            "body": "Interesting moves by RocketX. Attached their press release.",
            "attachments": ["competitor_press.txt"]
        }
    ]
    for email in emails:
        with open(f'data/emails/{email["id"]}.json', 'w') as f:
            json.dump(email, f, indent=2)
    
    # --- 附件内容 ---
    # v1 附件 (干扰)
    with open('data/emails/att_brief_v1.txt', 'w') as f:
        f.write("Mission: Aurora-5\nLaunch Date: 2025-04-15\nStatus: Cancelled\n")
    # v2 附件 (干扰，但日期不同)
    with open('data/emails/att_brief_v2.txt', 'w') as f:
        f.write("Mission: Aurora-6\nLaunch Date: 2025-05-10\nStatus: Delayed\n")
    # v3 附件 (正确答案)
    with open('data/emails/att_brief_v3.txt', 'w') as f:
        f.write("Mission: Aurora-7\nLaunch Date: 2025-05-20\nStatus: GO\nOverview: Orbital deployment of comm satellite. Window opens 09:00 UTC.\n")
    # 竞争对手附件
    with open('data/emails/competitor_press.txt', 'w') as f:
        f.write("RocketX announces first crewed flight in 2026.\n")
    
    # --- 社交帖子 (social) ---
    posts = [
        {
            "post_id": "pst_001",
            "platform": "x",
            "author_id": "u001",  # 用户
            "title": "",
            "community": "",
            "content": "Hey @auroralabs, any updates on the next launch? Heard some rumors.",
            "timestamp": (now - timedelta(days=1)).isoformat(),
            "tags": ["question"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "pst_002",
            "platform": "reddit",
            "author_id": "u002",
            "title": "When is Aurora Labs launching again?",
            "community": "r/AuroraSpace",
            "content": "I keep checking the website but no news. Anyone know?",
            "timestamp": (now - timedelta(hours=6)).isoformat(),
            "tags": ["question"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "pst_003",
            "platform": "x",
            "author_id": "u003",
            "title": "",
            "community": "",
            "content": "Just saw an amazing time lapse of the sunrise!",
            "timestamp": (now - timedelta(hours=3)).isoformat(),
            "tags": ["general"],
            "needs_response": False,
            "replies": []
        },
        {
            "post_id": "pst_004",
            "platform": "reddit",
            "author_id": "u004",
            "title": "SpaceX competitor analysis",
            "community": "r/SpaceInvesting",
            "content": "Aurora Labs seems to be falling behind.",
            "timestamp": (now - timedelta(days=2)).isoformat(),
            "tags": ["discussion"],
            "needs_response": False,
            "replies": []
        }
    ]
    for post in posts:
        with open(f'data/social/{post["post_id"]}.json', 'w') as f:
            json.dump(post, f, indent=2)
    
    # output 目录留空
    print("Environment built successfully.")

if __name__ == '__main__':
    build_env()
