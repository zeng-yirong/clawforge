import os
import json
import datetime

def build_env():
    # --- 创建目录结构 ---
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # data/attachments.json 也建一个

    # --- 资产数据 ---
    assets = {
        "asset-001": {
            "asset_id": "asset-001",
            "asset_name": "Unpublished Architecture Plan - V2",
            "asset_type": "technical_plan",
            "classification": "unpublished",
            "owner_team": "Architecture Office",
            "read_policy": "strict"
        },
        "asset-002": {
            "asset_id": "asset-002",
            "asset_name": "Finance Archive Bundle Q3",
            "asset_type": "finance_archive",
            "classification": "unpublished",
            "owner_team": "Finance Operations",
            "read_policy": "strict"
        },
        "asset-003": {
            "asset_id": "asset-003",
            "asset_name": "Public Meeting Notes",
            "asset_type": "general_report",
            "classification": "public",
            "owner_team": "Communications",
            "read_policy": "open"
        },
        "asset-004": {
            "asset_id": "asset-004",
            "asset_name": "Old Architecture Blueprint (published)",
            "asset_type": "technical_plan",
            "classification": "public",
            "owner_team": "Architecture Office",
            "read_policy": "open"
        }
    }

    # 写入 assets
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f, indent=2)

    # --- 请求数据 (包含正常+干扰+脏数据) ---
    requests = [
        # 正确命中：外部高风险，指向未发布技术计划
        {
            "request_id": "REQ-001",
            "channel": "external",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "external_access",
            "target_asset_id": "asset-001",
            "actor_name": "unknown_user_1",
            "claimed_role": "external_auditor",
            "message": "Need latest architecture plan for review",
            "status": "open"
        },
        # 干扰：内部审计，低风险，不应拒绝
        {
            "request_id": "REQ-002",
            "channel": "internal",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "internal_audit",
            "target_asset_id": "asset-001",
            "actor_name": "alice",
            "claimed_role": "internal_auditor",
            "message": "Scheduled audit of architecture docs",
            "status": "open"
        },
        # 正确命中：外部高风险，指向未发布财务档案
        {
            "request_id": "REQ-003",
            "channel": "external",
            "request_type": "download",
            "risk_level": "high",
            "risk_type": "external_access",
            "target_asset_id": "asset-002",
            "actor_name": "unknown_user_2",
            "claimed_role": "partner",
            "message": "Requesting Q3 financial bundle",
            "status": "open"
        },
        # 干扰：外部但目标资产是公开的（classification=public）
        {
            "request_id": "REQ-004",
            "channel": "external",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "external_access",
            "target_asset_id": "asset-003",
            "actor_name": "external_user",
            "claimed_role": "visitor",
            "message": "Wants to see meeting notes",
            "status": "open"
        },
        # 正确命中：外部高风险，指向未发布技术计划（asset-001 另一个请求）
        {
            "request_id": "REQ-005",
            "channel": "external",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "external_access",
            "target_asset_id": "asset-001",
            "actor_name": "unknown_user_3",
            "claimed_role": "researcher",
            "message": "Architecture plan access",
            "status": "pending"
        },
        # 干扰：已驳回的请求（status=denied），不应再处理
        {
            "request_id": "REQ-006",
            "channel": "external",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "external_access",
            "target_asset_id": "asset-002",
            "actor_name": "bot_user",
            "claimed_role": "crawler",
            "message": "Automated fetch",
            "status": "already_denied"
        },
        # 脏数据：target_asset_id 不存在于资产列表中
        {
            "request_id": "REQ-007",
            "channel": "external",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "external_access",
            "target_asset_id": "asset-missing",
            "actor_name": "phantom",
            "claimed_role": "unknown",
            "message": "??",
            "status": "open"
        },
        # 脏数据：risk_level 拼写为 "HIGH"（大写），应该被处理成忽略或容错？我们设定规则：只接受小写"high"，所以此条不应被选中
        {
            "request_id": "REQ-008",
            "channel": "external",
            "request_type": "read",
            "risk_level": "HIGH",
            "risk_type": "external_access",
            "target_asset_id": "asset-001",
            "actor_name": "hacker",
            "claimed_role": "none",
            "message": "Trying uppercase",
            "status": "open"
        },
        # 脏数据：缺少 risk_type 字段，应跳过
        {
            "request_id": "REQ-009",
            "channel": "external",
            "request_type": "read",
            "risk_level": "high",
            "target_asset_id": "asset-002",
            "actor_name": "sloppy",
            "claimed_role": "any",
            "message": "missing risk_type",
            "status": "open"
        },
        # 干扰：内部请求即使高风险也不应被拒绝（channel=internal）
        {
            "request_id": "REQ-010",
            "channel": "internal",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "external_access",
            "target_asset_id": "asset-001",
            "actor_name": "admin",
            "claimed_role": "sysadmin",
            "message": "Admin test",
            "status": "open"
        }
    ]

    # 写入 requests
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # --- 附件描述（纯干扰，不影响答案） ---
    attachments = {
        "attachments": [
            {
                "path": "attachments/req001_note.txt",
                "title": "External auditor credentials",
                "kind": "note",
                "description": "Attached ID card scan"
            },
            {
                "path": "attachments/req003_invoice.pdf",
                "title": "Invoice for Q3",
                "kind": "invoice",
                "description": "Fake invoice"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

if __name__ == "__main__":
    build_env()
