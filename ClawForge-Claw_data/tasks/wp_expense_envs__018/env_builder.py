import os
import json

def build_env():
    # 1. trip_info.json
    trip_info = {
        "trip_id": "TRIP-018",
        "tier": "senior",
        "destination": "北京",
        "duration_days": 3
    }
    with open("trip_info.json", "w", encoding="utf-8") as f:
        json.dump(trip_info, f, ensure_ascii=False, indent=2)

    # 2. policy_db/travel_policies.json  (包含多个等级，干扰项)
    os.makedirs("policy_db", exist_ok=True)
    policies = {
        "policies": [
            {
                "tier": "standard",
                "categories": [
                    {"category_id": "accommodation", "name": "住宿", "daily_budget": 300, "reimbursable": True},
                    {"category_id": "food", "name": "餐饮", "daily_budget": 150, "reimbursable": True},
                    {"category_id": "flight", "name": "机票", "total_budget": 1500, "reimbursable": True},
                    {"category_id": "taxi", "name": "出租车", "daily_budget": 80, "reimbursable": True},
                    {"category_id": "communication", "name": "通讯费", "daily_budget": 30, "reimbursable": True},
                    {"category_id": "metro", "name": "地铁公交", "daily_budget": 30, "reimbursable": True}
                ]
            },
            {
                "tier": "senior",
                "categories": [
                    {"category_id": "accommodation", "name": "住宿", "daily_budget": 500, "reimbursable": True},
                    {"category_id": "food", "name": "餐饮", "daily_budget": 200, "reimbursable": True},
                    {"category_id": "flight", "name": "机票", "total_budget": 2000, "reimbursable": True},
                    {"category_id": "taxi", "name": "出租车", "daily_budget": 100, "reimbursable": True},
                    {"category_id": "communication", "name": "通讯费", "daily_budget": 50, "reimbursable": True},
                    {"category_id": "metro", "name": "地铁公交", "daily_budget": 50, "reimbursable": True}
                ]
            },
            {
                "tier": "executive",
                "categories": [
                    {"category_id": "accommodation", "name": "住宿", "daily_budget": 800, "reimbursable": True},
                    {"category_id": "food", "name": "餐饮", "daily_budget": 300, "reimbursable": True},
                    {"category_id": "flight", "name": "机票", "total_budget": 5000, "reimbursable": True},
                    {"category_id": "taxi", "name": "出租车", "daily_budget": 200, "reimbursable": True}
                ]
            }
        ]
    }
    with open("policy_db/travel_policies.json", "w", encoding="utf-8") as f:
        json.dump(policies, f, ensure_ascii=False, indent=2)

    # 3. consumption/consumption_records.json (包含 TRIP-018 和干扰 trip)
    os.makedirs("consumption", exist_ok=True)
    records = [
        # TRIP-018 真实记录 (另有干扰记录)
        {"record_id": "R101", "trip_id": "TRIP-018", "category": "accommodation", "date": "2024-03-01", "amount": 800.0, "receipt": True, "vendor": "北京希尔顿", "nights": 1},
        {"record_id": "R102", "trip_id": "TRIP-018", "category": "accommodation", "date": "2024-03-02", "amount": 800.0, "receipt": True, "vendor": "北京希尔顿", "nights": 1},
        {"record_id": "R201", "trip_id": "TRIP-018", "category": "food", "date": "2024-03-01", "amount": 250.0, "receipt": True, "vendor": "午餐"},
        {"record_id": "R202", "trip_id": "TRIP-018", "category": "food", "date": "2024-03-02", "amount": 250.0, "receipt": True, "vendor": "晚餐"},
        {"record_id": "R203", "trip_id": "TRIP-018", "category": "food", "date": "2024-03-03", "amount": 250.0, "receipt": True, "vendor": "午餐"},
        {"record_id": "R301", "trip_id": "TRIP-018", "category": "flight", "date": "2024-03-01", "amount": 1800.0, "receipt": True, "vendor": "国航"},
        {"record_id": "R401", "trip_id": "TRIP-018", "category": "taxi", "date": "2024-03-01", "amount": 80.0, "receipt": True, "vendor": "滴滴"},
        {"record_id": "R402", "trip_id": "TRIP-018", "category": "taxi", "date": "2024-03-02", "amount": 70.0, "receipt": True, "vendor": "滴滴"},
        {"record_id": "R403", "trip_id": "TRIP-018", "category": "taxi", "date": "2024-03-03", "amount": 100.0, "receipt": True, "vendor": "滴滴"},
        # 干扰记录：其他 trip
        {"record_id": "R501", "trip_id": "TRIP-019", "category": "accommodation", "date": "2024-02-15", "amount": 600.0, "receipt": True, "vendor": "上海万豪", "nights": 1},
        {"record_id": "R502", "trip_id": "TRIP-019", "category": "food", "date": "2024-02-15", "amount": 120.0, "receipt": True, "vendor": "快餐"},
        {"record_id": "R601", "trip_id": "TRIP-020", "category": "flight", "date": "2024-01-10", "amount": 3000.0, "receipt": True, "vendor": "南航"},
        # 干扰：无收据记录 (receipt=false)
        {"record_id": "R701", "trip_id": "TRIP-018", "category": "communication", "date": "2024-03-01", "amount": 100.0, "receipt": False, "vendor": "手机充值"},
        # 干扰：重复记录 (record_id 不同但相同 trip 和 category)
        {"record_id": "R702", "trip_id": "TRIP-018", "category": "food", "date": "2024-03-01", "amount": 250.0, "receipt": True, "vendor": "午餐"},
    ]
    with open("consumption/consumption_records.json", "w", encoding="utf-8") as f:
        json.dump({"consumption_records": records}, f, ensure_ascii=False, indent=2)

    # 4. raw_logs 干扰目录
    os.makedirs("raw_logs", exist_ok=True)
    with open("raw_logs/server.log", "w") as f:
        f.write("2024-03-04 03:15:22 ERROR DB crash\n")
        f.write("2024-03-04 03:16:01 INFO Recovery started\n")

    # 5. ops 空目录 (留给 agent 输出)
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
