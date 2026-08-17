import os
import json

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)

    # 1. employees.json (含干扰员工)
    employees = [
        {"employee_id": "EMP003", "name": "张三", "tier": "senior"},
        {"employee_id": "EMP001", "name": "李四", "tier": "standard"},
        {"employee_id": "EMP002", "name": "王五", "tier": "executive"}
    ]
    with open("data/employees.json", "w", encoding="utf-8") as f:
        json.dump(employees, f, ensure_ascii=False, indent=2)

    # 2. trip_info.json
    trip_info = {
        "trip_id": "TRIP-2024-05",
        "employee_id": "EMP003",
        "destination": "深圳",
        "duration_days": 3
    }
    with open("data/trip_info.json", "w", encoding="utf-8") as f:
        json.dump(trip_info, f, ensure_ascii=False, indent=2)

    # 3. travel_policies.json (当前有效政策)
    policies = {
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True,
             "limits": {"standard_per_night": 400, "senior_per_night": 800, "executive_per_night": 1200}},
            {"category_id": "food", "name": "餐饮", "reimbursable": True,
             "limits": {"standard_per_day": 150, "senior_per_day": 200, "executive_per_day": 300}},
            {"category_id": "taxi", "name": "出租车", "reimbursable": True,
             "limits": {"standard_per_trip": 100, "senior_per_trip": 150, "executive_per_trip": 250}},
            {"category_id": "communication", "name": "通讯费", "reimbursable": True,
             "limits": {"standard_per_day": 30, "senior_per_day": 50, "executive_per_day": 80}},
            {"category_id": "metro", "name": "地铁公交", "reimbursable": True,
             "limits": {"standard_per_day": 20, "senior_per_day": 30, "executive_per_day": 50}},
            {"category_id": "flight", "name": "机票", "reimbursable": True,
             "limits": {"standard_per_flight": 800, "senior_per_flight": 1500, "executive_per_flight": 3000}},
            {"category_id": "misc", "name": "其他杂费", "reimbursable": False, "limits": {}}
        ]
    }
    with open("data/travel_policies.json", "w", encoding="utf-8") as f:
        json.dump(policies, f, ensure_ascii=False, indent=2)

    # 4. consumption_records.json (包含目标出差记录 + 干扰记录)
    records = [
        # --- 目标 trip 的记录 (TRIP-2024-05) ---
        {"record_id": "rec001", "trip_id": "TRIP-2024-05", "category": "accommodation",
         "date": "2024-09-01", "amount": 2800.0, "description": "深圳酒店住宿",
         "receipt": True, "vendor": "深圳丽思", "nights": 3},
        {"record_id": "rec002", "trip_id": "TRIP-2024-05", "category": "food",
         "date": "2024-09-01", "amount": 250.0, "description": "晚餐", "receipt": True, "vendor": "粤菜馆", "nights": None},
        {"record_id": "rec003", "trip_id": "TRIP-2024-05", "category": "food",
         "date": "2024-09-02", "amount": 250.0, "description": "午餐+晚餐", "receipt": True, "vendor": "快餐", "nights": None},
        {"record_id": "rec004", "trip_id": "TRIP-2024-05", "category": "food",
         "date": "2024-09-03", "amount": 250.0, "description": "团队聚餐", "receipt": True, "vendor": "火锅店", "nights": None},
        {"record_id": "rec005", "trip_id": "TRIP-2024-05", "category": "taxi",
         "date": "2024-09-01", "amount": 200.0, "description": "机场到酒店", "receipt": True, "vendor": "滴滴", "nights": None},
        {"record_id": "rec006", "trip_id": "TRIP-2024-05", "category": "taxi",
         "date": "2024-09-03", "amount": 150.0, "description": "酒店到机场", "receipt": True, "vendor": "滴滴", "nights": None},
        {"record_id": "rec007", "trip_id": "TRIP-2024-05", "category": "communication",
         "date": "2024-09-01", "amount": 50.0, "description": "电话卡", "receipt": True, "vendor": "移动", "nights": None},
        {"record_id": "rec008", "trip_id": "TRIP-2024-05", "category": "communication",
         "date": "2024-09-02", "amount": 50.0, "description": "流量包", "receipt": True, "vendor": "移动", "nights": None},
        {"record_id": "rec009", "trip_id": "TRIP-2024-05", "category": "metro",
         "date": "2024-09-02", "amount": 30.0, "description": "地铁", "receipt": True, "vendor": "深圳通", "nights": None},
        {"record_id": "rec010", "trip_id": "TRIP-2024-05", "category": "misc",
         "date": "2024-09-01", "amount": 100.0, "description": "零食", "receipt": False, "vendor": "便利店", "nights": None},
        # --- 干扰 trip 的记录 (TRIP-2024-03) ---
        {"record_id": "rec011", "trip_id": "TRIP-2024-03", "category": "accommodation",
         "date": "2024-08-15", "amount": 1200.0, "description": "上海酒店", "receipt": True, "vendor": "万豪", "nights": 2},
        {"record_id": "rec012", "trip_id": "TRIP-2024-03", "category": "food",
         "date": "2024-08-15", "amount": 120.0, "description": "午餐", "receipt": True, "vendor": "肯德基", "nights": None},
        # --- 缺少 trip_id 的记录 (无效数据) ---
        {"record_id": "rec013", "trip_id": None, "category": "taxi",
         "date": "2024-07-01", "amount": 80.0, "description": "本地打车", "receipt": True, "vendor": "滴滴", "nights": None}
    ]
    with open("data/consumption_records.json", "w", encoding="utf-8") as f:
        json.dump({"consumption_records": records}, f, ensure_ascii=False, indent=2)

    # 5. 干扰文件：备份的旧政策
    old_policy = {
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True,
             "limits": {"standard_per_night": 350, "senior_per_night": 700, "executive_per_night": 1000}}
        ]
    }
    with open("data/backup/old_travel_policies.json", "w", encoding="utf-8") as f:
        json.dump(old_policy, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
