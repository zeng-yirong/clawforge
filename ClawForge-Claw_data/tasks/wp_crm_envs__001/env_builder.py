import os, json, random

def build_env():
    # 公司数据
    companies = [
        {"company_id": "comp_001", "name": "TechCorp Industries", "account_manager": "ct_001"},
        {"company_id": "comp_002", "name": "Global Partners LLC", "account_manager": "ct_002"},
        {"company_id": "comp_003", "name": "OldClient Services", "account_manager": "ct_005"},
        {"company_id": "comp_004", "name": "ClientCo Operations", "account_manager": "ct_003"},
    ]
    os.makedirs("data", exist_ok=True)
    with open("data/companies.json", "w") as f:
        json.dump({"companies": companies}, f, indent=2)

    # 联系人数据（含干扰：不同公司、不同folder、重复名字的诱饵）
    contacts = [
        {"contact_id": "c001", "first_name": "Alice", "last_name": "Johnson",
         "email": "alice.j@techcorp.com", "company_id": "comp_001",
         "folder": "business", "tags": ["business"], "contact_type": "business"},
        {"contact_id": "c002", "first_name": "Bob", "last_name": "Smith",
         "email": "bob.smith@oldclient.com", "company_id": "comp_003",
         "folder": "business", "tags": ["personal"], "contact_type": "business"},
        {"contact_id": "c003", "first_name": "Carol", "last_name": "Williams",
         "email": "carol.w@oldclient.com", "company_id": "comp_003",
         "folder": "business", "tags": ["personal"], "contact_type": "business"},
        {"contact_id": "c004", "first_name": "David", "last_name": "Brown",
         "email": "david.brown@oldclient.com", "company_id": "comp_003",
         "folder": "inactive", "tags": ["inactive"], "contact_type": "business"},
        {"contact_id": "c005", "first_name": "Emma", "last_name": "Davis",
         "email": "emma.davis@globalpartners.com", "company_id": "comp_002",
         "folder": "business", "tags": ["business"], "contact_type": "business"},
        {"contact_id": "c006", "first_name": "Frank", "last_name": "Miller",
         "email": "frank.m@oldclient.com", "company_id": "comp_003",
         "folder": "personal", "tags": ["personal"], "contact_type": "personal"},
        # 干扰：另一个叫David Brown但不同公司，不应被排除
        {"contact_id": "c007", "first_name": "David", "last_name": "Brown",
         "email": "david.brown.other@clientco.com", "company_id": "comp_004",
         "folder": "business", "tags": ["business"], "contact_type": "business"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 标签定义（供参考，agent 可读取也可忽略）
    tags = [
        {"tag_id": "t01", "name": "business", "category": "relationship"},
        {"tag_id": "t02", "name": "personal", "category": "relationship"},
        {"tag_id": "t03", "name": "vip", "category": "priority"},
        {"tag_id": "t04", "name": "inactive", "category": "status"},
    ]
    os.makedirs("data/tags", exist_ok=True)
    with open("data/tags/tag_definitions.json", "w") as f:
        json.dump({"tag_definitions": tags}, f, indent=2)

    # 空目录干扰
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
