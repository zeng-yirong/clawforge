import os
import json

def build_env():
    # Prepare directories
    os.makedirs("data/tags", exist_ok=True)

    # --- companies.json ---
    companies = [
        {
            "company_id": "comp_clientco",
            "name": "ClientCo Operations",
            "industry": "Consulting",
            "size": "mid_market",
            "website": "https://clientco.com",
            "address": "123 Main St, City",
            "phone": "+1-555-1000",
            "tags": [],
            "annual_revenue": "5M-10M",
            "customer_since": "2020-01-15",
            "account_manager": "ct_001"
        },
        {
            "company_id": "comp_global",
            "name": "Global Partners LLC",
            "industry": "Consulting",
            "size": "enterprise",
            "website": "https://globalpartners.com",
            "address": "456 Oak Ave, Town",
            "phone": "+1-555-2000",
            "tags": [],
            "annual_revenue": "50M-100M",
            "customer_since": "2019-06-01",
            "account_manager": "ct_002"
        },
        {
            "company_id": "comp_techcorp",
            "name": "TechCorp Industries",
            "industry": "Technology",
            "size": "enterprise",
            "website": "https://techcorp.com",
            "address": "789 Tech Blvd, Silicon Valley",
            "phone": "+1-555-3000",
            "tags": [],
            "annual_revenue": "100M+",
            "customer_since": "2015-03-20",
            "account_manager": "ct_005"
        },
        {
            "company_id": "comp_oldclient",
            "name": "OldClient Services",
            "industry": "Manufacturing",
            "size": "small",
            "website": "https://oldclient.com",
            "address": "321 Factory Rd, Industrial Park",
            "phone": "+1-555-4000",
            "tags": [],
            "annual_revenue": "1M-5M",
            "customer_since": "2018-11-11",
            "account_manager": "ct_003"
        }
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

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
            "job_title": "CTO",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": ["tech"]
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
            "company_id": "comp_global",
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
            "company_id": "comp_oldclient",
            "job_title": "Procurement Manager",
            "department": "Operations",
            "contact_type": "personal",
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
            "company_id": None,
            "job_title": "Partnership Director",
            "department": "Business Development",
            "contact_type": "personal",
            "folder": "personal",
            "tags": []
        },
        {
            "contact_id": "ct_006",
            "first_name": "Frank",
            "last_name": "Miller",
            "full_name": "Frank Miller",
            "email": "frank.m@oldclient.com",
            "phone": "+1-555-0106",
            "company_id": "comp_oldclient",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "inactive",
            "tags": []
        },
        {
            "contact_id": "ct_007",
            "first_name": "Grace",
            "last_name": "Wilson",
            "full_name": "Grace Wilson",
            "email": "grace.wilson@vendor.co",
            "phone": "+1-555-0107",
            "company_id": "comp_techcorp",
            "job_title": "IT Manager",
            "department": "IT",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vip"]
        },
        {
            "contact_id": "ct_008",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "email": "john.doe@globalpartners.com",
            "phone": "+1-555-0108",
            "company_id": "comp_global",
            "job_title": "Partner",
            "department": "Business Development",
            "contact_type": "business",
            "folder": "business",
            "tags": []
        },
        # 脏数据：缺少company_id
        {
            "contact_id": "ct_009",
            "first_name": "NoCompany",
            "last_name": "Person",
            "full_name": "NoCompany Person",
            "email": "no@company.com",
            "phone": "+1-555-0109",
            "job_title": "Temp",
            "department": "Temp",
            "contact_type": "personal",
            "folder": "personal",
            "tags": []
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # --- tag_definitions.json ---
    tag_defs = [
        {
            "tag_id": "t_vip",
            "name": "vip",
            "color": "#FF0000",
            "description": "Very Important Person",
            "category": "priority"
        },
        {
            "tag_id": "t_tech",
            "name": "tech",
            "color": "#00FF00",
            "description": "Technology related",
            "category": "industry"
        },
        {
            "tag_id": "t_old",
            "name": "old",
            "color": "#CCCCCC",
            "description": "Legacy contact",
            "category": "status"
        }
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_defs}, f, indent=2)

if __name__ == "__main__":
    build_env()
