import os
import json
import random

def build_env():
    # 确保工作目录是 . (cwd)
    # 创建必要目录
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/consumption", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 生成政策文件 (3个, 只有 senior 是目标)
    standard_policy = {
        "tier": "standard",
        "duration_days": 3,
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "daily_limit": 500, "reimbursable": True},
            {"category_id": "food", "name": "餐饮", "daily_limit": 150, "reimbursable": True},
            {"category_id": "taxi", "name": "出租车", "daily_limit": 100, "reimbursable": True},
            {"category_id": "flight", "name": "机票", "daily_limit": 800, "reimbursable": True}
        ]
    }
    senior_policy = {
        "tier": "senior",
        "duration_days": 3,
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "daily_limit": 800, "reimbursable": True},
            {"category_id": "food", "name": "餐饮", "daily_limit": 300, "reimbursable": True},
            {"category_id": "taxi", "name": "出租车", "daily_limit": 200, "reimbursable": True},
            {"category_id": "flight", "name": "机票", "daily_limit": 1500, "reimbursable": True}
        ]
    }
    executive_policy = {
        "tier": "executive",
        "duration_days": 3,
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "daily_limit": 1200, "reimbursable": True},
            {"category_id": "food", "name": "餐饮", "daily_limit": 500, "reimbursable": True},
            {"category_id": "taxi", "name": "出租车", "daily_limit": 300, "reimbursable": True},
            {"category_id": "flight", "name": "机票", "daily_limit": 2500, "reimbursable": True}
        ]
    }
    with open("data/policies/standard_policy.json", "w") as f:
        json.dump(standard_policy, f, indent=2)
    with open("data/policies/senior_policy.json", "w") as f:
        json.dump(senior_policy, f, indent=2)
    with open("data/policies/executive_policy.json", "w") as f:
        json.dump(executive_policy, f, indent=2)

    # 2. 生成消费记录 (3个, 只有 trip_202312.json 是目标)
    # 目标记录: 住宿3晚共3000元 (每日1000 > 800), 餐饮共700 (合规), 出租车共500 (每日约167 > 200? 3天上限600, 500<600合规), 机票1600 (合规)
    # 住宿超支: 3000 - 2400 = 600; 出租车合规; 机票合规; 餐饮合规.
    # 总体预算: 住宿2400+餐饮900+出租车600+机票4500 = 8400; 实际: 3000+700+500+1600 = 5800; 实际小于预算? 不对, 住宿超支但总体仍低于预算? 需调整让总体也超支。
    # 重新设计: 让总体也超支。住宿3天800*3=2400, 实际3000 (超600); 餐饮900实际1000 (超100); 出租车600实际800 (超200); 机票4500实际5000 (超500). 总预算8400, 实际9800, 超1400.
    rec_trip = {
        "trip_id": "T-202312-01",
        "tier": "senior",
        "destination": "北京",
        "duration_days": 3,
        "records": [
            {"record_id": "R001", "category": "accommodation", "date": "2023-12-01", "amount": 1000.0, "description": "北京万达嘉华酒店", "receipt": True, "vendor": "万达", "nights": 1},
            {"record_id": "R002", "category": "accommodation", "date": "2023-12-02", "amount": 1000.0, "description": "北京万达嘉华酒店", "receipt": True, "vendor": "万达", "nights": 1},
            {"record_id": "R003", "category": "accommodation", "date": "2023-12-03", "amount": 1000.0, "description": "北京万达嘉华酒店", "receipt": True, "vendor": "万达", "nights": 1},
            {"record_id": "R004", "category": "food", "date": "2023-12-01", "amount": 300.0, "description": "午餐", "receipt": True, "vendor": "餐厅A"},
            {"record_id": "R005", "category": "food", "date": "2023-12-02", "amount": 350.0, "description": "晚餐", "receipt": True, "vendor": "餐厅B"},
            {"record_id": "R006", "category": "food", "date": "2023-12-03", "amount": 350.0, "description": "午餐+晚餐", "receipt": True, "vendor": "餐厅C"},
            {"record_id": "R007", "category": "taxi", "date": "2023-12-01", "amount": 250.0, "description": "酒店到机场", "receipt": True, "vendor": "滴滴"},
            {"record_id": "R008", "category": "taxi", "date": "2023-12-02", "amount": 300.0, "description": "市内交通", "receipt": True, "vendor": "滴滴"},
            {"record_id": "R009", "category": "taxi", "date": "2023-12-03", "amount": 250.0, "description": "酒店到机场", "receipt": True, "vendor": "滴滴"},
            {"record_id": "R010", "category": "flight", "date": "2023-12-01", "amount": 1500.0, "description": "上海-北京", "receipt": True, "vendor": "东方航空"},
            {"record_id": "R011", "category": "flight", "date": "2023-12-03", "amount": 1500.0, "description": "北京-上海", "receipt": True, "vendor": "东方航空"},
            {"record_id": "R012", "category": "flight", "date": "2023-12-03", "amount": 2000.0, "description": "升舱费", "receipt": True, "vendor": "东方航空"}
        ]
    }
    # 干扰记录 (11月, 1月)
    decoy1 = {
        "trip_id": "T-202311-01",
        "tier": "standard",
        "destination": "广州",
        "duration_days": 2,
        "records": [
            {"record_id": "R101", "category": "accommodation", "date": "2023-11-15", "amount": 400.0, "description": "酒店", "receipt": True, "vendor": "汉庭", "nights": 1},
            {"record_id": "R102", "category": "accommodation", "date": "2023-11-16", "amount": 400.0, "description": "酒店", "receipt": True, "vendor": "汉庭", "nights": 1}
        ]
    }
    decoy2 = {
        "trip_id": "T-202401-01",
        "tier": "executive",
        "destination": "深圳",
        "duration_days": 4,
        "records": [
            {"record_id": "R201", "category": "accommodation", "date": "2024-01-10", "amount": 1500.0, "description": "豪华酒店", "receipt": True, "vendor": "洲际", "nights": 1}
        ]
    }
    with open("data/consumption/trip_202311.json", "w") as f:
        json.dump(decoy1, f, indent=2)
    with open("data/consumption/trip_202312.json", "w") as f:
        json.dump(rec_trip, f, indent=2)
    with open("data/consumption/trip_202401.json", "w") as f:
        json.dump(decoy2, f, indent=2)

    # 3. 生成一个干扰的旧政策文件
    old_policy = {"tier": "old", "duration_days": 3, "categories": [{"category_id": "accommodation", "name": "住宿", "daily_limit": 200, "reimbursable": True}]}
    with open("data/old_policy.json", "w") as f:
        json.dump(old_policy, f, indent=2)

    # 4. 生成一个无关的 readme
    with open("data/README.txt", "w") as f:
        f.write("This directory contains expense data.\n")

if __name__ == "__main__":
    build_env()
