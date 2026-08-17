import os
import json
from datetime import datetime, timezone

def build_env():
    # emails
    emails_dir = "data/emails"
    attachments_dir = "attachments"
    ops_dir = "ops"
    os.makedirs(emails_dir, exist_ok=True)
    os.makedirs(attachments_dir, exist_ok=True)
    os.makedirs(ops_dir, exist_ok=True)  # empty for agent to write into

    # Helper to create email json
    def write_email(record_id, subject, folder, sender_id, importance, labels, timestamp, body, attachments_list):
        email = {
            "id": record_id,
            "thread_id": f"thr_{record_id}",
            "folder": folder,
            "sender_id": sender_id,
            "subject": subject,
            "timestamp": timestamp,
            "importance": importance,
            "labels": labels,
            "body": body,
            "attachments": attachments_list
        }
        with open(os.path.join(emails_dir, f"{record_id}.json"), "w") as f:
            json.dump(email, f, indent=2)

    # Create four emails, only one is the correct (latest approved)
    write_email(
        "em_001", "Draft Launch Brief v1", "inbox", "sender_01",
        "low", ["draft"], "2025-06-10T10:00:00Z",
        "This is an early draft, not approved.",
        ["attachments/draft_v1.txt"]
    )
    write_email(
        "em_002", "Launch Brief v2 - For Review", "inbox", "sender_02",
        "medium", ["review", "waiting_approval"], "2025-06-12T14:00:00Z",
        "Please review and send for approval.",
        ["attachments/review_v2.txt"]
    )
    write_email(
        "em_003", "Approved Launch Brief v3", "inbox", "sender_03",
        "high", ["approved", "final"], "2025-06-14T09:00:00Z",
        "Final approved brief. Use only this version.",
        ["attachments/approved_v3.txt"]
    )
    write_email(
        "em_004", "Launch Brief v2.1 - Updated", "inbox", "sender_03",
        "medium", ["approved", "old"], "2025-06-13T16:00:00Z",
        "Old approved version, superseded by v3.",
        ["attachments/approved_old.txt"]
    )

    # Create attachment files (interfering + correct)
    attachments = {
        "draft_v1.txt": "Product: Nova-5\nLaunch Date: 2025-06-10\nMessage for X: Old draft, ignore\nMessage for Reddit: Do not use",
        "review_v2.txt": "Product: Nova-6\nLaunch Date: 2025-06-18\nMessage for X: Still under review.\nMessage for Reddit: Not final.",
        "approved_v3.txt": "Product: Nova-7\nLaunch Date: 2025-06-20\nMessage for X: Excited to announce Nova-7, the next-gen orbital platform! #Nova7\nMessage for Reddit: We've been working hard on Nova-7. Check out the features! [link]",
        "approved_old.txt": "Product: Nova-7\nLaunch Date: 2025-06-19\nMessage for X: Slightly outdated message.\nMessage for Reddit: Outdated announcement.",
    }
    for fname, content in attachments.items():
        with open(os.path.join(attachments_dir, fname), "w") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
