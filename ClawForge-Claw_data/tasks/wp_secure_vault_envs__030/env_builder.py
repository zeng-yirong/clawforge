import os
import json

def build_env():
    os.makedirs("data", exist_ok=True)

    # 分类标准
    vault_schema = {
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
                "category_id": "e_commerce",
                "name": "电商平台",
                "priority": "high",
                "requires_mfa": False,
                "password_policy": {
                    "min_length": 8,
                    "require_uppercase": False,
                    "require_lowercase": True,
                    "require_digit": True,
                    "require_special": True
                }
            },
            {
                "category_id": "social_media",
                "name": "社交媒体",
                "priority": "medium",
                "requires_mfa": False,
                "password_policy": {
                    "min_length": 6,
                    "require_uppercase": False,
                    "require_lowercase": True,
                    "require_digit": True,
                    "require_special": False
                }
            },
            {
                "category_id": "uncategorized",
                "name": "未分类",
                "priority": "low",
                "requires_mfa": False,
                "password_policy": {
                    "min_length": 4
                }
            }
        ]
    }
    with open("data/vault_schema.json", "w") as f:
        json.dump(vault_schema, f, indent=2)

    # 主凭证数据
    credentials = [
        {
            "id": "cred_001",
            "platform": "example-mail.com",
            "username": "admin@example-mail.com",
            "password": "P@ssw0rd1234",
            "category": "work_email",
            "last_updated": "2024-01-01"
        },
        {
            "id": "cred_002",
            "platform": "shop.example.com",
            "username": "buyer123",
            "password": "shop123!",
            "category": "e_commerce",
            "last_updated": "2024-02-15"
        },
        {
            "id": "cred_003",
            "platform": "facebook.com",
            "username": "john_doe",
            "password": "pass123",
            "category": "social_media",
            "last_updated": "2024-03-10"
        },
        {
            "id": "cred_004",
            "platform": "random-site.org",
            "username": "testuser",
            "password": "weak",
            "category": "uncategorized",
            "last_updated": "2024-04-01"
        },
        {
            "id": "cred_005",
            "platform": "bank.example.com",
            "username": "finance",
            "password": "StrongBank#2024",
            "category": "financial",
            "last_updated": "2024-05-20"
        }
    ]
    with open("data/credentials.json", "w") as f:
        json.dump(credentials, f, indent=2)

    # 干扰项：旧备份（部分字段过时）
    old_creds = [
        {"id": "cred_001", "platform": "example-mail.com", "password": "oldpass"},
        {"id": "cred_003", "platform": "facebook.com", "password": "fb123"}
    ]
    with open("data/old_credentials.json", "w") as f:
        json.dump(old_creds, f, indent=2)

    # 诱饵文件
    with open("notes.txt", "w") as f:
        f.write("这是临时备注，别理我。")

if __name__ == "__main__":
    build_env()
