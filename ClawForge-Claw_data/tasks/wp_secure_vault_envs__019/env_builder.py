import os, json, datetime

def build_env():
    # 创建 credentials 目录
    os.makedirs("credentials", exist_ok=True)
    creds = [
        {"id":"cred_001","username":"alice@work.com","site":"mail.example.com","password":"pass123","strength":30,"expiry":"2025-01-01"},
        {"id":"cred_002","username":"bob@shop.com","site":"shop.example.com","password":"strong!Pass","strength":85,"expiry":"2026-06-01"},
        {"id":"cred_003","username":"carol@bank.com","site":"bank.example.com","password":"weak1","strength":20,"expiry":"2024-12-01"},
        {"id":"cred_004","username":"dave@bank.com","site":"bank.example.com","password":"weak2","strength":35,"expiry":"2025-03-01"},
        {"id":"cred_005","username":"eve@social.com","site":"social.example.com","password":"mediumPass","strength":55,"expiry":"2025-07-01"},
        {"id":"cred_006","username":"frank@unknown.com","site":"unknown.org","password":"any","strength":10,"expiry":"2024-01-01"},
    ]
    for c in creds:
        with open(f"credentials/{c['id']}.json","w") as f:
            json.dump(c, f)

    # 创建 config 目录
    os.makedirs("config", exist_ok=True)
    site_cat = {
        "mail.example.com": "工作邮箱",
        "shop.example.com": "电商平台",
        "bank.example.com": "银行账户",
        "social.example.com": "社交媒体"
    }
    with open("config/site_categories.json","w") as f:
        json.dump(site_cat, f, ensure_ascii=False, indent=2)

    # 创建 pool 目录
    os.makedirs("pool", exist_ok=True)
    strong_passwords = [
        {"cred_id":"cred_003","new_password":"NewStr0ng!Pass"},
        {"cred_id":"cred_004","new_password":"Another#1Strong"},
        {"cred_id":"cred_006","new_password":"UnusedPass123"}  # 干扰项
    ]
    with open("pool/strong_passwords.json","w") as f:
        json.dump(strong_passwords, f, indent=2)

if __name__ == "__main__":
    build_env()
