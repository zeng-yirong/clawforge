import os
import json
import random

def build_env():
    # Ensure base directories
    os.makedirs("shared_vault/finance", exist_ok=True)
    os.makedirs("shared_vault/devops", exist_ok=True)
    os.makedirs("personal", exist_ok=True)

    # --- finance/vault_2023.json ---
    vault_2023 = [
        {
            "id": "ACC-001",
            "username": "alice",
            "password": "p@ss1234",
            "category": "bank",
            "is_active": True,
            "last_updated": "2023-06-01"
        },
        {
            "id": "ACC-002",
            "username": "bob",
            "password": "securePass!2",
            "category": "bank",
            "is_active": False,
            "last_updated": "2023-05-12"
        },
        {
            "id": "ACC-003",
            "username": "charlie",
            "password": "Qwerty123!",
            "category": "social",
            "is_active": True,
            "last_updated": "2023-07-20"
        }
    ]
    with open("shared_vault/finance/vault_2023.json", "w") as f:
        json.dump(vault_2023, f, indent=2)

    # --- finance/vault_2024.json ---
    vault_2024 = [
        {
            "id": "ACC-001",
            "username": "alice",
            "password": "newP@ss456",
            "category": "bank",
            "is_active": True,
            "last_updated": "2024-01-15"
        },
        {
            "id": "ACC-004",
            "username": "dave",
            "password": "D@ve2024!",
            "category": "bank",
            "is_active": True,
            "last_updated": "2024-02-28"
        },
        {
            "id": "ACC-005",
            "username": "eve",
            "password": "Eve123$%",
            "category": "email",
            "is_active": True,
            "last_updated": "2024-03-01"
        }
    ]
    with open("shared_vault/finance/vault_2024.json", "w") as f:
        json.dump(vault_2024, f, indent=2)

    # --- devops/secrets_backup.json ---
    devops_backup = [
        {
            "id": "ACC-006",
            "username": "frank",
            "password": "F@nk!secure",
            "category": "bank",
            "is_active": True,
            "last_updated": "2024-04-10"
        },
        {
            "id": "ACC-002",
            "username": "bob",
            "password": "BobNewPass!",
            "category": "bank",
            "is_active": True,
            "last_updated": "2024-03-20"
        }
    ]
    with open("shared_vault/devops/secrets_backup.json", "w") as f:
        json.dump(devops_backup, f, indent=2)

    # --- shared_vault/old_backup.json ---
    old_backup = [
        {
            "id": "ACC-001",
            "username": "alice",
            "password": "oldP@ss",
            "category": "bank",
            "is_active": True,
            "last_updated": "2022-12-01"
        },
        {
            "id": "ACC-007",
            "username": "grace",
            "password": "Grace1",
            "category": "bank",
            "is_active": False,
            "last_updated": "2023-09-10"
        }
    ]
    with open("shared_vault/old_backup.json", "w") as f:
        json.dump(old_backup, f, indent=2)

    # --- personal/ 干扰文件 ---
    with open("personal/notes.txt", "w") as f:
        f.write("Personal reminders, not related to credentials.")

    # --- 一个非 JSON 的干扰文件 ---
    with open("shared_vault/readme.txt", "w") as f:
        f.write("This folder contains legacy vault backups.\n")

if __name__ == "__main__":
    build_env()
