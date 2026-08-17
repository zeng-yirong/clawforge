import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("ops", exist_ok=True)
    os.makedirs("user_profiles", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 类别定义（包含干扰类别：一个低优先级的未使用类别，一个已废弃的类别）
    categories = {
        "cat_01": {
            "name": "工作邮箱",
            "priority": "high",
            "requires_mfa": False,
            "password_policy": {"min_length": 12}
        },
        "cat_02": {
            "name": "电商平台",
            "priority": "low",
            "requires_mfa": True,
            "password_policy": {"min_length": 8}
        },
        "cat_03": {
            "name": "社交媒体",
            "priority": "medium",
            "requires_mfa": False,
            "password_policy": {"min_length": 10}
        },
        "cat_04": {
            "name": "银行账户",
            "priority": "critical",
            "requires_mfa": True,
            "password_policy": {"min_length": 16}
        },
        "cat_05": {
            "name": "测试账户",
            "priority": "low",
            "requires_mfa": False,
            "password_policy": {"min_length": 6}
        },
        "cat_06": {
            "name": "废弃类别",
            "priority": "obsolete",
            "requires_mfa": False,
            "password_policy": {}
        }
    }

    # 凭据列表（包含干扰与正常）
    credentials = [
        {
            "id": "001",
            "name": "work_email",
            "username": "alice@company.com",
            "category_id": "cat_01",
            "created_at": "2024-01-01"
        },
        {
            "id": "002",
            "name": "shop_account",
            "username": "alice_shop",
            "category_id": "cat_02",
            "created_at": "2024-02-01"
        },
        {
            "id": "003",
            "name": "social_media",
            "username": "alice_social",
            "category_id": "cat_03",
            "created_at": "2024-03-01"
        },
        {
            "id": "004",
            "name": "bank_login",
            "username": "alice_bank",
            "category_id": "cat_04",
            "created_at": "2024-04-01"
        },
        {
            "id": "005",
            "name": "legacy_test",
            "username": "test_user",
            "category_id": "cat_06",
            "created_at": "2023-12-01"
        },
        {
            "id": "006",
            "name": "backup_email",
            "username": "backup@company.com",
            "category_id": "cat_01",
            "created_at": "2024-05-01"
        },
        {
            "id": "007",
            "name": "second_shop",
            "username": "alice_shop2",
            "category_id": "cat_02",
            "created_at": "2024-06-01"
        },
        {
            "id": "008",
            "name": "dummy_credential",
            "username": "dummy",
            "category_id": "cat_99",  # 不存在的类别，应被过滤
            "created_at": "2024-07-01"
        },
        {
            "id": "009",
            "name": "test_account",
            "username": "tester",
            "category_id": "cat_05",  # 低优先级但未在 vault 中被要求？仍然要包括，因为 cat_05 是低优先级
            "created_at": "2024-08-01"
        }
    ]

    # 注意：cat_05 也是低优先级，所以凭据 009 也属于低风险，需要被包含。
    # 最终低优先级类别：cat_02 和 cat_05
    # 凭据：002 (cat_02), 007 (cat_02), 009 (cat_05)
    # 按 name 排序：dummy_credential? 不，009 是 test_account，002 是 shop_account，007 是 second_shop
    # 排序后：second_shop, shop_account, test_account
    # 但 dummy_credential (008) 的 category 不存在，应被过滤。
    # 预期结果：
    # [
    #   {"name": "second_shop", "username": "alice_shop2"},
    #   {"name": "shop_account", "username": "alice_shop"},
    #   {"name": "test_account", "username": "tester"}
    # ]

    with open("vault.json", "w", encoding="utf-8") as f:
        json.dump(credentials, f, indent=2, ensure_ascii=False)
    with open("categories.json", "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)

    # 干扰文件
    with open("user_profiles/admin_profile.json", "w") as f:
        json.dump({"name": "admin", "role": "superuser"}, f)
    with open("logs/access.log", "w") as f:
        f.write("2024-09-01 10:00:00 [INFO] login success\n2024-09-01 10:01:00 [WARN] failed attempt\n")

if __name__ == "__main__":
    build_env()
