import json
import os

def build_env():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Companies data (6 companies)
    companies = [
        {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise",
         "website": "https://techcorp.com", "address": "123 Tech Blvd", "phone": "+1-555-1000",
         "tags": ["tech"], "annual_revenue": "100M+", "customer_since": "2020-01-01", "account_manager": "ct_001"},
        {"company_id": "comp_002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market",
         "website": "https://clientco.com", "address": "456 Client St", "phone": "+1-555-2000",
         "tags": ["client"], "annual_revenue": "25M-50M", "customer_since": "2019-06-15", "account_manager": "ct_002"},
        {"company_id": "comp_003", "name": "StartupIO", "industry": "Technology", "size": "small",
         "website": "https://startup.io", "address": "789 Startup Ln", "phone": "+1-555-3000",
         "tags": ["startup"], "annual_revenue": "5M-10M", "customer_since": "2021-03-01", "account_manager": "ct_003"},
        {"company_id": "comp_004", "name": "Global Partners LLC", "industry": "Logistics", "size": "enterprise",
         "website": "https://globalpartners.com", "address": "321 Global Ave", "phone": "+1-555-4000",
         "tags": ["global"], "annual_revenue": "50M-100M", "customer_since": "2018-11-20", "account_manager": "ct_005"},
        {"company_id": "comp_005", "name": "VendorCo Supplies", "industry": "Manufacturing", "size": "mid_market",
         "website": "https://vendorco.com", "address": "654 Vendor Rd", "phone": "+1-555-5000",
         "tags": ["vendor"], "annual_revenue": "10M-25M", "customer_since": "2017-07-10", "account_manager": "ct_007"},
        {"company_id": "comp_006", "name": "OldClient Services", "industry": "Retail", "size": "small",
         "website": "https://oldclient.com", "address": "987 Old Client Dr", "phone": "+1-555-6000",
         "tags": ["old"], "annual_revenue": "1M-5M", "customer_since": "2016-02-28", "account_manager": "ct_002"},
    ]

    with open("data/companies.json", "w") as f:
        json.dump(companies, f, indent=2)

    # Contacts data (8 unique + 1 duplicate + 1 invalid)
    contacts = [
        # 1. Alice – email matches TechCorp, folder 'personal' → should become 'business'
        {"contact_id": "ct_001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson",
         "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_001",
         "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "personal",
         "tags": ["vip"]},
        # 2. Bob – email matches ClientCo, folder 'business', tags empty → needs "needs-review"
        {"contact_id": "ct_002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith",
         "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "comp_002",
         "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "business",
         "tags": []},
        # 3. Carol – email matches StartupIO, folder 'personal' → should become 'business'
        {"contact_id": "ct_003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams",
         "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "comp_003",
         "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "personal",
         "tags": ["lead"]},
        # 4. David – email does not match company (Global Partners), tags null → needs "needs-review"
        {"contact_id": "ct_004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown",
         "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "comp_004",
         "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "inactive",
         "tags": None},
        # 5. Emma – email does not match company (VendorCo), tags empty → needs "needs-review"
        {"contact_id": "ct_005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis",
         "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp_005",
         "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business",
         "folder": "personal", "tags": []},
        # 6. Frank – email matches OldClient, folder 'business', tags present → no change
        {"contact_id": "ct_006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller",
         "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp_006",
         "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business",
         "folder": "business", "tags": ["important"]},
        # 7. Grace – email matches VendorCo, folder 'business', tags present → no change
        {"contact_id": "ct_007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson",
         "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp_005",
         "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "business",
         "tags": ["vip"]},
        # 8. Henry – email does not match company (TechCorp), tags empty → needs "needs-review"
        {"contact_id": "ct_008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor",
         "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "comp_001",
         "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "personal",
         "tags": []},
        # 9. Duplicate of Alice (same full_name, email, etc. but different contact_id) → should be removed
        {"contact_id": "ct_009", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson",
         "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_001",
         "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "personal",
         "tags": ["vip"]},
        # 10. Invalid record – missing contact_id (set to empty string)
        {"contact_id": "", "first_name": "Ghost", "last_name": "Record", "full_name": "Ghost Record",
         "email": "ghost@nowhere.com", "phone": "+1-555-0000", "company_id": "comp_001",
         "job_title": "Unknown", "department": "Unknown", "contact_type": "business", "folder": "personal",
         "tags": []},
    ]

    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # Bonus: create a distraction file
    os.makedirs("data/tags", exist_ok=True)
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump([], f)

    # Another distraction: old backup
    with open("data/old_backup.json", "w") as f:
        json.dump({"note": "this is an old export, ignore"}, f)

if __name__ == "__main__":
    build_env()
