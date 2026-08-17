import os
import json

def build_env():
    # 创建目录
    for d in ["data/emails", "data/attachments", "data/social", "ops"]:
        os.makedirs(d, exist_ok=True)

    # ---------- 邮件 ----------
    # 正确的邮件 (em_003)
    emails = {
        "em_001": {
            "id": "em_001",
            "thread_id": "th_001",
            "folder": "inbox",
            "sender_id": "contact_001",
            "subject": "pre-brief notes",
            "timestamp": "2025-04-10T09:00:00Z",
            "importance": "low",
            "labels": [],
            "body": "Some early notes.",
            "attachments": [{"attachment_id": "att_001", "filename": "notes.txt"}]
        },
        "em_002": {
            "id": "em_002",
            "thread_id": "th_002",
            "folder": "inbox",
            "sender_id": "contact_002",
            "subject": "Aurora X1 brief v2 (draft)",
            "timestamp": "2025-05-01T10:00:00Z",
            "importance": "medium",
            "labels": ["draft"],
            "body": "Work in progress.",
            "attachments": [{"attachment_id": "att_002", "filename": "brief_v2_draft.json"}]
        },
        "em_003": {
            "id": "em_003",
            "thread_id": "th_002",
            "folder": "inbox",
            "sender_id": "contact_003",
            "subject": "FINAL APPROVED – Aurora X1 Launch Brief",
            "timestamp": "2025-05-20T14:30:00Z",
            "importance": "high",
            "labels": ["approved", "urgent"],
            "body": "Approved version attached. Go!",
            "attachments": [{"attachment_id": "att_003", "filename": "approved_brief.json"}]
        },
        "em_004": {
            "id": "em_004",
            "thread_id": "th_003",
            "folder": "inbox",
            "sender_id": "contact_004",
            "subject": "old campaign metrics",
            "timestamp": "2025-03-01T08:00:00Z",
            "importance": "low",
            "labels": ["archive"],
            "body": "Irrelevant data.",
            "attachments": []
        }
    }
    for eid, ebody in emails.items():
        with open(f"data/emails/{eid}.json", "w") as f:
            json.dump(ebody, f, indent=2)

    # ---------- 附件 ----------
    # 干扰附件：纯文本
    with open("data/attachments/att_001.txt", "w") as f:
        f.write("just notes")
    # 干扰附件：旧版brief JSON (缺少product_id或launch_date)
    with open("data/attachments/att_002.json", "w") as f:
        json.dump({"version": "draft", "product_name": "Aurora X1"}, f, indent=2)
    # 正确附件
    with open("data/attachments/att_003.json", "w") as f:
        json.dump({"product_id": "aurora_x1", "launch_date": "2025-06-01"}, f, indent=2)

    # ---------- 社交帖子 ----------
    posts = {
        "post_001": {
            "post_id": "post_001_aurora_x1_preview",
            "platform": "x",
            "author_id": "user_01",
            "title": "Aurora X1 sneak peek",
            "community": "tech",
            "content": "Check this out!",
            "timestamp": "2025-05-01T12:00:00Z",
            "tags": [],
            "needs_response": False,
            "replies": []
        },
        "post_002": {
            "post_id": "post_002_aurora_x1_teaser",
            "platform": "reddit",
            "author_id": "user_02",
            "title": "Teaser: Aurora X1 coming soon",
            "community": "gadgets",
            "content": "Stay tuned!",
            "timestamp": "2025-05-15T09:30:00Z",
            "tags": [],
            "needs_response": False,
            "replies": []
        },
        "post_003": {
            "post_id": "post_003_aurora_x1_review",
            "platform": "reddit",
            "author_id": "user_03",
            "title": "My Aurora X1 review (after launch)",
            "community": "reviews",
            "content": "Great product.",
            "timestamp": "2025-06-02T10:00:00Z",
            "tags": [],
            "needs_response": False,
            "replies": []
        },
        "post_004": {
            "post_id": "post_004_unrelated",
            "platform": "x",
            "author_id": "user_04",
            "title": "Coffee talk",
            "community": "life",
            "content": "Just a normal day.",
            "timestamp": "2025-04-20T07:00:00Z",
            "tags": [],
            "needs_response": False,
            "replies": []
        },
        "post_005": {
            "post_id": "post_005_aurora_x1_launch_day",
            "platform": "youtube",  # 非x或reddit但无所谓
            "author_id": "user_05",
            "title": "Aurora X1 launch day celebration",
            "community": "events",
            "content": "Today is the day!",
            "timestamp": "2025-06-01T00:00:00Z",  # 等于launch_date，不算早于
            "tags": [],
            "needs_response": False,
            "replies": []
        }
    }
    for pid, pbody in posts.items():
        with open(f"data/social/{pid}.json", "w") as f:
            json.dump(pbody, f, indent=2)

    # ---------- 账户 (占位，不必须) ----------
    accounts = {
        "accounts": [
            {"account_id": "acc_01", "display_name": "Ray", "brand_name": "Aurora Labs"}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
