import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)

    # === 主数据：vault_entries.json ===
    vault_entries = [
        {"credential_id": "C001", "platform": "公司邮箱", "username": "alice", "password": "abc123"},
        {"credential_id": "C002", "platform": "AWS控制台", "username": "bob", "password": "SecurePass12!"},
        {"credential_id": "C003", "platform": "GitHub", "username": "charlie", "password": "pass"},
        {"credential_id": "C004", "platform": "内部Wiki", "username": "dave", "password": "LongEnough11"},
        {"credential_id": "C005", "platform": "Jira", "username": "eve", "password": "hello123"},
        {"credential_id": "C006", "platform": "Confluence", "username": "frank", "password": "Test1234!"},
        {"credential_id": "C007", "platform": "Slack", "username": "grace", "password": "shorty7"},
        {"credential_id": "C008", "platform": "飞书", "username": "heidi", "password": "TooShort1"},
        {"credential_id": "C009", "platform": "ZOOM", "username": "ivan", "password": "MyLongPassword99"},
        {"credential_id": "C010", "platform": "云存储", "username": "judy", "password": "weakpw"}
    ]
    with open("data/vault_entries.json", "w") as f:
        json.dump(vault_entries, f, indent=2)

    # === 强密码备选池（固定顺序） ===
    strong_passwords = [
        "NewStrongPass1!",
        "AnotherStrong2@",
        "YetAnother3#",
        "FinalStrong4$",
        "ExtraStrong5%"
    ]
    with open("data/strong_passwords.txt", "w") as f:
        f.write("\n".join(strong_passwords))

    # === 干扰项：旧版备份（过期数据） ===
    old_backup = [
        {"credential_id": "C001", "platform": "公司邮箱", "username": "alice_old", "password": "password123"},
        {"credential_id": "C999", "platform": "废弃系统", "username": "zombie", "password": "dead"}
    ]
    os.makedirs("data/backup", exist_ok=True)
    with open("data/backup/old_vault.json", "w") as f:
        json.dump(old_backup, f, indent=2)

    # === 干扰项：无关日志 ===
    with open("raw_logs/access.log", "w") as f:
        f.write("2025-03-21 08:00:00 login success alice\n")
        f.write("2025-03-21 08:05:00 password change bob\n")

    # === 干扰项：已过期的报告（结构不同） ===
    outdated = {"status": "done", "date": "2025-01-01"}
    with open("ops/outdated_report.json", "w") as f:
        json.dump(outdated, f, indent=2)

if __name__ == "__main__":
    build_env()
