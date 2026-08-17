import os

def build_env():
    os.makedirs("logs/archive", exist_ok=True)

    # 主日志 —— 包含目标长事务
    with open("logs/postgresql.log", "w") as f:
        f.write("2025-04-07 02:50:00 UTC LOG:  checkpoint starting: time\n")
        f.write("2025-04-07 02:55:12 UTC LOG:  autovacuum: processing database \"mydb\"\n")
        f.write("2025-04-07 03:14:15 UTC WARNING:  long-running transaction detected: txn_a1b2c3d4, age 3421s, backend pid 12345\n")
        f.write("2025-04-07 03:20:00 UTC LOG:  checkpoint complete: wrote 123 buffers\n")
        f.write("2025-04-07 03:22:30 UTC ERROR:  relation \"foo\" does not exist at character 45\n")

    # 存档日志 —— 诱饵（事务 ID 不同）
    with open("logs/archive/postgresql.log", "w") as f:
        f.write("2025-04-06 12:00:00 UTC WARNING:  long-running transaction detected: txn_x9y8z7, age 5000s\n")

    # 干扰慢查询日志（不含长事务警告）
    with open("logs/slow_queries.log", "w") as f:
        f.write("2025-04-07 03:10:00 UTC | txn_abc | SELECT * FROM large_table WHERE ... | 3000ms\n")
        f.write("2025-04-07 03:12:00 UTC | txn_xyz | UPDATE ... | 5000ms\n")

    # 无关配置文件
    with open("config.yaml", "w") as f:
        f.write("db: postgres\nhost: localhost\n")
    with open("README.md", "w") as f:
        f.write("# Edge Cluster A12\nLogs are in logs/.\n")
