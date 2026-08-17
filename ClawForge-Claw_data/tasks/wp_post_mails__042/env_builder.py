import json
import os

def build_env():
    # emails
    emails_dir = "data/emails"
    attachments_dir = "data/attachments"
    os.makedirs(emails_dir, exist_ok=True)
    os.makedirs(attachments_dir, exist_ok=True)

    # --- 附件文件 ---
    # 干扰：草稿附件缺少字段
    draft_attachment = {
        "product_name": "Aurora X1",
        "launch_date": "2025-04-15",
        "platforms": ["x"]
    }
    with open(os.path.join(attachments_dir, "draft_brief.json"), "w") as f:
        json.dump(draft_attachment, f)

    # 干扰：旧版 approved 但时间较早
    old_attachment = {
        "product_name": "Aurora X1",
        "launch_date": "2025-04-10",
        "key_message": "Early Access",
        "platforms": ["x", "reddit"]
    }
    with open(os.path.join(attachments_dir, "old_brief.json"), "w") as f:
        json.dump(old_attachment, f)

    # 干扰：v2 虽然 approved 但不是最新
    v2_attachment = {
        "product_name": "Aurora X1",
        "launch_date": "2025-04-11",
        "key_message": "Innovate Tomorrow",
        "platforms": ["x", "reddit"]
    }
    with open(os.path.join(attachments_dir, "brief_v2.json"), "w") as f:
        json.dump(v2_attachment, f)

    # 正确答案：最新 approved + final 邮件对应的附件
    final_attachment = {
        "product_name": "Aurora X1",
        "launch_date": "2025-04-12",
        "key_message": "The Future is Now",
        "platforms": ["x", "reddit", "linkedin"]
    }
    with open(os.path.join(attachments_dir, "final_brief.json"), "w") as f:
        json.dump(final_attachment, f)

    # 干扰：垃圾文本（非JSON）
    with open(os.path.join(attachments_dir, "spam.txt"), "w") as f:
        f.write("This is not JSON")

    # --- 邮件 ---
    emails = [
        {
            "id": "em_001",
            "thread_id": "th_001",
            "folder": "inbox",
            "sender_id": "jon@example.com",
            "subject": "Draft Brief v1",
            "timestamp": "2025-04-01T10:00:00Z",
            "importance": "medium",
            "labels": ["draft"],
            "body": "First draft for review.",
            "attachments": [{"id": "att_draft", "file_path": "data/attachments/draft_brief.json"}]
        },
        {
            "id": "em_002",
            "thread_id": "th_001",
            "folder": "inbox",
            "sender_id": "nina.santos@auroralabs.com",
            "subject": "Approved Brief v2",
            "timestamp": "2025-04-02T09:00:00Z",
            "importance": "high",
            "labels": ["approved"],
            "body": "Here's the approved v2.",
            "attachments": [{"id": "att_approved_v2", "file_path": "data/attachments/brief_v2.json"}]
        },
        {
            "id": "em_003",
            "thread_id": "th_001",
            "folder": "inbox",
            "sender_id": "mia.hart@auroralabs.com",
            "subject": "Final Approved - Aurora X1 Launch",
            "timestamp": "2025-04-03T11:00:00Z",
            "importance": "high",
            "labels": ["approved", "final"],
            "body": "This is the final version, use it for launch.",
            "attachments": [{"id": "att_final", "file_path": "data/attachments/final_brief.json"}]
        },
        {
            "id": "em_004",
            "thread_id": "th_002",
            "folder": "inbox",
            "sender_id": "jon@example.com",
            "subject": "Old Approved (ignore)",
            "timestamp": "2025-03-30T08:00:00Z",
            "importance": "low",
            "labels": ["approved"],
            "body": "This was approved earlier but superseded.",
            "attachments": [{"id": "att_old", "file_path": "data/attachments/old_brief.json"}]
        },
        {
            "id": "em_005",
            "thread_id": "th_003",
            "folder": "spam",
            "sender_id": "spam@spam.com",
            "subject": "Win a free iPhone",
            "timestamp": "2025-04-04T12:00:00Z",
            "importance": "low",
            "labels": ["spam"],
            "body": "Click here.",
            "attachments": [{"id": "att_spam", "file_path": "data/attachments/spam.txt"}]
        }
    ]

    for mail in emails:
        file_path = os.path.join(emails_dir, f"{mail['id']}.json")
        with open(file_path, "w") as f:
            json.dump(mail, f, indent=2)

if __name__ == "__main__":
    build_env()
