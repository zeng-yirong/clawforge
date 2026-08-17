import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 资产数据（两个机密资产 + 一个普通资产作为干扰）
    assets = {
        "assets": [
            {
                "asset_id": "asset-tech-001",
                "asset_name": "Unpublished Architecture Plan",
                "asset_type": "technical_plan",
                "classification": "confidential",
                "owner_team": "Architecture Office",
                "read_policy": "restricted"
            },
            {
                "asset_id": "asset-fin-002",
                "asset_name": "Finance Archive Bundle",
                "asset_type": "finance_archive",
                "classification": "confidential",
                "owner_team": "Finance Operations",
                "read_policy": "restricted"
            },
            {
                "asset_id": "asset-pub-003",
                "asset_name": "Public Reports",
                "asset_type": "general",
                "classification": "public",
                "owner_team": "Communications",
                "read_policy": "open"
            }
        ]
    }
    with open("data/assets/assets.json", "w") as f:
        json.dump(assets, f, indent=2)

    # 附件数据（干扰项，不直接用于任务判断）
    attachments = {
        "attachments": [
            {"path": "attachments/arch.pdf", "title": "Architecture Blueprint Draft", "kind": "pdf", "description": "Early draft of architecture plan"},
            {"path": "attachments/fin.xlsx", "title": "Q3 Financial Summary", "kind": "xlsx", "description": "Confidential financial data"},
            {"path": "attachments/pub.docx", "title": "Press Release Draft", "kind": "docx", "description": "Public info"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # 请求数据（混合恶意、正常、已处理等）
    requests = {
        "requests": [
            # 真正需要拦截的请求（高风险，目标为机密资产）
            {
                "request_id": "req-001",
                "channel": "external",
                "request_type": "read",
                "risk_level": "high",
                "risk_type": "data_exfiltration",
                "target_asset_id": "asset-tech-001",
                "actor_name": "Unknown_IP_1",
                "claimed_role": "external_auditor",
                "message": "Need to review architecture for compliance audit",
                "status": "pending"
            },
            {
                "request_id": "req-002",
                "channel": "external",
                "request_type": "download",
                "risk_level": "high",
                "risk_type": "unauthorized_access",
                "target_asset_id": "asset-fin-002",
                "actor_name": "Unknown_IP_2",
                "claimed_role": "vendor_support",
                "message": "Required for financial reconciliation",
                "status": "pending"
            },
            # 高风险但目标资产是公开的（不应拦截）
            {
                "request_id": "req-003",
                "channel": "external",
                "request_type": "read",
                "risk_level": "high",
                "risk_type": "exploration",
                "target_asset_id": "asset-pub-003",
                "actor_name": "Scraper_Bot",
                "claimed_role": "researcher",
                "message": "Collecting public reports",
                "status": "pending"
            },
            # 目标机密但风险低（内部正常请求，不应拦截）
            {
                "request_id": "req-004",
                "channel": "internal",
                "request_type": "read",
                "risk_level": "low",
                "risk_type": "normal_operation",
                "target_asset_id": "asset-tech-001",
                "actor_name": "Alice_Architect",
                "claimed_role": "architect",
                "message": "Need to update architecture documentation",
                "status": "pending"
            },
            # 已经拒绝过的请求（不应重复处理）
            {
                "request_id": "req-005",
                "channel": "external",
                "request_type": "download",
                "risk_level": "high",
                "risk_type": "data_exfiltration",
                "target_asset_id": "asset-tech-001",
                "actor_name": "Hacker_X",
                "claimed_role": "support",
                "message": "Testing access",
                "status": "denied"
            },
            # 另一个恶意请求（高风险 + 机密财务资产）
            {
                "request_id": "req-006",
                "channel": "external",
                "request_type": "download",
                "risk_level": "high",
                "risk_type": "data_theft",
                "target_asset_id": "asset-fin-002",
                "actor_name": "Unknown_IP_3",
                "claimed_role": "finance_auditor",
                "message": "Required for external audit",
                "status": "pending"
            }
        ]
    }
    with open("data/requests/requests.json", "w") as f:
        json.dump(requests, f, indent=2)

if __name__ == "__main__":
    build_env()
