import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 目标目录

    # --- 邮件（干扰项） ---
    emails = [
        {
            "id": "em_001",
            "thread_id": "thr_001",
            "folder": "inbox",
            "sender_id": "kim@example.com",
            "subject": "Nova-7 Brief v2 (approved)",
            "timestamp": "2025-04-10T14:00:00Z",
            "importance": "high",
            "labels": ["approved", "internal"],
            "body": "This is the second draft, please use version 3 for launch.",
            "attachments": ["att_orbital_brief_v2.txt"]
        },
        {
            "id": "em_002",
            "thread_id": "thr_001",
            "folder": "inbox",
            "sender_id": "ceo@example.com",
            "subject": "Nova-7 ideas",
            "timestamp": "2025-04-11T08:30:00Z",
            "importance": "low",
            "labels": ["draft"],
            "body": "Maybe we can also mention the payload capacity.",
            "attachments": []
        },
        {
            "id": "em_003",
            "thread_id": "thr_001",
            "folder": "inbox",
            "sender_id": "legal@example.com",
            "subject": "Nova-7 Final Approved Brief v3",
            "timestamp": "2025-04-12T09:15:00Z",
            "importance": "high",
            "labels": ["approved", "final"],
            "body": "This is the final approved brief. Use this for all external communications.",
            "attachments": ["att_orbital_brief_v3.txt"]
        },
        {
            "id": "em_004",
            "thread_id": "thr_002",
            "folder": "inbox",
            "sender_id": "eng@example.com",
            "subject": "Nova-7 telemetry",
            "timestamp": "2025-04-09T16:45:00Z",
            "importance": "medium",
            "labels": ["info"],
            "body": "Attached is the launch window analysis.",
            "attachments": ["att_orbital_brief_v1.txt"]
        }
    ]
    for e in emails:
        with open(f"data/emails/{e['id']}.json", "w") as f:
            json.dump(e, f, indent=2)

    # --- 附件（干扰 + 目标） ---
    # v2 – 已过期的批准版本
    attach_v2 = {
        "brief_id": "bri_007",
        "mission_name": "Nova-7",
        "launch_date": "2025-04-20",
        "approved_message": "We are excited to announce the upcoming launch of Nova-7 on April 20. Stay tuned!",
        "version": 2
    }
    with open("data/attachments/att_orbital_brief_v2.txt", "w") as f:
        json.dump(attach_v2, f, indent=2)

    # v3 – 唯一的目标附件（最新、已审批）
    attach_v3 = {
        "brief_id": "bri_009",
        "mission_name": "Nova-7",
        "launch_date": "2025-04-18",
        "approved_message": "We are thrilled to announce the successful launch of Nova-7 satellite, marking a new era in orbital communications. The payload is now in orbit and performing nominally.",
        "version": 3
    }
    with open("data/attachments/att_orbital_brief_v3.txt", "w") as f:
        json.dump(attach_v3, f, indent=2)

    # v1 – 完全无关的旧文档
    attach_v1 = {
        "brief_id": "bri_005",
        "mission_name": "Nova-5",
        "launch_date": "2024-12-01",
        "approved_message": "Legacy satellite launch.",
        "version": 1
    }
    with open("data/attachments/att_orbital_brief_v1.txt", "w") as f:
        json.dump(attach_v1, f, indent=2)

if __name__ == "__main__":
    build_env()
