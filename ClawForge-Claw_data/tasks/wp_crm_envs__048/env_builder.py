import os
import json

def build_env():
    # create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- companies ----
    companies = {
        "wrapper": "companies",
        "companies": [
            {
                "company_id": "comp_clientco",
                "name": "ClientCo Operations",
                "industry": "Consulting",
                "size": "mid_market",
                "website": "https://clientco.com",
                "address": "123 Main St, City, State",
                "phone": "+1-555-1000",
                "tags": ["client"],
                "annual_revenue": "5M-10M",
                "customer_since": "2019-03-15",
                "account_manager": "ct_001"
            },
            {
                "company_id": "comp_techcorp",
                "name": "TechCorp Industries",
                "industry": "Technology",
                "size": "enterprise",
                "website": "https://techcorp.com",
                "address": "456 Oak Ave, Tech City, State",
                "phone": "+1-555-5000",
                "tags": ["tech", "partner"],
                "annual_revenue": "100M+",
                "customer_since": "2018-01-01",
                "account_manager": "ct_002"
            },
            {
                "company_id": "comp_other",
                "name": "Global Partners LLC",
                "industry": "Logistics",
                "size": "small",
                "website": "https://globalpartners.com",
                "address": "789 Pine Rd, Other City, State",
                "phone": "+1-555-2000",
                "tags": [],
                "annual_revenue": "1M-5M",
                "customer_since": "2020-07-01",
                "account_manager": "ct_003"
            }
        ]
    }
    with open("data/companies.json", "w") as f:
        json.dump(companies, f, indent=2)

    # ---- contacts ----
    contacts = {
        "wrapper": "contacts",
        "contacts": [
            {
                "contact_id": "c001",
                "first_name": "Alice",
                "last_name": "Johnson",
                "full_name": "Alice Johnson",
                "email": "alice.johnson@techcorp.com",
                "phone": "+1-555-0101",
                "company_id": "comp_techcorp",
                "job_title": "VP Engineering",
                "department": "Engineering",
                "contact_type": "business",
                "folder": "business",
                "tags": ["tech", "engineering"]
            },
            {
                "contact_id": "c002",
                "first_name": "Bob",
                "last_name": "Smith",
                "full_name": "Bob Smith",
                "email": "bob.smith@clientco.com",
                "phone": "+1-555-0102",
                "company_id": "comp_clientco",
                "job_title": "Account Manager",
                "department": "Sales",
                "contact_type": "business",
                "folder": "business",
                "tags": ["sales"]
            },
            {
                "contact_id": "c003",
                "first_name": "Carol",
                "last_name": "Williams",
                "full_name": "Carol Williams",
                "email": "carol.w@startup.io",
                "company_id": "comp_other",
                "job_title": "CEO",
                "department": "Leadership",
                "contact_type": "business",
                "folder": "business",
                "tags": ["ceo"]
            },
            {
                "contact_id": "c004",
                "first_name": "David",
                "last_name": "Brown",
                "full_name": "David Brown",
                "email": "david.brown@email.com",
                "company_id": "comp_clientco",
                "job_title": "IT Manager",
                "department": "IT",
                "contact_type": "business",
                "folder": "business",
                "tags": ["it"]
            },
            {
                "contact_id": "c005",
                "first_name": "Emma",
                "last_name": "Davis",
                "full_name": "Emma Davis",
                "email": "emma.davis@partner.net",
                "company_id": "comp_techcorp",
                "job_title": "Partnership Director",
                "department": "Business Development",
                "contact_type": "business",
                "folder": "business",
                "tags": ["partner", "bd"]
            },
            {
                "contact_id": "c006",
                "first_name": "Frank",
                "last_name": "Miller",
                "full_name": "Frank Miller",
                "email": "frank.m@oldclient.com",
                "company_id": "comp_clientco",
                "job_title": "Procurement Manager",
                "department": "Operations",
                "contact_type": "business",
                "folder": "business",
                "tags": ["procurement"]
            },
            {
                "contact_id": "c007",
                "first_name": "Grace",
                "last_name": "Wilson",
                "full_name": "Grace Wilson",
                "email": "grace.wilson@vendor.co",
                "company_id": "comp_other",
                "job_title": "CTO",
                "department": "Engineering",
                "contact_type": "business",
                "folder": "business",
                "tags": ["cto", "engineering"]
            }
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # create an empty ops directory (agent should place file here)
    # also add some distraction files
    os.makedirs("data/backups", exist_ok=True)
    with open("data/backups/contacts_old.json", "w") as f:
        json.dump({"note": "this is just an old copy"}, f)

if __name__ == "__main__":
    build_env()
