import os
import json

def build_env():
    # -- 数据目录 --
    os.makedirs("data", exist_ok=True)
    os.makedirs("consumption", exist_ok=True)
    os.makedirs("ops", exist_ok=True)   # 留给agent产出

    # ---- 1. 正确的senior政策 ----
    policy_senior = {
        "accommodation": {"name": "住宿", "reimbursable": True, "daily_budget": 0, "nightly_budget": 800},
        "food":          {"name": "餐饮", "reimbursable": True, "daily_budget": 200, "nightly_budget": 0},
        "taxi":          {"name": "出租车", "reimbursable": True, "daily_budget": 150, "nightly_budget": 0},
        "communication": {"name": "通讯费", "reimbursable": True, "daily_budget": 30, "nightly_budget": 0},
        "metro":         {"name": "地铁公交", "reimbursable": True, "daily_budget": 50, "nightly_budget": 0},
        "flight":        {"name": "机票", "reimbursable": True, "daily_budget": 1500, "nightly_budget": 0},
        "misc":          {"name": "其他杂费", "reimbursable": True, "daily_budget": 100, "nightly_budget": 0}
    }
    with open("data/travel_policy_senior.json", "w", encoding="utf-8") as f:
        json.dump(policy_senior, f, ensure_ascii=False, indent=2)

    # ---- 2. 干扰政策（executive级别，预算更高） ----
    policy_exec = {
        "accommodation": {"name": "住宿", "reimbursable": True, "daily_budget": 0, "nightly_budget": 1000},
        "food":          {"name": "餐饮", "reimbursable": True, "daily_budget": 300, "nightly_budget": 0},
        "taxi":          {"name": "出租车", "reimbursable": True, "daily_budget": 200, "nightly_budget": 0},
        "communication": {"name": "通讯费", "reimbursable": True, "daily_budget": 50, "nightly_budget": 0},
        "metro":         {"name": "地铁公交", "reimbursable": True, "daily_budget": 80, "nightly_budget": 0},
        "flight":        {"name": "机票", "reimbursable": True, "daily_budget": 2000, "nightly_budget": 0},
        "misc":          {"name": "其他杂费", "reimbursable": True, "daily_budget": 150, "nightly_budget": 0}
    }
    with open("data/travel_policy_executive.json", "w", encoding="utf-8") as f:
        json.dump(policy_exec, f, ensure_ascii=False, indent=2)

    # ---- 3. 另一个干扰政策（admin，不全） ----
    policy_admin = {
        "accommodation": {"name": "住宿", "reimbursable": True, "daily_budget": 0, "nightly_budget": 600},
        "food":          {"name": "餐饮", "reimbursable": True, "daily_budget": 150, "nightly_budget": 0}
    }
    with open("data/travel_policy_admin.json", "w", encoding="utf-8") as f:
        json.dump(policy_admin, f, ensure_ascii=False, indent=2)

    # ---- 4. 旧版备份干扰（数值与senior不同） ----
    policy_senior_old = {
        "accommodation": {"name": "住宿", "reimbursable": True, "daily_budget": 0, "nightly_budget": 700},
        "food":          {"name": "餐饮", "reimbursable": True, "daily_budget": 180, "nightly_budget": 0},
        "taxi":          {"name": "出租车", "reimbursable": True, "daily_budget": 120, "nightly_budget": 0},
        "communication": {"name": "通讯费", "reimbursable": True, "daily_budget": 25, "nightly_budget": 0},
        "metro":         {"name": "地铁公交", "reimbursable": True, "daily_budget": 40, "nightly_budget": 0},
        "flight":        {"name": "机票", "reimbursable": True, "daily_budget": 1400, "nightly_budget": 0},
        "misc":          {"name": "其他杂费", "reimbursable": True, "daily_budget": 80, "nightly_budget": 0}
    }
    with open("data/travel_policy_senior_backup.json", "w", encoding="utf-8") as f:
        json.dump(policy_senior_old, f, ensure_ascii=False, indent=2)

    # ---- 5. 正确的消费记录（trip-2025-001）----
    consumption_records = [
        {
            "record_id": "rec-001",
            "category": "accommodation",
            "amount": 2400.0,
            "nights": 3,
            "date": "2025-03-10",
            "vendor": "北京希尔顿",
            "receipt": True,
            "trip_id": "trip-2025-001"
        },
        {
            "record_id": "rec-002",
            "category": "food",
            "amount": 650.0,
            "date": "2025-03-10",
            "vendor": "海底捞",
            "receipt": True,
            "trip_id": "trip-2025-001"
        },
        {
            "record_id": "rec-003",
            "category": "taxi",
            "amount": 500.0,
            "date": "2025-03-11",
            "vendor": "滴滴",
            "receipt": True,
            "trip_id": "trip-2025-001"
        },
        {
            "record_id": "rec-004",
            "category": "communication",
            "amount": 100.0,
            "date": "2025-03-12",
            "vendor": "中国移动",
            "receipt": True,
            "trip_id": "trip-2025-001"
        },
        {
            "record_id": "rec-005",
            "category": "metro",
            "amount": 150.0,
            "date": "2025-03-10",
            "vendor": "北京地铁",
            "receipt": True,
            "trip_id": "trip-2025-001"
        },
        {
            "record_id": "rec-006",
            "category": "misc",
            "amount": 300.0,
            "date": "2025-03-11",
            "vendor": "便利店",
            "receipt": True,
            "trip_id": "trip-2025-001"
        }
    ]
    with open("consumption/records.json", "w", encoding="utf-8") as f:
        json.dump(consumption_records, f, ensure_ascii=False, indent=2)

    # ---- 6. 干扰消费记录（其他差旅）----
    extra_records = [
        {
            "record_id": "rec-007",
            "category": "food",
            "amount": 800.0,
            "date": "2025-02-20",
            "vendor": "全聚德",
            "receipt": True,
            "trip_id": "trip-2025-002"
        },
        {
            "record_id": "rec-008",
            "category": "accommodation",
            "amount": 2800.0,
            "nights": 3,
            "date": "2025-02-20",
            "vendor": "上海万豪",
            "receipt": True,
            "trip_id": "trip-2025-002"
        }
    ]
    with open("consumption/records_old.json", "w", encoding="utf-8") as f:
        json.dump(extra_records, f, ensure_ascii=False, indent=2)

    # ---- 7. 其他干扰文件 ----
    with open("consumption/README.txt", "w") as f:
        f.write("存放差旅消费记录，按trip_id区分。\n")

    with open("data/notes.txt", "w") as f:
        f.write("政策文件按级别命名，最新版请确认。\n")

if __name__ == "__main__":
    build_env()
