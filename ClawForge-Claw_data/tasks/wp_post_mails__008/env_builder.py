import os
import json
import shutil
from datetime import datetime, timedelta

def build_env():
    # Clean slate
    for d in ["data/emails", "attachments", "ops"]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)

    # ── Attachments ──────────────────────────────────────────
    # old version (decoy)
    old_brief = """# Brief: Nova-7 (Legacy)
## Mission Details
- Mission Name: Nova-7
- Launch Code: 0315
- Payload: Commsat-3
- Orbit: LEO 400km
- Status: SUPERSEDED
"""
    with open("attachments/brief_v1.md", "w") as f:
        f.write(old_brief)

    # another decoy from different sender
    draft_brief = """# Draft: Nova-7 (unreviewed)
- Mission: Nova-7
- Code: 0428
- Note: Not signed off
"""
    with open("attachments/brief_draft.md", "w") as f:
        f.write(draft_brief)

    # The real approved brief (only this one is from Mira, latest)
    final_brief = """# Approval: Nova-7 Final
## Mission
- Mission Name: Nova-7
- Launch Code: 0428
- Payload: Commsat-4 & Relay-2
- Orbit: GTO 35786km
## Sign-off
- Director: Mira Chen
- Date: 2025-04-10
"""
    with open("attachments/brief_final.md", "w") as f:
        f.write(final_brief)

    # ── Emails ───────────────────────────────────────────────
    base_time = datetime(2025, 4, 9, 10, 0, 0)

    # Email 1: from Jon, old subject, no attachment
    email1 = {
        "id": "em_001",
        "thread_id": "thr_001",
        "folder": "inbox",
        "sender_id": "jon_bell",
        "subject": "Re: Nova-7 timeline",
        "timestamp": (base_time - timedelta(days=2)).isoformat(),
        "importance": "medium",
        "labels": ["brief", "discussion"],
        "body": "Attaching the old brief for reference.",
        "attachments": []
    }
    with open("data/emails/em_001.json", "w") as f:
        json.dump(email1, f)

    # Email 2: from Mira, subject "Brief v3 – final", attaches brief_final.md
    email2 = {
        "id": "em_002",
        "thread_id": "thr_002",
        "folder": "inbox",
        "sender_id": "mira_chen",
        "subject": "Brief final – approved",
        "timestamp": (base_time - timedelta(hours=2)).isoformat(),
        "importance": "high",
        "labels": ["brief", "approved", "launch"],
        "body": "Here is the signed-off version. Use this for all comms.",
        "attachments": [
            {
                "attachment_id": "att_brief_final",
                "filename": "brief_final.md",
                "mime_type": "text/markdown"
            }
        ]
    }
    with open("data/emails/em_002.json", "w") as f:
        json.dump(email2, f)

    # Email 3: from Nina, decoy about budget
    email3 = {
        "id": "em_003",
        "thread_id": "thr_003",
        "folder": "inbox",
        "sender_id": "nina_santos",
        "subject": "Budget update for Nova-7",
        "timestamp": (base_time - timedelta(hours=6)).isoformat(),
        "importance": "low",
        "labels": ["finance"],
        "body": "All costs are within budget.",
        "attachments": []
    }
    with open("data/emails/em_003.json", "w") as f:
        json.dump(email3, f)

    # Email 4: from Mira, older version (decoy with wrong code)
    email4 = {
        "id": "em_004",
        "thread_id": "thr_002",
        "folder": "inbox",
        "sender_id": "mira_chen",
        "subject": "Brief v2",
        "timestamp": (base_time - timedelta(days=1)).isoformat(),
        "importance": "high",
        "labels": ["brief", "draft"],
        "body": "Please review the changes.",
        "attachments": [
            {
                "attachment_id": "att_brief_v1",
                "filename": "brief_v1.md",
                "mime_type": "text/markdown"
            }
        ]
    }
    with open("data/emails/em_004.json", "w") as f:
        json.dump(email4, f)

    # Create a dummy ops directory (empty)
    open("ops/.gitkeep", "w").close()

if __name__ == "__main__":
    build_env()
