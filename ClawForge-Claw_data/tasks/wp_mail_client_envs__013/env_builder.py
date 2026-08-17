import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Ensure base directories
    os.makedirs("data/emails", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Accounts
    accounts = [
        {
            "account_id": "acc_main",
            "display_name": "Main Office",
            "email_address": "office@company.com",
            "default_signature": "Best regards,\nMain Office",
            "auto_classify_enabled": True,
            "reply_templates_enabled": True,
            "task_generation_enabled": True,
            "folders": ["inbox", "spam", "newsletter", "work", "personal"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # Contacts
    contacts = [
        {"contact_id": "c001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "high"},
        {"contact_id": "c002", "name": "Bob Vendor", "email": "bob@vendor-services.com", "role": "Vendor", "team": "External", "priority": "normal"},
        {"contact_id": "c003", "name": "HR Department", "email": "hr@company.com", "role": "HR", "team": "Human Resources", "priority": "low"},
        {"contact_id": "c004", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "c005", "name": "Lottery Scam", "email": "winner@lottery-scam.com", "role": "Spammer", "team": "External", "priority": "low"},
        {"contact_id": "c006", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "normal"},
        {"contact_id": "c007", "name": "Tech Weekly", "email": "newsletter@techweekly.com", "role": "Newsletter", "team": "External", "priority": "low"},
        {"contact_id": "c008", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "normal"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # Helper to create email records
    def make_email(eid, thread_id, folder, sender_id, subject, importance, labels, body, attachments, auto_classify_suggestion, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        return {
            "id": eid,
            "thread_id": thread_id,
            "folder": folder,
            "sender_id": sender_id,
            "subject": subject,
            "timestamp": timestamp,
            "importance": importance,
            "labels": labels,
            "has_read": False,
            "body": body,
            "attachments": attachments,
            "auto_classify_suggestion": auto_classify_suggestion
        }

    # ========== Spam emails (2) ==========
    email_list = [
        make_email("e001", "t_spam1", "inbox", "c005", "You won a prize!", "high", ["spam"],
                   "Click here to claim your million dollars!",
                   [], "spam"),
        make_email("e002", "t_spam2", "inbox", "c005", "Urgent: Your account suspended", "high", ["spam"],
                   "Verify your account immediately or it will be deleted.",
                   [], "spam"),
        # ========== Newsletter emails (3) ==========
        make_email("e003", "t_news1", "inbox", "c007", "Tech Weekly Issue #42", "low", ["newsletter"],
                   "Top stories in tech this week: AI breakthroughs, new frameworks...",
                   [], "newsletter"),
        make_email("e004", "t_news2", "inbox", "c007", "Your weekly digest", "low", ["newsletter"],
                   "Here's what you missed: React 19 release notes, Python 3.13 beta.",
                   [], "newsletter"),
        make_email("e005", "t_news3", "inbox", "c007", "Special offer: Cloud courses", "low", ["newsletter"],
                   "Get 50% off on our cloud architect certification.",
                   [], "newsletter"),
        # ========== Alice Client complaint (need reply) ==========
        make_email("e010", "t_alice01", "inbox", "c001", "Invoice discrepancy - urgent", "high", ["work"],
                   "Hi,\nPlease review the attached quote. The total seems off from our agreement. I need confirmation of the final amount.\nRegards,\Alice\n\nTODO: Verify quote total and confirm receipt.",
                   ["data/attachments/quote_alice.csv"], "work"),
        # ========== Distractor emails ==========
        make_email("e020", "t_bob01", "inbox", "c002", "Monthly invoice", "normal", ["work"],
                   "Here is the invoice for February services. Total: 3200.00",
                   ["data/attachments/invoice_feb.csv"], "work"),
        make_email("e030", "t_hr01", "inbox", "c003", "Policy update", "low", ["hr"],
                   "Please read the new remote work policy attached.",
                   [], "hr"),
        make_email("e040", "t_spam_fake", "inbox", "c006", "Code review request", "normal", ["work"],
                   "Can you review my PR #42? Thanks!",
                   [], "work"),  # misclassified by system but suggestion is work
        make_email("e050", "t_news_fake", "inbox", "c004", "Team meeting notes", "normal", ["work"],
                   "Notes from Tuesday's meeting: project timeline updated.",
                   [], "work"),
    ]
    # add a few more for variety
    email_list.append(make_email("e060", "t_personal", "inbox", "c008", "Dinner this weekend?", "low", ["personal"],
                                 "Hey! Free on Saturday? Let's grab a burger.",
                                 [], "personal"))

    # Write email files
    for email in email_list:
        with open(f"data/emails/{email['id']}.json", "w") as f:
            json.dump(email, f, indent=2)

    # ========== Attachment for Alice ==========
    with open("data/attachments/quote_alice.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["item", "price"])
        writer.writerow(["Consulting", 1000.00])
        writer.writerow(["Tax (8%)", 80.00])
        writer.writerow(["Discount", -50.00])
        writer.writerow(["Shipping", 215.67])
        writer.writerow(["Total", 1245.67])

    # ========== Distractor attachment ==========
    with open("data/attachments/invoice_feb.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["description", "amount"])
        writer.writerow(["Service Fee", 3000.00])
        writer.writerow(["Tax", 200.00])
        writer.writerow(["Total", 3200.00])

    # Placeholder for agent output (initially empty)
    if not os.path.exists("ops/result.json"):
        with open("ops/result.json", "w") as f:
            f.write("{}")

if __name__ == "__main__":
    build_env()
