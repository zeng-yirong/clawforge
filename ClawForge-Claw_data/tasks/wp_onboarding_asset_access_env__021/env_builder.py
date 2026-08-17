import os
import json
import random

def build_env():
    # create directory structure
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # accounts.json
    accounts = [
        {"account_id": "E001", "display_name": "John Smith", "department": "Sales", "email": "john.smith@company.com", "permissions": ["sales_read"]},
        {"account_id": "E002", "display_name": "Jane Doe", "department": "Marketing", "email": "jane.doe@company.com", "permissions": ["marketing_all"]},
        {"account_id": "E003", "display_name": "Bob Lee", "department": "Engineering", "email": "bob.lee@company.com", "permissions": ["eng_read", "eng_write"]},
        {"account_id": "E004", "display_name": "Carol Wang", "department": "HR", "email": "carol.wang@company.com", "permissions": ["hr_all"]},
        {"account_id": "E005", "display_name": "Alice Chen", "department": "Engineering", "email": "alice.chen@company.com", "permissions": ["eng_standard"]},
        {"account_id": "E006", "display_name": "David Li", "department": "Finance", "email": "david.li@company.com", "permissions": ["finance_read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # contacts.json
    contacts = [
        {"contact_id": "C001", "name": "HR Helpdesk", "role": "HR", "email": "hr@company.com"},
        {"contact_id": "C002", "name": "IT Support", "role": "IT", "email": "it@company.com"},
        {"contact_id": "C003", "name": "Facilities", "role": "Admin", "email": "facilities@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # contracts.json
    contracts = [
        {"employee_id": "E001", "employee_name": "John Smith", "status": "signed", "email": "john.smith@company.com", "pack_id": "sales_basic", "start_date": "2024-01-15"},
        {"employee_id": "E002", "employee_name": "Jane Doe", "status": "draft", "email": "jane.doe@company.com", "pack_id": "marketing_pro", "start_date": "2024-02-01"},
        {"employee_id": "E003", "employee_name": "Bob Lee", "status": "signed", "email": "bob.lee@company.com", "pack_id": "eng_write", "start_date": "2023-11-20"},
        {"employee_id": "E004", "employee_name": "Carol Wang", "status": "signed", "email": "carol.wang@company.com", "pack_id": "hr_full", "start_date": "2024-03-10"},
        {"employee_id": "E005", "employee_name": "Alice Chen", "status": "signed", "email": "alice.chen@company.com", "pack_id": "eng_standard", "start_date": "2024-07-22"},
        {"employee_id": "E006", "employee_name": "David Li", "status": "pending", "email": "david.li@company.com", "pack_id": "finance_basic", "start_date": "2024-08-01"}
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # equipment_inventory.json
    equipment = [
        {"asset_tag": "TAG-001", "asset_type": "Laptop", "status": "assigned", "assigned_to": "E003"},
        {"asset_tag": "TAG-002", "asset_type": "Monitor", "status": "available", "assigned_to": None},
        {"asset_tag": "TAG-003", "asset_type": "Laptop", "status": "retired", "assigned_to": None},
        {"asset_tag": "TAG-004", "asset_type": "Laptop", "status": "available", "assigned_to": None},
        {"asset_tag": "TAG-005", "asset_type": "Laptop", "status": "available", "assigned_to": None},
        {"asset_tag": "TAG-006", "asset_type": "Keyboard", "status": "available", "assigned_to": None}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment}, f, indent=2)

    # permission_packs.json
    permission_packs = [
        {"pack_id": "eng_standard", "systems": [{"system": "Jira", "permission": "write"}, {"system": "GitLab", "permission": "read"}, {"system": "Slack", "permission": "read"}]},
        {"pack_id": "eng_write", "systems": [{"system": "Jira", "permission": "admin"}, {"system": "GitLab", "permission": "write"}, {"system": "Confluence", "permission": "write"}]},
        {"pack_id": "sales_basic", "systems": [{"system": "CRM", "permission": "read"}, {"system": "Slack", "permission": "read"}]},
        {"pack_id": "hr_full", "systems": [{"system": "HRIS", "permission": "admin"}, {"system": "Slack", "permission": "read"}]},
        {"pack_id": "marketing_pro", "systems": [{"system": "HubSpot", "permission": "write"}, {"system": "Slack", "permission": "read"}]},
        {"pack_id": "finance_basic", "systems": [{"system": "ERP", "permission": "read"}, {"system": "Slack", "permission": "read"}]}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": permission_packs}, f, indent=2)

    # outputs/ - create some existing onboarding bundles for signed employees (E003, E004)
    existing_bundle_e003 = {
        "employee_id": "E003",
        "email_profile": {"email": "bob.lee@company.com", "display_name": "Bob Lee", "department": "Engineering"},
        "system_access": [
            {"system": "Jira", "permission": "admin"},
            {"system": "GitLab", "permission": "write"},
            {"system": "Confluence", "permission": "write"}
        ],
        "equipment": {"asset_tag": "TAG-001", "asset_type": "Laptop"},
        "welcome_message": {"channel": "#general", "text": "欢迎 Bob Lee 加入 Engineering！"}
    }
    with open("outputs/employee_E003_onboarding.json", "w") as f:
        json.dump(existing_bundle_e003, f, indent=2)

    existing_bundle_e004 = {
        "employee_id": "E004",
        "email_profile": {"email": "carol.wang@company.com", "display_name": "Carol Wang", "department": "HR"},
        "system_access": [
            {"system": "HRIS", "permission": "admin"},
            {"system": "Slack", "permission": "read"}
        ],
        "equipment": None,
        "welcome_message": {"channel": "#general", "text": "欢迎 Carol Wang 加入 HR！"}
    }
    with open("outputs/employee_E004_onboarding.json", "w") as f:
        json.dump(existing_bundle_e004, f, indent=2)

if __name__ == "__main__":
    build_env()
