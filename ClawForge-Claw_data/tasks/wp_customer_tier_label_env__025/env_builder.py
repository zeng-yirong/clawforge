import json
import os

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)

    # 准备消费数据 (consumption_logs)
    consumption_records = [
        {"customer_id": "c001", "quarter_spend_usd": 60000},
        {"customer_id": "c002", "quarter_spend_usd": 30000},
        {"customer_id": "c003", "quarter_spend_usd": 10000},
        {"customer_id": "c004", "quarter_spend_usd": 80000},
        {"customer_id": "c005", "quarter_spend_usd": -1000},   # 无效：负数
        {"customer_id": "c006", "quarter_spend_usd": 50000},   # 有效的消费，但活动无效
        # c007 重复，取最后一次 (20000)
        {"customer_id": "c007", "quarter_spend_usd": 1000},
        {"customer_id": "c007", "quarter_spend_usd": 20000},
        {"customer_id": "c008", "quarter_spend_usd": 48000},
        {"customer_id": "c009", "quarter_spend_usd": 55000},
        {"customer_id": "c010", "quarter_spend_usd": 30000},   # 只在消费中出现
    ]
    consumption_data = {"consumption_logs": consumption_records}
    with open("data/consumption_logs.json", "w") as f:
        json.dump(consumption_data, f, indent=2)

    # 准备活动数据 (activity_logs)
    activity_records = [
        {"customer_id": "c001", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "c002", "risk_level": "low", "last_active_days": 45, "usage_trend": "down"},
        {"customer_id": "c003", "risk_level": "high", "last_active_days": 80, "usage_trend": "down"},
        {"customer_id": "c004", "risk_level": "low", "last_active_days": 25, "usage_trend": "up"},
        {"customer_id": "c005", "risk_level": "low", "last_active_days": 20, "usage_trend": "up"},   # 消费无效，活动虽有效但忽略
        {"customer_id": "c006", "risk_level": "low", "last_active_days": -5, "usage_trend": "up"},   # 无效：负数
        # c007 重复，取最后一次 (active=10)
        {"customer_id": "c007", "risk_level": "low", "last_active_days": 60, "usage_trend": "down"},
        {"customer_id": "c007", "risk_level": "low", "last_active_days": 10, "usage_trend": "up"},
        {"customer_id": "c008", "risk_level": "low", "last_active_days": 70, "usage_trend": "up"},
        {"customer_id": "c009", "risk_level": "high", "last_active_days": 35, "usage_trend": "down"},
        {"customer_id": "c011", "risk_level": "low", "last_active_days": 15, "usage_trend": "up"},   # 只在活动中出现
    ]
    activity_data = {"activity_logs": activity_records}
    with open("data/activity_logs.json", "w") as f:
        json.dump(activity_data, f, indent=2)

    # 创建一些干扰文件
    os.makedirs("data/old_data", exist_ok=True)
    with open("data/old_data/old_consumption_logs.json", "w") as f:
        json.dump({"consumption_logs": [{"customer_id": "c999", "quarter_spend_usd": 99999}]}, f)
    with open("data/notes.txt", "w") as f:
        f.write("These are some random notes, ignore me.\n")

if __name__ == "__main__":
    build_env()
