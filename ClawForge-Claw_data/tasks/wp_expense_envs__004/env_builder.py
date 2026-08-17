import os
import json
import math

def build_env():
    # 确保根目录下有 policy 和 consumption 文件
    # travel_policies.json 包含 standard 等级各项日限额
    # 其他等级（senior, executive）作为干扰项存在但不使用
    policies = {
        "categories": [
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True, "daily_limit": 500.0, "tier": "standard"},
            {"category_id": "food", "name": "餐饮", "reimbursable": True, "daily_limit": 200.0, "tier": "standard"},
            {"category_id": "taxi", "name": "出租车", "reimbursable": True, "daily_limit": 200.0, "tier": "standard"},
            {"category_id": "flight", "name": "机票", "reimbursable": True, "daily_limit": 800.0, "tier": "standard"},
            {"category_id": "metro", "name": "地铁公交", "reimbursable": True, "daily_limit": 50.0, "tier": "standard"},
            {"category_id": "communication", "name": "通讯费", "reimbursable": True, "daily_limit": 50.0, "tier": "standard"},
            {"category_id": "misc", "name": "其他杂费", "reimbursable": True, "daily_limit": 100.0, "tier": "standard"},
            # 干扰：其他等级
            {"category_id": "accommodation", "name": "住宿", "reimbursable": True, "daily_limit": 800.0, "tier": "senior"},
            {"category_id": "food", "name": "餐饮", "reimbursable": True, "daily_limit": 350.0, "tier": "senior"},
            # 干扰：不可报销类别
            {"category_id": "shopping", "name": "购物", "reimbursable": False, "daily_limit": 0, "tier": "standard"}
        ]
    }
    with open("travel_policies.json", "w", encoding="utf-8") as f:
        json.dump(policies, f, indent=2)

    # consumption_records.json
    # 主 trip: TRIP-2024-001, 3天 (2024-03-10 ~ 2024-03-12)
    # 干扰记录：其他trip、无发票、过期日期、不属于standard等级? 这里不需要等级字段，因为消费记录不直接含等级，但可以通过关联trip来确定。
    # 但为了增加难度，添加一条其他trip的记录以及一条无发票的记录
    records = {
        "consumption_records": [
            # 超支类别：accommodation
            {"record_id": "R001", "trip_id": "TRIP-2024-001", "category": "accommodation", "date": "2024-03-10", "amount": 1900.0, "description": "希尔顿酒店", "receipt": True, "vendor": "Hilton", "nights": 4},
            # 未超支类别：food
            {"record_id": "R002", "trip_id": "TRIP-2024-001", "category": "food", "date": "2024-03-11", "amount": 550.0, "description": "客户午餐", "receipt": True, "vendor": "某餐厅"},
            # 未超支：taxi
            {"record_id": "R003", "trip_id": "TRIP-2024-001", "category": "taxi", "date": "2024-03-12", "amount": 480.0, "description": "机场打车", "receipt": True, "vendor": "滴滴"},
            # 超支：flight
            {"record_id": "R004", "trip_id": "TRIP-2024-001", "category": "flight", "date": "2024-03-10", "amount": 2500.0, "description": "北京往返机票", "receipt": True, "vendor": "国航"},
            # 未超支：metro
            {"record_id": "R005", "trip_id": "TRIP-2024-001", "category": "metro", "date": "2024-03-11", "amount": 120.0, "description": "地铁充值", "receipt": True, "vendor": "北京地铁"},
            # 未超支：communication
            {"record_id": "R006", "trip_id": "TRIP-2024-001", "category": "communication", "date": "2024-03-10", "amount": 80.0, "description": "电话漫游", "receipt": True, "vendor": "中国移动"},
            # 超支：misc
            {"record_id": "R007", "trip_id": "TRIP-2024-001", "category": "misc", "date": "2024-03-12", "amount": 350.0, "description": "出差杂项", "receipt": True, "vendor": "便利店"},
            # 干扰：无发票（不应计入实际）
            {"record_id": "R008", "trip_id": "TRIP-2024-001", "category": "food", "date": "2024-03-12", "amount": 180.0, "description": "夜宵（无票）", "receipt": False, "vendor": "路边摊"},
            # 干扰：其他trip
            {"record_id": "R009", "trip_id": "TRIP-2024-002", "category": "accommodation", "date": "2024-04-01", "amount": 1200.0, "description": "其他差旅", "receipt": True, "vendor": "如家"},
            # 干扰：不属于standard等级（假设这条记录是senior等级的，但trip_id不同，不过我们只筛选TRIP-2024-001，所以自动忽略）
            {"record_id": "R010", "trip_id": "TRIP-2024-003", "category": "flight", "date": "2024-05-01", "amount": 3000.0, "description": "高管出差", "receipt": True, "vendor": "南航"},
            # 干扰：不可报销类别 shopping
            {"record_id": "R011", "trip_id": "TRIP-2024-001", "category": "shopping", "date": "2024-03-11", "amount": 500.0, "description": "买纪念品", "receipt": True, "vendor": "商场"}
        ]
    }
    with open("consumption_records.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    # 创建输出目录 ops
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
