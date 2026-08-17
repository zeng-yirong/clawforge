import os
import json
from pathlib import Path

def build_env():
    # 创建必要目录
    dirs = ["attachments", "db_dumps", "incidents", "ops", "data", "preprocessed"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # ----- attachments/runbook_ups_and_service.md -----
    runbook_content = """# UPS and Service Outage Runbook

## 数据库锁等待处置流程

1. 检查慢查询日志：`db_dumps/slow_query.log`
2. 筛选所有 `STATE` 为 `ACTIVE` 的行。
3. 按时间戳（第一列）升序排列，取最早出现的事务。
4. 记录该事务的 `PID` 值（冒号后的数字）。
5. 将该 `PID` 以 JSON 格式写入 `ops/kill_target.json`，键名为 `"transaction_id"`。

示例输出：`{"transaction_id": 123456}`
"""
    with open("attachments/runbook_ups_and_service.md", "w") as f:
        f.write(runbook_content)

    # ----- db_dumps/slow_query.log -----
    # 按时间升序，最旧 ACTIVE PID = 123456
    slow_log = """2025-04-01 03:10:00.000 UTC PID:123456 STATE:ACTIVE QUERY: UPDATE accounts SET balance = balance - 100 WHERE account_id = 'A001';
2025-04-01 03:15:22.123 UTC PID:789012 STATE:IDLE QUERY: SELECT 1;
2025-04-01 03:16:05.789 UTC PID:345678 STATE:ACTIVE QUERY: INSERT INTO logs VALUES (...);
2025-04-01 03:13:50.111 UTC PID:111222 STATE:IDLE IN TRANSACTION QUERY: DELETE FROM temp;
2025-04-01 03:12:30.222 UTC PID:999888 STATE:ACTIVE QUERY: CREATE INDEX CONCURRENTLY ON orders (created_at);
"""
    with open("db_dumps/slow_query.log", "w") as f:
        f.write(slow_log)

    # ----- db_dumps/pg_stat_activity.csv (干扰) -----
    csv_content = "pid,state,query_start\n123456,active,2025-04-01 03:10:00\n789012,idle,2025-04-01 03:15:22\n345678,active,2025-04-01 03:16:05\n"
    with open("db_dumps/pg_stat_activity.csv", "w") as f:
        f.write(csv_content)

    # ----- db_dumps/outdated_backup.tar.gz (干扰) -----
    with open("db_dumps/outdated_backup.tar.gz", "w") as f:
        f.write("fake tar content - not relevant")

    # ----- incidents/incident_pool.json (干扰) -----
    incidents = {
        "incidents": [
            {
                "incident_id": "INC-001",
                "title": "UPS 电池告警",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "west4-spine-uplink",
                "opened_at": "2025-04-01T02:00:00Z",
                "updated_at": "2025-04-01T03:00:00Z",
                "description": "UPS 负载异常",
                "tags": ["ups", "power"]
            },
            {
                "incident_id": "INC-042",
                "title": "数据库锁等待风暴",
                "category": "db_replica_lag",
                "severity": "critical",
                "status": "triaged",
                "assigned_team": "db_ops",
                "ticket_type": "watchlist",
                "service": "analytics-mirror",
                "opened_at": "2025-04-01T03:00:00Z",
                "updated_at": "2025-04-01T03:10:00Z",
                "description": "大量 UPDATE 阻塞，请检查慢查询",
                "tags": ["lock", "db"]
            },
            {
                "incident_id": "INC-003",
                "title": "网络抖动",
                "category": "network_degradation",
                "severity": "high",
                "status": "open",
                "assigned_team": "network_ops",
                "ticket_type": "risk_work_order",
                "service": "edge-cluster-a12",
                "opened_at": "2025-04-01T01:00:00Z",
                "updated_at": "2025-04-01T02:00:00Z",
                "description": "延迟上升",
                "tags": ["network"]
            }
        ]
    }
    with open("incidents/incident_pool.json", "w") as f:
        json.dump(incidents, f, indent=2)

    # ----- data/contacts.json (干扰) -----
    contacts = {
        "contacts": [
            {"contact_id": "C001", "name": "Harper Zhou", "role": "Database Reliability Engineer", "email": "harper.zhou@northstar.example.com"},
            {"contact_id": "C002", "name": "Lena Park", "role": "Facilities Power Coordinator", "email": "lena.park@northstar.example.com"},
            {"contact_id": "C003", "name": "Nikhil Rao", "role": "NOC Lead", "email": "nikhil.rao@northstar.example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ----- 创建空的 ops 目录（确保存在） -----
    # 已在开头创建

if __name__ == "__main__":
    build_env()
