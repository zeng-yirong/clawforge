import os
import json
import random

def build_env():
    # Ensure directories exist
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # Agent will write here, but we create empty dir for structure

    # --- Correct email (em_004) ---
    correct_key = "ORBITAL_LAUNCH_KEY_A1B2C3"
    # Attachment content for correct email
    attach_content = f"{correct_key}\nApproved by Mira Chen on 2025-04-01\n"
    attach_path = "attachments/orbital_brief_v3.txt"
    with open(attach_path, "w") as f:
        f.write(attach_content)

    correct_email = {
        "id": "em_004",
        "thread_id": "th_orbital_launch",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Orbital Launch – Final Approval",
        "timestamp": "2025-04-01T08:30:00Z",
        "importance": "high",
        "labels": ["approved"],
        "body": "Here is the final brief with the launch token. Use it to proceed.",
        "attachments": [
            {
                "id": "att_orbital_brief_v3",
                "filename": "orbital_brief_v3.txt",
                "path": "attachments/orbital_brief_v3.txt"
            }
        ]
    }
    with open("data/emails/em_004.json", "w") as f:
        json.dump(correct_email, f, indent=2)

    # --- Distractor emails ---
    # 1) Old draft (importance low, label draft, different token)
    distractor_key_1 = "OLD_DRAFT_KEY_X9Y8Z7"
    with open("attachments/orbital_brief_v1.txt", "w") as f:
        f.write(f"{distractor_key_1}\nDraft version, not approved\n")
    distractor_1 = {
        "id": "em_001",
        "thread_id": "th_orbital_launch",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Orbital Launch – Draft v1",
        "timestamp": "2025-03-28T10:00:00Z",
        "importance": "low",
        "labels": ["draft"],
        "body": "Here is the first draft.",
        "attachments": [
            {
                "id": "att_orbital_brief_v1",
                "filename": "orbital_brief_v1.txt",
                "path": "attachments/orbital_brief_v1.txt"
            }
        ]
    }
    with open("data/emails/em_001.json", "w") as f:
        json.dump(distractor_1, f, indent=2)

    # 2) Unrelated email with no attachment
    distractor_2 = {
        "id": "em_002",
        "thread_id": "th_meeting_notes",
        "folder": "inbox",
        "sender_id": "ava@example.com",
        "subject": "Weekly sync notes",
        "timestamp": "2025-03-30T14:00:00Z",
        "importance": "medium",
        "labels": ["meeting"],
        "body": "Please review the minutes.",
        "attachments": []
    }
    with open("data/emails/em_002.json", "w") as f:
        json.dump(distractor_2, f, indent=2)

    # 3) Approved but low importance + different token (trap: label approved but importance not high)
    trap_key = "TRAP_KEY_B2C3D4"
    with open("attachments/orbital_brief_v2.txt", "w") as f:
        f.write(f"{trap_key}\nApproved by Mira (old version)\n")
    distractor_3 = {
        "id": "em_003",
        "thread_id": "th_orbital_launch",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Orbital Launch – Final?",
        "timestamp": "2025-03-31T16:00:00Z",
        "importance": "low",
        "labels": ["approved"],
        "body": "Maybe this is the final one?",
        "attachments": [
            {
                "id": "att_orbital_brief_v2",
                "filename": "orbital_brief_v2.txt",
                "path": "attachments/orbital_brief_v2.txt"
            }
        ]
    }
    with open("data/emails/em_003.json", "w") as f:
        json.dump(distractor_3, f, indent=2)

    # Optional: accounts.json (not strictly needed but adds realism)
    accounts = [
        {
            "account_id": "acc_001",
            "display_name": "Mira Chen",
            "brand_name": "Aurora Labs",
            "x_handle": "@mirachen_legal",
            "reddit_profile": "u/mira_chen",
            "default_reddit_community": "r/auroralabs",
            "voice": ["professional", "confident"],
            "cta": "Visit auroralabs.com",
            "compliance_notes": ["All launch material must include disclaimer: 'Subject to regulatory approval.'"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
