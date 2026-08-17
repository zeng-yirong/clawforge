import os
import json

def build_env():
    # ---------- data/ ----------
    os.makedirs("data", exist_ok=True)

    accounts = [
        {
            "account_id": "emp_001",
            "display_name": "Alice Johnson",
            "department": "Sales",
            "email": "alice@company.com",
            "permissions": ["read"],
            "pack_id": "sales_pack"
        },
        {
            "account_id": "emp_002",
            "display_name": "Bob Smith",
            "department": "Engineering",
            "email": "bob.smith@company.com",
            "permissions": ["read", "write"],
            "pack_id": "eng_pack"
        },
        {
            "account_id": "emp_003",
            "display_name": "Charlie Brown",
            "department": "Marketing",
            "email": "charlie@company.com",
            "permissions": ["read"],
            "pack_id": "mkt_pack"
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "ct_01", "name": "HR Dept", "role": "admin", "email": "hr@company.com"},
        {"contact_id": "ct_02", "name": "IT Support", "role": "tech", "email": "it@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- onboarding/ ----------
    os.makedirs("onboarding", exist_ok=True)

    contracts = [
        {
            "employee_id": "emp_001",
            "employee_name": "Alice Johnson",
            "status": "expired",
            "email": "alice@company.com"
        },
        {
            "employee_id": "emp_002",
            "employee_name": "Bob Smith",
            "status": "signed",
            "email": "bob.smith@company.com"
        },
        {
            "employee_id": "emp_003",
            "employee_name": "Charlie Brown",
            "status": "pending",
            "email": "charlie@company.com"
        }
    ]
    with open("onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    equipment_inventory = [
        {"asset_tag": "LAP-001", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LAP-002", "asset_type": "laptop", "status": "damaged"},
        {"asset_tag": "LAP-003", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "DESK-001", "asset_type": "desktop", "status": "available"},
        {"asset_tag": "TBL-001", "asset_type": "tablet", "status": "available"}
    ]
    with open("onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment_inventory}, f, indent=2)

    permission_packs = [
        {"pack_id": "eng_pack", "systems": ["CRM", "ERP", "CodeRepo", "Jira"]},
        {"pack_id": "sales_pack", "systems": ["CRM", "Salesforce"]},
        {"pack_id": "mkt_pack", "systems": ["CRM", "Mailchimp"]}
    ]
    with open("onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": permission_packs}, f, indent=2)

if __name__ == "__main__":
    build_env()
