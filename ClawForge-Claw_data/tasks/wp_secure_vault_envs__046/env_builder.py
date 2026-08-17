import os
import json

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("output", exist_ok=True)  # 空目录，留待 agent 写入

    # 1. vault_schema.json
    schema = {
        "credential_categories": [
            {
                "category_id": "work_email",
                "name": "工作邮箱",
                "priority": "critical",
                "requires_mfa": True,
                "password_policy": {
                    "min_length": 12,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_digit": True,
                    "require_special": True,
                    "special_chars": "!@#$%^&*"
                }
            },
            {
                "category_id": "ecommerce",
                "name": "电商平台",
                "priority": "high",
                "requires_mfa": False,
                "password_policy": {
                    "min_length": 10,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_digit": True,
                    "require_special": False
                }
            },
            {
                "category_id": "social_media",
                "name": "社交媒体",
                "priority": "medium",
                "requires_mfa": False,
                "password_policy": {
                    "min_length": 8,
                    "require_uppercase": False,
                    "require_lowercase": True,
                    "require_digit": True,
                    "require_special": False
                }
            },
            {
                "category_id": "bank_account",
                "name": "银行账户",
                "priority": "critical",
                "requires_mfa": True,
                "password_policy": {
                    "min_length": 14,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_digit": True,
                    "require_special": True,
                    "special_chars": "!@#$%^&*"
                }
            }
        ]
    }
    with open("data/vault_schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    # 2. credentials.json
    credentials = [
        {"id": "cred-001", "username": "admin@work.com", "platform": "WorkMail", "password": "P@ssw0rd2024!", "category_id": "work_email", "created_at": "2024-10-01"},
        {"id": "cred-002", "username": "john.doe@shop.com", "platform": "ShopNow", "password": "Password123", "category_id": "ecommerce", "created_at": "2024-09-15"},
        {"id": "cred-003", "username": "jane_social", "platform": "Instagram", "password": "abc123", "category_id": "social_media", "created_at": "2024-11-01"},
        {"id": "cred-004", "username": "jane_social", "platform": "Instagram", "password": "Abcd1234!", "category_id": "social_media", "created_at": "2024-11-05"},
        {"id": "cred-005", "username": "bank.user", "platform": "BankApp", "password": "Short1!", "category_id": "bank_account", "created_at": "2024-08-20"},
        {"id": "cred-006", "username": "bank.user", "platform": "BankApp", "password": "Str0ng!BankPass2024", "category_id": "bank_account", "created_at": "2024-10-10"},
        {"id": "cred-007", "username": "unknown_user", "platform": "SomeApp", "password": "Test1234", "category_id": "unknown_category", "created_at": "2024-12-01"},
        {"id": "cred-008", "username": "guest", "platform": "GuestWiFi", "password": "", "category_id": "work_email", "created_at": "2024-11-20"},
        {"id": "cred-009", "username": "alice", "platform": "WorkMail", "password": "Alice!2024Long", "category_id": "work_email", "created_at": "2024-12-01"},
        {"id": "cred-010", "username": "bob", "platform": "Ebay", "password": "bobpassword", "category_id": "ecommerce", "created_at": "2024-11-11"}
    ]
    with open("data/credentials.json", "w", encoding="utf-8") as f:
        json.dump(credentials, f, indent=2)

    # 3. audit_log.csv
    import csv
    audit_rows = [
        {"credential_id": "cred-001", "accessed_at": "2024-12-15"},
        {"credential_id": "cred-002", "accessed_at": "2024-12-14"},
        {"credential_id": "cred-004", "accessed_at": "2024-12-13"},
        {"credential_id": "cred-006", "accessed_at": "2024-12-12"},
        {"credential_id": "cred-009", "accessed_at": "2024-12-11"},
        {"credential_id": "cred-010", "accessed_at": "2024-12-10"}
    ]
    with open("data/audit_log.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["credential_id", "accessed_at"])
        writer.writeheader()
        writer.writerows(audit_rows)

    # 4. 干扰文件：备份
    backup_creds = [
        {"id": "cred-003", "username": "jane_social", "platform": "Instagram", "password": "oldpass", "category_id": "social_media", "created_at": "2024-10-01"}
    ]
    with open("backups/old_vault.json", "w", encoding="utf-8") as f:
        json.dump({"version": "2024-09", "credentials": backup_creds}, f, indent=2)

    with open("backups/temp.txt", "w") as f:
        f.write("This is a temporary file, ignore me.\n")

if __name__ == "__main__":
    build_env()
