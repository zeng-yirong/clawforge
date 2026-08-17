import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # 确保工作区干净
    for d in ['data', 'records', 'report']:
        os.makedirs(d, exist_ok=True)

    # ---- 1. 政策文件 ----
    # 旧版本 (干扰项)
    old_policy = {
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True, "daily_limit": 500},
            {"category_id": "food", "name": "餐饮", "reimbursable": True, "daily_limit": 150},
            {"category_id": "flight", "name": "机票", "reimbursable": True, "total_limit": 1500},
            {"category_id": "taxi", "name": "出租车", "reimbursable": True, "daily_limit": 80},
            {"category_id": "metro", "name": "地铁公交", "reimbursable": True, "daily_limit": 30},
        ]
    }
    with open("data/policies_v1.json", "w", encoding="utf-8") as f:
        json.dump(old_policy, f, ensure_ascii=False, indent=2)

    # 最新政策（senior级别）—— 正确答案依据
    new_policy = {
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True, "daily_limit": 600},
            {"category_id": "food", "name": "餐饮", "reimbursable": True, "daily_limit": 250},
            {"category_id": "flight", "name": "机票", "reimbursable": True, "total_limit": 2000},
            {"category_id": "taxi", "name": "出租车", "reimbursable": True, "daily_limit": 100},
            {"category_id": "metro", "name": "地铁公交", "reimbursable": True, "daily_limit": 40},
        ]
    }
    with open("data/policies_v2.json", "w", encoding="utf-8") as f:
        json.dump(new_policy, f, ensure_ascii=False, indent=2)

    # 额外干扰：其他级别的政策
    exec_policy = {
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True, "daily_limit": 1200},
            {"category_id": "food", "name": "餐饮", "reimbursable": True, "daily_limit": 500},
        ]
    }
    with open("data/policies_executive.json", "w", encoding="utf-8") as f:
        json.dump(exec_policy, f, ensure_ascii=False, indent=2)

    # ---- 2. 消费记录 ----
    # 小李北京出差2天（2023-10-16 ~ 2023-10-17），但有个日期错误记录（2023-10-18）作为干扰
    records = {
        "record_id": "rec_001",
        "trip_id": "trip_LX_202310",
        "employee": "小李",
        "tier": "senior",
        "destination": "北京",
        "duration_days": 2,
        "items": [
            # 住宿：两晚，实际每晚650 → 超预算 (600*2=1200, 实际1300, 超100)
            {"category": "accommodation", "date": "2023-10-16", "amount": 650.0, "description": "汉庭北京站店", "receipt": True, "vendor": "华住", "nights": 1},
            {"category": "accommodation", "date": "2023-10-17", "amount": 650.0, "description": "汉庭北京站店", "receipt": True, "vendor": "华住", "nights": 1},
            # 餐饮：每天预算250，2天共500；实际第一天420（超170），第二天200（未超）
            {"category": "food", "date": "2023-10-16", "amount": 420.0, "description": "晚餐北京烤鸭", "receipt": True, "vendor": "全聚德"},
            {"category": "food", "date": "2023-10-17", "amount": 200.0, "description": "午餐便当", "receipt": True, "vendor": "711"},
            # 额外的第三天餐饮（干扰，日期2023-10-18）—— 不计入2天预算
            {"category": "food", "date": "2023-10-18", "amount": 180.0, "description": "早餐", "receipt": True, "vendor": "麦当劳"},
            # 机票：总上限2000，实际1950（未超）
            {"category": "flight", "date": "2023-10-16", "amount": 1950.0, "description": "上海-北京往返", "receipt": True, "vendor": "国航"},
            # 出租车：每天上限100，2天共200；实际第一天120（超20），第二天0（未超）
            {"category": "taxi", "date": "2023-10-16", "amount": 120.0, "description": "机场到酒店", "receipt": True, "vendor": "滴滴"},
            # 地铁：每天上限40，2天共80；实际第一天15，第二天10，共25（未超）
            {"category": "metro", "date": "2023-10-16", "amount": 15.0, "description": "地铁", "receipt": True, "vendor": "北京地铁"},
            {"category": "metro", "date": "2023-10-17", "amount": 10.0, "description": "地铁", "receipt": True, "vendor": "北京地铁"},
        ]
    }
    with open("records/trip_LX_202310.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # 干扰：其他员工的正常差旅记录
    liu_records = {
        "record_id": "rec_002",
        "trip_id": "trip_liu_202309",
        "employee": "老刘",
        "tier": "executive",
        "destination": "深圳",
        "duration_days": 3,
        "items": [
            {"category": "accommodation", "date": "2023-09-10", "amount": 1000.0, "description": "深圳万豪", "receipt": True, "vendor": "万豪", "nights": 1},
        ]
    }
    with open("records/trip_liu_202309.json", "w", encoding="utf-8") as f:
        json.dump(liu_records, f, ensure_ascii=False, indent=2)

    # 额外干扰：非JSON文件
    with open("records/notes.txt", "w") as f:
        f.write("这些记录都是小李的，别搞混了")

    # 确保report目录存在（初始为空）
    os.makedirs("report", exist_ok=True)

if __name__ == "__main__":
    build_env()
