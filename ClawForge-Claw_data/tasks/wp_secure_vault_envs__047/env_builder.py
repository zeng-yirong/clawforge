import os
import json
import csv

def build_env():
    # 创建目录结构
    os.makedirs("vault", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # 干扰目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # 1. vault/schema.json
    schema = {
        "categories": [
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
                    "require_special": True
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
                "category_id": "bank",
                "name": "银行账户",
                "priority": "critical",
                "requires_mfa": True,
                "password_policy": {
                    "min_length": 14,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_digit": True,
                    "require_special": True
                }
            }
        ]
    }
    with open("vault/schema.json", "w") as f:
        json.dump(schema, f, indent=2)

    # 2. vault/credentials.json (已有凭证，含干扰项)
    existing_creds = [
        {
            "platform": "internal_tools",
            "username": "admin",
            "password": "OldPass123!",
            "category_id": "work_email",
            "autofill": False
        },
        {
            "platform": "shopify",
            "username": "store_manager",
            "password": "Shopify123",
            "category_id": "ecommerce",
            "autofill": True
        }
    ]
    with open("vault/credentials.json", "w") as f:
        json.dump(existing_creds, f, indent=2)

    # 3. ops/password_rules.json
    rules = {
        "method": "concat",
        "parts": ["platform[:4]", "username[-4:]", "@2025"]
    }
    with open("ops/password_rules.json", "w") as f:
        json.dump(rules, f, indent=2)

    # 4. ops/onboard.csv
    onboard_data = [
        {"platform": "internal_dashboard", "username": "john.doe", "category_id": "work_email"},
        {"platform": "external_portal",   "username": "jane.smith", "category_id": "ecommerce"}
    ]
    with open("ops/onboard.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["platform", "username", "category_id"])
        writer.writeheader()
        writer.writerows(onboard_data)

    # 5. 干扰文件
    with open("logs/audit.log", "w") as f:
        f.write("2025-03-01 08:00:00 INFO Starting vault service\n")
        f.write("2025-03-01 08:05:12 WARN Password policy violation detected for user 'admin'\n")

    backup_creds = [
        {"platform": "deprecated", "username": "oldadmin", "password": "weak", "category_id": "work_email", "autofill": False}
    ]
    with open("backup/credentials_backup.json", "w") as f:
        json.dump(backup_creds, f, indent=2)

    # 6. 额外干扰：一个无关的 README.md
    with open("README.md", "w") as f:
        f.write("# Vault Manager\nDo not modify this file.\n")

if __name__ == "__main__":
    build_env()
