import os
import json
import random
import string

def random_id(prefix="REQ", length=8):
    return prefix + ''.join(random.choices(string.digits, k=length))

def build_env():
    # 确保工作目录正确（cwd 已是 ）
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("data/accounts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- 资产 ----------
    assets = [
        {"asset_id": "A-001", "asset_name": "2025 Architecture Blueprint", "asset_type": "technical_plan", "classification": "confidential", "owner_team": "Architecture Office", "read_policy": "strict"},
        {"asset_id": "A-002", "asset_name": "Finance Archive Bundle Q1", "asset_type": "finance_archive", "classification": "confidential", "owner_team": "Finance Operations", "read_policy": "strict"},
        {"asset_id": "A-003", "asset_name": "公开白皮书 v2", "asset_type": "technical_plan", "classification": "public", "owner_team": "Architecture Office", "read_policy": "open"},
        {"asset_id": "A-004", "asset_name": "Q3薪资明细", "asset_type": "finance_archive", "classification": "restricted", "owner_team": "Finance Operations", "read_policy": "internal"},
        {"asset_id": "A-005", "asset_name": "旧版架构草案 (已废弃)", "asset_type": "technical_plan", "classification": "confidential", "owner_team": "Architecture Office", "read_policy": "archived"},
    ]
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": assets}, f)

    # ---------- 账户 ----------
    accounts = [
        {"account_id": "U-100", "display_name": "外部承包商 张三", "department": "外部", "email": "zhangsan@outsider.com", "permissions": ["read_public"]},
        {"account_id": "U-101", "display_name": "内部审计 李四", "department": "审计部", "email": "lisi@internal.com", "permissions": ["read_internal"]},
        {"account_id": "U-102", "display_name": "架构师 王五", "department": "架构部", "email": "wangwu@internal.com", "permissions": ["read_all"]},
        {"account_id": "U-103", "display_name": "财务主管 赵六", "department": "财务部", "email": "zhaoliu@internal.com", "permissions": ["read_all"]},
        {"account_id": "U-104", "display_name": "运维 陈七", "department": "运维部", "email": "chenqi@internal.com", "permissions": ["read_internal"]},
    ]
    with open("data/accounts/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # ---------- 请求 ----------
    # 设计：
    # 需拒绝的：外部用户或低权限用户尝试访问 confidential 级别的 technical_plan 或 finance_archive，且状态为 pending 或 active
    # 干扰：已完结的同样目标的请求、内部高权限用户的合理请求、目标为公开资产的高风险请求
    requests = [
        # ── 越界请求（应拒绝） ──
        {"request_id": "REQ001", "channel": "web", "request_type": "download", "risk_level": "high", "risk_type": "unauthorized_access", "target_asset_id": "A-001", "actor_name": "外部承包商 张三", "claimed_role": "外部合作", "message": "需要架构图做集成", "status": "pending"},
        {"request_id": "REQ002", "channel": "api", "request_type": "read", "risk_level": "high", "risk_type": "data_leakage", "target_asset_id": "A-002", "actor_name": "第三方审计 刘大", "claimed_role": "外部审计", "message": "审计需要Q1财务数据", "status": "active"},
        {"request_id": "REQ003", "channel": "web", "request_type": "download", "risk_level": "medium", "risk_type": "policy_violation", "target_asset_id": "A-001", "actor_name": "运维 陈七", "claimed_role": "运维工程师", "message": "备份用", "status": "active"},
        # 注意：陈七是内部人员但权限仅 internal，目标A-001是confidential应拒绝
        {"request_id": "REQ004", "channel": "email", "request_type": "retrieve", "risk_level": "critical", "risk_type": "exfiltration", "target_asset_id": "A-004", "actor_name": "离职员工 周九", "claimed_role": "财务部(离职)", "message": "要最后一次访问薪资表", "status": "active"},
        # A-004是restricted但目标为finance_archive且风险critical，且actor为离职，应拒绝
        # ── 不应拒绝的干扰 ──
        {"request_id": "REQ005", "channel": "web", "request_type": "view", "risk_level": "low", "risk_type": "normal", "target_asset_id": "A-003", "actor_name": "外部承包商 张三", "claimed_role": "合作方", "message": "查看公开白皮书", "status": "approved"},
        {"request_id": "REQ006", "channel": "api", "request_type": "read", "risk_level": "low", "risk_type": "normal", "target_asset_id": "A-003", "actor_name": "架构师 王五", "claimed_role": "架构师", "message": "内部参考", "status": "active"},
        {"request_id": "REQ007", "channel": "web", "request_type": "download", "risk_level": "high", "risk_type": "unauthorized_access", "target_asset_id": "A-003", "actor_name": "外部恶意用户", "claimed_role": "研究员", "message": "要研究", "status": "pending"},
        # 目标A-003是public，即使高风险也不应拒绝（因为公开）
        {"request_id": "REQ008", "channel": "email", "request_type": "query", "risk_level": "medium", "risk_type": "curiosity", "target_asset_id": "A-005", "actor_name": "内部审计 李四", "claimed_role": "审计", "message": "检查废弃资产", "status": "completed"},
        # 已完结，不应处理
        {"request_id": "REQ009", "channel": "web", "request_type": "download", "risk_level": "high", "risk_type": "unauthorized_access", "target_asset_id": "A-001", "actor_name": "财务主管 赵六", "claimed_role": "财务主管", "message": "需要架构数据做预算", "status": "pending"},
        # 赵六有read_all权限，目标confidential但内部高权限，应允许（不拒绝）
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f)

    # ---------- 附件（制造干扰目录） ----------
    os.makedirs("data/attachments", exist_ok=True)
    attachments = [
        {"path": "data/attachments/arch_diagram_v3.pdf", "title": "架构图v3", "kind": "pdf", "description": "未发布"},
        {"path": "data/attachments/expense_report.xlsx", "title": "Q1费用报告", "kind": "spreadsheet", "description": "内部"},
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f)

    # ---------- 干扰文件 ----------
    with open("ops/previous_deny.log", "w") as f:
        f.write("这里有一些旧日志，不要混淆\n")
    with open("data/readme_old.txt", "w") as f:
        f.write("老版说明，勿读\n")

    print("环境构建完成。")

if __name__ == "__main__":
    build_env()
