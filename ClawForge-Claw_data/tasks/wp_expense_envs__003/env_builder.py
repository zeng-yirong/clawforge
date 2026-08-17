import os
import json
import csv

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 员工信息
    employee_profile = {
        "employee_id": "E001",
        "tier": "senior",
        "name": "张三",
        "destination": "上海",
        "trip_duration_days": 3
    }
    with open("data/employee_profile.json", "w", encoding="utf-8") as f:
        json.dump(employee_profile, f, ensure_ascii=False, indent=2)

    # 旅行政策（含干扰项）
    policies = [
        {
            "tier": "standard",
            "destination": "北京",
            "duration_days": 2,
            "categories": [
                {"name": "住宿", "budget": 800.0},
                {"name": "餐饮", "budget": 400.0}
            ]
        },
        {
            "tier": "senior",
            "destination": "上海",
            "duration_days": 3,
            "categories": [
                {"name": "住宿", "budget": 1500.0},
                {"name": "餐饮", "budget": 600.0},
                {"name": "交通", "budget": 300.0}
            ]
        },
        {
            "tier": "executive",
            "destination": "上海",
            "duration_days": 5,
            "categories": [
                {"name": "住宿", "budget": 4000.0},
                {"name": "餐饮", "budget": 1500.0},
                {"name": "交通", "budget": 500.0}
            ]
        }
    ]
    with open("data/travel_policies.json", "w", encoding="utf-8") as f:
        json.dump(policies, f, ensure_ascii=False, indent=2)

    # 消费记录（含干扰数据，其他员工）
    records = [
        ["1", "E001", "住宿", "1200.0", "酒店A"],
        ["2", "E001", "住宿", "600.0", "酒店B"],
        ["3", "E001", "餐饮", "200.0", "午餐"],
        ["4", "E001", "餐饮", "180.0", "晚餐"],
        ["5", "E001", "餐饮", "120.0", "早餐"],
        ["6", "E001", "交通", "150.0", "出租车"],
        ["7", "E001", "交通", "130.0", "地铁"],
        ["8", "E002", "住宿", "500.0", "其他员工住宿"],
        ["9", "E002", "餐饮", "100.0", "其他员工餐饮"]
    ]
    with open("data/consumption_records.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["record_id", "employee_id", "category", "amount", "description"])
        writer.writerows(records)

    # 干扰文件
    with open("logs/debug.log", "w") as f:
        f.write("2025-01-15 info: system ready\n")

if __name__ == "__main__":
    build_env()
