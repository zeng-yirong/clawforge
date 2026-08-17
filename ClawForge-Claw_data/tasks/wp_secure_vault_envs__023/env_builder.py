import os
import json
import datetime

def build_env():
    # Create directory structure
    os.makedirs("vault", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Write policies
    policies = [
        {
            "policy_id": "policy_001",
            "name": "Standard Policy",
            "min_length": 8,
            "require_uppercase": True,
            "require_digit": True,
            "require_special": True,
            "max_age_days": 180
        },
        {
            "policy_id": "policy_002",
            "name": "Legacy Policy",
            "min_length": 6,
            "require_uppercase": True,
            "require_digit": False,
            "require_special": False,
            "max_age_days": 365
        }
    ]
    with open("vault/policies.json", "w") as f:
        json.dump(policies, f, indent=2)

    # Define baseline date for age calculation
    base_date = datetime.date(2025, 3, 1)
    def date_ago(days):
        d = base_date - datetime.timedelta(days=days)
        return d.isoformat()

    # Credentials – mix of compliant and non-compliant
    credentials = [
        {
            "id": "cred_001",
            "name": "Admin Portal",
            "password": "Abc123!",
            "policy_id": "policy_001",
            "created_at": date_ago(30)
        },
        {
            "id": "cred_002",
            "name": "DevOps Dashboard",
            "password": "VeryLongPassword123",
            "policy_id": "policy_001",
            "created_at": date_ago(60)
        },
        {
            "id": "cred_003",
            "name": "Mail Server",
            "password": "Short1!",
            "policy_id": "policy_001",
            "created_at": date_ago(10)
        },
        {
            "id": "cred_004",
            "name": "CI/CD GitLab",
            "password": "Compliant@2023",
            "policy_id": "policy_001",
            "created_at": date_ago(90)
        },
        {
            "id": "cred_005",
            "name": "Legacy App",
            "password": "OldPass!2",
            "policy_id": "policy_002",
            "created_at": date_ago(400)  # expired under policy_002? max_age_days=365, 400>365 -> expired
        },
        {
            "id": "cred_006",
            "name": "HR System",
            "password": "Abcd1234",
            "policy_id": "policy_001",
            "created_at": date_ago(30)  # missing special char
        },
        {
            "id": "cred_007",
            "name": "Invoice Portal",
            "password": "!@#$%^&*",
            "policy_id": "policy_001",
            "created_at": date_ago(5)  # missing uppercase and digit
        },
        {
            "id": "cred_008",
            "name": "Backup Service",
            "password": "P@ssw0rd",
            "policy_id": "policy_001",
            "created_at": date_ago(200)  # 200 > 180 -> expired
        },
        {
            "id": "cred_009",
            "name": "Test Account",
            "password": "",             # empty password -> invalid record, skip
            "policy_id": "policy_001",
            "created_at": date_ago(1)
        },
        {
            "id": "cred_010",
            "name": "Old Monitor",
            # missing password field -> invalid record, skip
            "policy_id": "policy_002",
            "created_at": date_ago(100)
        },
        {
            "id": "cred_011",
            "name": "Audit Log",
            "password": "Stronger!1",
            "policy_id": "policy_001",
            "created_at": date_ago(170)  # compliant (8+ chars, upper, digit, special, not expired)
        }
    ]
    with open("vault/credentials.json", "w") as f:
        json.dump(credentials, f, indent=2)

    # Interference: backup with outdated data
    backup_creds = [
        {"id": "cred_old", "name": "Old Database", "password": "weak1", "policy_id": "policy_001"}
    ]
    with open("backups/old_credentials.json", "w") as f:
        json.dump(backup_creds, f, indent=2)

    # Interference: log file with unrelated content
    with open("logs/access.log", "w") as f:
        f.write("2025-03-01 10:23:45 INFO User login from 10.0.0.1\n")
        f.write("2025-03-01 10:24:01 WARN Failed password attempt for cred_001\n")

    # Ensure ops directory has placeholder (will be overwritten by agent)
    with open("ops/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
