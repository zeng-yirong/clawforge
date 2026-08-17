import json
import os

def build_env():
    # Ensure base directories
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- contracts.json (interference: multiple contracts, only one signed) ---
    contracts = [
        {
            "employee_id": "E123",
            "employee_name": "Alice Wang",
            "status": "signed",
            "email": "alice.wang@example.com",
            "department": "Engineering"
        },
        {
            "employee_id": "E456",
            "employee_name": "Bob Li",
            "status": "pending",
            "email": "bob.li@example.com",
            "department": "Engineering"
        },
        {
            "employee_id": "E789",
            "employee_name": "Carol Chen",
            "status": "expired",
            "email": "carol.chen@example.com",
            "department": "Marketing"
        },
        {
            "employee_id": "E101",
            "employee_name": "David Park",
            "status": "signed",
            "email": "david.park@example.com",
            "department": "Finance"
        }
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # --- permission_packs.json (only Engineering pack matches Alice) ---
    permission_packs = [
        {
            "pack_id": "eng-full",
            "department": "Engineering",
            "systems": ["JIRA", "GitLab", "Confluence"]
        },
        {
            "pack_id": "mkt-starter",
            "department": "Marketing",
            "systems": ["HubSpot", "Canva"]
        },
        {
            "pack_id": "fin-core",
            "department": "Finance",
            "systems": ["SAP", "Tableau"]
        }
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": permission_packs}, f, indent=2)

    # --- equipment_inventory.json (only one available laptop) ---
    inventory = [
        {
            "asset_tag": "LAP001",
            "asset_type": "laptop",
            "status": "available"
        },
        {
            "asset_tag": "LAP002",
            "asset_type": "laptop",
            "status": "broken"
        },
        {
            "asset_tag": "MON001",
            "asset_type": "monitor",
            "status": "available"
        },
        {
            "asset_tag": "LAP003",
            "asset_type": "laptop",
            "status": "allocated"
        }
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": inventory}, f, indent=2)

    # --- interference files (accounts and contacts) ---
    accounts = [
        {"account_id": "A001", "display_name": "Existing User", "department": "IT", "email": "it@company.com", "permissions": ["admin"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "C001", "name": "HR Contact", "role": "HR", "email": "hr@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
