import os
import json

def build_env():
    # data/emails
    emails_dir = "data/emails"
    os.makedirs(emails_dir, exist_ok=True)

    # 邮件1：来自老板的审核邮件（唯一含附件列表）
    email_boss = {
        "id": "em_001",
        "thread_id": "th_018",
        "folder": "inbox",
        "sender_id": "priya.dev@auroralabs.com",
        "subject": "简报审核",
        "timestamp": "2025-03-21T09:15:00Z",
        "importance": "high",
        "labels": ["work", "approval"],
        "body": "附件里是几版简报，请用最终版。",
        "attachments": ["att_brief_v1", "att_brief_v2", "att_brief_final"]
    }
    with open(os.path.join(emails_dir, "em_001.json"), "w") as f:
        json.dump(email_boss, f)

    # 邮件2：无关的自动提醒
    email_spam = {
        "id": "em_002",
        "thread_id": "th_099",
        "folder": "inbox",
        "sender_id": "noreply@system.com",
        "subject": "系统通知",
        "timestamp": "2025-03-20T14:22:00Z",
        "importance": "low",
        "labels": ["system"],
        "body": "例行维护已完成。",
        "attachments": []
    }
    with open(os.path.join(emails_dir, "em_002.json"), "w") as f:
        json.dump(email_spam, f)

    # 邮件3：另一个同事的讨论（干扰）
    email_chat = {
        "id": "em_003",
        "thread_id": "th_018",
        "folder": "inbox",
        "sender_id": "jon@example.com",
        "subject": "Re: 简报审核",
        "timestamp": "2025-03-21T08:30:00Z",
        "importance": "medium",
        "labels": ["work"],
        "body": "我看了第一版，有些建议...",
        "attachments": []
    }
    with open(os.path.join(emails_dir, "em_003.json"), "w") as f:
        json.dump(email_chat, f)

    # data/attachments
    att_dir = "data/attachments"
    os.makedirs(att_dir, exist_ok=True)

    # 附件1：草稿版
    with open(os.path.join(att_dir, "att_brief_v1.txt"), "w") as f:
        f.write("DRAFT BRIEF\nSummary: 早期方案，未定。\n")

    # 附件2：过期版
    with open(os.path.join(att_dir, "att_brief_v2.txt"), "w") as f:
        f.write("REVIEW DRAFT\nSummary: 已废弃，请参考最新版。\n")

    # 附件3：最终批准版（唯一正确）
    final_summary = "Alpha 发射计划定于2025年Q3，首先覆盖北美和欧洲市场，后续扩展至亚太区。"
    with open(os.path.join(att_dir, "att_brief_final.txt"), "w") as f:
        f.write(f"FINAL APPROVED BRIEF\nSummary: {final_summary}\n")

    # data/social (干扰，不影响任务)
    social_dir = "data/social"
    os.makedirs(social_dir, exist_ok=True)
    post = {
        "post_id": "post_001",
        "platform": "x",
        "author_id": "ava@example.com",
        "title": "预热贴",
        "community": "tech",
        "content": "即将有大事发生！",
        "timestamp": "2025-03-19T10:00:00Z",
        "tags": ["teaser"],
        "needs_response": False,
        "replies": []
    }
    with open(os.path.join(social_dir, "post_001.json"), "w") as f:
        json.dump(post, f)

    # data/accounts.json (无实际用途，仅环境真实)
    accounts = [
        {
            "account_id": "acc_priya",
            "display_name": "Priya Dev",
            "brand_name": "Aurora Labs",
            "x_handle": "@priyadev_ops",
            "reddit_profile": "u/priya_dev",
            "default_reddit_community": "r/auroralabs",
            "voice": ["professional", "clear"],
            "cta": "Learn more at auroralabs.com",
            "compliance_notes": ["no unverified claims"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # data/contacts.json
    contacts = [
        {"contact_id": "ct_priya", "name": "Priya Dev", "email": "priya.dev@auroralabs.com", "role": "Product Marketing Lead", "team": "Marketing", "social_handle": "@priyadev_ops"},
        {"contact_id": "ct_jon", "name": "Jon Bell", "email": "jon@example.com", "role": "Support Manager", "team": "Support", "social_handle": "@jonbellops"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # ops 目录（空，等待 agent 写入）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
