import os
import json
from datetime import datetime, timedelta

def build_env():
    # --- emails ---
    emails_dir = "data/emails"
    os.makedirs(emails_dir, exist_ok=True)

    # genuine approved brief (latest)
    brief = {
        "id": "em_009",
        "thread_id": "th_orbital",
        "folder": "inbox",
        "sender_id": "mira.chen@auroralabs.com",
        "subject": "Approved Brief – Orbital Launch",
        "timestamp": "2025-03-19T14:30:00Z",
        "importance": "high",
        "labels": ["approved", "brief", "launch"],
        "body": (
            "Product: Orbital Launch\n"
            "Launch Date: 2025-03-20\n"
            "Key Features:\n"
            "  - Real-time satellite tracking\n"
            "  - Modular payload integration\n"
            "  - One-click orbit adjustment\n"
            "Compliance notes: no competitor mentions, use 'next-gen' not 'revolutionary'\n"
            "CTA: Join the waitlist at orbital.auroralabs.com"
        ),
        "attachments": []
    }

    # older brief (also approved, but earlier – trap)
    old_brief = {
        "id": "em_003",
        "thread_id": "th_orbital",
        "folder": "inbox",
        "sender_id": "nina.santos@auroralabs.com",
        "subject": "Approved Brief v2 – Orbital Launch",
        "timestamp": "2025-03-17T09:00:00Z",
        "importance": "medium",
        "labels": ["approved", "brief"],
        "body": (
            "Product: Orbital Launch (old draft)\n"
            "Launch Date: 2025-03-22\n"
            "Key Features:\n"
            "  - Basic tracking\n"
            "  - Fixed payload\n"
            "Compliance: avoid the word 'revolutionary'\n"
            "CTA: Sign up"
        ),
        "attachments": []
    }

    # another random email – not approved, high importance
    spam = {
        "id": "em_012",
        "thread_id": "th_other",
        "folder": "inbox",
        "sender_id": "spam@example.com",
        "subject": "URGENT – Account Suspended",
        "timestamp": "2025-03-19T18:00:00Z",
        "importance": "high",
        "labels": ["spam"],
        "body": "Click here to verify your account.",
        "attachments": []
    }

    # email with no labels, just distraction
    noise = {
        "id": "em_015",
        "thread_id": "th_meeting",
        "folder": "inbox",
        "sender_id": "ava@example.com",
        "subject": "Team standup notes",
        "timestamp": "2025-03-18T10:15:00Z",
        "importance": "low",
        "labels": [],
        "body": "All good for this week.",
        "attachments": []
    }

    for em in [brief, old_brief, spam, noise]:
        with open(os.path.join(emails_dir, f"{em['id']}.json"), "w") as f:
            json.dump(em, f, indent=2)

    # --- social posts ---
    social_dir = "data/social"
    os.makedirs(social_dir, exist_ok=True)

    posts = [
        {
            "post_id": "p001",
            "platform": "reddit",
            "author_id": "user_delta",
            "title": "Any news on new launch system?",
            "community": "r/spacetech",
            "content": "I heard Orbital Launch is coming. When and what features?",
            "timestamp": "2025-03-18T20:00:00Z",
            "tags": ["question", "launch"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "p002",
            "platform": "x",
            "author_id": "user_gamma",
            "title": "",
            "community": "",
            "content": "When will Orbital Launch be available? Need details!",
            "timestamp": "2025-03-19T08:00:00Z",
            "tags": ["question"],
            "needs_response": True,
            "replies": []
        },
        {
            "post_id": "p003",
            "platform": "reddit",
            "author_id": "user_epsilon",
            "title": "Orbital Launch rumors",
            "community": "r/space",
            "content": "Saw some leaks. Is it true?",
            "timestamp": "2025-03-18T12:00:00Z",
            "tags": ["rumor"],
            "needs_response": False,        # already answered in thread
            "replies": [{"author": "support", "content": "Please wait for official announcement."}]
        },
        {
            "post_id": "p004",
            "platform": "x",
            "author_id": "user_beta",
            "title": "",
            "community": "",
            "content": "Just saw the teaser! Hype! #OrbitalLaunch",
            "timestamp": "2025-03-19T10:00:00Z",
            "tags": ["hype"],
            "needs_response": False,        # no question, just hype
            "replies": []
        },
        {
            "post_id": "p005",
            "platform": "reddit",
            "author_id": "user_alpha",
            "title": "Comparison with competitors?",
            "community": "r/spacetech",
            "content": "How does Orbital Launch compare to Starship?",
            "timestamp": "2025-03-19T11:00:00Z",
            "tags": ["comparison", "question"],
            "needs_response": True,
            "replies": []
        }
    ]
    for p in posts:
        with open(os.path.join(social_dir, f"{p['post_id']}.json"), "w") as f:
            json.dump(p, f, indent=2)

    # --- accounts ---
    accounts = {
        "accounts": [
            {
                "account_id": "acc_main",
                "display_name": "Aurora Labs",
                "brand_name": "Aurora Labs",
                "x_handle": "@auroralabs",
                "reddit_profile": "u/auroralabs_official",
                "default_reddit_community": "r/spacetech",
                "voice": ["professional", "enthusiastic"],
                "cta": "Join the waitlist at orbita... via the link in bio",
                "compliance_notes": [
                    "Never compare directly with competitors",
                    "Do not use 'revolutionary' or 'disruptive'",
                    "Keep X posts under 280 characters"
                ]
            }
        ]
    }
    os.makedirs("data", exist_ok=True)
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- contacts ---
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Mira Chen", "email": "mira.chen@auroralabs.com", "role": "Product Marketing Lead", "team": "Marketing", "social_handle": "@mirachen_legal"},
            {"contact_id": "c002", "name": "Nina Santos", "email": "nina.santos@auroralabs.com", "role": "Community Lead", "team": "Community", "social_handle": "@ninasantos_pm"},
            {"contact_id": "c003", "name": "Ava Price", "email": "ava@example.com", "role": "Support Manager", "team": "Support", "social_handle": "@avapractical"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ensure ops directory exists for output
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
