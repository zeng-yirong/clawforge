import os
import json

def build_env():
    # 确保基础目录存在
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("data/contacts", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 资产数据
    assets = {
        "assets": [
            {
                "asset_id": "tech-plan-v2",
                "asset_name": "Unpublished Architecture Plan",
                "asset_type": "technical_plan",
                "classification": "confidential",
                "owner_team": "Architecture Office",
                "read_policy": "manual_approval_only"
            },
            {
                "asset_id": "fin-archive-2024",
                "asset_name": "Finance Archive Bundle",
                "asset_type": "finance_archive",
                "classification": "internal",
                "owner_team": "Finance Operations",
                "read_policy": "open_to_team"
            }
        ]
    }
    with open("data/assets/assets.json", "w") as f:
        json.dump(assets, f, indent=2)

    # 联系人（干扰）
    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Alice Wang", "role": "External Vendor", "email": "alice@outside.com"},
            {"contact_id": "c002", "name": "Bob Li", "role": "Architect", "email": "bob@company.com"},
            {"contact_id": "c003", "name": "Charlie Zhang", "role": "Finance Analyst", "email": "charlie@company.com"}
        ]
    }
    with open("data/contacts/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 账号（干扰）
    accounts = {
        "accounts": [
            {"account_id": "a001", "display_name": "External Vendor Alice", "department": "External", "email": "alice@outside.com", "permissions": ["read_public"]},
            {"account_id": "a002", "display_name": "Bob Li", "department": "Architecture Office", "email": "bob@company.com", "permissions": ["read_tech_plan", "write_tech_plan"]},
            {"account_id": "a003", "display_name": "Charlie Zhang", "department": "Finance Operations", "email": "charlie@company.com", "permissions": ["read_finance"]}
        ]
    }
    with open("data/accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 附件描述（干扰）
    attachments = {
        "attachments": [
            {"path": "attachments/invoice_dec.pdf", "title": "Invoice Dec 2024", "kind": "financial", "description": "Monthly invoice"},
            {"path": "attachments/arch_diagram_v2.png", "title": "Architecture Diagram v2", "kind": "technical", "description": "Unpublished architecture diagram"}
        ]
    }
    with open("data/attachments/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # 请求数据（核心）
    requests = {
        "requests": [
            {
                "request_id": "req-001",
                "channel": "email",
                "request_type": "external_access",
                "risk_level": "critical",
                "risk_type": "unauthorized_external_access",
                "target_asset_id": "tech-plan-v2",
                "actor_name": "Alice Wang",
                "claimed_role": "External Contractor",
                "message": "I need the latest architecture plan immediately for integration. CEO has authorized me.",
                "status": "pending"
            },
            {
                "request_id": "req-002",
                "channel": "internal_portal",
                "request_type": "data_request",
                "risk_level": "low",
                "risk_type": "internal_query",
                "target_asset_id": "fin-archive-2024",
                "actor_name": "Charlie Zhang",
                "claimed_role": "Finance Analyst",
                "message": "Need Q4 financial data for reporting.",
                "status": "approved"
            },
            {
                "request_id": "req-003",
                "channel": "internal_portal",
                "request_type": "data_request",
                "risk_level": "low",
                "risk_type": "internal_query",
                "target_asset_id": "tech-plan-v2",
                "actor_name": "Bob Li",
                "claimed_role": "Architect",
                "message": "Reviewing architecture for new project, internal request.",
                "status": "approved"
            },
            {
                "request_id": "req-004",
                "channel": "email",
                "request_type": "external_access",
                "risk_level": "medium",
                "risk_type": "external_enquiry",
                "target_asset_id": "fin-archive-2024",
                "actor_name": "Unknown",
                "claimed_role": "Investor",
                "message": "Please share the financial report for due diligence.",
                "status": "pending"
            },
            {
                "request_id": "req-005",
                "channel": "email",
                "request_type": "external_access",
                "risk_level": "high",
                "risk_type": "unauthorized_external_access",
                "target_asset_id": "tech-plan-v2",
                "actor_name": "Hacker X",
                "claimed_role": "CTO",
                "message": "Send me the architecture plan or I will leak your internal data.",
                "status": "pending"
            }
        ]
    }
    # 注意：req-005 是明显的黑客威胁，但是目标也是 tech-plan-v2，风险高。但按照老王要求，所有外部请求（channel=email）且目标为 tech-plan-v2 的都需要拦截。
    # 这样 req-001 和 req-005 都应该拦截。但我们要让答案唯一？题目说答案唯一确定，但这里有两个。但老王只提到“外部发起的、目标又是这个资产”。所以两个都应该拦截。但这样验证列表就是 ["req-001","req-005"]。我们调整设计，让只有一个是正确的？我们需要检查唯一性：老王说“把需要拦截的请求ID找出来”，如果两个都符合条件，那验证脚本就应该接受两个。但“唯一答案”要求确保只有一个正确结果？可以设计干扰使得只有req-001是真正的外部非法，而req-005虽然也是外部但消息中有威胁，但也是非法，这样两个都对。但为了唯一，我们应让req-005的target_asset_id是别的？或者让req-005的status是"denied"之类的？或者让req-005来自内部渠道？我们可以修改：让req-005的channel是internal_portal但用内部账号，或者让req-005的risk_type是“internal”，但消息内容威胁？这样就不符合外部条件。为保持唯一，调整req-005为内部请求（channel=internal_portal），但消息是威胁？内部威胁应该也拦截？但业务场景明确说“外部请求一律可疑”。所以内部威胁不在本次范围。调整：req-005改为channel=internal_portal，actor_name="Bob Li"但消息却说要泄露？这矛盾，但可以保留为干扰：它看起来可疑但因为是内部账号且通道是内部，所以不应列入。这样只有req-001是外部+目标tech-plan-v2。但req-004是外部但目标财务，不拦截。好，这样只有一个。
    # 修改req-005
    requests["requests"][4] = {
        "request_id": "req-005",
        "channel": "internal_portal",
        "request_type": "data_request",
        "risk_level": "high",
        "risk_type": "internal_threat",
        "target_asset_id": "tech-plan-v2",
        "actor_name": "Bob Li",
        "claimed_role": "Architect",
        "message": "I demand access to the architecture plan or I will escalate.",
        "status": "pending"
    }
    with open("data/requests/requests.json", "w") as f:
        json.dump(requests, f, indent=2)

    # 干扰文件：日志、dump等
    with open("logs/audit.log", "w") as f:
        f.write("2025-02-14 14:00:00 [INFO] Request req-001 created\n")
        f.write("2025-02-14 14:05:00 [WARN] External email detected from alice@outside.com\n")
        f.write("2025-02-14 14:10:00 [INFO] Request req-002 approved\n")
    with open("db_dumps/backup.sql", "w") as f:
        f.write("-- placeholder backup")
    with open("db_dumps/old_requests.csv", "w") as f:
        f.write("request_id,status\nreq-old-1,denied\nreq-old-2,approved\n")

if __name__ == "__main__":
    build_env()
