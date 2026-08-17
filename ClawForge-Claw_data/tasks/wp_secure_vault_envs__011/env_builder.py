import csv
import json
import os
import shutil
from datetime import datetime, timedelta

def build_env():
    # 清理旧结构
    if os.path.exists("vault"):
        shutil.rmtree("vault")
    if os.path.exists("policy.json"):
        os.remove("policy.json")
    if os.path.exists("category_rules.json"):
        os.remove("category_rules.json")

    # 创建 vault 目录
    os.makedirs("vault", exist_ok=True)

    # 策略文件
    policy = {
        "password_min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digit": True,
        "require_special": True,
        "default_password": "N3w!SecureP@ss",
        "expire_threshold_days": 90,
        "reference_date": "2025-06-01"
    }
    with open("policy.json", "w") as f:
        json.dump(policy, f, indent=2)

    # 分类规则
    category_rules = {
        "bank": {"domains": ["bank", "credit", "fin"]},
        "ecommerce": {"domains": ["shop", "store", "market"]},
        "social": {"domains": ["social", "chat", "media"]},
        "work": {"domains": ["corp", "company", "internal"]},
        "other": {"domains": []}
    }
    with open("category_rules.json", "w") as f:
        json.dump(category_rules, f, indent=2)

    # 基准日期
    ref_date = datetime.strptime(policy["reference_date"], "%Y-%m-%d")
    expire_limit = ref_date - timedelta(days=policy["expire_threshold_days"])

    # 定义有效凭证 (应保留)
    valid_creds = [
        ("internal.corp.com", "alice", "Alice@2024!", "2025-05-01"),
        ("shop.example.com", "bob", "Bob#12345", "2025-04-15"),
        ("social.example.com", "charlie", "Charlie!2025", "2025-05-20"),
        ("bank.example.com", "dave", "Dave@Secure1", "2025-05-10"),
        ("market.example.com", "eve", "Eve!StrongPwd", "2025-03-01"),
    ]

    # 定义重复凭证 (应去重，保留最新)
    dup_creds = [
        ("internal.corp.com", "alice", "OldPass1!", "2024-12-01"),   # 旧
        ("shop.example.com", "bob", "BobWeak1", "2024-11-15"),     # 旧
        ("bank.example.com", "dave", "DaveOld!", "2024-10-20"),    # 旧
    ]

    # 定义过期凭证 (应删除)
    expired_creds = [
        ("oldbank.example.com", "frank", "Frank2022!", "2024-06-01"),
        ("chatsocial.example.com", "grace", "Grace!Old", "2024-05-15"),
    ]

    # 定义弱密码凭证 (应替换)
    weak_creds = [
        ("weakshop.example.com", "hank", "short", "2025-04-01"),          # 太短
        ("weakbank.example.com", "iris", "alllowercase", "2025-04-10"),   # 无大写数字特殊
        ("weakcorp.example.com", "jack", "NODIGIT!", "2025-05-01"),       # 无数字
    ]

    # 写入主要凭证文件
    main_file = "vault/credentials_main.csv"
    with open(main_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "username", "password", "created"])
        for row in valid_creds + weak_creds:
            writer.writerow(row)

    # 写入第二个文件 (包含重复和过期)
    extra_file = "vault/legacy_export.csv"
    with open(extra_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "username", "password", "created"])
        for row in dup_creds + expired_creds:
            writer.writerow(row)

    # 诱饵文件 - 备份
    backup_file = "vault/backup_2024.csv"
    with open(backup_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "username", "password", "created"])
        writer.writerow(["fake.com", "ghost", "ghostpwd", "2023-01-01"])

    # 诱饵文件 - 格式错误的行
    bad_file = "vault/note.txt"
    with open(bad_file, "w") as f:
        f.write("This is not a credential file\n")

    # 诱饵文件 - 重复表头数据
    dup_header_file = "vault/duplicate_header.csv"
    with open(dup_header_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "username", "password", "created"])
        writer.writerow(["domain", "username", "password", "created"])
        writer.writerow(["test.com", "user", "pass", "2025-01-01"])

    # 旧版格式 (无表头) - 忽略
    old_format = "vault/old_format.csv"
    with open(old_format, "w") as f:
        f.write("domain,user,pass,created\n")
        f.write("old.com,o,secret,2020-01-01\n")

    # 生成预期答案供验证参考 (但不暴露给agent)
    # 预期处理结果在 verify 中计算

if __name__ == "__main__":
    build_env()
