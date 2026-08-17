import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # Ensure base directories exist
    for d in ["data/emails", "data/attachments", "data/social"]:
        os.makedirs(d, exist_ok=True)

    # --- Contacts (background noise) ---
    contacts = [
        {"contact_id": "c001", "name": "Ava Price", "email": "ava@example.com", "role": "Community Lead", "team": "Community", "social_handle": "@avapractical"},
        {"contact_id": "c002", "name": "Mia Hart", "email": "mia.hart@auroralabs.com", "role": "Legal Counsel", "team": "Legal", "social_handle": "@mirachen_legal"},
        {"contact_id": "c003", "name": "Nina Santos", "email": "nina.santos@auroralabs.com", "role": "Product Marketing Lead", "team": "Marketing", "social_handle": "@ninasantos_pm"},
        {"contact_id": "c004", "name": "Owen Park", "email": "owen.park@auroralabs.com", "role": "Support Manager", "team": "Support", "social_handle": "@owen_builds"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- Accounts (background) ---
    accounts = [
        {"account_id": "acc_aurora", "display_name": "Aurora Labs", "brand_name": "Aurora", "x_handle": "@auroralabs", "reddit_profile": "u/auroralabs", "default_reddit_community": "r/aurora", "voice": ["professional", "enthusiastic"], "cta": "Join the mesh", "compliance_notes": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- Emails ---
    # Correct answer: em_004 (latest, approved, high importance, with attachment)
    emails = [
        # 1) Old draft brief – high importance but not approved
        {
            "id": "em_001",
            "thread_id": "th_launch",
            "folder": "inbox",
            "sender_id": "owen.park@auroralabs.com",
            "subject": "Draft Brief v1 – feedback needed",
            "timestamp": "2025-06-18T09:15:00Z",
            "importance": "high",
            "labels": ["draft", "feedback"],
            "body": "Here is the first version of the brief, please review.",
            "attachments": [{"id": "att_brief_v1", "type": "brief"}]
        },
        # 2) Discussion thread – no attachment
        {
            "id": "em_002",
            "thread_id": "th_launch",
            "folder": "inbox",
            "sender_id": "nina.santos@auroralabs.com",
            "subject": "Re: timeline discussion",
            "timestamp": "2025-06-19T14:22:00Z",
            "importance": "medium",
            "labels": ["discussion"],
            "body": "Let's sync on the timeline later.",
            "attachments": []
        },
        # 3) Another draft – importance low, not approved
        {
            "id": "em_003",
            "thread_id": "th_launch",
            "folder": "inbox",
            "sender_id": "owen.park@auroralabs.com",
            "subject": "Draft Brief v2 – minor updates",
            "timestamp": "2025-06-19T16:45:00Z",
            "importance": "low",
            "labels": ["draft"],
            "body": "Updated version with new features list.",
            "attachments": [{"id": "att_brief_v2", "type": "brief"}]
        },
        # 4) Final approved brief – correct answer
        {
            "id": "em_004",
            "thread_id": "th_launch",
            "folder": "inbox",
            "sender_id": "mia.hart@auroralabs.com",
            "subject": "Final Approval – Orbital Mesh Brief",
            "timestamp": "2025-06-20T10:30:00Z",
            "importance": "high",
            "labels": ["approved", "legal", "final"],
            "body": "All checks passed. Attached is the final brief for launch.",
            "attachments": [{"id": "att_brief_v3", "type": "brief"}]
        },
        # 5) Spam / noise – malformed (missing attachments field)
        {
            "id": "em_005",
            "thread_id": "th_spam",
            "folder": "inbox",
            "sender_id": "spam@spam.com",
            "subject": "You won a prize!",
            "timestamp": "2025-06-20T11:00:00Z",
            "importance": "low",
            "labels": ["spam"],
            "body": "Click here to claim."
            # deliberately no "attachments" key
        }
    ]
    # Write emails, skipping malformed one (em_005) which we write without attachments key
    for em in emails:
        fname = f"data/emails/{em['id']}.json"
        with open(fname, "w") as f:
            json.dump(em, f, indent=2)

    # --- Attachments ---
    attachments = [
        {
            "id": "att_brief_v1",
            "type": "brief",
            "content": {
                "product_name": "Orbital Mesh Alpha",
                "launch_date": "2025-08-01",
                "features": ["Basic routing", "Standard encryption"]
            }
        },
        {
            "id": "att_brief_v2",
            "type": "brief",
            "content": {
                "product_name": "Orbital Mesh Beta",
                "launch_date": "2025-09-01",
                "features": ["Enhanced routing", "AES-256 encryption"]
            }
        },
        {
            "id": "att_brief_v3",
            "type": "brief",
            "content": {
                "product_name": "Orbital Mesh",
                "launch_date": "2025-09-15",
                "features": ["Auto-optimizing routing", "Quantum-safe encryption", "Real-time mesh analytics"]
            }
        }
    ]
    for att in attachments:
        fname = f"data/attachments/{att['id']}.json"
        with open(fname, "w") as f:
            json.dump(att, f, indent=2)

    # --- Social posts ---
    posts = [
        {
            "post_id": "post_001",
            "platform": "reddit",
            "author_id": "user_xyz",
            "title": "Question about launch",
            "content": "When will the product be available?",
            "timestamp": "2025-06-19T08:00:00Z",
            "tags": ["question"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "post_002",
            "platform": "x",
            "author_id": "user_abc",
            "title": "",
            "content": "Interested in beta features!",
            "timestamp": "2025-06-20T12:00:00Z",
            "tags": ["interest"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "post_003",
            "platform": "reddit",
            "author_id": "user_def",
            "title": "Great news",
            "content": "Looking forward to the launch!",
            "timestamp": "2025-06-18T20:00:00Z",
            "tags": ["praise"],
            "needs_response": False,
            "replies": []
        },
        {
            "post_id": "post_004",
            "platform": "x",
            "author_id": "user_ghi",
            "title": "",
            "content": "Any pricing info?",
            "timestamp": "2025-06-21T09:00:00Z",
            "tags": ["question"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "post_005",
            "platform": "reddit",
            "author_id": "user_jkl",
            "title": "Rant",
            "content": "This is not good enough",
            "timestamp": "2025-06-17T15:00:00Z",
            "tags": ["rant"],
            "needs_response": False,
            "replies": []
        }
    ]
    for p in posts:
        fname = f"data/social/{p['post_id']}.json"
        with open(fname, "w") as f:
            json.dump(p, f, indent=2)

if __name__ == "__main__":
    build_env()
