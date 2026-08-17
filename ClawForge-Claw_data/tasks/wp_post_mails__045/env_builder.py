import os
import json
import shutil
from datetime import datetime, timedelta

def build_env():
    # Clean and create directories
    for d in ['emails', 'attachments', 'social']:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)

    # --- Accounts (single account) ---
    accounts = [{
        "account_id": "aurora_main",
        "display_name": "Aurora Labs",
        "brand_name": "Aurora Labs",
        "x_handle": "@AuroraLabs",
        "reddit_profile": "u/aurora_official",
        "default_reddit_community": "r/Aerospace",
        "voice": ["professional", "excited"],
        "cta": "Learn more at auroralabs.com",
        "compliance_notes": ["All launch dates must match approved press release"]
    }]
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # --- Contacts ---
    contacts = [
        {"contact_id": "c001", "name": "Mira Chen", "email": "mira.chen@auroralabs.com",
         "role": "Product Marketing Lead", "team": "Marketing", "social_handle": "@mirachen_pm"},
        {"contact_id": "c002", "name": "Jon Bell", "email": "jon@example.com",
         "role": "Creator", "team": "External", "social_handle": "@jonbellops"},
        {"contact_id": "c003", "name": "Priya Dev", "email": "priya.dev@auroralabs.com",
         "role": "Community Lead", "team": "Community", "social_handle": "@priyadev_ops"}
    ]
    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- Build email files (7 emails, only one is approved and latest) ---
    base_time = datetime(2025, 4, 10, 14, 0, 0)  # April 10, 2025

    # Email 1: old draft (importance low, not approved)
    email1 = {
        "id": "em_001",
        "thread_id": "th_orion",
        "folder": "inbox",
        "sender_id": "c002",  # Jon Bell (creator)
        "subject": "Orion launch draft v1",
        "timestamp": (base_time - timedelta(days=5)).isoformat(),
        "importance": "low",
        "labels": ["draft"],
        "body": "Attached is the first draft for the Orion launch. Needs review.",
        "attachments": ["att_orion_draft_v1.txt"]
    }
    with open("emails/em_001.json", "w") as f:
        json.dump(email1, f, indent=2)

    # Email 2: another draft (low, not approved)
    email2 = {
        "id": "em_002",
        "thread_id": "th_orion",
        "folder": "inbox",
        "sender_id": "c003",
        "subject": "Orion revised draft v2",
        "timestamp": (base_time - timedelta(days=3)).isoformat(),
        "importance": "low",
        "labels": ["draft"],
        "body": "Updated draft with corrected satellite count. Still waiting for approval.",
        "attachments": ["att_orion_draft_v2.txt"]
    }
    with open("emails/em_002.json", "w") as f:
        json.dump(email2, f, indent=2)

    # Email 3: competitor spam (irrelevant)
    email3 = {
        "id": "em_003",
        "thread_id": "th_other",
        "folder": "inbox",
        "sender_id": "c002",
        "subject": "SpaceX Starship news",
        "timestamp": (base_time - timedelta(days=2)).isoformat(),
        "importance": "low",
        "labels": ["news"],
        "body": "Check out this Starship update.",
        "attachments": []
    }
    with open("emails/em_003.json", "w") as f:
        json.dump(email3, f, indent=2)

    # Email 4: marketing team's unauthorized version (high but not approved)
    email4 = {
        "id": "em_004",
        "thread_id": "th_orion",
        "folder": "inbox",
        "sender_id": "c001",  # Mira herself (marketing)
        "subject": "Orion launch - marketing version",
        "timestamp": (base_time - timedelta(days=1)).isoformat(),
        "importance": "high",
        "labels": ["marketing", "final"],
        "body": "I polished the numbers a bit. Sending to legal for quick check.",
        "attachments": ["att_orion_marketing_v3.txt"]
    }
    with open("emails/em_004.json", "w") as f:
        json.dump(email4, f, indent=2)

    # Email 5: legal review (medium, not approved)
    email5 = {
        "id": "em_005",
        "thread_id": "th_orion",
        "folder": "inbox",
        "sender_id": "c003",
        "subject": "Legal feedback on Orion",
        "timestamp": (base_time - timedelta(hours=12)).isoformat(),
        "importance": "medium",
        "labels": ["legal"],
        "body": "Need to remove unverified claim about fuel efficiency. Revised version attached.",
        "attachments": ["att_orion_legal_v4.txt"]
    }
    with open("emails/em_005.json", "w") as f:
        json.dump(email5, f, indent=2)

    # Email 6: **THE APPROVED FINAL** (high, approved label, latest timestamp)
    email6 = {
        "id": "em_006",
        "thread_id": "th_orion",
        "folder": "inbox",
        "sender_id": "c003",
        "subject": "APPROVED - Orion launch brief FINAL",
        "timestamp": (base_time - timedelta(hours=1)).isoformat(),
        "importance": "high",
        "labels": ["approved", "final"],
        "body": "Product VP signed off. Use this for all official comms.",
        "attachments": ["att_orion_brief_final.txt"]
    }
    with open("emails/em_006.json", "w") as f:
        json.dump(email6, f, indent=2)

    # Email 7: old approved but outdated (approved label, but timestamp older than em_006)
    email7 = {
        "id": "em_007",
        "thread_id": "th_orion",
        "folder": "inbox",
        "sender_id": "c003",
        "subject": "Old approved brief - do not use",
        "timestamp": (base_time - timedelta(days=7)).isoformat(),
        "importance": "medium",
        "labels": ["approved"],
        "body": "This was approved last month but superseded.",
        "attachments": ["att_orion_brief_v0.txt"]
    }
    with open("emails/em_007.json", "w") as f:
        json.dump(email7, f, indent=2)

    # --- Attachments (text files) ---
    # 1. Draft v1
    with open("attachments/att_orion_draft_v1.txt", "w") as f:
        f.write("Project Orion Launch Draft v1\nLaunch date: TBD\nSatellites: 10\nPayload: communication\nPartner: None\n")
    # 2. Draft v2
    with open("attachments/att_orion_draft_v2.txt", "w") as f:
        f.write("Orion Launch v2\nLaunch date: 2025-08-15\nSatellites: 14\nPayload: communication + weather\nPartner: NASA\n")
    # 3. Marketing v3 (fudged numbers)
    with open("attachments/att_orion_marketing_v3.txt", "w") as f:
        f.write("Marketing Orion Launch\nLaunch date: 2025-09-01\nSatellites: 15\nPayload: broadband\nPartner: SpaceX\n")
    # 4. Legal v4
    with open("attachments/att_orion_legal_v4.txt", "w") as f:
        f.write("Legal reviewed Orion\nLaunch date: 2025-09-20\nSatellites: 12\nPayload: communication, weather, imaging\nPartner: ESA\n")
    # 5. **FINAL APPROVED** (this is the truth)
    with open("attachments/att_orion_brief_final.txt", "w") as f:
        f.write("ORION LAUNCH BRIEF – APPROVED FINAL\nLaunch Date: 2025-09-20\nNumber of Satellites: 12\nPrimary Payload: Communication, Weather Imaging, Earth Observation\nPartner: European Space Agency (ESA)\nKey Fact: First commercial constellation to include ESA's new VISIR sensor.\n")
    # 6. Old v0
    with open("attachments/att_orion_brief_v0.txt", "w") as f:
        f.write("Legacy Orion Brief\nLaunch date: 2025-07-04\nSatellites: 8\nPayload: comms\nPartner: None\n")

    # --- Social posts (one needs_response) ---
    # Existing post 1: announcement placeholder (needs_response false)
    post1 = {
        "post_id": "x_001",
        "platform": "x",
        "author_id": "c001",
        "title": "Orion launch teaser",
        "community": "",
        "content": "Something big is coming... #Orion",
        "timestamp": (base_time - timedelta(hours=2)).isoformat(),
        "tags": ["teaser"],
        "needs_response": False,
        "replies": []
    }
    with open("social/x_001.json", "w") as f:
        json.dump(post1, f, indent=2)

    # Existing post 2: community question (needs_response true)
    post2 = {
        "post_id": "reddit_101",
        "platform": "reddit",
        "author_id": "c003",
        "title": "Question about Orion payload capabilities",
        "community": "r/Aerospace",
        "content": "I read that Orion will carry a new sensor. Can anyone confirm the exact payloads and whether ESA is involved?",
        "timestamp": (base_time - timedelta(hours=6)).isoformat(),
        "tags": ["question", "Orion"],
        "needs_response": True,
        "replies": [
            {
                "author_id": "c002",
                "content": "I think it's only communication satellites.",
                "timestamp": (base_time - timedelta(hours=5)).isoformat()
            }
        ]
    }
    with open("social/reddit_101.json", "w") as f:
        json.dump(post2, f, indent=2)

    # Existing post 3: other unrelated (needs_response false)
    post3 = {
        "post_id": "x_002",
        "platform": "x",
        "author_id": "c003",
        "title": "Office tour",
        "community": "",
        "content": "Come see our new lab.",
        "timestamp": (base_time - timedelta(hours=3)).isoformat(),
        "tags": ["office"],
        "needs_response": False,
        "replies": []
    }
    with open("social/x_002.json", "w") as f:
        json.dump(post3, f, indent=2)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
