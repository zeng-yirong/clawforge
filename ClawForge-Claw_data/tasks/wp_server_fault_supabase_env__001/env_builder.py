import os
import json
import shutil

def build_env():
    # 清理可能遗留的旧目录（安全起见）
    for d in ['incidents', 'attachments', 'ops', 'logs']:
        if os.path.exists(d):
            shutil.rmtree(d)

    # 创建目录
    os.makedirs('incidents', exist_ok=True)
    os.makedirs('attachments', exist_ok=True)
    os.makedirs('ops', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # 干扰文件：旧的 incident pool 快照（避免误读）
    old_pool = [
        {
            "incident_id": "INC-001",
            "title": "DB replica lag spike",
            "category": "db_replica_lag",
            "severity": "critical",
            "status": "open",
            "assigned_team": "db_ops",
            "ticket_type": "risk_work_order",
            "service": "analytics-mirror",
            "opened_at": "2025-03-01T02:00:00Z",
            "updated_at": "2025-03-01T03:00:00Z",
            "description": "Replication lag exceeded 300s",
            "tags": ["replication", "lag"]
        }
    ]
    with open('incidents/incident_pool_backup.json', 'w') as f:
        json.dump(old_pool, f)

    # 正式 incident pool（含干扰项和唯一正确答案）
    incidents = [
        {
            "incident_id": "INC-002",
            "title": "West4 spine uplink degraded",
            "category": "network_degradation",
            "severity": "high",
            "status": "open",
            "assigned_team": "network_ops",
            "ticket_type": "watchlist",
            "service": "west4-spine-uplink",
            "opened_at": "2025-03-01T04:00:00Z",
            "updated_at": "2025-03-01T05:00:00Z",
            "description": "Packet loss observed",
            "tags": ["network", "degradation"]
        },
        {
            "incident_id": "INC-003",
            "title": "UPS battery low - floor 3",
            "category": "ups_outage",
            "severity": "medium",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-03-01T06:00:00Z",
            "updated_at": "2025-03-01T06:30:00Z",
            "description": "UPS battery below 30%",
            "tags": ["ups", "battery"]
        },
        {
            "incident_id": "INC-004",
            "title": "Critical UPS outage in North DC",
            "category": "ups_outage",
            "severity": "critical",
            "status": "open",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-03-01T01:00:00Z",
            "updated_at": "2025-03-01T02:30:00Z",
            "description": "Main UPS failed, replication stuck",
            "tags": ["ups", "outage", "critical"]
        },
        {
            "incident_id": "INC-005",
            "title": "UPS maintenance completed",
            "category": "ups_outage",
            "severity": "critical",
            "status": "resolved",
            "assigned_team": "power_ops",
            "ticket_type": "risk_work_order",
            "service": "edge-cluster-a12",
            "opened_at": "2025-02-28T12:00:00Z",
            "updated_at": "2025-02-28T14:00:00Z",
            "description": "UPS replaced, no issues",
            "tags": ["ups", "resolved"]
        }
    ]
    with open('incidents/incident_pool.json', 'w') as f:
        json.dump(incidents, f)

    # runbook（唯一的事务 ID 嵌入在文本中）
    runbook_content = """# UPS and Service Outage Runbook

## 1. Verify UPS status
Check that the UPS is in bypass mode.

## 2. Identify stuck transactions
Run the following query on the primary database:

SELECT * FROM pg_stat_activity WHERE state = 'active' AND wait_event_type = 'Lock';
Look for the transaction that holds the conflicting lock.

## 3. Terminate the blocking transaction
Execute this command on the primary:
SELECT pg_terminate_backend(12345);
Use the actual PID from step 2, for example: **txn_7f9a2b1c** is the transaction ID to kill.

## 4. Restart replication
After termination, verify replication lag drops to zero.
"""
    with open('attachments/runbook_ups_and_service.md', 'w') as f:
        f.write(runbook_content)

    # 额外干扰：一个旧的 runbook（避免误读）
    old_runbook = "# Old runbook (deprecated)\nNo longer valid."
    with open('attachments/runbook_old.md', 'w') as f:
        f.write(old_runbook)

    # 创建空文件占位（agent 需要自己写 ops/remediation.json 和 logs/audit.json）
    # 但也可以不预创建，agent 会创建

if __name__ == '__main__':
    build_env()
