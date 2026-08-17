import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("vault/credentials", exist_ok=True)
    os.makedirs("vault/categories", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 分类定义
    categories = {
        "banking": {
            "id": "cat_bank",
            "name": "银行账户",
            "requires_mfa": True,
            "password_policy": {"min_length": 12, "require_special": True, "require_digit": True}
        },
        "social": {
            "id": "cat_social",
            "name": "社交媒体",
            "requires_mfa": False,
            "password_policy": {"min_length": 8, "require_special": False, "require_digit": True}
        },
        "email": {
            "id": "cat_email",
            "name": "工作邮箱",
            "requires_mfa": True,
            "password_policy": {"min_length": 10, "require_special": True, "require_digit": True}
        },
        "ecommerce": {
            "id": "cat_ecom",
            "name": "电商平台",
            "requires_mfa": False,
            "password_policy": {"min_length": 8, "require_special": True, "require_digit": False}
        }
    }

    # 写入分类文件
    for key, cat in categories.items():
        with open(f"vault/categories/{key}.json", "w") as f:
            json.dump(cat, f)

    # 有效凭证（6个）
    credentials = [
        {"id": "c001", "username": "alice",   "password": "abc123",       "platform": "mybank",  "category_id": "cat_bank"},
        {"id": "c002", "username": "bob",     "password": "Str0ng!Pass",  "platform": "socialzz","category_id": "cat_social"},
        {"id": "c003", "username": "charlie", "password": "password",     "platform": "workmail","category_id": "cat_email"},
        {"id": "c004", "username": "diana",   "password": "abcdefgh!@#$", "platform": "shopnow", "category_id": "cat_ecom"},
        {"id": "c005", "username": "eve",     "password": "Complex123$",  "platform": "bank2",   "category_id": "cat_bank"},
        {"id": "c006", "username": "frank",   "password": "x!yz1234",     "platform": "mail2",   "category_id": "cat_email"}
    ]

    for i, cred in enumerate(credentials, 1):
        with open(f"vault/credentials/cred_{i:03d}.json", "w") as f:
            json.dump(cred, f)

    # 干扰文件
    # 1. 重复 ID（c001），缺少必要字段
    duplicate = {"id": "c001", "username": None, "password": "abc", "platform": "fake", "category_id": "cat_bank"}
    with open("vault/credentials/duplicate_cred_001.json", "w") as f:
        json.dump(duplicate, f)

    # 2. 格式错误（非 JSON）
    with open("vault/credentials/cred_bad.json", "w") as f:
        f.write("this is not json")

    # 3. 不完整（缺少关键字段）
    incomplete = {"id": "c007", "username": "grace"}
    with open("vault/credentials/cred_incomplete.json", "w") as f:
        json.dump(incomplete, f)

    # 4. 空文件
    open("vault/credentials/cred_empty.json", "w").close()

if __name__ == "__main__":
    build_env()
