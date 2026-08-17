import os
import csv
import json
import random

def build_env():
    # Ensure base directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("policies", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # ---- raw_credentials.csv (15 rows with duplicates and mixed categories) ----
    raw_creds = [
        # id, username, password, category
        (1, "alice",   "Pass123!",       "work"),
        (2, "bob",     "password123",    "personal"),
        (3, "charlie", "Secure#1",       "bank"),
        (4, "dave",    "weak",           "personal"),
        (5, "eve",     "Eve@2023",       "shop"),
        (6, "frank",   "Str0ng!Pass",    "bank"),
        (7, "grace",   "12345678",       "work"),        # weak: 8 digits, no upper/special
        (8, "heidi",   "Heidi!99",       "shop"),
        (9, "ivan",    "Ivan#2023",      "mail"),        # mail category not in mapping
        (1, "alice2",  "NewPass456",     "work"),        # duplicate id=1, last occurrence
        (10, "judy",   "Judy@1",         "personal"),    # weak because length 7
        (11, "karl",   "Karl!Pass1",     "bank"),
        (12, "lisa",   "Lisa#1",         "shop"),
        (13, "mike",   "Mike!2023",      "work"),
        (7, "grace2", "Grace!1",         "work"),        # duplicate id=7
        (14, "nina",   "Nina!2023",      "bank"),
        (15, "oscar",  "Oscar#1",        "personal"),
        (2, "bob2",   "bobpassword",     "personal"),    # duplicate id=2
    ]
    with open("data/raw_credentials.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id","username","password","category"])
        for row in raw_creds:
            writer.writerow(row)

    # ---- category_mapping.csv ----
    cat_mapping = [
        ("work",     "工作邮箱"),
        ("personal", "社交媒体"),
        ("bank",     "银行账户"),
        ("shop",     "电商平台"),
    ]
    with open("data/category_mapping.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["raw_category","vault_category"])
        writer.writerows(cat_mapping)

    # ---- vault_schema.json (reference only) ----
    vault_schema = {
        "categories": [
            {"category_id": "work",       "name": "工作邮箱", "priority": "high", "requires_mfa": True},
            {"category_id": "personal",   "name": "社交媒体", "priority": "medium", "requires_mfa": False},
            {"category_id": "bank",       "name": "银行账户", "priority": "critical", "requires_mfa": True},
            {"category_id": "shop",       "name": "电商平台", "priority": "low", "requires_mfa": False},
        ]
    }
    with open("data/vault_schema.json", "w") as f:
        json.dump(vault_schema, f, indent=2)

    # ---- password_policy.json ----
    policy = {
        "min_length": 8,
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_special": True
    }
    with open("policies/password_policy.json", "w") as f:
        json.dump(policy, f, indent=2)

    # ---- Distractor files ----
    # Log file (irrelevant)
    with open("logs/audit.log", "w") as f:
        f.write("[2025-01-15 03:12:44] INFO  Credential audit started\n")
        f.write("[2025-01-15 03:13:21] WARN  Duplicate entry detected (id=1)\n")
        f.write("[2025-01-15 03:14:05] INFO  Audit finished\n")
    # Backup file (irrelevant)
    with open("backup/old_credentials.json", "w") as f:
        json.dump([{"id": 100, "username": "legacy"}], f)

if __name__ == "__main__":
    build_env()
