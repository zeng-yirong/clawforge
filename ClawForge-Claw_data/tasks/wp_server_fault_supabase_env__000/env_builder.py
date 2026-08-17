import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/incidents", exist_ok=True)

    # ---------- 核心数据：InnoDB 状态快照 ----------
    innodb_status = """=====================================
2025-03-15 03:15:22 0x7f1234567890 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 1 second
-----------------
BACKGROUND THREAD
-----------------
srv_master_thread loops: 1234 1_second, 1234 sleeps, 12 10_second, 123 background, 1234 flush
srv_master_thread log flush and writes: 1234
----------
SEMAPHORES
----------
OS WAIT ARRAY INFO: reservation count 1234
OS WAIT ARRAY INFO: signal count 1234
RW-shared spins 0, rounds 1234, OS waits 123
RW-excl spins 0, rounds 1234, OS waits 123
Spin rounds per wait: 123.00 RW-shared, 123.00 RW-excl
------------------------
LATEST DETECTED DEADLOCK
------------------------
(无死锁)
------------------------
TRANSACTIONS
------------------------
Trx id counter 77200
Purge done for trx's n:o < 77100 undo n:o < 0 state: running but idle
History list length 1234
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 77139, ACTIVE 15 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 2 lock struct(s), heap size 1136, 1 row lock(s)
MySQL thread id 456, OS thread handle 14001, query id 789 localhost root
SELECT * FROM orders WHERE id = 9999 FOR UPDATE
------- TRX HAS BEEN WAITING 15 SEC FOR THIS LOCK TO BE GRANTED:
RECORD LOCKS space id 10 page no 5 n bits 72 index PRIMARY of table `mydb`.`orders`
trx id 77139 lock_mode X locks rec but not gap waiting
---TRANSACTION 77138, ACTIVE 123 sec
2 lock struct(s), heap size 1136, 1 row lock(s)
MySQL thread id 123, OS thread handle 14000, query id 456 localhost root
TABLE LOCK table `mydb`.`orders` trx id 77138 lock mode IX
RECORD LOCKS space id 10 page no 5 n bits 72 index PRIMARY of table `mydb`.`orders`
trx id 77138 lock_mode X locks rec but not gap
---------------- END OF INNODB MONITOR OUTPUT
================"""

    with open("db_dumps/innodb_status.txt", "w") as f:
        f.write(innodb_status)

    # ---------- 干扰数据：慢查询日志 ----------
    slow_queries = """# Time: 2025-03-15T03:01:15.123456Z
# User@Host: root[root] @ localhost []
# Query_time: 45.123  Lock_time: 0.000 Rows_sent: 0  Rows_examined: 100000
SET autocommit=0;
START TRANSACTION;
UPDATE orders SET status='processing' WHERE id = 12345;
COMMIT;

# Time: 2025-03-15T03:02:30.654321Z
# User@Host: app_user[app_user] @ localhost []
# Query_time: 2.345  Lock_time: 0.010 Rows_sent: 0  Rows_examined: 500
SELECT * FROM orders WHERE customer_id = 67890;

# Time: 2025-03-15T03:03:00.000000Z
# User@Host: root[root] @ localhost []
# Query_time: 0.001  Lock_time: 0.000 Rows_sent: 0  Rows_examined: 0
KILL QUERY 456;"""

    with open("logs/slow_queries.log", "w") as f:
        f.write(slow_queries)

    # ---------- 干扰文件：过期的 kill 目标 ----------
    with open("ops/old_kill.json", "w") as f:
        json.dump({"transaction_id": 77000, "reason": "test"}, f, indent=2)

    # ---------- 干扰文件：无关的事故池 ----------
    incidents = {
        "incidents": [
            {
                "incident_id": "INC-001",
                "title": "UPS outage in west4",
                "category": "ups_outage",
                "severity": "critical",
                "status": "open",
                "assigned_team": "power_ops",
                "ticket_type": "risk_work_order",
                "service": "west4-spine-uplink",
                "opened_at": "2025-03-14T23:00:00Z",
                "updated_at": "2025-03-15T01:00:00Z",
                "description": "Battery backup drained.",
                "tags": ["west4", "power"]
            }
        ]
    }
    with open("data/incidents/incident_pool.json", "w") as f:
        json.dump(incidents, f, indent=2)

    # ---------- 无意义的 README ----------
    with open("README.txt", "w") as f:
        f.write("Server fault incident data snapshot for triage.\n")
