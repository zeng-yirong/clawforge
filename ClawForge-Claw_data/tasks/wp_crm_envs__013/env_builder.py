import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/reminders", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- 联系人 ----------
    contacts = [
        {"contact_id": "ct_001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson",
         "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_001",
         "job_title": "CTO", "department": "Engineering", "contact_type": "business", "folder": "business",
         "tags": ["tag_eng", "tag_priority"]},
        {"contact_id": "ct_002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith",
         "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "comp_002",
         "job_title": "CEO", "department": "Leadership", "contact_type": "business", "folder": "business",
         "tags": ["tag_vip_2"]},  # 干扰：已经有一个小写 vip 标签
        {"contact_id": "ct_003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams",
         "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "comp_004",
         "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business", "folder": "business",
         "tags": []},
        {"contact_id": "ct_004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown",
         "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "comp_003",
         "job_title": "IT Manager", "department": "IT", "contact_type": "personal", "folder": "personal",
         "tags": ["tag_personal"]},
        {"contact_id": "ct_005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis",
         "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp_005",
         "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business",
         "folder": "business", "tags": ["tag_partner"]},
        {"contact_id": "ct_006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller",
         "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp_003",
         "job_title": "Account Manager", "department": "Sales", "contact_type": "business", "folder": "inactive",
         "tags": []},
        {"contact_id": "ct_007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson",
         "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp_006",
         "job_title": "Procurement Manager", "department": "Operations", "contact_type": "business", "folder": "business",
         "tags": []},  # 目标联系人，初始无标签
        {"contact_id": "ct_008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor",
         "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "comp_002",
         "job_title": "IT Manager", "department": "IT", "contact_type": "business", "folder": "business",
         "tags": ["tag_it"]}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---------- 公司 ----------
    companies = [
        {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise",
         "website": "https://techcorp.com", "address": "1 Tech Ave", "phone": "+1-555-5000",
         "tags": ["tag_tech"], "annual_revenue": "100M+", "customer_since": "2018-01-01", "account_manager": "ct_001"},
        {"company_id": "comp_002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market",
         "website": "https://clientco.com", "address": "2 Client Rd", "phone": "+1-555-1000",
         "tags": ["tag_client"], "annual_revenue": "25M-50M", "customer_since": "2020-06-15", "account_manager": "ct_002"},
        {"company_id": "comp_003", "name": "OldClient Services", "industry": "Manufacturing", "size": "small",
         "website": "https://oldclient.com", "address": "3 Old St", "phone": "+1-555-3000",
         "tags": ["tag_old"], "annual_revenue": "1M-5M", "customer_since": "2015-03-20", "account_manager": "ct_005"},
        {"company_id": "comp_004", "name": "StartupIO", "industry": "Technology", "size": "small",
         "website": "https://startup.io", "address": "4 Startup Ln", "phone": "+1-555-4000",
         "tags": ["tag_startup"], "annual_revenue": "5M-10M", "customer_since": "2023-09-01", "account_manager": "ct_003"},
        {"company_id": "comp_005", "name": "Global Partners LLC", "industry": "Logistics", "size": "mid_market",
         "website": "https://globalpartners.com", "address": "5 Global Dr", "phone": "+1-555-2000",
         "tags": ["tag_global"], "annual_revenue": "50M-100M", "customer_since": "2019-11-11", "account_manager": "ct_007"},
        {"company_id": "comp_006", "name": "VendorCo Supplies", "industry": "Logistics", "size": "mid_market",
         "website": "https://vendorco.com", "address": "6 Vendor Way", "phone": "+1-555-6000",
         "tags": ["tag_logistics"], "annual_revenue": "25M-50M", "customer_since": "2019-03-01", "account_manager": "ct_007"}
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

    # ---------- 标签定义 ----------
    tag_definitions = [
        {"tag_id": "tag_vip_1", "name": "VIP", "color": "#FFD700", "description": "Very Important Person",
         "category": "priority"},  # 正确的VIP标签
        {"tag_id": "tag_vip_2", "name": "vip", "color": "#C0C0C0", "description": "Vendor Important Person (deprecated)",
         "category": "priority"},  # 干扰：小写vip，过期标签
        {"tag_id": "tag_eng", "name": "Engineering", "color": "#00BFFF", "description": "Engineering department",
         "category": "role"},
        {"tag_id": "tag_priority", "name": "Priority", "color": "#FF4500", "description": "High priority contact",
         "category": "priority"},
        {"tag_id": "tag_personal", "name": "Personal", "color": "#32CD32", "description": "Personal contact",
         "category": "relationship"},
        {"tag_id": "tag_partner", "name": "Partner", "color": "#8A2BE2", "description": "Business partner",
         "category": "relationship"},
        {"tag_id": "tag_it", "name": "IT Support", "color": "#696969", "description": "IT support contact",
         "category": "role"},
        {"tag_id": "tag_tech", "name": "Tech", "color": "#1E90FF", "description": "Technology sector", "category": "industry"},
        {"tag_id": "tag_client", "name": "Client", "color": "#FF69B4", "description": "Client company", "category": "relationship"},
        {"tag_id": "tag_old", "name": "Old", "color": "#A0522D", "description": "Old client", "category": "status"},
        {"tag_id": "tag_startup", "name": "Startup", "color": "#00FA9A", "description": "Startup company",
         "category": "industry"},
        {"tag_id": "tag_global", "name": "Global", "color": "#4682B4", "description": "Global partner", "category": "relationship"},
        {"tag_id": "tag_logistics", "name": "Logistics", "color": "#DAA520", "description": "Logistics industry",
         "category": "industry"}
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_definitions}, f, indent=2)

    # ---------- 空的提醒文件（保持结构完整） ----------
    reminders = []
    with open("data/reminders/reminders.json", "w") as f:
        json.dump({"reminders": reminders}, f, indent=2)

if __name__ == "__main__":
    build_env()
