import os
import json
import random

def build_env():
    # --- 有效凭据（最终应保留）---
    valid_credentials = [
        {"platform": "workmail", "username": "alice@company.com", "password": "K8#mNp2x!q", "expiry": "2026-12-31", "strength": 85, "category": "工作邮箱"},
        {"platform": "shopee",    "username": "shop_buyer",        "password": "vL@9Zq3wR", "expiry": "2025-08-15", "strength": 78, "category": "电商平台"},
        {"platform": "wechat",    "username": "tech_support",      "password": "P@ssw0rd!2025", "expiry": "2025-06-30", "strength": 72, "category": "社交媒体"},
        {"platform": "bank_icbc", "username": "finance_zhang",     "password": "Yh@7kL9mN", "expiry": "2027-04-01", "strength": 92, "category": "银行账户"},
        {"platform": "alipay",    "username": "payment_bot",       "password": "Qw!3eR5tY", "expiry": "2026-11-20", "strength": 81, "category": "电商平台"},
    ]

    # --- 干扰项：过期凭据 ---
    expired_credentials = [
        {"platform": "old_workmail", "username": "admin@old", "password": "abc123", "expiry": "2023-01-01", "strength": 30, "category": "工作邮箱"},
        {"platform": "legacy_shop",  "username": "test_user", "password": "password", "expiry": "2022-06-15", "strength": 15, "category": "电商平台"},
    ]

    # --- 干扰项：强度不达标（strength < 50）---
    weak_credentials = [
        {"platform": "twitter_spare", "username": "hacker_123", "password": "123456", "expiry": "2025-10-10", "strength": 20, "category": "社交媒体"},
    ]

    # --- 已知泄露密码列表 ---
    known_breaches = ["P@ssw0rd!2025", "abc123", "password", "123456", "qwerty"]

    # --- 构建文件 ---
    # 1. CSV 文件（混合有效、过期、弱密码）
    csv_lines = ["platform,username,password,expiry,strength,category"]
    for cred in valid_credentials + expired_credentials + weak_credentials:
        csv_lines.append(f"{cred['platform']},{cred['username']},{cred['password']},{cred['expiry']},{cred['strength']},{cred['category']}")
    os.makedirs("ops", exist_ok=True)
    with open("ops/legacy_credentials.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(csv_lines) + "\n")

    # 2. 散乱文本 notes（包含一些有效凭据的文字描述，但混杂其他无用信息）
    notes_content = (
        "John's test account: workmail, john@test.com, Temp!2023, exp 2023-12-31 strength 45\n"
        "Temp password for staging: admin, admin123, no expiry, strength 10\n"
        "AliPay bot credentials: payment_bot, Qw!3eR5tY, valid until 2026-11-20, score 81\n"
        "Bank ICBC: finance_zhang, Yh@7kL9mN, expiry 2027-04-01, score 92\n"
        "Note: old wechat account was deactivated.\n"
        "Shopee buyer: shop_buyer, vL@9Zq3wR, expiry 2025-08-15, strength 78\n"
        "Never use: password, 123456, qwerty.\n"
    )
    with open("ops/scattered_notes.txt", "w", encoding="utf-8") as f:
        f.write(notes_content)

    # 3. 已知泄露列表文件
    with open("data/known_breaches.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(known_breaches) + "\n")

    # 4. 类别映射（简单映射）
    category_map = {
        "workmail": "工作邮箱",
        "shopee": "电商平台",
        "wechat": "社交媒体",
        "bank_icbc": "银行账户",
        "alipay": "电商平台",
        "old_workmail": "工作邮箱",
        "legacy_shop": "电商平台",
        "twitter_spare": "社交媒体"
    }
    with open("data/category_mapping.json", "w", encoding="utf-8") as f:
        json.dump(category_map, f, indent=2)

    # 5. 密码策略（仅供上下文，不直接用于验证）
    policy = {
        "min_length": 8,
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_special": True,
        "min_strength": 50
    }
    with open("data/password_policy.json", "w", encoding="utf-8") as f:
        json.dump(policy, f, indent=2)

    # 6. 干扰文件
    with open("ops/backup.zip", "w") as f:
        f.write("fake zip content")
    with open("config.yaml", "w") as f:
        f.write("version: 1.0\ndebug: false")
    with open("README.md", "w") as f:
        f.write("# Legacy Password Repository\nThis is a placeholder.")

    print("env_builder: workspace initialized with legacy credentials, notes, and supporting files.")

if __name__ == "__main__":
    # 确保在 . 下运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 移到 tasks 目录？但规范说 cwd 已经是 assets 下
    build_env()
