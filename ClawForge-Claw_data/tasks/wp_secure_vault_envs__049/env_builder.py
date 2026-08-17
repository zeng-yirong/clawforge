import json
import os
import random
import string

def build_env():
    # 标准分类 schema
    vault_schema = {
        "credential_categories": [
            {
                "category_id": "cat_work",
                "name": "工作邮箱",
                "name_en": "work_email",
                "priority": "critical",
                "requires_mfa": True,
                "password_policy": {"min_length": 12, "require_upper": True, "require_digit": True}
            },
            {
                "category_id": "cat_ecom",
                "name": "电商平台",
                "name_en": "ecommerce",
                "priority": "high",
                "requires_mfa": False,
                "password_policy": {"min_length": 8, "require_upper": False, "require_digit": True}
            },
            {
                "category_id": "cat_social",
                "name": "社交媒体",
                "name_en": "social_media",
                "priority": "medium",
                "requires_mfa": False,
                "password_policy": {"min_length": 6, "require_upper": False, "require_digit": False}
            },
            {
                "category_id": "cat_bank",
                "name": "银行账户",
                "name_en": "banking",
                "priority": "critical",
                "requires_mfa": True,
                "password_policy": {"min_length": 14, "require_upper": True, "require_digit": True, "require_special": True}
            }
        ]
    }

    # 旧的凭证库（包含有效和无效记录）
    records = [
        # 有效记录
        {"id": "cred_001", "username": "alice@corp.com", "platform": "mail.corp.com", "category_name": "工作邮箱", "password": "Alice2024!Strong"},
        {"id": "cred_002", "username": "bob_store", "platform": "amazon.com", "category_name": "电商平台", "password": "Bob123"},
        {"id": "cred_003", "username": "charlie_social", "platform": "twitter.com", "category_name": "社交媒体", "password": "charlie!"},
        # 无效记录：缺少 username
        {"id": "cred_004", "platform": "bank.com", "category_name": "银行账户", "password": "p@ssW0rdLong1"},
        # 有效记录
        {"id": "cred_005", "username": "dave_bank", "platform": "chase.com", "category_name": "银行账户", "password": "DaveBank!2024StrongSecure"},
        # 无效记录：category_name 不匹配（大小写错误）
        {"id": "cred_006", "username": "eve_work", "platform": "mail2.corp.com", "category_name": "工作邮箱 ", "password": "Eve2024!"},  # 尾部空格
        # 无效记录：缺少 password
        {"id": "cred_007", "username": "frank", "platform": "fb.com", "category_name": "社交媒体"},
        # 有效记录（但密码强度需要计算）
        {"id": "cred_008", "username": "grace_social", "platform": "instagram.com", "category_name": "社交媒体", "password": "Grace2024!"},
        # 重复记录（id不同，但内容相同，视为不同凭证）
        {"id": "cred_009", "username": "alice@corp.com", "platform": "mail.corp.com", "category_name": "工作邮箱", "password": "Alice2024!Strong"},
    ]

    # 创建 data 目录
    os.makedirs("data", exist_ok=True)
    with open("data/vault_schema.json", "w", encoding="utf-8") as f:
        json.dump(vault_schema, f, indent=2)
    with open("data/credential_store.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    # 添加一些干扰文件
    os.makedirs("logs", exist_ok=True)
    with open("logs/audit.log", "w") as f:
        f.write("2025-04-01 00:00:00 INFO credentials synced\n2025-04-01 00:01:00 WARN invalid entry skipped\n")
    os.makedirs("ops", exist_ok=True)
    with open("ops/backup_old_vault.json", "w") as f:
        json.dump({"archived": True}, f)

if __name__ == "__main__":
    build_env()
