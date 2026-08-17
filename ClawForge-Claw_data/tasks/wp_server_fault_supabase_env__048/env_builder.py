import os

def build_env():
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 干扰：较早的正常慢查询日志（无锁等待）
    with open("db_dumps/slow_queries_20250324.log", "w") as f:
        f.write(
            "# Time: 2025-03-24T12:00:00\n"
            "# Query_time: 0.001  Lock_time: 0.000\n"
            "SELECT 1;\n"
        )

    # 目标日志：凌晨3点的慢查询，显式锁等待
    with open("db_dumps/slow_queries_20250325.log", "w") as f:
        f.write(
            "# Time: 2025-03-25T03:00:00\n"
            "# User@Host: app_user@app_host [app_user] @  [10.0.0.1]  Id:   42\n"
            "# Query_time: 45.678  Lock_time: 23.456  Rows_sent: 0  Rows_examined: 1000000\n"
            "SET timestamp=1742857200;\n"
            "UPDATE orders SET status='processing' WHERE order_id IN (select ...);\n"
            "# WAIT_FOR_LOCK: session_id=12345, table='orders', mode=IX\n"
        )

    # 干扰：无关的数据库快照文件
    with open("db_dumps/snapshot.sql", "w") as f:
        f.write("-- PostgreSQL snapshot placeholder\n")
