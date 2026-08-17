import os
import json
import random
from datetime import date, timedelta

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)  # 干扰目录
    os.makedirs("db_backups", exist_ok=True)  # 干扰目录

    # ========== 1. trip_info.json (唯一正确信息) ==========
    trip_info = {
        "trip_id": "trip_alpha",
        "employee_tier": "standard",
        "destination": "Shanghai",
        "days": 3,
        "start_date": "2024-11-04",
        "end_date": "2024-11-06"
    }
    with open("data/trip_info.json", "w") as f:
        json.dump(trip_info, f, indent=2)

    # ========== 2. travel_policies.json (含干扰旧政策) ==========
    policies = {
        "categories": [
            {
                "category_id": "accommodation",
                "name": "住宿",
                "reimbursable": True,
                "daily_limit": 500.0,   # 标准级别：500/晚
                "tier": "standard"
            },
            {
                "category_id": "food",
                "name": "餐饮",
                "reimbursable": True,
                "daily_limit": 200.0,
                "tier": "standard"
            },
            {
                "category_id": "flight",
                "name": "机票",
                "reimbursable": True,
                "daily_limit": 1500.0,  # 总额限制（非每日），这里简单按单次也做每日上限糊弄一下
                "tier": "standard"
            },
            {
                "category_id": "taxi",
                "name": "出租车",
                "reimbursable": True,
                "daily_limit": 100.0,
                "tier": "standard"
            },
            {
                "category_id": "metro",
                "name": "地铁公交",
                "reimbursable": True,
                "daily_limit": 50.0,
                "tier": "standard"
            },
            {
                "category_id": "communication",
                "name": "通讯费",
                "reimbursable": True,
                "daily_limit": 30.0,
                "tier": "standard"
            },
            {
                "category_id": "misc",
                "name": "其他杂费",
                "reimbursable": True,
                "daily_limit": 100.0,
                "tier": "standard"
            }
        ]
    }
    with open("data/travel_policies.json", "w") as f:
        json.dump(policies, f, indent=2)

    # 旧版干扰政策
    old_policies = {
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True, "daily_limit": 600.0},
            {"category_id": "food", "name": "餐饮", "reimbursable": True, "daily_limit": 180.0}
        ]
    }
    with open("data/travel_policies_old.json", "w") as f:
        json.dump(old_policies, f, indent=2)

    # ========== 3. consumption_records.json (含目标trip与其他干扰trip) ==========
    # 目标trip_alpha的消费记录（精心设计：住宿超支300，餐饮刚好，其他不超）
    target_records = [
        {"record_id": "r001", "category": "accommodation", "date": "2024-11-04", "amount": 500.0, "description": "酒店住宿第一晚", "receipt": True, "vendor": "锦江之星", "nights": 1},
        {"record_id": "r002", "category": "accommodation", "date": "2024-11-05", "amount": 600.0, "description": "酒店住宿第二晚", "receipt": True, "vendor": "锦江之星", "nights": 1},
        {"record_id": "r003", "category": "accommodation", "date": "2024-11-06", "amount": 700.0, "description": "酒店住宿第三晚", "receipt": True, "vendor": "锦江之星", "nights": 1},
        # 住宿合计 1800，预算 3*500=1500，超支300
        {"record_id": "r004", "category": "food", "date": "2024-11-04", "amount": 200.0, "description": "午餐", "receipt": True, "vendor": "小杨生煎"},
        {"record_id": "r005", "category": "food", "date": "2024-11-05", "amount": 250.0, "description": "晚餐", "receipt": True, "vendor": "外婆家"},
        {"record_id": "r006", "category": "food", "date": "2024-11-06", "amount": 150.0, "description": "早餐+午餐", "receipt": True, "vendor": "全家"},
        # 餐饮合计 600，预算 3*200=600，刚好
        {"record_id": "r007", "category": "taxi", "date": "2024-11-04", "amount": 80.0, "description": "机场到酒店", "receipt": True, "vendor": "滴滴"},
        {"record_id": "r008", "category": "taxi", "date": "2024-11-05", "amount": 45.0, "description": "酒店到客户", "receipt": True, "vendor": "滴滴"},
        # 出租车合计 125，预算 3*100=300，未超
        {"record_id": "r009", "category": "metro", "date": "2024-11-06", "amount": 12.0, "description": "地铁去高铁站", "receipt": True, "vendor": "上海地铁"},
        # 地铁合计12，预算150，未超
        {"record_id": "r010", "category": "communication", "date": "2024-11-04", "amount": 25.0, "description": "电话费", "receipt": True, "vendor": "中国移动"},
        # 通讯合计25，预算90，未超
        {"record_id": "r011", "category": "flight", "date": "2024-11-04", "amount": 1200.0, "description": "北京-上海机票", "receipt": True, "vendor": "国航"},
        # 机票1200，预算1500（视为单次上限），未超
        {"record_id": "r012", "category": "misc", "date": "2024-11-05", "amount": 50.0, "description": "打印资料", "receipt": True, "vendor": "打印店"},
    ]

    # 干扰 trip "trip_beta" 的消费
    interference_records = [
        {"record_id": "r101", "category": "accommodation", "date": "2024-10-10", "amount": 400.0, "description": "杭州出差", "receipt": True, "vendor": "汉庭", "nights": 2},
        {"record_id": "r102", "category": "food", "date": "2024-10-10", "amount": 350.0, "description": "晚餐", "receipt": True, "vendor": "绿茶"},
        {"record_id": "r103", "category": "taxi", "date": "2024-10-11", "amount": 120.0, "description": "打车", "receipt": True, "vendor": "滴滴"},
    ]

    # 合并并打乱顺序
    all_records = target_records + interference_records
    random.shuffle(all_records)

    # 为每条记录添加trip_id字段（但不在prompt中强调，让Agent自己从trip_info.json推断）
    # 实际设计：消费记录中不显式写trip_id，而是通过日期范围与trip_info匹配？更清晰的方式：每条记录带trip_id字段。
    # 我们显式添加trip_id，但agent需要读取trip_info中的trip_id然后筛选。
    for rec in target_records:
        rec["trip_id"] = "trip_alpha"
    for rec in interference_records:
        rec["trip_id"] = "trip_beta"

    consumption_data = {"records": all_records}
    with open("data/consumption_records.json", "w") as f:
        json.dump(consumption_data, f, indent=2)

    # ========== 4. 干扰文件 ==========
    # 旧版备份（完全无效）
    with open("data/consumption_records_backup.json", "w") as f:
        json.dump({"records": []}, f)

    # raw_logs 中无用的日志
    for i in range(3):
        with open(f"raw_logs/debug_{i}.log", "w") as f:
            f.write("2024-11-04 10:00:00 INFO: nothing relevant\n")

    # db_backups 中的假快照
    snapshot = {"trip": "trip_alpha", "total": 9999.0}
    with open("db_backups/snapshot_202411.json", "w") as f:
        json.dump(snapshot, f)

    # 创建一个空 ops 目录下的占位文件（让agent知道要写入）
    # 但不要预置答案，所以只放一个 readme.txt
    with open("ops/readme.txt", "w") as f:
        f.write("Place analysis results here.\n")

if __name__ == "__main__":
    build_env()
