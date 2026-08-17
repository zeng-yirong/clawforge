import os

def build_env():
    """Build a messy server fault workplace with lock contention clues."""
    # 目录结构
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)          # 目标目录，初始空
    os.makedirs("backups", exist_ok=True)      # 干扰目录
    os.makedirs("config", exist_ok=True)       # 干扰目录

    # --- 1. pg_stat_activity 快照 (模拟真实输出) ---
    pg_stat = """datid | datname  | pid   | state  | wait_event | query
------+----------+-------+--------+------------+----------------------------------------
 16384 | northstar | 12345 | active | Lock       | UPDATE orders SET status='shipped' WHERE order_id=123;
 16384 | northstar | 12346 | active | ClientRead | SELECT * FROM inventory WHERE warehouse_id=42;
 16384 | northstar | 12347 | idle   |            | 
 16384 | northstar | 12348 | active | IO         | COPY sales_2024 FROM '/tmp/sales.csv' WITH CSV;
 16384 | northstar | 12349 | active | Lock       | SELECT ... FOR UPDATE;
"""
    with open("db_dumps/pg_stat_activity.txt", "w") as f:
        f.write(pg_stat)

    # --- 2. 慢查询日志 (多个慢查询，只有一个是锁等待的) ---
    slow_log = """# Time: 2025-03-21 03:12:30 UTC
# Query_time: 5000  Lock_time: 4500  Rows_sent: 0  Rows_examined: 100000
# PID: 12345
UPDATE orders SET status='shipped' WHERE order_id=123;

# Time: 2025-03-21 03:11:15 UTC
# Query_time: 3000  Lock_time: 10  Rows_sent: 100  Rows_examined: 50000
# PID: 12346
SELECT * FROM inventory WHERE warehouse_id=42;

# Time: 2025-03-21 03:10:00 UTC
# Query_time: 2000  Lock_time: 0  Rows_sent: 1  Rows_examined: 200
# PID: 12350
INSERT INTO audit_log VALUES (...);
"""
    with open("db_dumps/slow_queries.log", "w") as f:
        f.write(slow_log)

    # --- 3. 干扰文件：旧备份、配置文件等 ---
    with open("backups/old_snapshot.sql", "w") as f:
        f.write("-- fake backup content")
    with open("config/postgresql.conf", "w") as f:
        f.write("max_connections = 200\nlock_timeout = 5000")
    # 干扰的 JSON 文件，与目标无关
    with open("config/incident_metadata.json", "w") as f:
        f.write('{"incident_id": "INC-007", "owner": "nobody"}')
    # 创建一个空的 ops 目录骗一下
    with open("ops/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
