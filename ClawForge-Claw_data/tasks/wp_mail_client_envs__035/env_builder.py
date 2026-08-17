import os
import json

def build_env():
    # Create directories
    os.makedirs("data/emails", exist_ok=True)
    
    # Contacts data
    contacts = [
        {"contact_id": "sarah-dev-001", "name": "Sarah Developer", "email": "sarah.dev@company.com", "role": "Developer", "team": "Engineering", "priority": "high"},
        {"contact_id": "john-manager-001", "name": "John Manager", "email": "john.manager@company.com", "role": "Manager", "team": "Leadership", "priority": "high"},
        {"contact_id": "alice-client-001", "name": "Alice Client", "email": "alice@clientcorp.com", "role": "Client", "team": "External", "priority": "normal"},
        {"contact_id": "tom-friend-001", "name": "Tom Friend", "email": "tom.friend@gmail.com", "role": "Friend", "team": "Personal", "priority": "low"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)
    
    # Accounts (distractor)
    accounts = [
        {"account_id": "default", "display_name": "Me", "email_address": "me@company.com", "default_signature": "Best,\nMe", "auto_classify_enabled": True, "reply_templates_enabled": True, "task_generation_enabled": True, "folders": ["inbox", "work", "personal", "archive", "spam"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)
    
    # Emails – two target, three distractors
    emails = {
        "email-001": {
            "id": "email-001",
            "thread_id": "thread-001",
            "folder": "inbox",
            "sender_id": "sarah-dev-001",
            "subject": "Urgent: Budget Planning",
            "timestamp": "2025-03-01T08:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Hi,\n\nWe need the Q3 budget report ASAP. TODO: Prepare Q3 budget report\n\nThanks,\nSarah",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        "email-002": {
            "id": "email-002",
            "thread_id": "thread-002",
            "folder": "inbox",
            "sender_id": "sarah-dev-001",
            "subject": "Meeting Request",
            "timestamp": "2025-03-01T09:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Hi,\n\nLet's schedule a team meeting for next week. TODO: Schedule team meeting\n\nCheers,\nSarah",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        "email-003": {
            "id": "email-003",
            "thread_id": "thread-003",
            "folder": "work",
            "sender_id": "sarah-dev-001",
            "subject": "Printer issue",
            "timestamp": "2025-03-01T10:00:00Z",
            "importance": "low",
            "labels": [],
            "has_read": False,
            "body": "The printer is jammed. TODO: Check printer\n",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        "email-004": {
            "id": "email-004",
            "thread_id": "thread-004",
            "folder": "inbox",
            "sender_id": "sarah-dev-001",
            "subject": "Proposal Review",
            "timestamp": "2025-03-01T11:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": True,
            "body": "Please review the proposal. TODO: Review proposal\n",
            "attachments": [],
            "auto_classify_suggestion": "work"
        },
        "email-005": {
            "id": "email-005",
            "thread_id": "thread-005",
            "folder": "work",
            "sender_id": "john-manager-001",
            "subject": "Timesheet",
            "timestamp": "2025-03-01T12:00:00Z",
            "importance": "high",
            "labels": [],
            "has_read": False,
            "body": "Please submit your timesheet. TODO: Submit timesheet\n",
            "attachments": [],
            "auto_classify_suggestion": "work"
        }
    }
    
    for eid, data in emails.items():
        with open(f"data/emails/{eid}.json", "w") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    build_env()
