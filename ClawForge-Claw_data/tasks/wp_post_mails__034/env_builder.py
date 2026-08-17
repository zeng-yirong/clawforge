import os

def build_env():
    # 创建目录结构
    os.makedirs("slow_logs", exist_ok=True)
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ===== 主慢查询日志 (包含目标事务) =====
    slow_main = """\
# Time: 240321 3:10:00
# User@Host: root[root] @ localhost []
# Thread_id: 100001  Schema: test  Last_errno: 0  Killed: 0
# Query_time: 0.500  Lock_time: 0.001  Rows_sent: 10  Rows_examined: 100
use test;
SELECT * FROM large_table WHERE id=1;

# Time: 240321 3:15:00
# User@Host: root[root] @ localhost []
# Thread_id: 123456  Schema: test  Last_errno: 0  Killed: 0
# Query_time: 1000.123  Lock_time: 999.000  Rows_sent: 1  Rows_examined: 1000000
UPDATE locked_table SET value=1 WHERE id=999;

# Time: 240321 3:20:00
# User@Host: app_user@app_host []
# Thread_id: 200002  Schema: test  Last_errno: 0  Killed: 0
# Query_time: 0.200  Lock_time: 0.010  Rows_sent: 100  Rows_examined: 500
SELECT * FROM small_table;
"""
    with open("slow_logs/mysql-slow.log", "w") as f:
        f.write(slow_main)

    # ===== 干扰慢日志文件 (短查询) =====
    slow_interference = """\
# Time: 240321 2:00:00
# Thread_id: 99999  Query_time: 0.100
"""
    with open("slow_logs/other.log", "w") as f:
        f.write(slow_interference)

    # ===== InnoDB 状态快照 (包含目标事务) =====
    innodb_status = """\
=====================================
2024-03-21 03:16:00 0x1234 INNODB MONITOR OUTPUT
=====================================
Per second averages calculated from the last 30 seconds
-----------------
TRANSACTIONS
-----------------
Trx id counter 1234567
Purge done for trx's n:o < 1234567 undo n:o < 0
History list length 100
Total number of lock structs in row lock hash table 2
LIST OF TRANSACTIONS FOR EACH SESSION:
---TRANSACTION 123456, ACTIVE 1000 sec
MySQL thread id 12, OS thread handle 1234, query id 5678 localhost root
TABLE LOCK table `test`.`locked_table` trx id 123456 lock mode IX
WAITING FOR THIS LOCK TO BE GRANTED:
...
---TRANSACTION 200002, ACTIVE 0 sec
MySQL thread id 13, OS thread handle 1235, query id 5679 localhost root
TABLE LOCK table `test`.`other_table` trx id 200002 lock mode IS
...
"""
    with open("db_dumps/innodb_status.txt", "w") as f:
        f.write(innodb_status)

    # ===== 干扰文件 =====
    with open("db_dumps/extra.txt", "w") as f:
        f.write("Some extra data not relevant.")
    with open("slow_logs/readme.md", "w") as f:
        f.write("This directory contains slow query logs from the primary database.")
