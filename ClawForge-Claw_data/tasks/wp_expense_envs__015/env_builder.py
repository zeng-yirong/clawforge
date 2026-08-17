import os
import json
import shutil

def build_env():
    # Clean slate
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("ops"):
        shutil.rmtree("ops")
    os.makedirs("data")
    os.makedirs("ops")

    # ── Travel policies (main) ──
    policies = {
        "categories": [
            {
                "category_id": "accommodation",
                "name": "住宿",
                "reimbursable": True,
                "daily_limit": 800.0,
                "policy_tier": "standard"
            },
            {
                "category_id": "food",
                "name": "餐饮",
                "reimbursable": True,
                "daily_limit": 200.0,
                "policy_tier": "standard"
            },
            {
                "category_id": "flight",
                "name": "机票",
                "reimbursable": True,
                "per_trip_limit": 1500.0,
                "policy_tier": "standard"
            },
            {
                "category_id": "metro",
                "name": "地铁公交",
                "reimbursable": True,
                "daily_limit": 50.0,
                "policy_tier": "standard"
            },
            {
                "category_id": "taxi",
                "name": "出租车",
                "reimbursable": True,
                "daily_limit": 100.0,
                "policy_tier": "standard"
            },
            {
                "category_id": "communication",
                "name": "通讯费",
                "reimbursable": True,
                "daily_limit": 50.0,
                "policy_tier": "standard"
            },
            {
                "category_id": "misc",
                "name": "其他杂费",
                "reimbursable": True,
                "daily_limit": 100.0,
                "policy_tier": "standard"
            }
        ],
        "policy_meta": {
            "tier": "standard",
            "destination": "北京",
            "duration_days": 3,
            "effective_date": "2024-01-01"
        }
    }
    with open("data/travel_policies.json", "w", encoding="utf-8") as f:
        json.dump(policies, f, ensure_ascii=False, indent=2)

    # ── Old/obsolete policy (interference) ──
    old_policy = {
        "categories": [
            {
                "category_id": "accommodation",
                "name": "住宿",
                "reimbursable": True,
                "daily_limit": 500.0,
                "policy_tier": "standard"
            }
        ],
        "policy_meta": {"tier": "standard", "destination": "北京", "duration_days": 3, "effective_date": "2023-06-01"}
    }
    with open("data/old_policy.json", "w", encoding="utf-8") as f:
        json.dump(old_policy, f, ensure_ascii=False, indent=2)

    # ── Consumption records (main) ──
    records = {
        "consumption_records": [
            # ── EMP007's records (小明) ──
            {"record_id": "R001", "employee": "EMP007", "category": "accommodation", "date": "2024-06-01", "amount": 1100.0, "description": "北京酒店6月1日", "receipt": True, "vendor": "如家", "nights": 1},
            {"record_id": "R002", "employee": "EMP007", "category": "accommodation", "date": "2024-06-02", "amount": 1100.0, "description": "北京酒店6月2日", "receipt": True, "vendor": "如家", "nights": 1},
            {"record_id": "R003", "employee": "EMP007", "category": "food", "date": "2024-06-01", "amount": 150.0, "description": "午餐", "receipt": True, "vendor": "海底捞"},
            {"record_id": "R004", "employee": "EMP007", "category": "food", "date": "2024-06-02", "amount": 180.0, "description": "晚餐", "receipt": True, "vendor": "西贝"},
            {"record_id": "R005", "employee": "EMP007", "category": "food", "date": "2024-06-03", "amount": 200.0, "description": "午餐", "receipt": True, "vendor": "肯德基"},
            {"record_id": "R006", "employee": "EMP007", "category": "taxi", "date": "2024-06-01", "amount": 100.0, "description": "机场到酒店", "receipt": False, "vendor": "滴滴"},
            {"record_id": "R007", "employee": "EMP007", "category": "taxi", "date": "2024-06-02", "amount": 120.0, "description": "酒店到客户", "receipt": False, "vendor": "滴滴"},
            {"record_id": "R008", "employee": "EMP007", "category": "flight", "date": "2024-06-01", "amount": 1500.0, "description": "北京机票", "receipt": True, "vendor": "国航"},
            {"record_id": "R009", "employee": "EMP007", "category": "metro", "date": "2024-06-01", "amount": 30.0, "description": "地铁", "receipt": True, "vendor": "北京地铁"},
            {"record_id": "R010", "employee": "EMP007", "category": "metro", "date": "2024-06-02", "amount": 50.0, "description": "地铁", "receipt": True, "vendor": "北京地铁"},
            {"record_id": "R011", "employee": "EMP007", "category": "metro", "date": "2024-06-03", "amount": 40.0, "description": "地铁", "receipt": True, "vendor": "北京地铁"},
            {"record_id": "R012", "employee": "EMP007", "category": "communication", "date": "2024-06-01", "amount": 50.0, "description": "电话费", "receipt": True, "vendor": "中国移动"},
            {"record_id": "R013", "employee": "EMP007", "category": "communication", "date": "2024-06-02", "amount": 50.0, "description": "电话费", "receipt": True, "vendor": "中国移动"},
            {"record_id": "R014", "employee": "EMP007", "category": "misc", "date": "2024-06-01", "amount": 100.0, "description": "办公用品", "receipt": True, "vendor": "文具店"},
            {"record_id": "R015", "employee": "EMP007", "category": "misc", "date": "2024-06-02", "amount": 100.0, "description": "办公用品", "receipt": True, "vendor": "文具店"},
            # ── EMP008's records (干扰) ──
            {"record_id": "R016", "employee": "EMP008", "category": "accommodation", "date": "2024-06-05", "amount": 800.0, "description": "上海酒店", "receipt": True, "vendor": "汉庭", "nights": 1},
            {"record_id": "R017", "employee": "EMP008", "category": "food", "date": "2024-06-05", "amount": 300.0, "description": "晚餐", "receipt": True, "vendor": "日料"},
            # ── Duplicate record (干扰) ──
            {"record_id": "R018", "employee": "EMP007", "category": "accommodation", "date": "2024-06-01", "amount": 1100.0, "description": "北京酒店6月1日（重复）", "receipt": True, "vendor": "如家", "nights": 1}
        ]
    }
    with open("data/consumption_records.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # ── Irrelevant CSV (干扰) ──
    with open("data/employee_list.csv", "w") as f:
        f.write("employee_id,name,department\nEMP007,小明,技术部\nEMP008,小红,市场部\n")

    # ── Empty placeholder ──
    with open("ops/.gitkeep", "w") as f:
        pass
