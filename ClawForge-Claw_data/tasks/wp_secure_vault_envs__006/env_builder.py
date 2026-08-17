import os
import json
import csv

def build_env():
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # vault schema
    vault_schema = {
        "credential_categories": {
            "工作邮箱": {"priority": "high", "requires_mfa": True},
            "电商平台": {"priority": "critical", "requires_mfa": False},
            "社交媒体": {"priority": "medium", "requires_mfa": False},
            "银行账户": {"priority": "critical", "requires_mfa": True}
        }
    }
    with open("data/vault_schema.json", "w", encoding="utf-8") as f:
        json.dump(vault_schema, f, ensure_ascii=False, indent=2)

    # password policy
    policy = {
        "min_length": 12,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digit": True,
        "require_special": True,
        "suggested_passwords": [
            "P@ssw0rd!2024",
            "Xy9#kL2m!Ab",
            "F@ct0ry#1"
        ]
    }
    with open("ops/password_policy.json", "w", encoding="utf-8") as f:
        json.dump(policy, f, ensure_ascii=False, indent=2)

    # credential dump CSV (with deliberate dirty data)
    rows = [
        {"id": "1", "username": "alice",   "password": "abc123",        "category": "工作邮箱", "platform": "example.com", "status": "active",  "strength": "20"},
        {"id": "2", "username": "bob",     "password": "Tr0ub4dor&3",   "category": "电商平台",  "platform": "shop.com",    "status": "active",  "strength": "95"},
        {"id": "3", "username": "carol",   "password": "Passw0rd!",     "category": "银行账户",  "platform": "bank.com",    "status": "active",  "strength": "70"},
        {"id": "4", "username": "dave",    "password": "Str0ng!Pass",   "category": "社交媒体",  "platform": "social.io",   "status": "retired", "strength": "90"},
        {"id": "5", "username": "eve",     "password": "password123",   "category": "电商平台",  "platform": "",            "status": "active",  "strength": "10"},
        {"id": "6", "username": "frank",   "password": "Qw3rty!@#",     "category": "电商平台",  "platform": "store.com",   "status": "active",  "strength": "80"},
    ]
    with open("data/credential_dump.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id","username","password","category","platform","status","strength"])
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    build_env()
