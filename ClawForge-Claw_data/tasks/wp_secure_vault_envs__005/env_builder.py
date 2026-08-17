import os
import json

def build_env():
    # Create directories
    os.makedirs("vault", exist_ok=True)
    os.makedirs("policies", exist_ok=True)

    # Password policies per category
    policies = {
        "banking": {"min_length": 12, "require_special": True, "require_digit": True},
        "social": {"min_length": 8, "require_special": False, "require_digit": False},
        "work_email": {"min_length": 10, "require_uppercase": True}
    }
    with open("policies/password_policies.json", "w") as f:
        json.dump(policies, f, indent=2)

    # Vault credentials (some strong, some weak, one corrupted)
    credentials = [
        # cred_001 – banking, password too short (9 chars, need 12)
        {"id": "cred_001", "name": "admin@bank.com", "category": "banking", "password": "Abc12345!"},
        # cred_002 – social, too short (5 chars)
        {"id": "cred_002", "name": "user@social.com", "category": "social", "password": "short"},
        # cred_003 – work_email, OK (11 chars, has uppercase)
        {"id": "cred_003", "name": "boss@work.com", "category": "work_email", "password": "StrongPass1"},
        # cred_004 – banking, OK (22 chars, meets all)
        {"id": "cred_004", "name": "user@bank.com", "category": "banking", "password": "VeryLongAndComplex@123"},
        # cred_005 – social, too short (7 chars)
        {"id": "cred_005", "name": "test@social.com", "category": "social", "password": "1234567"},
        # cred_006 – work_email, too short and lacks uppercase
        {"id": "cred_006", "name": "admin@work.com", "category": "work_email", "password": "weakpass"},
        # cred_007 – banking, OK
        {"id": "cred_007", "name": "secure@bank.com", "category": "banking", "password": "Secure!Pass1234"},
    ]

    for cred in credentials:
        filename = f"vault/{cred['id']}.json"
        with open(filename, "w") as f:
            json.dump(cred, f)

    # Corrupted file (not valid JSON)
    with open("vault/cred_008.json", "w") as f:
        f.write("this is not json")

if __name__ == "__main__":
    build_env()
