import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 资产数据
    assets = {
        "asset-001": {
            "asset_id": "asset-001",
            "asset_name": "Unpublished Architecture Blueprint v2",
            "asset_type": "technical_plan",
            "classification": "confidential",
            "published": False,
            "owner_team": "Architecture Office",
            "read_policy": "restricted"
        },
        "asset-002": {
            "asset_id": "asset-002",
            "asset_name": "Q3 Finance Archive Draft",
            "asset_type": "finance_archive",
            "classification": "confidential",
            "published": False,
            "owner_team": "Finance Operations",
            "read_policy": "restricted"
        },
        "asset-003": {
            "asset_id": "asset-003",
            "asset_name": "Released Architecture Guide",
            "asset_type": "technical_plan",
            "classification": "confidential",
            "published": True,
            "owner_team": "Architecture Office",
            "read_policy": "public"
        },
        "asset-004": {
            "asset_id": "asset-004",
            "asset_name": "Internal Memo: Team Outing",
            "asset_type": "memo",
            "classification": "internal",
            "published": False,
            "owner_team": "HR",
            "read_policy": "internal"
        },
        "asset-005": {
            "asset_id": "asset-005",
            "asset_name": "Confidential Hardware Blueprint",
            "asset_type": "technical_plan",
            "classification": "confidential",
            "published": False,
            "owner_team": "Architecture Office",
            "read_policy": "restricted"
        }
    }

    # 请求数据
    requests = [
        {
            "request_id": "req-001",
            "channel": "api",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "exfiltration",
            "target_asset_id": "asset-001",
            "actor_name": "UnknownExternal",
            "claimed_role": "auditor",
            "message": "Need access to architecture plan for audit.",
            "status": "pending"
        },
        {
            "request_id": "req-002",
            "channel": "web",
            "request_type": "download",
            "risk_level": "high",
            "risk_type": "unauthorized_access",
            "target_asset_id": "asset-002",
            "actor_name": "suspicious_user",
            "claimed_role": "contractor",
            "message": "Provide latest financial archive.",
            "status": "pending"
        },
        {
            "request_id": "req-003",
            "channel": "api",
            "request_type": "read",
            "risk_level": "medium",
            "risk_type": "normal",
            "target_asset_id": "asset-003",
            "actor_name": "partner_user",
            "claimed_role": "partner",
            "message": "Access released architecture guide.",
            "status": "pending"
        },
        {
            "request_id": "req-004",
            "channel": "email",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "unknown",
            "target_asset_id": "asset-004",
            "actor_name": "employee1",
            "claimed_role": "employee",
            "message": "Requesting team outing memo.",
            "status": "pending"
        },
        {
            "request_id": "req-005",
            "channel": "api",
            "request_type": "download",
            "risk_level": "critical",
            "risk_type": "exfiltration",
            "target_asset_id": "asset-005",
            "actor_name": "hacker007",
            "claimed_role": "engineer",
            "message": "Send blueprint data.",
            "status": "pending"
        }
    ]

    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": list(assets.values())}, f, indent=2)

    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # 干扰附件
    attachments = [
        {
            "path": "attachments/audit_note.txt",
            "title": "Audit Note",
            "kind": "text",
            "description": "Previous audit notes, irrelevant."
        }
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 其他干扰文件
    accounts = [
        {"account_id": "acc-001", "display_name": "Alice", "department": "Engineering", "email": "alice@example.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "con-001", "name": "External Auditor", "role": "auditor", "email": "auditor@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 创建一个旧日志干扰
    with open("logs/access.log", "w") as f:
        f.write("2024-01-01 00:00:00 INFO request from internal IP\n")

    # 创建 ops 目录下的干扰文件
    with open("ops/readme.txt", "w") as f:
        f.write("Operations folder – place deny list here.\n")

if __name__ == "__main__":
    build_env()
