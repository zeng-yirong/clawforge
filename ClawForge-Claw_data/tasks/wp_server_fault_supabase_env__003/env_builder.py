import os

def build_env():
    # 创建目录
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- 干扰文件：索引碎片统计 ---
    with open("db_dumps/index_fragmentation.txt", "w") as f:
        f.write("table: orders, fragmentation: 78%\n")
        f.write("table: users, fragmentation: 12%\n")
        f.write("table: payments, fragmentation: 45%\n")

    # --- 干扰文件：缓冲池状态 ---
    with open("db_dumps/buffer_pool_stats.txt", "w") as f:
        f.write("buffer_pool_size: 64G\nused: 51G\ndirty: 3G\n")

    # --- 核心：慢查询日志 ---
    # 格式: timestamp,transaction_id,query,duration_sec,lock_wait_sec
    with open("db_dumps/slow_query.log", "w") as f:
        f.write("2025-04-03 03:00:12,98765,UPDATE orders SET status='shipped' WHERE order_id=1001,120.5,115.2\n")
        f.write("2025-04-03 03:01:45,12345,SELECT * FROM inventory WHERE warehouse_id=5,45.1,0.3\n")
        f.write("2025-04-03 03:02:30,98765,UPDATE orders SET status='shipped' WHERE order_id=1002,98.7,93.4\n")
        f.write("2025-04-03 03:03:01,54321,DELETE FROM logs WHERE created_at < '2024-01-01',0.2,0.0\n")
        f.write("2025-04-03 03:04:22,98765,UPDATE orders SET status='shipped' WHERE order_id=1003,132.1,128.9\n")
        f.write("2025-04-03 03:05:00,10001,SELECT * FROM orders WHERE customer_id=42,80.0,79.8\n")
        f.write("2025-04-03 03:05:12,10002,UPDATE orders SET priority='high' WHERE order_id=1004,75.3,74.9\n")
        f.write("2025-04-03 03:06:33,10003,SELECT * FROM orders WHERE customer_id=73,90.1,89.7\n")
        f.write("2025-04-03 03:07:01,10004,INSERT INTO order_audit VALUES (...),60.5,60.0\n")
        f.write("2025-04-03 03:08:44,10005,UPDATE orders SET shipment_date=NOW(),55.2,54.8\n")

    # --- 核心：锁信息 ---
    # 格式：每个锁区块，标明持有者和等待列表
    with open("db_dumps/lock_info.txt", "w") as f:
        f.write("=== LOCK BLOCKADE ANALYSIS ===\n")
        f.write("Lock ID: LOCK-001\n")
        f.write("Object: orders (table-level IX lock)\n")
        f.write("Held by Transaction: 98765\n")
        f.write("Lock Mode: X\n")
        f.write("Waits: [10001, 10002, 10003, 10004, 10005]\n")
        f.write("---\n")
        f.write("Lock ID: LOCK-002\n")
        f.write("Object: inventory (table-level IS lock)\n")
        f.write("Held by Transaction: 12345\n")
        f.write("Lock Mode: S\n")
        f.write("Waits: []\n")
        f.write("---\n")
        f.write("Lock ID: LOCK-003\n")
        f.write("Object: logs (table-level IX lock)\n")
        f.write("Held by Transaction: 54321 (COMMITTED, no longer active)\n")
        f.write("Lock Mode: X\n")
        f.write("Waits: []\n")
        f.write("---\n")

    # 确保 ops 目录下没有任何初始文件
    # 空文件占位，但验证时不应存在目标文件
    with open("ops/.gitkeep", "w") as f:
        f.write("")

build_env()
