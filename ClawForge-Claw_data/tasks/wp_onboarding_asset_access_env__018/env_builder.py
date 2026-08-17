import json
import os

def build_env():
    # --- contracts.json ---
    contracts = [
        {
            "employee_id": "EMP003",
            "employee_name": "John Smith",
            "status": "signed",
            "department": "Engineering"
        },
        {
            "employee_id": "EMP007",
            "employee_name": "Alice Johnson",
            "status": "signed",
            "department": "Sales"
        },
        {
            "employee_id": "EMP012",
            "employee_name": "Bob Lee",
            "status": "draft",
            "department": "Engineering"
        },
        {
            "employee_id": "EMP018",
            "employee_name": "Carol White",
            "status": "expired",
            "department": "Marketing"
        },
        {
            "employee_id": "EMP021",
            "employee_name": "David Brown",
            "status": "signed",
            "department": "Marketing"
        }
    ]
    os.makedirs("data/onboarding", exist_ok=True)
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump({"contracts": contracts}, f, indent=2)

    # --- equipment_inventory.json ---
    equipment = [
        {"asset_tag": "LT-2025-001", "asset_type": "Laptop", "status": "available"},
        {"asset_tag": "LT-2025-002", "asset_type": "Laptop", "status": "assigned"},
        {"asset_tag": "LT-2024-088", "asset_type": "Laptop", "status": "repair"},
        {"asset_tag": "MN-2025-003", "asset_type": "Monitor", "status": "available"},
        {"asset_tag": "DK-2023-012", "asset_type": "Docking Station", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump({"equipment_inventory": equipment}, f, indent=2)

    # --- permission_packs.json ---
    permission_packs = [
        {
            "pack_id": "eng_standard",
            "applicable_department": "Engineering",
            "systems": ["GitLab", "Jira", "Confluence"]
        },
        {
            "pack_id": "sales_crm",
            "applicable_department": "Sales",
            "systems": ["Salesforce", "HubSpot", "Slack"]
        },
        {
            "pack_id": "marketing_tools",
            "applicable_department": "Marketing",
            "systems": ["Mailchimp", "Google Analytics", "Canva"]
        }
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump({"permission_packs": permission_packs}, f, indent=2)

    # --- accounts.json (interference – existing accounts, not used for onboarding) ---
    accounts = [
        {"account_id": "A100", "display_name": "John Smith", "department": "Engineering", "email": "john.smith@oldcompany.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # --- contacts.json (interference) ---
    contacts = [
        {"contact_id": "C001", "name": "Jane Doe", "role": "Manager", "email": "jane@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
