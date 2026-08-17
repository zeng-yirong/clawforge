import os
import json
import random

def build_env():
    # 基础目录
    os.makedirs("vault", exist_ok=True)
    # 密码策略
    policy = {
        "min_length": 10,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digit": True,
        "require_special": True
    }
    with open("vault/password_policy.json", "w") as f:
        json.dump(policy, f)

    # 分类
    categories = [
        {"category_id": "cat_email", "name": "工作邮箱", "requires_mfa": True, "priority": "high"},
        {"category_id": "cat_ecom", "name": "电商平台", "requires_mfa": False, "priority": "medium"},
        {"category_id": "cat_social", "name": "社交媒体", "requires_mfa": True, "priority": "low"},
        {"category_id": "cat_bank", "name": "银行账户", "requires_mfa": True, "priority": "critical"},
        {"category_id": "cat_int", "name": "内部系统", "requires_mfa": False, "priority": "high"}
    ]
    with open("vault/categories.json", "w") as f:
        json.dump(categories, f)

    # 凭据数据（包含干扰项：inactive状态，以及一个虚拟的mfa字段等）
    credentials = [
        {"id": "cred_001", "username": "alice", "password": "Pass123!", "platform": "mail.company.com", "category": "cat_email", "status": "active"},
        {"id": "cred_002", "username": "bob", "password": "weak", "platform": "shop.example.com", "category": "cat_ecom", "status": "active"},
        {"id": "cred_003", "username": "carol", "password": "Str0ng!Pass", "platform": "fb.login", "category": "cat_social", "status": "active"},
        {"id": "cred_004", "username": "dave", "password": "12345678", "platform": "bank.secure.com", "category": "cat_bank", "status": "active"},
        {"id": "cred_005", "username": "eve", "password": "Abcdef123!", "platform": "internal.tool", "category": "cat_int", "status": "active"},
        {"id": "cred_006", "username": "frank", "password": "NoDigits!", "platform": "email2.company.com", "category": "cat_email", "status": "inactive"},  # 干扰：inactive
        {"id": "cred_007", "username": "grace", "password": "Short1a", "platform": "shop2.example.com", "category": "cat_ecom", "status": "active"},
        {"id": "cred_008", "username": "heidi", "password": "vvvweak", "platform": "legacy.tool", "category": "cat_int", "status": "archived"}  # 干扰：archived
    ]
    # 打乱顺序，但输出时需按原始顺序（保持不变）
    random.shuffle(credentials)  # 增加挑战，但agent需保持原顺序
    with open("vault/credentials.json", "w") as f:
        json.dump(credentials, f)

    # 安全密码池（至少覆盖所有需要替换的凭据）
    # 根据策略，需要替换的凭据有：cred_002 (weak), cred_004 (12345678), cred_007 (Short1a)
    # cred_005 (Abcdef123!) 检查：长度10，有大小写、数字、特殊字符？特殊字符没有，所以不合格
    # cred_003 (Str0ng!Pass) 检查：长度12，有大小写，有! 有数字？没有数字，所以不合格
    # 实际上需要详细判断才能确定，但为了确定，我们让builder预先算出哪些不合格，并生成对应数量的密码
    # 手动计算：policy需要>=10长度，大小写数字特殊。
    # cred_001: Pass123! -> 长度8 <10 不合格
    # cred_002: weak -> 长度4 <10 不合格
    # cred_003: Str0ng!Pass -> 长度12，有大小写，有!特殊，但无数字 不合格
    # cred_004: 12345678 -> 长度8 <10 不合格
    # cred_005: Abcdef123! -> 长度11，有大小写，有数字，有!特殊，符合？但政策要求require_special，有! ok，长度>=10，有大小写数字，合格
    # cred_006: inactive 忽略
    # cred_007: Short1a -> 长度7 <10 不合格
    # cred_008: archived 忽略
    # 所以需要替换的active有：cred_001, cred_002, cred_003, cred_004, cred_007 (5个)
    # 注意cred_005是合格的，所以无需替换。密码池需要5个密码
    pool = [
        "A8#fG9!kLm",   # 给cred_001
        "z7@Wx2pQrT",   # 给cred_002
        "Kd5%Yh3JcV",   # 给cred_003
        "Bv9$Nq1WxE",   # 给cred_004
        "Rm2&Lp6ZsA"    # 给cred_007
    ]
    with open("vault/secure_passwords_pool.json", "w") as f:
        json.dump(pool, f)

if __name__ == "__main__":
    build_env()
