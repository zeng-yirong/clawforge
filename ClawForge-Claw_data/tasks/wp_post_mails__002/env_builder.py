import os
import json
import shutil

def build_env():
    """
    Build the initial file tree for wp_post_mails__002.
    Creates emails, attachments, accounts, and empty output directory.
    """
    # Clean slate
    dirs = ["data/emails", "data/attachments", "ops"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ---------- Accounts (only one relevant account) ----------
    accounts = {
        "accounts": [
            {
                "account_id": "aurora_labs",
                "display_name": "Aurora Labs Official",
                "brand_name": "Aurora Labs",
                "x_handle": "@auroralabs",
                "reddit_profile": "u/auroralabs",
                "default_reddit_community": "r/space",
                "voice": ["technical", "excited"],
                "cta": "Join the launch watch → [link]",
                "compliance_notes": ["Must include #Ad for paid promos"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---------- Attachments (brief content as JSON) ----------
    briefs = {
        "att_orbital_brief_v1": {
            "title": "Orbital Launch – Old Version",
            "content": "This is the initial draft, outdated. Do not use."
        },
        "att_orbital_brief_v2": {
            "title": "Orbital Launch Test",
            "content": "Test content for dry run. Not final."
        },
        "att_orbital_brief_v3": {  # **CORRECT**
            "title": "Orbital Launch Day",
            "content": "We are excited to announce our orbital launch on April 1st! #OrbitalLaunch"
        },
        "att_orbital_brief_v2_draft": {
            "title": "Orbital Launch Draft – Unapproved",
            "content": "WIP draft – pending legal review."
        },
    }
    for att_id, cont in briefs.items():
        with open(f"data/attachments/{att_id}.json", "w") as f:
            json.dump(cont, f, indent=2)

    # ---------- Emails ----------
    emails = {
        "em_001": {
            "id": "em_001",
            "thread_id": "th_orbital",
            "folder": "inbox",
            "sender_id": "mia.hart@auroralabs.com",
            "subject": "Approved Brief v1 – Orbital Launch",
            "timestamp": "2025-03-10T08:00:00Z",
            "importance": "high",
            "labels": ["approved", "brief"],
            "body": "Attached is the first approved brief (v1).",
            "attachments": ["att_orbital_brief_v1"]
        },
        "em_002": {
            "id": "em_002",
            "thread_id": "th_orbital",
            "folder": "inbox",
            "sender_id": "nina.santos@auroralabs.com",
            "subject": "Approved Brief v3 – Orbital Launch (FINAL)",
            "timestamp": "2025-03-15T10:30:00Z",
            "importance": "high",
            "labels": ["approved", "brief", "final"],
            "body": "Final approved brief with legal sign-off.",
            "attachments": ["att_orbital_brief_v3"]
        },
        "em_003": {
            "id": "em_003",
            "thread_id": "th_orbital",
            "folder": "drafts",
            "sender_id": "owen.park@auroralabs.com",
            "subject": "Draft Brief v2.5 – Orbital Launch",
            "timestamp": "2025-03-14T16:45:00Z",
            "importance": "medium",
            "labels": ["brief"],
            "body": "Not yet approved – waiting for legal.",
            "attachments": ["att_orbital_brief_v2_draft"]
        },
        "em_004": {
            "id": "em_004",
            "thread_id": "th_orbital",
            "folder": "inbox",
            "sender_id": "priya.dev@auroralabs.com",
            "subject": "Old test – v2 approved previously",
            "timestamp": "2025-03-12T09:00:00Z",
            "importance": "low",
            "labels": ["approved", "test"],
            "body": "Attached v2 approved but superseded by v3.",
            "attachments": ["att_orbital_brief_v2"]
        },
        "em_005": {
            "id": "em_005",
            "thread_id": "th_orbital",
            "folder": "spam",
            "sender_id": "spam@phish.com",
            "subject": "Approved Brief ????",
            "timestamp": "2025-03-16T02:00:00Z",
            "importance": "low",
            "labels": [],
            "body": "This is spam.",
            "attachments": []
        },
    }
    for em_id, content in emails.items():
        with open(f"data/emails/{em_id}.json", "w") as f:
            json.dump(content, f, indent=2)

    # ---------- Empty ops directory for output ----------
    # already created above

if __name__ == "__main__":
    build_env()
