import os
import json
import random
import string

def build_env():
    # 确保当前目录是 .
    # 这里不要加前缀，直接使用相对路径

    # 1. 创建 vault_schema.json
    schema = {
        "credential_categories": [
            {
                "category_id": "work_email",
                "name": "工作邮箱",
                "priority": "medium",
                "requires_mfa": False,
                "password_policy": {"min_length": 8, "require_special": False}
            },
            {
                "category_id": "ecommerce",
                "name": "电商平台",
                "priority": "medium",
                "requires_mfa": False,
                "password_policy": {"min_length": 10, "require_special": True}
            },
            {
                "category_id": "social_media",
                "name": "社交媒体",
                "priority": "low",
                "requires_mfa": False,
                "password_policy": {"min_length": 8, "require_special": False}
            },
            {
                "category_id": "bank",
                "name": "银行账户",
                "priority": "critical",
                "requires_mfa": True,
                "password_policy": {"min_length": 12, "require_special": True, "require_uppercase": True}
            }
        ]
    }
    with open("vault_schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    # 2. 创建 mapping.json（关键词到分类名称的映射）
    mapping = {
        "work": "工作邮箱",
        "email": "工作邮箱",
        "mail": "工作邮箱",
        "shop": "电商平台",
        "buy": "电商平台",
        "store": "电商平台",
        "social": "社交媒体",
        "friend": "社交媒体",
        "bank": "银行账户",
        "finance": "银行账户",
        "card": "银行账户"
    }
    with open("mapping.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    # 3. 创建 vault_export.json（原始凭据，含干扰项）
    credentials = [
        {"id": "1", "platform": "my-work-email", "username": "alice@company.com", "password": "P@ss1234", "category": None},
        {"id": "2", "platform": "amazon-shop", "username": "bob_smith", "password": "Qwerty!23", "category": "电商平台"},
        {"id": "3", "platform": "facebook-social", "username": "charlie_dev", "password": "Fan#2023", "category": "社交媒体"},
        {"id": "4", "platform": "bank-of-america", "username": "dave_money", "password": "B@nk!Pass99", "category": "银行账户"},
        {"id": "5", "platform": "personal-email", "username": "eve_dream", "password": "Eve2024!!", "category": None},
        {"id": "6", "platform": "social-twitter", "username": "frank_public", "password": "Tweet!123", "category": "工作邮箱"},  # 错误分类
        {"id": "7", "platform": "aliexpress-shop", "username": "grace_buy", "password": "Grace#Shop", "category": "银行账户"},   # 错误分类
        {"id": "8", "platform": "bank-of-china", "username": "heidi_safe", "password": "ChinaBank!1", "category": None},
    ]
    with open("vault_export.json", "w", encoding="utf-8") as f:
        json.dump(credentials, f, indent=2, ensure_ascii=False)

    # 4. 创造一些干扰文件（不影响验证）
    # 旧备份
    with open("old_vault_backup.json", "w") as f:
        json.dump([{"dummy": True}], f)
    # 无用的笔记
    with open("notes.txt", "w") as f:
        f.write("These are old notes, ignore.\n")
    # 过时的映射
    with open("deprecated_mapping.csv", "w") as f:
        f.write("keyword,category\nweb,工作邮箱\nbank,银行账户\n")
    # 随机数据文件
    random_data = [random.randint(0,100) for _ in range(10)]
    with open("random_vals.json", "w") as f:
        json.dump(random_data, f)

if __name__ == "__main__":
    build_env()
