import json
import os

def build_env():
    # ---------- 数据目录 ----------
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---------- 1. 差旅政策 (包含多个等级，executive 为张总所用) ----------
    travel_policies = [
        {
            "tier": "executive",
            "destination": "New York",
            "duration_days": 4,
            "budgets": {
                "accommodation": {"daily_limit": 800, "unit": "USD"},
                "food": {"daily_limit": 250},
                "metro": {"daily_limit": 200},
                "taxi": {"daily_limit": 200},
                "flight": {"reimbursable": True, "note": "实报实销"}
            }
        },
        {
            "tier": "senior",
            "destination": "New York",
            "duration_days": 4,
            "budgets": {
                "accommodation": {"daily_limit": 600},
                "food": {"daily_limit": 180},
                "metro": {"daily_limit": 150},
                "taxi": {"daily_limit": 150},
                "flight": {"reimbursable": True}
            }
        },
        {
            "tier": "standard",
            "destination": "New York",
            "duration_days": 4,
            "budgets": {
                "accommodation": {"daily_limit": 400},
                "food": {"daily_limit": 120},
                "metro": {"daily_limit": 100},
                "taxi": {"daily_limit": 100},
                "flight": {"reimbursable": True}
            }
        }
    ]
    with open("data/travel_policies.json", "w", encoding="utf-8") as f:
        json.dump(travel_policies, f, indent=2)

    # ---------- 2. 消费记录（包含张总 trip 及其他干扰记录） ----------
    consumption_records = [
        # ----- 张总 TRIP-2024-011 的记录 -----
        {"record_id": "R001", "trip_id": "TRIP-2024-011", "category": "accommodation",
         "date": "2024-06-10", "amount": 850.0, "description": "Hilton New York - night1", "receipt": True, "vendor": "Hilton", "nights": 1},
        {"record_id": "R002", "trip_id": "TRIP-2024-011", "category": "accommodation",
         "date": "2024-06-11", "amount": 850.0, "description": "Hilton New York - night2", "receipt": True, "vendor": "Hilton", "nights": 1},
        {"record_id": "R003", "trip_id": "TRIP-2024-011", "category": "accommodation",
         "date": "2024-06-12", "amount": 850.0, "description": "Hilton New York - night3", "receipt": True, "vendor": "Hilton", "nights": 1},
        {"record_id": "R004", "trip_id": "TRIP-2024-011", "category": "accommodation",
         "date": "2024-06-13", "amount": 850.0, "description": "Hilton New York - night4", "receipt": True, "vendor": "Hilton", "nights": 1},
        {"record_id": "R005", "trip_id": "TRIP-2024-011", "category": "food",
         "date": "2024-06-10", "amount": 300.0, "description": "Lunch & dinner", "receipt": True, "vendor": "Various"},
        {"record_id": "R006", "trip_id": "TRIP-2024-011", "category": "food",
         "date": "2024-06-11", "amount": 300.0, "description": "Lunch & dinner", "receipt": True, "vendor": "Various"},
        {"record_id": "R007", "trip_id": "TRIP-2024-011", "category": "food",
         "date": "2024-06-12", "amount": 300.0, "description": "Lunch & dinner", "receipt": True, "vendor": "Various"},
        {"record_id": "R008", "trip_id": "TRIP-2024-011", "category": "food",
         "date": "2024-06-13", "amount": 300.0, "description": "Lunch & dinner", "receipt": True, "vendor": "Various"},
        {"record_id": "R009", "trip_id": "TRIP-2024-011", "category": "metro",
         "date": "2024-06-10", "amount": 45.0, "description": "Subway pass", "receipt": True, "vendor": "MTA"},
        {"record_id": "R010", "trip_id": "TRIP-2024-011", "category": "metro",
         "date": "2024-06-11", "amount": 55.0, "description": "Subway pass", "receipt": True, "vendor": "MTA"},
        {"record_id": "R011", "trip_id": "TRIP-2024-011", "category": "metro",
         "date": "2024-06-12", "amount": 50.0, "description": "Subway pass", "receipt": True, "vendor": "MTA"},
        {"record_id": "R012", "trip_id": "TRIP-2024-011", "category": "metro",
         "date": "2024-06-13", "amount": 50.0, "description": "Subway pass", "receipt": True, "vendor": "MTA"},
        {"record_id": "R013", "trip_id": "TRIP-2024-011", "category": "taxi",
         "date": "2024-06-10", "amount": 100.0, "description": "JFK to hotel", "receipt": True, "vendor": "Yellow Cab"},
        {"record_id": "R014", "trip_id": "TRIP-2024-011", "category": "flight",
         "date": "2024-06-09", "amount": 1200.0, "description": "Round trip flight", "receipt": True, "vendor": "Delta"},

        # ----- 干扰记录：其他 trip -----
        {"record_id": "R015", "trip_id": "TRIP-2024-012", "category": "accommodation",
         "date": "2024-06-15", "amount": 400.0, "description": "Hotel", "receipt": True, "vendor": "Marriott", "nights": 1},
        {"record_id": "R016", "trip_id": "TRIP-2024-012", "category": "food",
         "date": "2024-06-15", "amount": 150.0, "description": "dinner", "receipt": True, "vendor": "Restaurant"},
        {"record_id": "R017", "trip_id": "TRIP-2024-013", "category": "taxi",
         "date": "2024-06-20", "amount": 200.0, "description": "airport", "receipt": False, "vendor": "Uber"},
        # 脏数据：金额为负、缺少receipt等
        {"record_id": "R018", "trip_id": "TRIP-2024-011", "category": "misc",
         "date": "2024-06-10", "amount": -50.0, "description": "refund??", "receipt": False, "vendor": "Unknown"},
        {"record_id": "R019", "trip_id": "TRIP-2024-011", "category": "accommodation",
         "date": "2024-06-10", "amount": 0.0, "description": "cancellation", "receipt": False, "vendor": "Booking"},
        # 同 trip 但属于 future 无关类别
        {"record_id": "R020", "trip_id": "TRIP-2024-011", "category": "communication",
         "date": "2024-06-11", "amount": 20.0, "description": "phone card", "receipt": True, "vendor": "T-Mobile"}
    ]
    with open("data/consumption_records.json", "w", encoding="utf-8") as f:
        json.dump({"collection": "consumption_records", "records": consumption_records}, f, indent=2)

    # ---------- 3. 干扰文件：旧版本政策（过期） ----------
    old_policy = [
        {"tier": "executive", "daily_accommodation": 700, "daily_food": 200}
    ]
    with open("data/travel_policies_old.json", "w", encoding="utf-8") as f:
        json.dump(old_policy, f, indent=2)

    # ---------- 4. 预期答案（仅供开发者参考，不写入工作区） ----------
    # 实际验证时依赖 verify_workplace.py 中的硬编码值

if __name__ == "__main__":
    build_env()
