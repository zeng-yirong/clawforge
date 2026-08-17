import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/requests", exist_ok=True)
    os.makedirs("data/assets", exist_ok=True)
    os.makedirs("data/attachments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # —— 资产清单 ——
    assets = {
        "asset_001": {
            "asset_id": "asset_001",
            "asset_name": "API Key Vault",
            "asset_type": "credential_store",
            "classification": "internal",
            "owner_team": "Platform Security",
            "read_policy": "restricted"
        },
        "asset_002": {
            "asset_id": "asset_002",
            "asset_name": "Prompt Vault",
            "asset_type": "prompt_store",
            "classification": "internal",
            "owner_team": "Model Platform",
            "read_policy": "restricted"
        },
        "asset_003": {
            "asset_id": "asset_003",
            "asset_name": "Production DB",
            "asset_type": "database",
            "classification": "critical",
            "owner_team": "Infrastructure",
            "read_policy": "normal"
        }
    }
    with open("data/assets/assets.json", "w") as f:
        json.dump({"assets": list(assets.values())}, f, indent=2)

    # —— 请求数据（含干扰项） ——
    requests = [
        {
            "request_id": "req_001",
            "channel": "email",
            "request_type": "vault_access",
            "risk_level": "critical",
            "risk_type": "privilege_escalation",
            "target_asset_id": "asset_003",          # Production DB，不是保险库
            "actor_name": "Alice",
            "claimed_role": "DBA",
            "message": "Need immediate read access to resolve replication lag",
            "status": "pending"
        },
        {
            "request_id": "req_002",                 # 正确答案之一
            "channel": "slack",
            "request_type": "vault_access",
            "risk_level": "critical",
            "risk_type": "credential_exfiltration",
            "target_asset_id": "asset_001",          # API Key Vault
            "actor_name": "Bob",
            "claimed_role": "SRE",
            "message": "Urgent: prod API keys need rotation, must read from vault now",
            "status": "pending"
        },
        {
            "request_id": "req_003",
            "channel": "ticket",
            "request_type": "vault_access",
            "risk_level": "high",                   # 不是 critical
            "risk_type": "routine_maintenance",
            "target_asset_id": "asset_002",          # Prompt Vault，但风险等级不符合
            "actor_name": "Charlie",
            "claimed_role": "ML Engineer",
            "message": "Need to review stored prompts for a patch",
            "status": "pending"
        },
        {
            "request_id": "req_004",                 # 正确答案之二
            "channel": "email",
            "request_type": "vault_access",
            "risk_level": "critical",
            "risk_type": "credential_exfiltration",
            "target_asset_id": "asset_002",          # Prompt Vault
            "actor_name": "Dave",
            "claimed_role": "Security Auditor",
            "message": "Mandated compliance check on prompt vault contents, grant immediate access",
            "status": "pending"
        },
        {
            "request_id": "req_005",
            "channel": "webform",
            "request_type": "vault_access",
            "risk_level": "low",                    # 风险极低
            "risk_type": "info_request",
            "target_asset_id": "asset_001",
            "actor_name": "Eve",
            "claimed_role": "Intern",
            "message": "I lost my API key, can I retrieve it from the vault?",
            "status": "pending"
        }
    ]
    with open("data/requests/requests.json", "w") as f:
        json.dump({"requests": requests}, f, indent=2)

    # —— 附件（仅作为背景，不影响答案） ——
    attachments = [
        {
            "path": "data/attachments/vault_access_policy.md",
            "title": "Vault Access Policy",
            "kind": "policy",
            "description": "Internal policy restricting vault read access to Platform Security and Model Platform teams."
        }
    ]
    with open("data/attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 创建空的策略文件（为真实性）
    with open("data/attachments/vault_access_policy.md", "w") as f:
        f.write("# Vault Access Policy\n\nOnly Platform Security and Model Platform teams may access API Key Vault or Prompt Vault.\nAll critical-risk requests must be reviewed and denied unless explicitly approved by SOC.\n")

    # —— 干扰项：一个无关的日志目录 ——
    os.makedirs("raw_logs", exist_ok=True)
    with open("raw_logs/syslog.txt", "w") as f:
        f.write("Mar 10 03:15:22 host kernel: [12345] INFO: task blocked for more than 120 seconds.\n")
        f.write("Mar 10 03:15:22 host kernel: [12345] \"echo 0 > /proc/sys/kernel/hung_task_timeout_secs\" \n")

if __name__ == "__main__":
    build_env()
