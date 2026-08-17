import json
import os

def build_env():
    # Ensure directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- companies.json ---
    companies = [
        {
            "company_id": "comp_tech1",
            "name": "TechCorp Industries",
            "industry": "Technology",
            "size": "enterprise",
            "website": "https://techcorp.com",
            "address": "123 Tech St",
            "phone": "+1-555-1000",
            "tags": [],
            "annual_revenue": "100M+",
            "customer_since": "2020-01-01",
            "account_manager": "ct_001"
        },
        {
            "company_id": "comp_tech2",
            "name": "StartupIO",
            "industry": "Technology",
            "size": "small",
            "website": "https://startup.io",
            "address": "456 Startup Ave",
            "phone": "+1-555-2000",
            "tags": [],
            "annual_revenue": "1M-5M",
            "customer_since": "2023-06-01",
            "account_manager": "ct_003"
        },
        {
            "company_id": "comp_consult",
            "name": "ClientCo Operations",
            "industry": "Consulting",
            "size": "mid_market",
            "website": "https://clientco.com",
            "address": "789 Consult Blvd",
            "phone": "+1-555-3000",
            "tags": [],
            "annual_revenue": "25M-50M",
            "customer_since": "2019-03-15",
            "account_manager": "ct_002"
        }
    ]
    with open("data/companies.json", "w") as f:
        json.dump(companies, f, indent=2)

    # --- contacts.json ---
    contacts = [
        {
            "contact_id": "ct_001",
            "first_name": "Alice",
            "last_name": "Johnson",
            "full_name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "company_id": "comp_tech1",
            "job_title": "CTO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "inactive",
            "tags": []
        },
        {
            "contact_id": "ct_002",
            "first_name": "Bob",
            "last_name": "Smith",
            "full_name": "Bob Smith",
            "email": "bob.smith@clientco.com",
            "phone": "+1-555-0102",
            "company_id": "comp_tech1",
            "job_title": "Account Manager",
            "department": "Sales",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip"]
        },
        {
            "contact_id": "ct_003",
            "first_name": "Carol",
            "last_name": "Williams",
            "full_name": "Carol Williams",
            "email": "carol.w@startup.io",
            "phone": "+1-555-0103",
            "company_id": "comp_tech2",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "inactive",
            "tags": ["old"]
        },
        {
            "contact_id": "ct_004",
            "first_name": "David",
            "last_name": "Brown",
            "full_name": "David Brown",
            "email": "david.brown@email.com",
            "phone": "+1-555-0104",
            "company_id": "comp_consult",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "inactive",
            "tags": []
        },
        {
            "contact_id": "ct_005",
            "first_name": "Emma",
            "last_name": "Davis",
            "full_name": "Emma Davis",
            "email": "emma.davis@partner.net",
            "phone": "+1-555-0105",
            "company_id": "comp_tech2",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "inactive",
            "tags": []
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- Distracting files (empty) ---
    with open("data/reminders/reminders.json", "w") as f:
        json.dump([], f)
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump([], f)

if __name__ == "__main__":
    build_env()
