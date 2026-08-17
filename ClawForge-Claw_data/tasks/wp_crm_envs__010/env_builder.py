import os
import json

def build_env():
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- companies ----------
    companies = {
        "companies": [
            {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise", "website": "https://techcorp.com", "address": "123 Tech St", "phone": "+1-555-5000", "tags": ["tech"], "annual_revenue": "100M+", "customer_since": "2018-01-15", "account_manager": "ct_001"},
            {"company_id": "comp_002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market", "website": "https://clientco.com", "address": "456 Client Ave", "phone": "+1-555-1000", "tags": ["consulting"], "annual_revenue": "25M-50M", "customer_since": "2020-03-20", "account_manager": "ct_002"},
            {"company_id": "comp_003", "name": "OldClient Services", "industry": "Retail", "size": "small", "website": "https://oldclient.com", "address": "789 Old St", "phone": "+1-555-3000", "tags": ["old"], "annual_revenue": "5M-10M", "customer_since": "2015-06-01", "account_manager": "ct_003"},
            {"company_id": "comp_004", "name": "StartupIO", "industry": "Technology", "size": "small", "website": "https://startup.io", "address": "321 Startup Blvd", "phone": "+1-555-4000", "tags": ["startup"], "annual_revenue": "1M-5M", "customer_since": "2022-11-10", "account_manager": "ct_005"},
            {"company_id": "comp_005", "name": "Global Partners LLC", "industry": "Logistics", "size": "enterprise", "website": "https://globalpartners.com", "address": "654 Global Dr", "phone": "+1-555-2000", "tags": ["logistics"], "annual_revenue": "50M-100M", "customer_since": "2019-08-05", "account_manager": "ct_007"},
        ]
    }
    with open("data/companies.json", "w") as f:
        json.dump(companies, f, indent=2)

    # ---------- contacts (with distractors) ----------
    contacts = {
        "contacts": [
            # --- 5 contacts belonging to OldClient Services (comp_003) ---
            {"contact_id": "ct_101", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller", "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp_003", "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "inactive", "tags": ["churn_risk"]},
            {"contact_id": "ct_102", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson", "email": "grace.wilson@oldclient.com", "phone": "+1-555-0107", "company_id": "comp_003", "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business", "folder": "business", "tags": []},
            {"contact_id": "ct_103", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor", "email": "henry.t@oldclient.com", "phone": "+1-555-0108", "company_id": "comp_003", "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "personal", "tags": ["vip"]},
            {"contact_id": "ct_104", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson", "email": "alice.johnson@oldclient.com", "phone": "+1-555-0101", "company_id": "comp_003", "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "inactive", "tags": []},
            {"contact_id": "ct_105", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith", "email": "bob.smith@oldclient.com", "phone": "+1-555-0102", "company_id": "comp_003", "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": ["old_client"]},
            # --- Distractors ---
            # Same company but wrong company_id
            {"contact_id": "ct_106", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams", "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "comp_999", "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "business", "tags": []},
            # Different company, name similar
            {"contact_id": "ct_107", "first_name": "David", "last_name": "Brown", "full_name": "David Brown", "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "comp_001", "job_title": "IT Manager", "department": "IT", "contact_type": "personal", "folder": "personal", "tags": ["vip"]},
            # Already inactive but not from OldClient
            {"contact_id": "ct_108", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis", "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp_005", "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business", "folder": "inactive", "tags": []},
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ---------- tag_definitions (no churn_risk initially) ----------
    tag_definitions = {
        "tag_definitions": [
            {"tag_id": "tag_vip", "name": "vip", "color": "#FFD700", "description": "Very Important Person", "category": "priority"},
            {"tag_id": "tag_old_client", "name": "old_client", "color": "#808080", "description": "Previously loyal customer", "category": "relationship"},
            {"tag_id": "tag_tech", "name": "tech", "color": "#00BFFF", "description": "Technology related", "category": "industry"},
            {"tag_id": "tag_startup", "name": "startup", "color": "#32CD32", "description": "Startup company", "category": "industry"},
        ]
    }
    with open("data/tag_definitions.json", "w") as f:
        json.dump(tag_definitions, f, indent=2)

if __name__ == "__main__":
    build_env()
