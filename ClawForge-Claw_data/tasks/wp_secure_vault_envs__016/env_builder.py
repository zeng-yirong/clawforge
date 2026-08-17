import json
import os

def build_env():
    # Create directories
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("ops", exist_ok=False)  # let agent create this; we don't pre-create

    # 1. category definitions
    categories = [
        {
            "category_id": "cat_work",
            "name": "工作邮箱",
            "priority": "critical",
            "requires_mfa": True,
            "password_policy": {"min_length": 12, "require_special": True, "require_digit": True}
        },
        {
            "category_id": "cat_bank",
            "name": "银行账户",
            "priority": "high",
            "requires_mfa": True,
            "password_policy": {"min_length": 12, "require_special": True, "require_digit": True}
        },
        {
            "category_id": "cat_ecom",
            "name": "电商平台",
            "priority": "medium",
            "requires_mfa": False,
            "password_policy": {"min_length": 8, "require_special": False, "require_digit": True}
        },
        {
            "category_id": "cat_social",
            "name": "社交媒体",
            "priority": "low",
            "requires_mfa": False,
            "password_policy": {"min_length": 8, "require_special": False, "require_digit": False}
        }
    ]
    with open("data/category_definitions.json", "w") as f:
        json.dump(categories, f, indent=2)

    # 2. vault dump with 5 valid + 3 invalid records (one missing password, one missing platform, one duplicate id)
    vault_records = [
        # valid records
        {"id": "C001", "platform": "gmail.com", "username": "alice", "password": "P@ssw0rd123!"},
        {"id": "C002", "platform": "outlook.com", "username": "bob", "password": "hello123"},
        {"id": "C003", "platform": "amazon.com", "username": "carol", "password": "Secure#123"},
        {"id": "C004", "platform": "bankofamerica.com", "username": "dave", "password": "Str0ng!Pass#"},
        {"id": "C005", "platform": "twitter.com", "username": "eve", "password": "eve123"},
        # invalid: missing password
        {"id": "C006", "platform": "github.com", "username": "frank", "password": ""},
        # invalid: missing platform
        {"id": "C007", "username": "grace", "password": "SomePass1!"},
        # duplicate id (same as C001, but different password) – should be ignored (first kept)
        {"id": "C001", "platform": "gmail.com", "username": "alice", "password": "weakpass1"}
    ]
    with open("data/vault_dump.json", "w") as f:
        json.dump(vault_records, f, indent=2)

    # 3. interference: backup directory with old vault files
    with open("data/backup/old_vault_2023.json", "w") as f:
        json.dump([{"id": "X001", "platform": "old", "username": "legacy", "password": "oldpass"}], f)
    with open("data/backup/README.txt", "w") as f:
        f.write("Do not use this.\n")

    # 4. extra unrelated file
    with open("data/notes.txt", "w") as f:
        f.write("Some irrelevant notes.\n")

if __name__ == "__main__":
    build_env()
