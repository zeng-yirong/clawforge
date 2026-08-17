import os
import json
import shutil

def build_env():
    # 清理可能存在的旧数据（仅用于测试）
    for path in ['data', 'policies', 'logs', 'old_reports', 'report']:
        if os.path.exists(path):
            shutil.rmtree(path)

    # ---------- 创建目录 ----------
    os.makedirs('data', exist_ok=True)
    os.makedirs('policies', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('old_reports', exist_ok=True)

    # ---------- 1. 行程信息 (data/trips.json) ----------
    trips = [
        {
            "trip_id": "TRIP-2024-001",
            "destination": "上海",
            "start_date": "2024-03-01",
            "end_date": "2024-03-03",
            "duration_days": 3,
            "employee_tier": "standard"
        },
        {
            "trip_id": "TRIP-2024-002",
            "destination": "广州",
            "start_date": "2024-03-10",
            "end_date": "2024-03-14",
            "duration_days": 5,
            "employee_tier": "senior"
        },
        {
            "trip_id": "TRIP-2023-001",
            "destination": "北京",
            "start_date": "2023-11-20",
            "end_date": "2023-11-22",
            "duration_days": 3,
            "employee_tier": "executive"
        }
    ]
    with open('data/trips.json', 'w', encoding='utf-8') as f:
        json.dump(trips, f, ensure_ascii=False, indent=2)

    # ---------- 2. 消费记录 (data/consumption_records.json) ----------
    consumption = [
        # ---- TRIP-2024-001 有效记录 ----
        {"record_id": "R001", "category": "accommodation", "date": "2024-03-01", "amount": 800, "description": "锦江之星", "receipt": True, "vendor": "锦江之星", "nights": 1},
        {"record_id": "R002", "category": "food", "date": "2024-03-01", "amount": 250, "description": "午餐-餐厅A", "receipt": True, "vendor": "餐厅A"},
        {"record_id": "R003", "category": "food", "date": "2024-03-02", "amount": 300, "description": "晚餐-餐厅B", "receipt": True, "vendor": "餐厅B"},
        {"record_id": "R004", "category": "food", "date": "2024-03-03", "amount": 150, "description": "早餐-酒店", "receipt": True, "vendor": "酒店餐厅"},
        {"record_id": "R005", "category": "taxi", "date": "2024-03-01", "amount": 60, "description": "机场-酒店", "receipt": True, "vendor": "滴滴"},
        {"record_id": "R006", "category": "taxi", "date": "2024-03-03", "amount": 60, "description": "酒店-机场", "receipt": True, "vendor": "滴滴"},
        # ---- 干扰：其他 trip 的有效记录 ----
        {"record_id": "R010", "category": "food", "date": "2024-03-11", "amount": 500, "description": "客户宴请", "receipt": True, "vendor": "广州酒家"},
        {"record_id": "R011", "category": "accommodation", "date": "2024-03-11", "amount": 1200, "description": "广州酒店", "receipt": True, "vendor": "白云宾馆", "nights": 2},
        # ---- 干扰：无效记录（缺失category、负金额、未知类别） ----
        {"record_id": "R100", "category": None, "date": "2024-03-01", "amount": 100, "description": "未知", "receipt": False, "vendor": "unknown"},
        {"record_id": "R101", "category": "food", "date": "2024-03-02", "amount": -50, "description": "退款", "receipt": True, "vendor": "某店"},
        {"record_id": "R102", "category": "unknown", "date": "2024-03-01", "amount": 200, "description": "其他", "receipt": False, "vendor": "某店"}
    ]
    with open('data/consumption_records.json', 'w', encoding='utf-8') as f:
        json.dump({"records": consumption}, f, ensure_ascii=False, indent=2)  # 包装成对象

    # ---------- 3. 差旅政策 ----------
    # 最新政策 v2
    policy_v2 = {
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True, "max_daily_amount": 500},
            {"category_id": "food", "name": "餐饮", "reimbursable": True, "max_daily_amount": 200},
            {"category_id": "taxi", "name": "出租车", "reimbursable": True, "max_daily_amount": 100},
            {"category_id": "metro", "name": "地铁公交", "reimbursable": True, "max_daily_amount": 50},
            {"category_id": "flight", "name": "机票", "reimbursable": True, "max_daily_amount": 2000},
            {"category_id": "communication", "name": "通讯费", "reimbursable": True, "max_daily_amount": 30},
            {"category_id": "misc", "name": "其他杂费", "reimbursable": False, "max_daily_amount": 0}
        ]
    }
    with open('policies/travel_policies_v2.json', 'w', encoding='utf-8') as f:
        json.dump(policy_v2, f, ensure_ascii=False, indent=2)

    # 旧政策 v1（干扰）
    policy_v1 = {
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True, "max_daily_amount": 600},
            {"category_id": "food", "name": "餐饮", "reimbursable": True, "max_daily_amount": 150},
            {"category_id": "taxi", "name": "出租车", "reimbursable": True, "max_daily_amount": 120},
            {"category_id": "metro", "name": "地铁公交", "reimbursable": True, "max_daily_amount": 40},
            {"category_id": "flight", "name": "机票", "reimbursable": True, "max_daily_amount": 1800},
            {"category_id": "communication", "name": "通讯费", "reimbursable": True, "max_daily_amount": 20},
            {"category_id": "misc", "name": "其他杂费", "reimbursable": False, "max_daily_amount": 0}
        ]
    }
    with open('policies/travel_policies_v1.json', 'w', encoding='utf-8') as f:
        json.dump(policy_v1, f, ensure_ascii=False, indent=2)

    # ---------- 4. 干扰目录 ----------
    # logs 目录
    with open('logs/system.log', 'w') as f:
        f.write("2024-03-01 INFO: system startup\n")
    # old_reports 目录
    with open('old_reports/expense_analysis_2023.json', 'w') as f:
        json.dump({"dummy": True}, f)

    # 确保 report 目录不存在（Agent 需要自己创建）
    if os.path.exists('report'):
        shutil.rmtree('report')

if __name__ == '__main__':
    build_env()
