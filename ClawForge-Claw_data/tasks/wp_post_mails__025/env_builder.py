import os
import json
import shutil
from datetime import datetime

def build_env():
    # 创建目录
    os.makedirs("emails", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("social", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 留给 agent 输出

    # ---------- 干扰项 1：旧版邮件 (v1) ----------
    email_v1 = {
        "id": "em_001",
        "thread_id": "th_orbital_brief",
        "folder": "inbox",
        "sender_id": "prod_mgr",
        "subject": "Old Brief v1 (do not use)",
        "timestamp": "2025-06-10T08:00:00Z",
        "importance": "low",
        "labels": ["obsolete"],
        "body": "This is the very first draft.",
        "attachments": [
            {"attachment_id": "att_brief_v1", "filename": "brief_v1.json"}
        ]
    }
    with open("emails/em_001.json", "w") as f:
        json.dump(email_v1, f, indent=2)

    # ---------- 干扰项 2：草稿邮件 (v2) ----------
    email_v2 = {
        "id": "em_002",
        "thread_id": "th_orbital_brief",
        "folder": "inbox",
        "sender_id": "prod_mgr",
        "subject": "Draft Brief v2 – not approved",
        "timestamp": "2025-06-12T14:30:00Z",
        "importance": "medium",
        "labels": ["draft"],
        "body": "Needs final review.",
        "attachments": [
            {"attachment_id": "att_brief_v2", "filename": "brief_v2.json"}
        ]
    }
    with open("emails/em_002.json", "w") as f:
        json.dump(email_v2, f, indent=2)

    # ---------- 正确答案邮件 (v3) ----------
    email_v3 = {
        "id": "em_003",
        "thread_id": "th_orbital_brief",
        "folder": "inbox",
        "sender_id": "prod_mgr",
        "subject": "Final Approved Brief v3",
        "timestamp": "2025-06-14T09:15:00Z",
        "importance": "high",
        "labels": ["approved", "final"],
        "body": "This is the final approved version. Use the attachment directly.",
        "attachments": [
            {"attachment_id": "att_brief_v3", "filename": "brief_v3.json"}
        ]
    }
    with open("emails/em_003.json", "w") as f:
        json.dump(email_v3, f, indent=2)

    # ---------- 干扰项 3：无关邮件 ----------
    email_noise = {
        "id": "em_004",
        "thread_id": "th_standup",
        "folder": "inbox",
        "sender_id": "dev_lead",
        "subject": "Standup notes",
        "timestamp": "2025-06-14T10:00:00Z",
        "importance": "low",
        "labels": ["meeting"],
        "body": "Sprint demo tomorrow.",
        "attachments": []
    }
    with open("emails/em_004.json", "w") as f:
        json.dump(email_noise, f, indent=2)

    # ---------- 附件文件 ----------
    # v1 (干扰)
    att_v1 = {
        "version": "1.0.0",
        "release_date": "2025-01-15",
        "x_post": "",
        "reddit_post": "",
        "replies": [],
        "status": "obsolete"
    }
    with open("attachments/att_brief_v1.json", "w") as f:
        json.dump(att_v1, f, indent=2)

    # v2 (干扰)
    att_v2 = {
        "version": "2.0.0",
        "release_date": "2025-03-20",
        "x_post": "",
        "reddit_post": "",
        "replies": [],
        "status": "draft"
    }
    with open("attachments/att_brief_v2.json", "w") as f:
        json.dump(att_v2, f, indent=2)

    # v3 (正确答案)
    att_v3 = {
        "version": "3.2.1",
        "release_date": "2025-06-15",
        "x_post": "🚀 OrbitalLaunch v3.2.1 is live! Full Linux support & new telemetry API. Update now!",
        "reddit_post": "We are thrilled to announce OrbitalLaunch v3.2.1! This release brings native Linux support and a powerful telemetry API. See changelog in comments.",
        "replies": [
            {
                "post_id": "post_002",
                "reply_content": "Yes, Linux support is confirmed in v3.2.1!"
            },
            {
                "post_id": "post_005",
                "reply_content": "The telemetry API documentation has been updated. Check the dev portal."
            }
        ]
    }
    with open("attachments/att_brief_v3.json", "w") as f:
        json.dump(att_v3, f, indent=2)

    # ---------- 社交帖子 (social/) ----------
    posts = [
        {
            "post_id": "post_001",
            "platform": "reddit",
            "author_id": "user_alpha",
            "title": "Any ETA for Linux?",
            "community": "r/OrbitalLaunch",
            "content": "Will there be native Linux support soon?",
            "timestamp": "2025-06-13T11:00:00Z",
            "tags": ["question", "linux"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "post_002",
            "platform": "x",
            "author_id": "user_beta",
            "title": "",
            "community": "",
            "content": "I need Linux support before upgrading!",
            "timestamp": "2025-06-13T12:30:00Z",
            "tags": ["linux", "feature-request"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "post_003",
            "platform": "reddit",
            "author_id": "user_gamma",
            "title": "Love the new UI!",
            "community": "r/OrbitalLaunch",
            "content": "The new dashboard is beautiful.",
            "timestamp": "2025-06-14T07:00:00Z",
            "tags": ["feedback", "UI"],
            "needs_response": False,
            "replies": []
        },
        {
            "post_id": "post_004",
            "platform": "x",
            "author_id": "user_delta",
            "title": "",
            "community": "",
            "content": "When will you fix the bug in v2.5?",
            "timestamp": "2025-06-14T08:00:00Z",
            "tags": ["bug"],
            "needs_response": False,
            "replies": []
        },
        {
            "post_id": "post_005",
            "platform": "reddit",
            "author_id": "user_epsilon",
            "title": "Telemetry API docs?",
            "community": "r/OrbitalLaunch",
            "content": "Is there updated documentation for the new telemetry API?",
            "timestamp": "2025-06-14T10:00:00Z",
            "tags": ["api", "documentation"],
            "needs_response": True,
            "replies": []
        }
    ]
    for p in posts:
        with open(f"social/{p['post_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

if __name__ == "__main__":
    build_env()
