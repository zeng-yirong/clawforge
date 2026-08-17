import os
import json
import shutil

def build_env():
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # --- companies.json ---
    companies = [
        {
            "company_id": "comp_techcorp",
            "name": "TechCorp Industries",
            "industry": "Technology",
            "size": "enterprise",
            "website": "https://techcorp.com",
            "address": "1 Tech Plaza",
            "phone": "+1-555-5000",
            "tags": ["tech", "enterprise"],
            "annual_revenue": "100M+",
            "customer_since": "2020-01-01",
            "account_manager": "ct_001"
        },
        {
            "company_id": "comp_clientco",
            "name": "ClientCo Operations",
            "industry": "Consulting",
            "size": "mid_market",
            "website": "https://clientco.com",
            "address": "2 Business Ave",
            "phone": "+1-555-1000",
            "tags": ["consulting"],
            "annual_revenue": "5M-10M",
            "customer_since": "2019-06-15",
            "account_manager": "ct_002"
        },
        {
            "company_id": "comp_startupio",
            "name": "StartupIO",
            "industry": "Technology",
            "size": "small",
            "website": "https://startup.io",
            "address": "3 Innovation Blvd",
            "phone": "+1-555-4000",
            "tags": ["startup", "tech"],
            "annual_revenue": "1M-5M",
            "customer_since": "2021-11-01",
            "account_manager": "ct_007"
        },
        {
            "company_id": "comp_vendorco",
            "name": "VendorCo Supplies",
            "industry": "Logistics",
            "size": "mid_market",
            "website": "https://vendorco.com",
            "address": "4 Supply Chain Rd",
            "phone": "+1-555-6000",
            "tags": ["logistics"],
            "annual_revenue": "25M-50M",
            "customer_since": "2018-03-20",
            "account_manager": "ct_005"
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
            "company_id": "comp_techcorp",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "personal",
            "tags": []
        },
        {
            "contact_id": "ct_002",
            "first_name": "Bob",
            "last_name": "Smith",
            "full_name": "Bob Smith",
            "email": "bob.smith@clientco.com",
            "phone": "+1-555-0102",
            "company_id": "comp_clientco",
            "job_title": "Account Manager",
            "department": "Sales",
            "contact_type": "business",
            "folder": "personal",
            "tags": []
        },
        {
            "contact_id": "ct_003",
            "first_name": "Carol",
            "last_name": "Williams",
            "full_name": "Carol Williams",
            "email": "carol.w@startup.io",
            "phone": "+1-555-0103",
            "company_id": "comp_startupio",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "personal",
            "folder": "personal",
            "tags": []
        },
        {
            "contact_id": "ct_004",
            "first_name": "David",
            "last_name": "Brown",
            "full_name": "David Brown",
            "email": "david.brown@email.com",
            "phone": "+1-555-0104",
            "company_id": "comp_techcorp",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "business",
            "tags": ["existing"]
        },
        {
            "contact_id": "ct_005",
            "first_name": "Emma",
            "last_name": "Davis",
            "full_name": "Emma Davis",
            "email": "emma.davis@partner.net",
            "phone": "+1-555-0105",
            "company_id": "comp_vendorco",
            "job_title": "Partnership Director",
            "department": "Business Development",
            "contact_type": "business",
            "folder": "business",
            "tags": []
        },
        {
            "contact_id": "ct_006",
            "first_name": "Frank",
            "last_name": "Miller",
            "full_name": "Frank Miller",
            "email": "frank.m@oldclient.com",
            "phone": "+1-555-0106",
            "company_id": "comp_techcorp",
            "job_title": "Procurement Manager",
            "department": "Operations",
            "contact_type": "business",
            "folder": "inactive",
            "tags": ["priority"]
        },
        {
            "contact_id": "ct_007",
            "first_name": "Grace",
            "last_name": "Wilson",
            "full_name": "Grace Wilson",
            "email": "grace.wilson@vendor.co",
            "phone": "+1-555-0107",
            "company_id": "comp_startupio",
            "job_title": "CTO",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": []
        },
        {
            "contact_id": "ct_008",
            "first_name": "Henry",
            "last_name": "Taylor",
            "full_name": "Henry Taylor",
            "email": "henry.t@bigcorp.com",
            "phone": "+1-555-0108",
            "company_id": "comp_clientco",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": []
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # --- Distractors: old backup, notes, irrelevant csv ---
    with open("backup/contacts_backup_2023.json", "w") as f:
        json.dump([], f)
    with open("backup/contacts_backup_2024.json", "w") as f:
        json.dump(contacts, f, indent=2)
    with open("data/notes.txt", "w") as f:
        f.write("TODO: review contact folders after Q2 campaign\n")
    with open("data/import_log.csv", "w") as f:
        f.write("timestamp,status\n2025-01-01,ok\n")
    # Leave ops/ empty for agent output

build_env()
