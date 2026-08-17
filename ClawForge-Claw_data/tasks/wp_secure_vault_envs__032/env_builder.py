import json
import os
import random

def build_env():
    # 确保工作区干净，但实际cwd已切换，只创建相对路径
    os.makedirs("vault/credentials", exist_ok=True)
    os.makedirs("vault/quarantined", exist_ok=True)  # 空目录，等待agent移动
    os.makedirs("vault/log", exist_ok=True)          # 干扰目录
    os.makedirs("backup", exist_ok=True)             # 干扰目录

    # 定义schema
    schema = {
        "categories": [
            {"id": "bank",       "name": "银行账户", "priority": "critical", "requires_mfa": True, "min_strength": 80},
            {"id": "social",     "name": "社交媒体", "priority": "medium",   "requires_mfa": False, "min_strength": 60},
            {"id": "email",      "name": "工作邮箱", "priority": "high",     "requires_mfa": True, "min_strength": 70},
            {"id": "ecommerce",  "name": "电商平台", "priority": "low",      "requires_mfa": False, "min_strength": 50}
        ]
    }
    with open("vault/schema.json", "w") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    # 生成凭证文件，确保唯一答案：只有3个银行账户凭证强度不足
    # 正常银行账户：cred_001强度85（合格），cred_002强度45（不合格），cred_003强度90（合格）
    # 干扰：社交媒体 cred_004强度30（不合格但类别不对），工作邮箱 cred_005强度65（合格），电商平台 cred_006强度20（不合格但类别不对）
    # 另加一个重复凭证 cred_007（银行账户，强度75不合格，且与cred_002的credential_id不同，防止唯一性冲突）
    # 再加一个凭证cred_008（银行账户，强度79不合格，但requires_mfa字段缺失，作为边界情况，但策略只根据强度，不影响）
    credentials = [
        {"credential_id": "C001", "category_id": "bank",    "strength_score": 85, "service": "Chase",       "username": "jdoe",       "requires_mfa": True},
        {"credential_id": "C002", "category_id": "bank",    "strength_score": 45, "service": "Wells Fargo",  "username": "asmith",     "requires_mfa": True},
        {"credential_id": "C003", "category_id": "bank",    "strength_score": 90, "service": "Bank of America", "username": "mjones",  "requires_mfa": True},
        {"credential_id": "C004", "category_id": "social",  "strength_score": 30, "service": "Twitter",      "username": "tweeter1",   "requires_mfa": False},
        {"credential_id": "C005", "category_id": "email",   "strength_score": 65, "service": "Outlook",      "username": "work1",      "requires_mfa": True},
        {"credential_id": "C006", "category_id": "ecommerce","strength_score": 20, "service": "Amazon",       "username": "shopaholic", "requires_mfa": False},
        {"credential_id": "C007", "category_id": "bank",    "strength_score": 75, "service": "Ally Bank",    "username": "savings1",   "requires_mfa": True},
        {"credential_id": "C008", "category_id": "bank",    "strength_score": 79, "service": "Capital One",  "username": "ccuser",     "requires_mfa": False},  # 强度不足，且不满足requires_mfa
    ]

    # 添加一些干扰文件：旧的备份、日志、无关txt
    for i in range(3):
        dummy = {"fake": True, "id": f"dummy{i}"}
        with open(f"vault/credentials/old_cred_{i}.json", "w") as f:
            json.dump(dummy, f)

    with open("vault/log/audit_2023.log", "w") as f:
        f.write("2023-01-01 00:00:00 INFO: All good\n")

    with open("backup/cred_backup.json", "w") as f:
        json.dump({"backup": True}, f)

    # 写正式凭证文件
    for cred in credentials:
        filename = f"vault/credentials/cred_{cred['credential_id'].lower()}.json"  # 如cred_c001.json
        with open(filename, "w") as f:
            json.dump(cred, f, indent=2)

    # 确保唯一答案：C002, C007, C008 应该被移走 (45<80, 75<80, 79<80)
    # 其他银行账户（C001:85, C003:90）留下
    # 非银行账户（C004,C005,C006）留下

if __name__ == "__main__":
    build_env()
