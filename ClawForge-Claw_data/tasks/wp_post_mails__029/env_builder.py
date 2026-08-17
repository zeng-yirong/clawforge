import os
import json
from datetime import datetime, timedelta

def build_env():
    # 创建目录结构
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data/social", exist_ok=True)
    os.makedirs("publish", exist_ok=True)

    # ---- 干扰邮件 ----
    # 1) 老版本 approved，但 importance low
    emails = []
    emails.append({
        "id": "em_001",
        "thread_id": "th_001",
        "folder": "inbox",
        "sender_id": "alice@example.com",
        "subject": "Brief v1 (approved but low priority)",
        "timestamp": "2025-04-10T08:00:00Z",
        "importance": "low",
        "labels": ["approved", "brief"],
        "body": "Old approved brief.",
        "attachments": ["att_old_brief"]
    })
    # 2) 近期的 approved 但 importance low
    emails.append({
        "id": "em_003",
        "thread_id": "th_002",
        "folder": "inbox",
        "sender_id": "bob@example.com",
        "subject": "Latest v2?",
        "timestamp": "2025-04-13T09:30:00Z",
        "importance": "low",
        "labels": ["approved", "brief"],
        "body": "Another approved brief.",
        "attachments": ["att_another_brief"]
    })
    # 3) high importance 但未 approved（标签不含 approved）
    emails.append({
        "id": "em_005",
        "thread_id": "th_003",
        "folder": "inbox",
        "sender_id": "carol@example.com",
        "subject": "Urgent draft needs approval",
        "timestamp": "2025-04-14T14:00:00Z",
        "importance": "high",
        "labels": ["draft", "urgent"],
        "body": "Not yet approved.",
        "attachments": ["att_draft"]
    })
    # 4) 正确答案：最新、high importance、approved
    correct_timestamp = "2025-04-15T10:00:00Z"
    emails.append({
        "id": "em_009",
        "thread_id": "th_004",
        "folder": "inbox",
        "sender_id": "alice@example.com",
        "subject": "FINAL APPROVED BRIEF - high priority",
        "timestamp": correct_timestamp,
        "importance": "high",
        "labels": ["approved", "brief", "final"],
        "body": "Please use this attachment for launch.",
        "attachments": ["att_orbital_brief_v3"]
    })

    # 写入所有邮件
    for em in emails:
        path = f"data/emails/{em['id']}.json"
        with open(path, "w") as f:
            json.dump(em, f)

    # ---- 附件 ----
    # 干扰附件
    with open("data/attachments/att_old_brief", "w") as f:
        f.write("Old plan: launch on 2025-06-01.\n")
    with open("data/attachments/att_another_brief", "w") as f:
        f.write("Another plan: launch on 2025-08-10.\n")
    with open("data/attachments/att_draft", "w") as f:
        f.write("Draft content: not final.\n")

    # 正确附件
    correct_content = (
        "Launch Date: 2025-08-15\n"
        "Mission: Orbit Insertion\n"
        "Payload: Comms Array\n"
        "\n"
        "This is the approved final brief. Use for all launch communications.\n"
    )
    with open("data/attachments/att_orbital_brief_v3", "w") as f:
        f.write(correct_content)

if __name__ == "__main__":
    build_env()
