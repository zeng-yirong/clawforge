import os

def build_env():
    # 创建主目录
    os.makedirs("db_dumps/archived", exist_ok=True)
    # 慢查询日志（唯一活跃排他锁事务 Txn-9876）
    slow_log = """2025-04-12 03:15:22 | transaction_id: Txn-9876 | table: orders | lock: exclusive | status: active
2025-04-12 03:14:30 | transaction_id: Txn-1111 | table: inventory | lock: shared | status: idle
2025-04-12 03:16:10 | transaction_id: Txn-2345 | table: products | lock: shared | status: idle
2025-04-12 03:13:45 | transaction_id: Txn-5432 | table: orders | lock: exclusive | status: completed
2025-04-12 03:17:00 | transaction_id: Txn-6789 | table: shipping | lock: exclusive | status: idle
"""
    with open("db_dumps/slow_queries.log", "w") as f:
        f.write(slow_log)
    
    # 干扰旧日志（无活跃排他锁）
    old_log = """2025-04-11 22:10:05 | transaction_id: Txn-0001 | table: users | lock: shared | status: completed
2025-04-11 23:45:30 | transaction_id: Txn-0002 | table: billing | lock: exclusive | status: active
"""
    with open("db_dumps/archived/slow_queries_old.log", "w") as f:
        f.write(old_log)
    
    # 事件池快照（干扰项，包含可能指向错误的 TX）
    incidents = {
        "incidents": [
            {"incident_id": "INC-100", "title": "DB replica lag", "category": "db_replica_lag", "severity": "critical", "description": "Transaction Txn-9876 holding exclusive lock on orders for 15 minutes"},
            {"incident_id": "INC-200", "title": "UPS failure", "category": "ups_outage", "severity": "high", "description": "Power event on west4, no transaction impact"}
        ]
    }
    with open("db_dumps/incident_pool.json", "w") as f:
        import json
        json.dump(incidents, f, indent=2)

if __name__ == "__main__":
    build_env()
