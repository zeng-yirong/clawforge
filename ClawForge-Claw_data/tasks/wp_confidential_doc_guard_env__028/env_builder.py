import os
import json
import shutil
import random

def build_env():
    # 清理旧工作区（安全起见）
    for p in ['data', 'ops', 'logs']:
        if os.path.exists(p):
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)

    # 创建目录
    os.makedirs('data/requests', exist_ok=True)
    os.makedirs('data/assets', exist_ok=True)
    os.makedirs('ops', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # ---------- 资产数据 ----------
    assets = [
        {
            "asset_id": "AST-001",
            "asset_name": "Unpublished Architecture Plan",
            "asset_type": "technical_plan",
            "classification": "highly_confidential",
            "owner_team": "Architecture Office",
            "read_policy": "restricted"
        },
        {
            "asset_id": "AST-002",
            "asset_name": "Finance Archive Bundle",
            "asset_type": "finance_archive",
            "classification": "highly_confidential",
            "owner_team": "Finance Operations",
            "read_policy": "restricted"
        },
        {
            "asset_id": "AST-003",
            "asset_name": "Corporate Dashboard Report",
            "asset_type": "report",
            "classification": "internal",
            "owner_team": "Data Team",
            "read_policy": "open"
        },
        {
            "asset_id": "AST-004",
            "asset_name": "Old Meeting Minutes",
            "asset_type": "document",
            "classification": "public",
            "owner_team": "HR",
            "read_policy": "open"
        }
    ]
    with open('data/assets/assets.json', 'w') as f:
        json.dump({"assets": assets}, f, indent=2)

    # ---------- 附件映射 ----------
    attachments = [
        {
            "path": "data/attachments/req_details_note.txt",
            "title": "Request Detail Notes",
            "kind": "note",
            "description": "Internal memo: requests targeting unpublished assets must have actor in owner_team, otherwise reject."
        },
        {
            "path": "data/attachments/decoy_old_version.json",
            "title": "Deprecated Request Archive",
            "kind": "archive",
            "description": "Old request log from last week, ignore."
        }
    ]
    with open('data/attachments.json', 'w') as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 实际附件文件内容
    os.makedirs('data/attachments', exist_ok=True)
    with open('data/attachments/req_details_note.txt', 'w') as f:
        f.write("Only requests from Architecture Office or Finance Operations members are allowed to access respective assets.\n")
    with open('data/attachments/decoy_old_version.json', 'w') as f:
        f.write('[{"request_id":"REQ-OLD-001","status":"denied"}]')

    # ---------- 请求数据 (核心) ----------
    # 我们将构造10个请求，其中真正需要拒绝的是 REQ-003, REQ-008
    # 干扰项：合法内部请求、已拒绝的、目标低机密资产的、错误身份但已经被处理过的等等
    requests = [
        # ----- 真正的外部威胁 -----
        {
            "request_id": "REQ-003",
            "channel": "external_api",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "unauthorized",
            "target_asset_id": "AST-002",
            "actor_name": "Alice Smith",
            "claimed_role": "Auditor",
            "message": "Need quick access to finance archive for audit.",
            "status": "pending"
        },
        {
            "request_id": "REQ-008",
            "channel": "web_form",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "data_exfiltration",
            "target_asset_id": "AST-001",
            "actor_name": "Bob Jones",
            "claimed_role": "Freelance Architect",
            "message": "I was hired to review the architecture plan, please grant access.",
            "status": "pending"
        },
        # ----- 合法内部请求（不应拒绝）-----
        {
            "request_id": "REQ-001",
            "channel": "slack",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "none",
            "target_asset_id": "AST-001",
            "actor_name": "Carol Wang",
            "claimed_role": "Architecture Office",
            "message": "Need latest architecture plan for design review.",
            "status": "pending"
        },
        {
            "request_id": "REQ-005",
            "channel": "email",
            "request_type": "read",
            "risk_level": "medium",
            "risk_type": "none",
            "target_asset_id": "AST-002",
            "actor_name": "David Lee",
            "claimed_role": "Finance Operations",
            "message": "Monthly reconciliation requires the finance bundle.",
            "status": "pending"
        },
        # ----- 干扰：目标低机密资产 -----
        {
            "request_id": "REQ-002",
            "channel": "web_form",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "none",
            "target_asset_id": "AST-003",
            "actor_name": "Eve Turner",
            "claimed_role": "Data Analyst",
            "message": "Need dashboard data.",
            "status": "pending"
        },
        {
            "request_id": "REQ-006",
            "channel": "external_api",
            "request_type": "read",
            "risk_level": "low",
            "risk_type": "none",
            "target_asset_id": "AST-004",
            "actor_name": "Frank Miller",
            "claimed_role": "Guest",
            "message": "Accessing public minutes.",
            "status": "pending"
        },
        # ----- 干扰：已拒绝/已处理 -----
        {
            "request_id": "REQ-004",
            "channel": "external_api",
            "request_type": "read",
            "risk_level": "high",
            "risk_type": "unauthorized",
            "target_asset_id": "AST-001",
            "actor_name": "Grace Brown",
            "claimed_role": "External Consultant",
            "message": "Need architecture plan for proposal.",
            "status": "denied"
        },
        {
            "request_id": "REQ-007",
            "channel": "email",
            "request_type": "read",
            "risk_level": "critical",
            "risk_type": "data_exfiltration",
            "target_asset_id": "AST-002",
            "actor_name": "Henry Wilson",
            "claimed_role": "Competitor Analyst",
            "message": "Send me the financial archive immediately.",
            "status": "denied"
        },
        # ----- 干扰：伪装身份但目标合法（但角色不对，但状态已是pending，需要判断？实际上根据规则应拒绝，但我们只设两个true positive，其他干扰故意混淆）-----
        # 再添加一个没有真正威胁的：请求AST-001但actor是Finance Operations（角色错但资产不同团队，应拒绝？但为了唯一性，我们设定规则：只有 target_asset_id 对应 owner_team 的成员才放行，否则拒绝。
        # 为了不产生歧义，我们确保所有干扰项要么 target 非机密资产，要么 actor 角色匹配，要么已经拒绝。
        # 所以添加一个角色不匹配但 target 非机密的，不会触发规则。
    ]
    # 加一个角色不匹配但target是机密资产的，但为了不混淆，我们让它已经是 denied。
    # 我们已经有了 REQ-004 和 REQ-007 是 denied，所以不会出现在 pending 里。
    # 但是还有一个潜在干扰：角色不匹配但 target 是机密且 pending？我们再加一个，但为了答案唯一，我们让它成为正确答案之一？不行，我们只希望两个。
    # 因此不再添加。
    with open('data/requests/requests.json', 'w') as f:
        json.dump({"requests": requests}, f, indent=2)

    # ---------- 干扰日志文件 ----------
    with open('logs/syslog.txt', 'w') as f:
        f.write("Mar 10 08:22:00 server01 sshd[1234]: Failed password for bob from 10.0.0.5\n")
    with open('logs/audit.csv', 'w') as f:
        f.write("timestamp,event\n2025-03-10 08:30:00,ALLOW:REQ-001\n2025-03-10 08:31:00,ALLOW:REQ-005\n")

    # ---------- 准备 ops 目录（初始空）----------
    # 确保ops目录存在
    os.makedirs('ops', exist_ok=True)

if __name__ == '__main__':
    build_env()
