import os
import json

def build_env():
    # create directory structure
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- Attachments ----
    # v1 (old approved)
    with open("data/attachments/att_orbital_brief_v1.txt", "w") as f:
        f.write("Mission Name: Aurora-6\nLaunch Date: 2025-06-01\nPayload: Communication Satellite\n")
    # v2 (draft)
    with open("data/attachments/att_orbital_brief_v2.txt", "w") as f:
        f.write("Mission Name: Aurora-7\nLaunch Date: 2025-09-01\nPayload: Experimental Module\n")
    # v3 (final approved)
    with open("data/attachments/att_orbital_brief_v3.txt", "w") as f:
        f.write("Mission Name: Aurora-7\nLaunch Date: 2025-08-15\nPayload: Communication Satellite\n")
    # decoy – budget report (no mission data)
    with open("data/attachments/att_budget_report.txt", "w") as f:
        f.write("Budget: $2M\nDepartment: Marketing\n")

    # ---- Emails ----
    # em_001 – old approved v1
    em1 = {
        "id": "em_001",
        "thread_id": "th_001",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Launch Brief v1 – Approved",
        "timestamp": "2025-07-20T09:00:00Z",
        "importance": "high",
        "labels": ["approved"],
        "body": "Attached is the first approved version.",
        "attachments": [{"attachment_id": "att_orbital_brief_v1", "filename": "orbital_brief_v1.txt"}]
    }
    # em_002 – draft v2
    em2 = {
        "id": "em_002",
        "thread_id": "th_001",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Launch Brief v2 – Draft",
        "timestamp": "2025-07-23T11:30:00Z",
        "importance": "medium",
        "labels": ["draft"],
        "body": "Draft version, not yet final.",
        "attachments": [{"attachment_id": "att_orbital_brief_v2", "filename": "orbital_brief_v2.txt"}]
    }
    # em_003 – final approved v3
    em3 = {
        "id": "em_003",
        "thread_id": "th_001",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Launch Brief v3 – Final Approval",
        "timestamp": "2025-07-25T14:30:00Z",
        "importance": "high",
        "labels": ["approved", "final", "action-required"],
        "body": "Please find the final approved brief attached. Use this for all communications.",
        "attachments": [{"attachment_id": "att_orbital_brief_v3", "filename": "orbital_brief_v3.txt"}]
    }
    # em_004 – irrelevant meeting notes
    em4 = {
        "id": "em_004",
        "thread_id": "th_002",
        "folder": "inbox",
        "sender_id": "ava@example.com",
        "subject": "Budget Meeting Notes",
        "timestamp": "2025-07-24T10:00:00Z",
        "importance": "low",
        "labels": ["meeting"],
        "body": "Please review the budget spreadsheet attached.",
        "attachments": []
    }

    for em in [em1, em2, em3, em4]:
        path = f"data/emails/{em['id']}.json"
        with open(path, "w") as f:
            json.dump(em, f, indent=2)

    # ---- Accounts (decoy only, not needed for the task) ----
    accounts = {
        "accounts": [
            {
                "account_id": "acc_001",
                "display_name": "Aurora Labs",
                "brand_name": "Aurora Labs",
                "x_handle": "@aurora_labs",
                "reddit_profile": "u/auroralabs",
                "default_reddit_community": "r/AuroraSpace",
                "voice": ["professional", "excited"],
                "cta": "Stay tuned for the launch!",
                "compliance_notes": ["No military payloads", "All dates must be confirmed"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
