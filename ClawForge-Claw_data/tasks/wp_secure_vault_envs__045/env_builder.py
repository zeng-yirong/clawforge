import os
import json

def build_env():
    # 创建 vault_backup 目录
    os.makedirs("vault_backup", exist_ok=True)

    # 构建凭据数据
    credentials = [
        {"id": "id1", "password": "Abc12345", "category": "工作邮箱"},
        {"id": "id2", "password": "P@ssw0rd", "category": "电商平台"},
        {"id": "id3", "password": "Strong#Pass1", "category": "社交媒体"},
        {"id": "id4", "password": "12345678", "category": "银行账户"},
        {"id": "id5", "password": "Abcdefgh1@", "category": "工作邮箱"},
        {"id": "id6", "password": "Valid@Pass123", "category": "电商平台"},
    ]

    # 写主凭据文件
    with open("vault_backup/credentials.json", "w", encoding="utf-8") as f:
        json.dump({"credentials": credentials}, f, indent=2, ensure_ascii=False)

    # 干扰文件：旧的备份（字段名不同、数据格式不同）
    old_credentials = [
        {"id": "old1", "passwd": "weak", "category": "工作邮箱"},
    ]
    with open("vault_backup/old_credentials.json", "w", encoding="utf-8") as f:
        json.dump(old_credentials, f, indent=2)

    # 干扰文件：文本说明
    with open("vault_backup/notes.txt", "w", encoding="utf-8") as f:
        f.write("This is a temporary backup snapshot. Please use credentials.json for analysis.\n")

if __name__ == "__main__":
    build_env()
