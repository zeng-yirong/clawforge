import os
import json
import random

def build_env():
    # Ensure we are in the correct working directory (.)
    base = os.getcwd()

    # Create necessary directories
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Write contacts.json (with Bob and several others)
    contacts = [
        {"contact_id": "bob_vendor", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "high"},
        {"contact_id": "alice_client", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "normal"},
        {"contact_id": "john_manager", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "lottery_scam", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "sarah_dev", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # Write a minimal accounts.json (required by schema but not used directly)
    accounts = {
        "accounts": [{
            "account_id": "default",
            "display_name": "Mike Sales",
            "email_address": "mike@company.com",
            "default_signature": "Best, Mike",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["inbox", "sent", "archived"]
        }]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # Helper to create an email JSON
    def make_email(eid, sender_id, folder, subject, body, attachments, has_read=False, importance="normal", labels=None, auto_classify="work"):
        if labels is None:
            labels = ["inbox"]
        return {
            "id": eid,
            "thread_id": f"thread_{eid}",
            "folder": folder,
            "sender_id": sender_id,
            "subject": subject,
            "timestamp": "2025-03-20T10:00:00Z",
            "importance": importance,
            "labels": labels,
            "has_read": has_read,
            "body": body,
            "attachments": attachments,
            "auto_classify_suggestion": auto_classify
        }

    # ---- Email list ----
    emails = []

    # Bob's unread orders (3 emails) – the target
    bob_amounts = [150, 200, 350]  # total = 700? Wait 150+200+350=700, but let's use 150+200+350=700? Actually 150+200+350=700.
    # Let's change to 100, 200, 350 => 650
    bob_amounts = [100, 200, 350]
    for i, amt in enumerate(bob_amounts, 1):
        eid = f"email_bob_unread_{i:03d}"
        att_path = f"data/attachments/att_{eid}.txt"
        with open(att_path, "w") as f:
            f.write(f"{amt}\n")
        email = make_email(
            eid=eid,
            sender_id="bob_vendor",
            folder="inbox",
            subject=f"Order confirmation #{i}",
            body=f"Please see attached order details.",
            attachments=[{"filename": f"order_{i}.txt", "path": att_path}],
            has_read=False,
            importance="high",
            labels=["inbox"],
            auto_classify="work"
        )
        emails.append(email)

    # Bob's read email (should be ignored) – also has an attachment
    eid_read = "email_bob_read_001"
    att_read = f"data/attachments/att_{eid_read}.txt"
    with open(att_read, "w") as f:
        f.write("500\n")
    emails.append(make_email(
        eid=eid_read,
        sender_id="bob_vendor",
        folder="inbox",
        subject="Already reviewed order",
        body="Old order.",
        attachments=[{"filename": "old_order.txt", "path": att_read}],
        has_read=True,
        importance="normal"
    ))

    # Alice's email (different sender) – has attachment but should be ignored
    eid_alice = "email_alice_001"
    att_alice = f"data/attachments/att_{eid_alice}.txt"
    with open(att_alice, "w") as f:
        f.write("99.99\n")
    emails.append(make_email(
        eid=eid_alice,
        sender_id="alice_client",
        folder="inbox",
        subject="Feedback on project",
        body="Let's discuss.",
        attachments=[{"filename": "feedback.txt", "path": att_alice}],
        has_read=False,
        importance="normal"
    ))

    # Lottery scam (spam) – no attachment, should be ignored
    emails.append(make_email(
        eid="email_scam_001",
        sender_id="lottery_scam",
        folder="inbox",
        subject="You won!",
        body="Click here.",
        attachments=[],
        has_read=False,
        importance="low",
        auto_classify="spam"
    ))

    # John's email (manager) – no attachment
    emails.append(make_email(
        eid="email_john_001",
        sender_id="john_manager",
        folder="inbox",
        subject="Meeting reminder",
        body="Tomorrow at 10.",
        attachments=[],
        has_read=True,
        importance="normal",
        auto_classify="work"
    ))

    # Sarah's email – attachment with non-numeric content (text)
    eid_sarah = "email_sarah_001"
    att_sarah = f"data/attachments/att_{eid_sarah}.txt"
    with open(att_sarah, "w") as f:
        f.write("Hello, this is not a number.\n")
    emails.append(make_email(
        eid=eid_sarah,
        sender_id="sarah_dev",
        folder="inbox",
        subject="Code review",
        body="See attached notes.",
        attachments=[{"filename": "notes.txt", "path": att_sarah}],
        has_read=False,
        importance="normal"
    ))

    # Write all emails
    for email in emails:
        eid = email["id"]
        with open(f"data/emails/{eid}.json", "w") as f:
            json.dump(email, f, indent=2)

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
