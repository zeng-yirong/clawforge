import os
import random

def build_env():
    # 创建目录结构
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("old_logs", exist_ok=True)
    os.makedirs("backups", exist_ok=True)

    # 写入 db_dumps 快照（干扰）
    with open("db_dumps/postgres_dump_20250321.sql", "w") as f:
        f.write("-- PostgreSQL database dump\n")
        f.write("CREATE TABLE accounts (id INT, balance DECIMAL);\n")
        f.write("INSERT INTO accounts VALUES (1, 1000);\n")

    # 写入慢查询日志（核心数据）
    # 事务 tx_42 锁等待 8000ms（最长）
    # 其他事务锁等待较短
    slow_log_lines = [
        "# Time: 2025-03-21 03:12:34 UTC\n",
        "# User@Host: app_user[app_user] @  [10.0.0.5]  Id: 42\n",
        "# Query_time: 12.000  Lock_time: 8.000  Rows_sent: 0  Rows_examined: 1000\n",
        "SET timestamp=1742515954;\n",
        "UPDATE accounts SET balance=balance-100 WHERE id=10;\n",
        "# Time: 2025-03-21 03:12:36 UTC\n",
        "# User@Host: app_user[app_user] @  [10.0.0.6]  Id: 43\n",
        "# Query_time: 0.500  Lock_time: 0.200  Rows_sent: 0  Rows_examined: 5\n",
        "SET timestamp=1742515956;\n",
        "SELECT * FROM users WHERE id=100;\n",
        "# Time: 2025-03-21 03:12:38 UTC\n",
        "# User@Host: batch_job[batch_job] @  [10.0.0.7]  Id: 44\n",
        "# Query_time: 2.000  Lock_time: 1.000  Rows_sent: 0  Rows_examined: 200\n",
        "SET timestamp=1742515958;\n",
        "INSERT INTO logs (message) VALUES ('heartbeat');\n",
        "# Time: 2025-03-21 03:12:40 UTC\n",
        "# User@Host: app_user[app_user] @  [10.0.0.8]  Id: 45\n",
        "# Query_time: 6.000  Lock_time: 5.000  Rows_sent: 0  Rows_examined: 500\n",
        "SET timestamp=1742515960;\n",
        "DELETE FROM sessions WHERE expiry < NOW();\n",
    ]
    with open("logs/slow_queries.log", "w") as f:
        f.writelines(slow_log_lines)

    # 干扰日志文件
    with open("logs/access.log", "w") as f:
        f.write("127.0.0.1 - - [21/Mar/2025:03:10:00 +0000] GET /health HTTP/1.1 200 0\n")
        f.write("127.0.0.1 - - [21/Mar/2025:03:11:00 +0000] POST /api/login HTTP/1.1 200 12\n")

    # 旧日志干扰（包含另一个更长的锁等待，但不应被纳入）
    old_log_lines = [
        "# Time: 2025-03-20 22:00:00 UTC\n",
        "# User@Host: admin[admin] @  [10.0.0.1]  Id: 999\n",
        "# Query_time: 15.000  Lock_time: 12.000  Rows_sent: 0  Rows_examined: 10000\n",
        "SET timestamp=1742515200;\n",
        "ALTER TABLE huge_table ADD COLUMN new_col INT;\n",
    ]
    with open("old_logs/slow_queries_old.log", "w") as f:
        f.writelines(old_log_lines)

    # 备份目录干扰
    with open("backups/README.txt", "w") as f:
        f.write("Backup storage - not relevant.\n")

if __name__ == "__main__":
    build_env()
