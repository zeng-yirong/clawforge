import os
import json
import csv
from datetime import datetime, timedelta

def build_env():
    # Create directories
    os.makedirs("db_dumps", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # empty, agent will write kill_target.json

    # --- lock_info.csv ---
    # Correct answer: transaction_id = "txn_045", locks inventory exclusively for 45s
    # Interference rows:
    #   - other txn locking orders (short wait)
    #   - txn locking inventory with shared lock
    #   - txn locking inventory but only 15s wait
    lock_rows = [
        ["txn_045",   "inventory", "EXCLUSIVE", "45000", "GRANTED"],  # correct
        ["txn_101",   "orders",    "EXCLUSIVE", "2000",  "GRANTED"],
        ["txn_102",   "inventory", "SHARED",    "12000", "GRANTED"],
        ["txn_073",   "inventory", "EXCLUSIVE", "15000", "GRANTED"],
        ["txn_208",   "returns",   "EXCLUSIVE", "800",   "GRANTED"],
    ]
    lock_path = os.path.join("db_dumps", "lock_info.csv")
    with open(lock_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "table_name", "lock_type", "wait_time_ms", "status"])
        writer.writerows(lock_rows)

    # --- active_transactions.json ---
    # Only txn_045 matches: lock on inventory, exclusive, wait > 30s, and present here
    now = datetime.utcnow().isoformat() + "Z"
    earlier = (datetime.utcnow() - timedelta(minutes=45)).isoformat() + "Z"
    active_txns = {
        "transactions": [
            {"transaction_id": "txn_045", "start_time": earlier, "session_id": "sess_88", "state": "ACTIVE", "user": "batch_sync"},
            {"transaction_id": "txn_101", "start_time": now,     "session_id": "sess_12", "state": "ACTIVE", "user": "web_app"},
            {"transaction_id": "txn_102", "start_time": now,     "session_id": "sess_34", "state": "ACTIVE", "user": "read_replica"},
            {"transaction_id": "txn_073", "start_time": now,     "session_id": "sess_56", "state": "ACTIVE", "user": "data_pipeline"},
            {"transaction_id": "txn_208", "start_time": now,     "session_id": "sess_78", "state": "ACTIVE", "user": "return_import"},
        ]
    }
    active_path = os.path.join("db_dumps", "active_transactions.json")
    with open(active_path, "w") as f:
        json.dump(active_txns, f, indent=2)

    # --- slow_queries.log (干扰) ---
    slow_log_lines = [
        "2025-03-22 03:12:01 | 15000ms | UPDATE inventory SET stock_level = stock_level - 5 WHERE sku = 'SKU-1002' AND warehouse_id = 'wh_001' [txn_045]",
        "2025-03-22 03:15:33 | 2000ms  | SELECT * FROM orders WHERE status = 'pending'  [txn_101]",
        "2025-03-22 03:16:10 | 800ms   | INSERT INTO returns (return_id, order_id) VALUES ('ret_099', 'ord_777') [txn_208]",
    ]
    slow_path = os.path.join("db_dumps", "slow_queries.log")
    with open(slow_path, "w") as f:
        f.write("\n".join(slow_log_lines) + "\n")

    # --- 干扰文件, 不相关但增加迷惑性 ---
    # orders_dump.csv (与锁无关)
    orders_dump = [
        ["order_id","status","total_amount"],
        ["ord_1","shipped","125.00"],
        ["ord_2","processing","340.00"],
    ]
    orders_path = os.path.join("db_dumps", "orders_dump.csv")
    with open(orders_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(orders_dump)

    # returns_dump.csv
    returns_dump = [
        ["return_id","reason","status"],
        ["ret_001","defective","pending_inspection"],
        ["ret_003","wrong item","pending_review"],
    ]
    returns_path = os.path.join("db_dumps", "returns_dump.csv")
    with open(returns_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(returns_dump)

if __name__ == "__main__":
    build_env()
