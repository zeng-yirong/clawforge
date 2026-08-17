import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # 创建工作区子目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 创建 vault_schema.json (分类规则)
    schema = {
        "credential_categories": [
            {"category_id": "work_email", "name": "工作邮箱", "priority": "critical", "requires_mfa": True},
            {"category_id": "ecommerce", "name": "电商平台", "priority": "high", "requires_mfa": False},
            {"category_id": "social", "name": "社交媒体", "priority": "medium", "requires_mfa": False},
            {"category_id": "bank", "name": "银行账户", "priority": "critical", "requires_mfa": True},
        ]
    }
    with open("data/vault_schema.json", "w") as f:
        json.dump(schema, f, indent=2)

    # 2. 创建 credentials.csv (包含干扰项、重复、缺失分类、弱密码)
    # 定义一批凭证，部分重复（同名不同时间戳），部分分类缺失，部分密码弱
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    records = []

    # 凭证列表 (name, category, password, timestamp_offset_minutes)
    # 故意加入重复项：最后一个出现的保留
    items = [
        ("alice@work.com", "work_email", "P@ssw0rd123!", 10),
        ("alice@work.com", "work_email", "P@ssw0rd123!", 15),   # 重复，更新同密码
        ("bob_shop", "ecommerce", "weakpass1", 20),             # 弱密码（长度8）
        ("bob_shop", "ecommerce", "BetterP@ss99!", 25),         # 重复，更新为强密码
        ("carol_social", "", "Social#2024", 30),                # 缺失分类
        ("dave_bank", "bank", "Bank_Secret_99", 35),            # 强密码
        ("eve_mall", "", "12345", 40),                          # 弱密码 + 缺失分类
        ("frank_work", "work_email", "Frank@123", 45),
        ("grace_shop", "ecommerce", "Grace_Shop_2024!", 50),
        ("grace_shop", "ecommerce", "Grace_Shop_2024!", 55),    # 重复，完全一致，保留最后一个
        ("henry_social", "social", "HenRy#789", 60),            # 强
        ("alice@work.com", "work_email", "WeakAl1!", 65),      # 新重复，密码弱，应该保留这个弱密码版本？按规则保留最后一条
        ("ivan_bank", "bank", "Ivan_Strong#1", 70),
        ("jane_mall", "", "JanePass7", 75),                    # 弱密码（长度9）
        ("kate_social", "social", "Kate@Social2024", 80),
    ]

    for name, cat, pwd, offset in items:
        ts = base_time + timedelta(minutes=offset)
        records.append({
            "name": name,
            "category": cat if cat else "",          # 空字符串表示缺失
            "password": pwd,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
        })

    # 写入 CSV
    csv_path = "credentials.csv"
    fieldnames = ["name", "category", "password", "timestamp"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # 3. 额外干扰文件 (无关文件)
    with open("data/backup_old_vault.json", "w") as f:
        json.dump({"note": "这文件没用"}, f)
    with open("ops/note.txt", "w") as f:
        f.write("临时笔记，不用管")

    # 4. 创建预期结果 (用于验证脚本内部参考，但不会暴露给 agent)
    # 注意：验证脚本不需要读取此文件，而是独立计算
    # 这里仅为设计时参考，不写入工作区
    print("环境构建完成")

if __name__ == "__main__":
    build_env()
