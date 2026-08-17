import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 创建一个干扰文件在 ops 下
    with open("ops/old_report.json", "w") as f:
        json.dump({"note": "this is old"}, f)

    # 写入 accounts.json (简化但符合 schema)
    with open("data/accounts.json", "w") as f:
        json.dump({
            "accounts": [
                {
                    "account_id": "acc_001",
                    "display_name": "Main Account",
                    "email": "admin@company.com",
                    "default_tag_color": "#336699",
                    "auto_tagging_enabled": True,
                    "birthday_reminders_enabled": True,
                    "reminder_days_before": 3,
                    "available_folders": ["business", "personal", "archive", "inactive"]
                }
            ]
        }, f, indent=2)

    # 写入 companies.json
    companies = [
        {"company_id": "comp_001", "name": "TechCorp Industries", "industry": "Technology", "size": "enterprise",
         "website": "https://techcorp.com", "address": "123 Tech St", "phone": "+1-555-1000",
         "tags": ["partner", "vip"], "annual_revenue": "100M+", "customer_since": "2018-01-01",
         "account_manager": "ct_001"},
        {"company_id": "comp_002", "name": "ClientCo Operations", "industry": "Consulting", "size": "mid_market",
         "website": "https://clientco.com", "address": "456 Client Ave", "phone": "+1-555-2000",
         "tags": ["premium"], "annual_revenue": "25M-50M", "customer_since": "2019-06-15",
         "account_manager": "ct_002"},
        {"company_id": "comp_003", "name": "StartupIO", "industry": "Technology", "size": "small",
         "website": "https://startup.io", "address": "789 Start St", "phone": "+1-555-3000",
         "tags": ["tech_partner"], "annual_revenue": "1M-5M", "customer_since": "2024-03-01",
         "account_manager": "ct_005"},
        {"company_id": "comp_004", "name": "OldClient Services", "industry": "Manufacturing", "size": "mid_market",
         "website": "https://oldclient.com", "address": "321 Old Rd", "phone": "+1-555-4000",
         "tags": ["legacy"], "annual_revenue": "5M-10M", "customer_since": "2015-11-20",
         "account_manager": "ct_003"}
    ]
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

    # 写入 contacts.json，包含干扰项
    contacts = [
        {"contact_id": "c001", "first_name": "Alice", "last_name": "Johnson", "full_name": "Alice Johnson",
         "email": "alice.johnson@techcorp.com", "phone": "+1-555-0101", "company_id": "comp_001",
         "job_title": "CEO", "department": "Leadership", "contact_type": "business",
         "folder": "business", "tags": ["vip"]},
        # 需要修正：c002 (StartupIO, personal)
        {"contact_id": "c002", "first_name": "Bob", "last_name": "Smith", "full_name": "Bob Smith",
         "email": "bob.smith@clientco.com", "phone": "+1-555-0102", "company_id": "comp_003",
         "job_title": "CTO", "department": "Engineering", "contact_type": "business",
         "folder": "personal", "tags": []},
        # 已经正确：c003 (StartupIO, business) 不处理
        {"contact_id": "c003", "first_name": "Carol", "last_name": "Williams", "full_name": "Carol Williams",
         "email": "carol.w@startup.io", "phone": "+1-555-0103", "company_id": "comp_003",
         "job_title": "VP Engineering", "department": "Engineering", "contact_type": "business",
         "folder": "business", "tags": ["partner"]},
        # 干扰：其他公司 personal
        {"contact_id": "c004", "first_name": "David", "last_name": "Brown", "full_name": "David Brown",
         "email": "david.brown@email.com", "phone": "+1-555-0104", "company_id": "comp_002",
         "job_title": "IT Manager", "department": "IT", "contact_type": "business",
         "folder": "personal", "tags": []},
        # 需要修正：c005 (StartupIO, personal)
        {"contact_id": "c005", "first_name": "Emma", "last_name": "Davis", "full_name": "Emma Davis",
         "email": "emma.davis@partner.net", "phone": "+1-555-0105", "company_id": "comp_003",
         "job_title": "Partnership Director", "department": "Business Development", "contact_type": "business",
         "folder": "personal", "tags": ["new"]},
        # 干扰：其他公司 inactive
        {"contact_id": "c006", "first_name": "Frank", "last_name": "Miller", "full_name": "Frank Miller",
         "email": "frank.m@oldclient.com", "phone": "+1-555-0106", "company_id": "comp_004",
         "job_title": "Account Manager", "department": "Sales", "contact_type": "business",
         "folder": "inactive", "tags": []},
        # 干扰：其他公司 personal
        {"contact_id": "c007", "first_name": "Grace", "last_name": "Wilson", "full_name": "Grace Wilson",
         "email": "grace.wilson@vendor.co", "phone": "+1-555-0107", "company_id": "comp_002",
         "job_title": "Procurement Manager", "department": "Operations", "contact_type": "personal",
         "folder": "personal", "tags": []},
        # 干扰：其他公司 business
        {"contact_id": "c008", "first_name": "Henry", "last_name": "Taylor", "full_name": "Henry Taylor",
         "email": "henry.t@bigcorp.com", "phone": "+1-555-0108", "company_id": "comp_004",
         "job_title": "CEO", "department": "Leadership", "contact_type": "business",
         "folder": "business", "tags": []}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 写入 tag_definitions.json，包含 tech_partner
    tag_defs = [
        {"tag_id": "tag_001", "name": "vip", "color": "#FFD700", "description": "Very Important Person", "category": "priority"},
        {"tag_id": "tag_002", "name": "partner", "color": "#00BFFF", "description": "Strategic Partner", "category": "relationship"},
        {"tag_id": "tag_003", "name": "tech_partner", "color": "#32CD32", "description": "Technology Partner", "category": "industry"},
        {"tag_id": "tag_004", "name": "new", "color": "#FF69B4", "description": "New contact", "category": "status"},
        {"tag_id": "tag_005", "name": "premium", "color": "#8A2BE2", "description": "Premium client", "category": "priority"},
        {"tag_id": "tag_006", "name": "legacy", "color": "#A9A9A9", "description": "Legacy client", "category": "status"}
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tag_defs}, f, indent=2)

    # 额外干扰文件
    with open("data/backup_contacts.json", "w") as f:
        json.dump({"note": "backup"}, f)

if __name__ == "__main__":
    build_env()
