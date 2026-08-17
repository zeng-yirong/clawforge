import os
import json
import random

def build_env():
    # Create directories
    os.makedirs("ops", exist_ok=True)         # agent will place result here
    os.makedirs("vault_records/backup", exist_ok=True)

    # ==============================
    # Policy file (password rules)
    # ==============================
    policy = {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digit": True,
        "require_special": False
    }
    with open("policy.json", "w") as f:
        json.dump(policy, f, indent=2)

    # ==============================
    # Main vault export
    # ==============================
    records = [
        {"id": "id1",  "site": "gmail.com",       "username": "alice@corp.com",  "password": "Abcdef1!",   "category": "work_email"},
        {"id": "id2",  "site": "amazon.com",       "username": "bob@corp.com",   "password": "password",   "category": "ecommerce"},
        {"id": "id3",  "site": "bankofamerica.com","username": "charlie",        "password": "BankPass1",  "category": "banking"},
        {"id": "id4",  "site": "facebook.com",     "username": "david",          "password": "Fb12345",    "category": "social_media"},
        {"id": "id5",  "site": "outlook.com",      "username": "eve@corp.com",   "password": "EvePass9",   "category": "ecommerce"},   # misclassified (should be work_email)
        {"id": "id6",  "site": "ebay.com",         "username": "frank",          "password": "frank1234",  "category": "ecommerce"},
        {"id": "id7",  "site": "twitter.com",      "username": "grace",          "password": "Grace!2",    "category": "social_media"},
        {"id": "id8",  "site": "chase.com",        "username": "henry",          "password": "Henry123!",  "category": "banking"},
        {"id": "id9",  "site": "yahoo.com",        "username": "iris@corp.com",  "password": "iris123",    "category": "social_media"}, # misclassified (should be work_email)
        {"id": "id10", "site": "shopify.com",      "username": "jack",           "password": "Jack1234",   "category": "ecommerce"},
        {"id": "id11", "site": "linkedin.com",     "username": "kate",           "password": "pass",       "category": "social_media"},
        {"id": "id12", "site": "citi.com",         "username": "leo",            "password": "CitiPass1",  "category": "banking"},
    ]
    with open("vault_export.json", "w") as f:
        json.dump(records, f, indent=2)

    # ==============================
    # Distractors – backup directory
    # ==============================
    # Old vault format (different structure, ids not matching)
    old_records = [
        {"id": "old1", "service": "gmail.com", "user": "alice", "pw": "123456", "group": "old_work"},
        {"id": "old2", "service": "amazon.com", "user": "bob", "pw": "qwerty", "group": "old_shopping"},
    ]
    with open("vault_records/backup/vault_old.json", "w") as f:
        json.dump(old_records, f, indent=2)

    # Old schema (deprecated)
    old_schema = {
        "collection": "credential_categories",
        "categories": [
            {"name": "工作邮箱", "priority": "high", "requires_mfa": True},
            {"name": "电商平台", "priority": "medium", "requires_mfa": False}
        ]
    }
    with open("vault_records/backup/old_schema.json", "w") as f:
        json.dump(old_schema, f, indent=2)

    # Some irrelevant files
    with open("vault_records/backup/README.txt", "w") as f:
        f.write("This is an old backup. Ignore for current audit.\n")

    # A fake log file in root (noise)
    with open("recent_changes.log", "w") as f:
        f.write("2025-03-20 14:32: Updated vault export\n")
        f.write("2025-03-19 09:15: Policy revision applied\n")


if __name__ == "__main__":
    build_env()
