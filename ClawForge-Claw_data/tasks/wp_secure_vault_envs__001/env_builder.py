import os
import json

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)
    
    # 1. vault_schema.json
    schema = {
        "collection": "credential_categories",
        "wrapper": "credential_categories",
        "key": "category_id",
        "categories": [
            {
                "category_id": "email",
                "name": "工作邮箱",
                "priority": "critical",
                "requires_mfa": True,
                "password_policy": {"min_length": 12, "special_chars": 1, "uppercase": 1}
            },
            {
                "category_id": "ecommerce",
                "name": "电商平台",
                "priority": "high",
                "requires_mfa": False,
                "password_policy": {"min_length": 10, "special_chars": 0, "uppercase": 1}
            },
            {
                "category_id": "social",
                "name": "社交媒体",
                "priority": "medium",
                "requires_mfa": False,
                "password_policy": {"min_length": 8, "special_chars": 0, "uppercase": 0}
            },
            {
                "category_id": "bank",
                "name": "银行账户",
                "priority": "critical",
                "requires_mfa": True,
                "password_policy": {"min_length": 14, "special_chars": 2, "uppercase": 2}
            }
        ]
    }
    with open("data/vault_schema.json", "w") as f:
        json.dump(schema, f, indent=2)
    
    # 2. credentials.json (主数据)
    credentials = [
        # 正常记录1 (合规)
        {"id": "cred-001", "service": "mail.company.io", "username": "alice", "password": "A!b2c3d4e5f6g", "category_id": "email", "password_strength": "strong", "expired": False},
        # 正常记录2
        {"id": "cred-002", "service": "shop.example.com", "username": "bob", "password": "B!x9y8z7", "category_id": "ecommerce", "password_strength": "strong", "expired": False},
        # 无效分类 (category_id 'finance' 不存在)
        {"id": "cred-003", "service": "invest.bank.com", "username": "charlie", "password": "C@d3f4g5h6", "category_id": "finance", "password_strength": "medium", "expired": False},
        # 弱密码 (medium)
        {"id": "cred-004", "service": "social.feed.net", "username": "dave", "password": "pass1234", "category_id": "social", "password_strength": "weak", "expired": False},
        # 过期记录
        {"id": "cred-005", "service": "old.bank.com", "username": "eve", "password": "E!x9y8z7w6v5u", "category_id": "bank", "password_strength": "strong", "expired": True},
        # 重复记录1 (与cred-006重复)
        {"id": "cred-006", "service": "duplicate.app.com", "username": "frank", "password": "F!a1b2c3d4", "category_id": "social", "password_strength": "strong", "expired": False},
        # 重复记录2 (相同 service+username，密码不同)
        {"id": "cred-007", "service": "duplicate.app.com", "username": "frank", "password": "F!z9y8x7w6", "category_id": "social", "password_strength": "strong", "expired": False},
        # 正常记录3
        {"id": "cred-008", "service": "mail.personal.com", "username": "grace", "password": "G!h2i3j4k5l6m", "category_id": "email", "password_strength": "strong", "expired": False},
        # 弱密码+无效分类双重问题
        {"id": "cred-009", "service": "unknown.service.io", "username": "heidi", "password": "abc123", "category_id": "mobile", "password_strength": "weak", "expired": False},
        # 过期+弱密码
        {"id": "cred-010", "service": "retired.vault.com", "username": "ivan", "password": "I!v4n5pwd", "category_id": "ecommerce", "password_strength": "weak", "expired": True},
        # 完全合规 (另一个平台)
        {"id": "cred-011", "service": "store.another.com", "username": "judy", "password": "J!u5d6y7p8q9r", "category_id": "ecommerce", "password_strength": "strong", "expired": False},
        # 诱饵：正常但分类是email
        {"id": "cred-012", "service": "backup.mail.org", "username": "karl", "password": "K@r1l2p3a4s5s", "category_id": "email", "password_strength": "strong", "expired": False},
        # 小写的strong？但schema要求精确，这里写 'Strong' 作为干扰 (大小写敏感)
        {"id": "cred-013", "service": "test.case.com", "username": "lisa", "password": "L!i9s8a7b6c5", "category_id": "social", "password_strength": "Strong", "expired": False},
    ]
    with open("data/credentials.json", "w") as f:
        json.dump(credentials, f, indent=2)
    
    # 3. 创建一些无关的干扰目录和文件
    os.makedirs("old_backup", exist_ok=True)
    with open("old_backup/credentials_backup.json", "w") as f:
        json.dump([{"fake": "data"}], f)
    os.makedirs("temp", exist_ok=True)
    with open("temp/note.txt", "w") as f:
        f.write("Don't look here")
    # 副本目录
    os.makedirs("ops", exist_ok=True)  # 预创建ops目录，方便verifier检查

if __name__ == "__main__":
    build_env()
