import os
import json
import random

def build_env():
    # 创建目录结构
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 模拟一次严重锁冲突的场景
    # 正确的事务 ID: tx_2025032108
    # 干扰项: 其他事务 ID，有的已提交，有的已回滚，有的只是轻微等待

    # 1. 慢查询日志 (模拟)
    slow_log = """# Time: 2025-03-21T03:10:00.123
# User@Host: app_user[app_user] @  [10.0.0.15] Id: 108
# Query_time: 45.2  Lock_time: 38.4 Rows_sent: 0  Rows_examined: 2400000
SET tx_id='tx_2025032108';
INSERT INTO orders (id, amount) SELECT id, amount*0.8 FROM temp_orders WHERE status='pending';

# Time: 2025-03-21T03:11:00.456
# User@Host: batch[batch] @  [10.0.0.22] Id: 209
# Query_time: 12.1  Lock_time: 0.2 Rows_sent: 0  Rows_examined: 100
SET tx_id='tx_2025032104';
UPDATE users SET last_login=NOW() WHERE id=843;

# Time: 2025-03-21T03:12:00.789
# User@Host: replicator[rep] @  [10.0.0.33] Id: 312
# Query_time: 0.5  Lock_time: 0.1 Rows_sent: 0  Rows_examined: 1
SET tx_id='tx_2025032105';
SELECT 1;
"""

    with open("db_dumps/slow_queries_03_21.log", "w") as f:
        f.write(slow_log)

    # 2. 锁信息 (pg_locks 模拟)
    lock_info = [
        {"tx_id": "tx_2025032108", "lock_type": "relation", "relation": "orders", "mode": "AccessExclusiveLock", "granted": True, "waiting": False},
        {"tx_id": "tx_2025032108", "lock_type": "tuple", "relation": "orders", "mode": "RowExclusiveLock", "granted": True, "waiting": False},
        {"tx_id": "tx_2025032109", "lock_type": "relation", "relation": "orders", "mode": "ShareLock", "granted": False, "waiting": True},
        {"tx_id": "tx_2025032106", "lock_type": "relation", "relation": "users", "mode": "AccessShareLock", "granted": True, "waiting": False},
        {"tx_id": "tx_2025032104", "lock_type": "relation", "relation": "users", "mode": "RowExclusiveLock", "granted": True, "waiting": False},
        {"tx_id": "tx_2025032108", "lock_type": "transactionid", "mode": "ExclusiveLock", "granted": True, "waiting": False},
    ]
    with open("db_dumps/lock_info.json", "w") as f:
        json.dump(lock_info, f, indent=2)

    # 3. 事务快照 (transaction_snapshot.csv) 包含干扰项
    txn_snapshot = """tx_id,state,age_seconds,query
tx_2025032108,active,780,"INSERT INTO orders SELECT ..."
tx_2025032104,idle_in_transaction,120,"UPDATE users ..."
tx_2025032109,active,10,"SELECT ..."
tx_2025032105,committed,5,
tx_2025032106,rollback,600,
"""
    with open("db_dumps/transaction_snapshot.csv", "w") as f:
        f.write(txn_snapshot)

    # 4. 干扰文件：过期慢查询
    old_slow = """# Time: 2025-03-20T23:00:00
SET tx_id='tx_2025032001';
SELECT * FROM large_table;
"""
    with open("db_dumps/slow_queries_yesterday.log", "w") as f:
        f.write(old_slow)

    # 5. 确保 ops 目录有一个空文件作为干扰
    with open("ops/.gitkeep", "w") as f:
        f.write("")

    # 确保不写入答案文件，由 agent 自己创建
