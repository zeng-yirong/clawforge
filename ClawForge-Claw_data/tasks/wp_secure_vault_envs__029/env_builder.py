import os
import json
import csv
import random
import string
import math

def build_env():
    # Ensure subdirectories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ========== vault_schema.json (category definitions) ==========
    categories = [
        {"category_id": "cat_work", "name": "工作邮箱", "priority": "critical", "requires_mfa": True, "password_policy": {"min_length": 12, "require_special": True}},
        {"category_id": "cat_ecom", "name": "电商平台", "priority": "high", "requires_mfa": True, "password_policy": {"min_length": 10, "require_special": True}},
        {"category_id": "cat_social", "name": "社交媒体", "priority": "medium", "requires_mfa": False, "password_policy": {"min_length": 8, "require_special": False}},
        {"category_id": "cat_bank", "name": "银行账户", "priority": "critical", "requires_mfa": True, "password_policy": {"min_length": 14, "require_special": True}},
    ]
    with open("data/vault_schema.json", "w") as f:
        json.dump(categories, f, indent=2)

    # ========== credentials.csv (with noise and traps) ==========
    rows = []
    # Weak passwords (targets)
    weak_def = [
        ("cred_001", "cat_work", "alice@company.com", "123456"),
        ("cred_002", "cat_ecom", "bob@shop.com", "password"),
        ("cred_003", "cat_social", "charlie@insta.com", "abc123"),
        ("cred_004", "cat_bank", "dave@bank.com", "qwerty"),
        ("cred_005", "cat_work", "eve@corp.com", "letmein"),
        ("cred_006", "cat_ecom", "frank@amazon.com", "111111"),
        ("cred_007", "cat_social", "grace@fb.com", "sunshine"),
        ("cred_008", "cat_bank", "hank@chase.com", "iloveyou"),
    ]
    # Strong passwords (noise)
    strong_def = [
        ("cred_009", "cat_work", "iris@acme.com", "G7#kLp9@zQ2$mNx"),
        ("cred_010", "cat_ecom", "jack@store.com", "P@ssw0rd!2024"),
        ("cred_011", "cat_social", "karen@twitter.com", "MyC@t!sFluffy"),
        ("cred_012", "cat_bank", "leo@wells.com", "3^R#tY8uI*opL"),
        ("cred_013", "cat_work", "mike@startup.com", "CorrectHorseBatteryStaple"),
        ("cred_014", "cat_ecom", "nina@etsy.com", "aB3!xYz9&l"),
        ("cred_015", "cat_social", "oliver@tiktok.com", "TomorrowNeverDies!23"),
        ("cred_016", "cat_bank", "pat@citi.com", "JkL8#mN2$qR5^wS1"),
    ]
    # Tricky ones: look weak but actually strong (length≥8, not all numeric/alpha)
    tricky_def = [
        ("cred_017", "cat_work", "quinn@tech.com", "Admin123!"),       # length 9, has special
        ("cred_018", "cat_ecom", "rachel@buy.com", "Welcome1!"),       # length 9, special
        ("cred_019", "cat_social", "sam@snap.com", "Password1#"),      # length 10, special
        ("cred_020", "cat_bank", "tina@boa.com", "Changeme!9"),        # length 10, special
    ]
    # Combine all
    all_creds = weak_def + strong_def + tricky_def
    # Shuffle to add difficulty
    random.shuffle(all_creds)

    # Build category name mapping for later use
    cat_map = {c["category_id"]: c["name"] for c in categories}

    with open("data/credentials.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "category_id", "platform", "username", "password"])
        for cid, cat, uname, pw in all_creds:
            writer.writerow([cid, cat, uname.split('@')[1] if '@' in uname else 'unknown', uname, pw])

    # ========== autofill_rules.json (distractor) ==========
    autofill = [
        {"platform": "mail.company.com", "credential_id": "cred_001", "field_map": {"username": "#email", "password": "#pass"}},
        {"platform": "shop.amazon.com", "credential_id": "cred_002", "field_map": {"login": "#email", "pw": "#password"}},
        {"platform": "facebook.com", "credential_id": "cred_007", "field_map": {"user": "#user", "pass": "#pass"}},
        {"platform": "chase.com", "credential_id": "cred_008", "field_map": {"uid": "#uid", "pwd": "#pwd"}},
    ]
    with open("data/autofill_rules.json", "w") as f:
        json.dump(autofill, f, indent=2)

    # ========== Also create an empty op score file (placeholder) ==========
    with open("ops/weak_creds.json", "w") as f:
        f.write("{}")   # empty, agent must overwrite

    print("Environment built: data/ and ops/ directories created with realistic credential data.")

if __name__ == "__main__":
    build_env()
