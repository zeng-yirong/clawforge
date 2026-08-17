import os
import json

def build_env():
    # 创建目录
    os.makedirs("creds", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 留空，等待agent写入

    # 1. 创建凭据文件 (creds/)
    creds = {
        "google.json": {
            "id": "cred_001",
            "platform": "google",
            "username": "user1",
            "password": "password123",
            "category": "社交媒体",
            "autofill": {"url": "https://mail.google.com", "enabled": True}
        },
        "twitter.json": {
            "id": "cred_002",
            "platform": "twitter",
            "username": "user2",
            "password": "SecurePass1!",
            "category": "社交媒体",
            "autofill": None
        },
        "bank.json": {
            "id": "cred_003",
            "platform": "bank",
            "username": "user3",
            "password": "12345678",
            "category": None,
            "autofill": {"url": "https://bank.example.com", "enabled": False}
        },
        "shop.json": {
            "id": "cred_004",
            "platform": "shop",
            "username": "user4",
            "password": "ComplexP@ssw0rd!",
            "category": "电商平台",
            "autofill": {"url": "https://shop.example.com", "enabled": True}
        },
        "old_backup.json": {
            "id": "cred_005",
            "platform": "old",
            "username": "old",
            "password": "weakpw",
            "category": "旧备份",
            "autofill": None
        }
    }
    for fname, content in creds.items():
        with open(f"creds/{fname}", "w") as f:
            json.dump(content, f, indent=2)

    # 2. 创建配置文件 (config/)
    # 密码策略
    policy = {
        "min_length": 8,
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_special": True
    }
    with open("config/password_policy.json", "w") as f:
        json.dump(policy, f, indent=2)

    # 弱密码列表
    weak_passwords = ["password123", "12345678", "weakpw", "qwerty"]
    with open("config/weak_passwords.json", "w") as f:
        json.dump(weak_passwords, f, indent=2)

    # 弱密码替换映射
    remediation = {
        "password123": "Strong@123",
        "12345678": "Strong@456",
        "weakpw": "Strong@789"
    }
    with open("config/remediation_rules.json", "w") as f:
        json.dump(remediation, f, indent=2)

    # 平台到分类的映射
    category_map = {
        "google": "社交媒体",
        "twitter": "社交媒体",
        "bank": "银行账户",
        "shop": "电商平台",
        "old": "旧备份"
    }
    with open("config/category_mapping.json", "w") as f:
        json.dump(category_map, f, indent=2)

if __name__ == "__main__":
    build_env()
