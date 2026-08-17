import os
import csv
import json
import random

def build_env():
    # 创建 vault 目录
    os.makedirs("vault", exist_ok=True)
    
    # 创建干扰文件
    with open("README.txt", "w") as f:
        f.write("Legacy vault export notes, ignore.\n")
    with open("old_backup.json", "w") as f:
        json.dump({"backup_date": "2024-01-01", "entries_count": 42}, f)
    
    # 定义凭证条目（按顺序添加，保证答案唯一）
    rows = []
    
    # 1-3: 目标类别弱密码（答案核心）
    rows.append({
        "id": 10, "platform": "corpmail", "username": "admin@company.com",
        "password": "pass123", "category": "工作邮箱", "priority": "critical", "requires_mfa": "false"
    })
    rows.append({
        "id": 20, "platform": "bofa", "username": "jdoe",
        "password": "12345678", "category": "银行账户", "priority": "high", "requires_mfa": "false"
    })
    rows.append({
        "id": 30, "platform": "outlook", "username": "user1",
        "password": "abcdefg", "category": "工作邮箱", "priority": "medium", "requires_mfa": "false"
    })
    
    # 4-6: 目标类别但强密码（干扰）
    rows.append({
        "id": 40, "platform": "gmail", "username": "boss@gmail.com",
        "password": "X3@kLp#9qRz", "category": "工作邮箱", "priority": "critical", "requires_mfa": "true"
    })
    rows.append({
        "id": 50, "platform": "chase", "username": "john.smith",
        "password": "S@fePass2024!", "category": "银行账户", "priority": "high", "requires_mfa": "true"
    })
    rows.append({
        "id": 60, "platform": "yahoo", "username": "info@corp.com",
        "password": "Strong!2#4", "category": "工作邮箱", "priority": "low", "requires_mfa": "false"
    })
    
    # 7-9: 非目标类别弱密码（干扰）
    rows.append({
        "id": 70, "platform": "wechat", "username": "zhangsan",
        "password": "123", "category": "社交媒体", "priority": "low", "requires_mfa": "false"
    })
    rows.append({
        "id": 80, "platform": "amazon", "username": "buyer1",
        "password": "password", "category": "电商平台", "priority": "medium", "requires_mfa": "false"
    })
    rows.append({
        "id": 90, "platform": "twitter", "username": "twit_user",
        "password": "111111", "category": "社交媒体", "priority": "low", "requires_mfa": "false"
    })
    
    # 10-12: 非目标类别强密码（填充）
    rows.append({
        "id": 100, "platform": "taobao", "username": "shop_owner",
        "password": "Ta0ba0#Secure!", "category": "电商平台", "priority": "high", "requires_mfa": "true"
    })
    rows.append({
        "id": 110, "platform": "facebook", "username": "fb_user",
        "password": "Meta@2024#Pass", "category": "社交媒体", "priority": "medium", "requires_mfa": "false"
    })
    rows.append({
        "id": 120, "platform": "jingdong", "username": "jd_member",
        "password": "JD_Strong9!", "category": "电商平台", "priority": "low", "requires_mfa": "false"
    })
    
    # 确保有重复 id 和格式错误行（脏数据）
    rows.append({
        "id": 10, "platform": "corpmail", "username": "duplicate_admin",
        "password": "pass123", "category": "工作邮箱", "priority": "critical", "requires_mfa": "false"
    })
    # 缺少 password 字段的行
    rows.append({
        "id": 999, "platform": "broken", "username": "no_pass",
        "category": "工作邮箱", "priority": "low", "requires_mfa": "false"
    })
    
    # 写入 CSV
    fieldnames = ["id", "platform", "username", "password", "category", "priority", "requires_mfa"]
    with open("vault/vault_entries.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # 额外干扰：其他格式的凭证文件（非CSV，不应被处理）
    with open("vault/legacy_creds.txt", "w") as f:
        f.write("platform: test\nusername: test\npassword: test\n")
    
    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
