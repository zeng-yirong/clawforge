import json
import os

def build_env():
    # Ensure required directories
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Interference directories
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("data/old", exist_ok=True)

    # ── Companies ──────────────────────────────────────────
    companies = [
        {
            "company_id": "techcorp",
            "name": "TechCorp Industries",
            "industry": "Technology",
            "size": "enterprise",
            "website": "https://techcorp.com",
            "address": "100 Tech Lane",
            "phone": "+1-555-5000",
            "tags": ["tech"],
            "annual_revenue": "100M+",
            "customer_since": "2019",
            "account_manager": "ct_001",
        },
        {
            "company_id": "clientco",
            "name": "ClientCo Operations",
            "industry": "Consulting",
            "size": "mid_market",
            "website": "https://clientco.com",
            "address": "200 Business Ave",
            "phone": "+1-555-1000",
            "tags": ["consulting"],
            "annual_revenue": "25M-50M",
            "customer_since": "2020",
            "account_manager": "ct_002",
        },
        {
            "company_id": "oldclient",
            "name": "OldClient Services",
            "industry": "Logistics",
            "size": "small",
            "website": "https://oldclient.com",
            "address": "300 Old Rd",
            "phone": "+1-555-3000",
            "tags": ["logistics"],
            "annual_revenue": "5M-10M",
            "customer_since": "2018",
            "account_manager": "ct_003",
        },
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f)

    # ── Contacts ───────────────────────────────────────────
    contacts = [
        {
            "contact_id": "ct_001",
            "first_name": "Alice",
            "last_name": "Johnson",
            "full_name": "Alice Johnson",
            "email": "alice.johnson@techcorp.com",
            "phone": "+1-555-0101",
            "company_id": "techcorp",
            "job_title": "CTO",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "personal",
            "tags": ["vip"],
        },
        {
            "contact_id": "ct_002",
            "first_name": "Bob",
            "last_name": "Smith",
            "full_name": "Bob Smith",
            "email": "bob.smith@techcorp.com",
            "phone": "+1-555-0102",
            "company_id": "techcorp",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip"],
        },
        {
            "contact_id": "ct_003",
            "first_name": "Carol",
            "last_name": "Williams",
            "full_name": "Carol Williams",
            "email": "carol.williams@techcorp.com",
            "phone": "+1-555-0103",
            "company_id": "techcorp",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": ["tech-partner"],
        },
        # Non‑TechCorp contacts (interference)
        {
            "contact_id": "ct_004",
            "first_name": "David",
            "last_name": "Brown",
            "full_name": "David Brown",
            "email": "david.brown@clientco.com",
            "phone": "+1-555-0104",
            "company_id": "clientco",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip"],
        },
        {
            "contact_id": "ct_005",
            "first_name": "Emma",
            "last_name": "Davis",
            "full_name": "Emma Davis",
            "email": "emma.davis@oldclient.com",
            "phone": "+1-555-0105",
            "company_id": "oldclient",
            "job_title": "Partnership Director",
            "department": "Business Development",
            "contact_type": "business",
            "folder": "inactive",
            "tags": ["partner"],
        },
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # ── Tag Definitions ────────────────────────────────────
    tag_defs = [
        {
            "tag_id": "tag_vip",
            "name": "vip",
            "color": "#FFD700",
            "description": "Very important person",
            "category": "priority",
        },
        {
            "tag_id": "tag_tech",
            "name": "tech-partner",
            "color": "#00BFFF",
            "description": "Technology partner",
            "category": "relationship",
        },
        {
            "tag_id": "tag_partner",
            "name": "partner",
            "color": "#32CD32",
            "description": "Business partner",
            "category": "relationship",
        },
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_defs}, f)

    # ── Interference files ─────────────────────────────────
    with open("data/tags/legacy_tags.json", "w") as f:
        json.dump({"tags": [{"name": "tech", "color": "blue"}]}, f)

    with open("data/backup/contacts_backup.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    with open("data/raw_contacts.csv", "w") as f:
        f.write("name,email,company\n")
        f.write("Fake,User,fake@email.com,Unknown\n")

if __name__ == "__main__":
    build_env()
