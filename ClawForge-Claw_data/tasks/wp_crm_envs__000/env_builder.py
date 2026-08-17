import json
import os

def build_env():
    # 确保基础目录存在
    os.makedirs("data/tags", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ========== 公司数据 ==========
    companies = [
        {
            "company_id": "comp_techcorp",
            "name": "TechCorp Industries",
            "industry": "Technology",
            "size": "enterprise",
            "website": "https://techcorp.com",
            "address": "1 Tech Way, Silicon Valley, CA",
            "phone": "+1-555-5000",
            "tags": ["tech", "partner"],
            "annual_revenue": "100M+",
            "customer_since": "2018-03-01",
            "account_manager": "ct_001"
        },
        {
            "company_id": "comp_clientco",
            "name": "ClientCo Operations",
            "industry": "Consulting",
            "size": "mid_market",
            "website": "https://clientco.com",
            "address": "2 Market St, New York, NY",
            "phone": "+1-555-1000",
            "tags": ["client"],
            "annual_revenue": "25M-50M",
            "customer_since": "2019-06-15",
            "account_manager": "ct_002"
        },
        {
            "company_id": "comp_startup",
            "name": "StartupIO",
            "industry": "Technology",
            "size": "small",
            "website": "https://startup.io",
            "address": "3 Innovation Blvd, Austin, TX",
            "phone": "+1-555-4000",
            "tags": ["startup"],
            "annual_revenue": "1M-5M",
            "customer_since": "2021-01-10",
            "account_manager": "ct_003"
        },
        {
            "company_id": "comp_oldclient",
            "name": "OldClient Services",
            "industry": "Consulting",
            "size": "small",
            "website": "https://oldclient.com",
            "address": "4 Legacy Rd, Boston, MA",
            "phone": "+1-555-3000",
            "tags": ["legacy"],
            "annual_revenue": "5M-10M",
            "customer_since": "2015-11-20",
            "account_manager": "ct_005"
        },
        {
            "company_id": "comp_vendor",
            "name": "VendorCo Supplies",
            "industry": "Manufacturing",
            "size": "mid_market",
            "website": "https://vendorco.com",
            "address": "5 Supply Ave, Chicago, IL",
            "phone": "+1-555-6000",
            "tags": ["vendor"],
            "annual_revenue": "50M-100M",
            "customer_since": "2017-08-05",
            "account_manager": "ct_007"
        }
    ]
    with open("data/companies.json", "w") as f:
        json.dump(companies, f, indent=2)

    # ========== 联系人数据（含干扰/脏数据） ==========
    contacts = [
        {
            "contact_id": "cont_001",
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
            "tags": ["vip", "business"]
        },
        {
            "contact_id": "cont_002",
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
            "tags": []
        },
        {
            "contact_id": "cont_003",
            "first_name": "Carol",
            "last_name": "Williams",
            "full_name": "Carol Williams",
            "email": "carol.w@startup.io",
            "phone": "+1-555-0103",
            "company_id": "comp_startup",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": ["leadership"]
        },
        {
            "contact_id": "cont_004",
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
            "tags": ["tech_partner"]  # 已有目标标签，不应再添加
        },
        {
            "contact_id": "cont_005",
            "first_name": "Emma",
            "last_name": "Davis",
            "full_name": "Emma Davis",
            "email": "emma.davis@partner.net",
            "phone": "+1-555-0105",
            "company_id": "comp_techcorp",
            "job_title": "Partnership Director",
            "department": "Business Development",
            "contact_type": "business",
            "folder": "business",
            "tags": ["partner"]   # 无tech_partner，需添加
        },
        {
            "contact_id": "cont_006",
            "first_name": "Frank",
            "last_name": "Miller",
            "full_name": "Frank Miller",
            "email": "frank.m@oldclient.com",
            "phone": "+1-555-0106",
            "company_id": "comp_oldclient",
            "job_title": "VP Engineering",
            "department": "Engineering",
            "contact_type": "business",
            "folder": "business",
            "tags": []
        },
        {
            "contact_id": "cont_007",
            "first_name": "Grace",
            "last_name": "Wilson",
            "full_name": "Grace Wilson",
            "email": "grace.wilson@vendor.co",
            "phone": "+1-555-0107",
            "company_id": "comp_vendor",
            "job_title": "Procurement Manager",
            "department": "Operations",
            "contact_type": "business",
            "folder": "business",
            "tags": ["vendor"]
        },
        {
            "contact_id": "cont_008",
            "first_name": "Henry",
            "last_name": "Taylor",
            "full_name": "Henry Taylor",
            "email": "henry.t@bigcorp.com",
            "phone": "+1-555-0108",
            "company_id": "comp_techcorp",
            "job_title": "CEO",
            "department": "Leadership",
            "contact_type": "business",
            "folder": "business",
            "tags": ["tech_partner", "vip"]  # 已有，不应添加
        },
        # 脏数据：company_id 不存在于公司列表，应被忽略（不参与筛选）
        {
            "contact_id": "cont_009",
            "first_name": "Ivy",
            "last_name": "Clark",
            "full_name": "Ivy Clark",
            "email": "ivy@unknown.com",
            "phone": "+1-555-0109",
            "company_id": "comp_unknown",
            "job_title": "Consultant",
            "department": "Business Development",
            "contact_type": "business",
            "folder": "business",
            "tags": []
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ========== 标签定义 ==========
    tag_definitions = [
        {
            "tag_id": "tag_vip",
            "name": "vip",
            "color": "gold",
            "description": "Very Important Person",
            "category": "priority"
        },
        {
            "tag_id": "tag_tech_partner",
            "name": "tech_partner",
            "color": "blue",
            "description": "Technology partner",
            "category": "relationship"
        },
        {
            "tag_id": "tag_business",
            "name": "business",
            "color": "green",
            "description": "Business contact",
            "category": "status"
        },
        {
            "tag_id": "tag_leadership",
            "name": "leadership",
            "color": "purple",
            "description": "Leadership role",
            "category": "role"
        },
        {
            "tag_id": "tag_partner",
            "name": "partner",
            "color": "orange",
            "description": "Partner contact",
            "category": "relationship"
        },
        {
            "tag_id": "tag_vendor",
            "name": "vendor",
            "color": "red",
            "description": "Vendor contact",
            "category": "relationship"
        }
    ]
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump(tag_definitions, f, indent=2)

if __name__ == "__main__":
    build_env()
