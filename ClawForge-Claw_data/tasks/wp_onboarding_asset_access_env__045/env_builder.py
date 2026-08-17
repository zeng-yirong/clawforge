import os
import json

def build_env():
    # Create directories
    os.makedirs("data/onboarding", exist_ok=True)
    os.makedirs("data/templates", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Contracts
    contracts = [
        {"employee_id": "EMP-045", "employee_name": "John Doe", "status": "signed", "email": "jdoe@example.com", "department": "Engineering"},
        {"employee_id": "EMP-046", "employee_name": "Jane Smith", "status": "pending", "email": "jsmith@example.com", "department": "Sales"},
        {"employee_id": "EMP-047", "employee_name": "Bob Lee", "status": "terminated", "email": "blee@example.com", "department": "Engineering"},
        {"employee_id": "EMP-048", "employee_name": "Alice Wu", "status": "signed", "email": "awu@example.com", "department": "Marketing"},
        {"employee_id": "EMP-049", "employee_name": "Carlos M", "status": "signed", "email": "carlos@old-email", "department": "Engineering"}  # invalid email format
    ]
    with open("data/onboarding/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)

    # Permission packs (department-based)
    permission_packs = [
        {"pack_id": "engineering_pack", "department": "Engineering", "systems": ["GitLab", "Jira", "Docker"]},
        {"pack_id": "sales_pack", "department": "Sales", "systems": ["Salesforce", "HubSpot"]},
        {"pack_id": "marketing_pack", "department": "Marketing", "systems": ["Mailchimp", "Canva", "GoogleAnalytics"]}
    ]
    with open("data/onboarding/permission_packs.json", "w") as f:
        json.dump(permission_packs, f, indent=2)

    # Equipment inventory (only one available laptop for Engineering)
    equipment_inventory = [
        {"asset_tag": "LT-044", "asset_type": "laptop", "status": "assigned"},
        {"asset_tag": "LT-045", "asset_type": "laptop", "status": "available"},
        {"asset_tag": "LT-046", "asset_type": "laptop", "status": "maintenance"},
        {"asset_tag": "DT-001", "asset_type": "desktop", "status": "available"},
        {"asset_tag": "MB-001", "asset_type": "monitor", "status": "available"}
    ]
    with open("data/onboarding/equipment_inventory.json", "w") as f:
        json.dump(equipment_inventory, f, indent=2)

    # Welcome message templates (with one correct standard template)
    templates = [
        {"filename": "welcome_standard.txt", "content": "Welcome {name} to {department}!"},
        {"filename": "welcome_short.txt", "content": "Hello {name}"},
        {"filename": "welcome_verbose.txt", "content": "Greetings {name}, we are excited to have you in {department}."}
    ]
    for t in templates:
        with open(f"data/templates/{t['filename']}", "w") as f:
            f.write(t["content"])

    # Create a dummy ops file to ensure directory exists (will be overwritten)
    with open("ops/onboarding_plan.json", "w") as f:
        f.write("{}")

if __name__ == "__main__":
    build_env()
