import csv
import os
import json
import datetime

# 创建 vault_export.csv（主文件）
os.makedirs("ops", exist_ok=True)

rows = [
    {"id": "CR-001", "name": "邮箱-work",    "password": "Abc123!@#$%",        "email": "alice@company.com",   "last_updated": "2025-03-10"},
    {"id": "CR-002", "name": "邮箱-personal","password": "qwerty12345",       "email": "alice@gmail.com",     "last_updated": "2025-02-20"},
    {"id": "CR-003", "name": "电商-amazon",  "password": "Pa$$word2024",      "email": "biz@amazon.com",      "last_updated": "2025-01-15"},
    {"id": "CR-004", "name": "电商-ebay",    "password": "ebaySeller42!",     "email": "seller@ebay.com",     "last_updated": "2024-12-01"},
    {"id": "CR-005", "name": "社交媒体-tw",  "password": "Short1!",           "email": "twit@twitter.com",    "last_updated": "2025-03-05"},
    {"id": "CR-006", "name": "社交媒体-fb",  "password": "VeryLongPass1234!@#","email": "fb@meta.com",         "last_updated": "2025-03-08"},
    {"id": "CR-007", "name": "银行-工行",    "password": "ICBC_secure!2025",  "email": "bank@icbc.com",       "last_updated": "2025-03-12"},
    {"id": "CR-008", "name": "银行-招行",    "password": "nopass",            "email": "cmb@chinabank.com",   "last_updated": "2024-11-20"},
    {"id": "CR-009", "name": "工作域-LDAP",  "password": "Ldap@1234567890",   "email": "admin@domain.com",    "last_updated": "2025-03-01"},
    {"id": "CR-010", "name": "测试账号",     "password": "test123",           "email": "test@dev.com",        "last_updated": "2025-03-14"},
]

with open("vault_export.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id","name","password","email","last_updated"])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

# 创建干扰文件：老旧备份（包含一些已失效凭据）
old_rows = [
    {"id": "CR-011", "name": "旧邮箱", "password": "old123", "email": "old@old.com", "last_updated": "2023-06-01"},
    {"id": "CR-012", "name": "测试备份", "password": "Backup2022!", "email": "backup@test.com", "last_updated": "2023-12-31"},
]
with open("vault_backup_old.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id","name","password","email","last_updated"])
    writer.writeheader()
    for row in old_rows:
        writer.writerow(row)

# 创建 ops 目录下的一个已有文件（干扰）
with open("ops/.gitkeep", "w") as f:
    f.write("placeholder")
