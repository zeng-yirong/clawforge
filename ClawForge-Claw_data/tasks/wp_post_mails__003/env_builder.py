import os
import json
from datetime import datetime, timezone

def build_env():
    os.makedirs("emails", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)

    # 干扰邮件1：草稿
    email_draft = {
        "id": "em_001",
        "thread_id": "th_orbital",
        "folder": "inbox",
        "sender_id": "jon@example.com",
        "subject": "Orbital Brief v2 (draft)",
        "timestamp": "2025-04-17T14:30:00Z",
        "importance": "low",
        "labels": ["draft", "brief"],
        "body": "Here is a draft version, not final.",
        "attachments": [{"id": "att_draft", "filename": "orbital_brief_draft.txt"}]
    }
    with open("emails/em_001.json", "w") as f:
        json.dump(email_draft, f)

    # 正确邮件：最终批准
    email_approved = {
        "id": "em_002",
        "thread_id": "th_orbital",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "FINAL APPROVED: Orbital Messenger Launch Brief",
        "timestamp": "2025-04-18T10:00:00Z",
        "importance": "high",
        "labels": ["brief", "approved", "final"],
        "body": "Attached is the final approved launch brief. Please proceed.",
        "attachments": [{"id": "att_final", "filename": "orbital_brief_final.txt"}]
    }
    with open("emails/em_002.json", "w") as f:
        json.dump(email_approved, f)

    # 干扰邮件2：旧版本
    email_old = {
        "id": "em_003",
        "thread_id": "th_orbital",
        "folder": "inbox",
        "sender_id": "nina.santos@auroralabs.com",
        "subject": "Orbital Brief v1 (old)",
        "timestamp": "2025-04-15T08:00:00Z",
        "importance": "medium",
        "labels": ["brief", "archived"],
        "body": "This is the original brief, superseded.",
        "attachments": [{"id": "att_v1", "filename": "orbital_brief_v1.txt"}]
    }
    with open("emails/em_003.json", "w") as f:
        json.dump(email_old, f)

    # 附件内容
    # 正确附件
    with open("attachments/orbital_brief_final.txt", "w") as f:
        f.write(
            "Mission: Orbital Messenger\n"
            "Launch Date: 2025-04-20\n"
            "Tagline: Your messages, beyond the clouds.\n"
            "Key Features: Low latency, quantum encryption, global coverage.\n"
            "Approved by: Mira Chen, Legal Counsel.\n"
            "Status: Approved\n"
        )

    # 干扰附件1：草稿
    with open("attachments/orbital_brief_draft.txt", "w") as f:
        f.write(
            "Mission: Orbital Messenger (Draft)\n"
            "Launch Date: TBD\n"
            "Tagline: Coming soon\n"
            "Key Features: placeholder\n"
            "Approved by: none\n"
            "Status: Draft\n"
        )

    # 干扰附件2：旧版
    with open("attachments/orbital_brief_v1.txt", "w") as f:
        f.write(
            "Mission: Orbital Messenger Alpha\n"
            "Launch Date: 2025-03-15\n"
            "Tagline: Old tagline\n"
            "Key Features: basic\n"
            "Approved by: Jon Bell\n"
            "Status: Archived\n"
        )

if __name__ == "__main__":
    build_env()
