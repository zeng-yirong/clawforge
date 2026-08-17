import os
import json

def build_env():
    # 目录结构
    os.makedirs("emails", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)

    # ---------- 邮件 ----------
    emails = [
        {
            "id": "em_001",
            "thread_id": "th_001",
            "folder": "inbox",
            "sender_id": "nina.santos@auroralabs.com",
            "subject": "Re: Orbital Launch Budget Review",
            "timestamp": "2026-07-10T09:00:00Z",
            "importance": "high",
            "labels": ["budget"],
            "body": "Please review the budget attachments.",
            "attachments": [{"id": "budget_v2", "type": "pdf", "filename": "budget_v2.pdf"}]
        },
        {
            "id": "em_002",
            "thread_id": "th_002",
            "folder": "inbox",
            "sender_id": "mira.chen@auroralabs.com",
            "subject": "Approved Brief – Orbital Launch",
            "timestamp": "2026-07-14T22:30:00Z",
            "importance": "high",
            "labels": ["approval", "launch"],
            "body": "Final approved brief attached. Please use this version.",
            "attachments": [{"id": "orbital_brief_v3", "type": "json", "filename": "orbital_brief_v3.json"}]
        },
        {
            "id": "em_003",
            "thread_id": "th_002",
            "folder": "inbox",
            "sender_id": "mira.chen@auroralabs.com",
            "subject": "Draft Brief – Orbital Launch",
            "timestamp": "2026-07-13T18:00:00Z",
            "importance": "medium",
            "labels": ["draft"],
            "body": "Here is a draft version for review.",
            "attachments": [{"id": "orbital_brief_v2", "type": "json", "filename": "orbital_brief_v2.json"}]
        },
        {
            "id": "em_004",
            "thread_id": "th_003",
            "folder": "inbox",
            "sender_id": "owen.park@auroralabs.com",
            "subject": "Reminder: Launch Checklist",
            "timestamp": "2026-07-14T10:00:00Z",
            "importance": "low",
            "labels": ["reminder"],
            "body": "Don't forget to check the final brief.",
            "attachments": []
        },
        {
            "id": "em_005",
            "thread_id": "th_002",
            "folder": "sent",
            "sender_id": "mira.chen@auroralabs.com",
            "subject": "Approved Brief (v3)",
            "timestamp": "2026-07-14T22:35:00Z",
            "importance": "high",
            "labels": ["approval"],
            "body": "This is the same as em_002.",
            "attachments": [{"id": "orbital_brief_v3", "type": "json", "filename": "orbital_brief_v3.json"}]
        }
    ]
    for e in emails:
        with open(f"emails/{e['id']}.json", "w") as f:
            json.dump(e, f, indent=2)

    # ---------- 附件 ----------
    # v3 – 正确的已批准版本
    v3 = {
        "product_name": "Aurora Orbital Launch",
        "version_build": 3.0,
        "launch_date": "2026-07-15",
        "features": ["RTLS", "Fairing reuse"],
        "approved_by": "Mira Chen"
    }
    with open("attachments/orbital_brief_v3.json", "w") as f:
        json.dump(v3, f, indent=2)

    # v2 – 干扰（版本 < 2.5）
    v2 = {
        "product_name": "Aurora Orbital Launch",
        "version_build": 2.0,
        "launch_date": "2026-07-15",
        "features": ["RTLS"],
        "approved_by": "Mira Chen"
    }
    with open("attachments/orbital_brief_v2.json", "w") as f:
        json.dump(v2, f, indent=2)

    # v1 – 干扰（更旧且批准人不同）
    v1 = {
        "product_name": "Aurora Orbital Launch",
        "version_build": 1.0,
        "launch_date": "2026-07-20",
        "features": [],
        "approved_by": "Nina Santos"
    }
    with open("attachments/orbital_brief_v1.json", "w") as f:
        json.dump(v1, f, indent=2)

    # 非 JSON 干扰文件
    with open("attachments/notes.txt", "w") as f:
        f.write("This is not a valid attachment.")

    # 意外格式的 CSV 干扰
    with open("attachments/schedule.csv", "w") as f:
        f.write("item,date\nLaunch,2026-07-15\n")
