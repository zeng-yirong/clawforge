import os
import json

def build_env():
    # Create directories
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- Attachment files ---
    attachments = {
        "att_brief_v1.txt": "Product: AuraCore\nLaunch: 2025-06-01\nVersion: 1.0.0",
        "att_brief_v2.txt": "Product: AuraEdge\nLaunch: 2025-08-01\nVersion: 2.0.0",
        "att_brief_v3.txt": "Product: AuraSync\nLaunch: 2025-09-15\nVersion: 3.2.1",
        "att_brief_v2_approved.txt": "Product: AuraEdge\nLaunch: 2025-08-01\nVersion: 2.0.0",
    }
    for fname, content in attachments.items():
        with open(f"data/attachments/{fname}", "w") as f:
            f.write(content)

    # --- Email definitions ---
    emails = [
        {
            "id": "em_001",
            "thread_id": "th_000",
            "folder": "inbox",
            "sender_id": "alice@example.com",
            "subject": "Meeting notes",
            "timestamp": "2025-05-18T09:00:00Z",
            "importance": "low",
            "labels": ["meeting"],
            "body": "Notes from standup.",
            "attachments": []
        },
        {
            "id": "em_002",
            "thread_id": "th_001",
            "folder": "inbox",
            "sender_id": "bob@example.com",
            "subject": "Draft Brief - AuraCore",
            "timestamp": "2025-05-19T11:30:00Z",
            "importance": "low",
            "labels": ["draft"],
            "body": "Here is a draft of the brief.",
            "attachments": [{"id": "att_001", "filename": "att_brief_v1.txt", "path": "data/attachments/att_brief_v1.txt"}]
        },
        {
            "id": "em_003",
            "thread_id": "th_002",
            "folder": "inbox",
            "sender_id": "carol@example.com",
            "subject": "Review Brief - AuraEdge",
            "timestamp": "2025-05-20T14:00:00Z",
            "importance": "medium",
            "labels": ["review"],
            "body": "Please review the latest brief.",
            "attachments": [{"id": "att_002", "filename": "att_brief_v2.txt", "path": "data/attachments/att_brief_v2.txt"}]
        },
        {
            "id": "em_004",
            "thread_id": "th_003",
            "folder": "inbox",
            "sender_id": "director@example.com",
            "subject": "Approved Brief - AuraSync",
            "timestamp": "2025-05-22T14:30:00Z",
            "importance": "high",
            "labels": ["approved", "launch"],
            "body": "Final approved brief attached.",
            "attachments": [{"id": "att_003", "filename": "att_brief_v3.txt", "path": "data/attachments/att_brief_v3.txt"}]
        },
        {
            "id": "em_005",
            "thread_id": "th_004",
            "folder": "inbox",
            "sender_id": "old_director@example.com",
            "subject": "Old Approved Brief",
            "timestamp": "2025-05-20T10:00:00Z",
            "importance": "high",
            "labels": ["approved"],
            "body": "This is an older approved brief.",
            "attachments": [{"id": "att_004", "filename": "att_brief_v2_approved.txt", "path": "data/attachments/att_brief_v2_approved.txt"}]
        },
        {
            "id": "em_006",
            "thread_id": "th_005",
            "folder": "inbox",
            "sender_id": "bot@example.com",
            "subject": "Re: Approved Brief",
            "timestamp": "2025-05-21T08:00:00Z",
            "importance": "medium",
            "labels": ["approved", "auto"],
            "body": "This is an automatic confirmation, no attachment.",
            "attachments": []
        }
    ]

    for email in emails:
        with open(f"data/emails/{email['id']}.json", "w") as f:
            json.dump(email, f, indent=2)

    print("Environment built for wp_post_mails__043")

if __name__ == "__main__":
    build_env()
