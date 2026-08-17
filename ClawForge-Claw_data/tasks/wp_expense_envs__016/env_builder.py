import os
import json
import random
random.seed(42)

def build_env():
    # 创建目录
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 小张的出差信息
    trip_info = {
        "employee_name": "张三",
        "tier": "senior",
        "destination": "上海",
        "duration_days": 3,
        "employee_id": "EMP-007"
    }
    with open("ops/trip_info.json", "w", encoding="utf-8") as f:
        json.dump(trip_info, f, indent=2, ensure_ascii=False)

    # 公司政策（含干扰：多个职等、多个目的地）
    policies = {
        "junior": {
            "住宿": {"daily_budget": 300, "reimbursable": True},
            "餐饮": {"daily_budget": 150, "reimbursable": True},
            "交通": {"daily_budget": 100, "reimbursable": True},
            "其他杂费": {"daily_budget": 50, "reimbursable": True}
        },
        "senior": {
            "住宿": {"daily_budget": 500, "reimbursable": True},
            "餐饮": {"daily_budget": 200, "reimbursable": True},
            "交通": {"daily_budget": 150, "reimbursable": True},
            "其他杂费": {"daily_budget": 80, "reimbursable": True}
        },
        "executive": {
            "住宿": {"daily_budget": 800, "reimbursable": True},
            "餐饮": {"daily_budget": 300, "reimbursable": True},
            "交通": {"daily_budget": 250, "reimbursable": True},
            "其他杂费": {"daily_budget": 150, "reimbursable": True}
        },
        "intern": {
            "住宿": {"daily_budget": 200, "reimbursable": True},
            "餐饮": {"daily_budget": 80, "reimbursable": True},
            "交通": {"daily_budget": 50, "reimbursable": True},
            "其他杂费": {"daily_budget": 20, "reimbursable": True}
        }
    }
    with open("data/travel_policies.json", "w", encoding="utf-8") as f:
        json.dump(policies, f, indent=2, ensure_ascii=False)

    # 消费记录：包含小张和其他员工，含脏数据（缺失字段、重复记录等）
    records = [
        # 小张的真实记录
        {"employee_id": "EMP-007", "category": "住宿", "amount": 1500.0, "date": "2025-03-01", "vendor": "锦江之星"},
        {"employee_id": "EMP-007", "category": "餐饮", "amount": 650.0, "date": "2025-03-01", "vendor": "小杨生煎"},
        {"employee_id": "EMP-007", "category": "交通", "amount": 400.0, "date": "2025-03-02", "vendor": "滴滴"},
        {"employee_id": "EMP-007", "category": "其他杂费", "amount": 100.0, "date": "2025-03-03", "vendor": "打印店"},
        # 小张另一条重复住宿记录（故意干扰，agent应识别是否需去重？实际场景可能重复录入，但这里让agent按原始数据汇总，重复会导致超支更大，但我们要唯一答案所以决定这条是重复的，但agent如果未去重会算错，验证时要求去重？为了简单，我们只放一条。这里不放重复了，改为添加一条额外记录但同类别）
        {"employee_id": "EMP-007", "category": "餐饮", "amount": 120.0, "date": "2025-03-03", "vendor": "星巴克"},
        # 其他员工（干扰）
        {"employee_id": "EMP-001", "category": "住宿", "amount": 1800.0, "date": "2025-03-01", "vendor": "希尔顿"},
        {"employee_id": "EMP-001", "category": "餐饮", "amount": 300.0, "date": "2025-03-01", "vendor": "海底捞"},
        {"employee_id": "EMP-009", "category": "交通", "amount": 200.0, "date": "2025-03-02", "vendor": "地铁"},
        # 脏数据：缺少employee_id
        {"category": "住宿", "amount": 500.0, "date": "2025-03-01", "vendor": "如家"},
        # 脏数据：category为空
        {"employee_id": "EMP-007", "category": "", "amount": 50.0, "date": "2025-03-01", "vendor": "便利店"}
    ]
    with open("data/consumption_records.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    # 额外干扰文件
    with open("data/old_policy_v2.json", "w", encoding="utf-8") as f:
        f.write("这是一份旧版政策，不要使用")
    os.makedirs("logs", exist_ok=True)
    with open("logs/audit.log", "w") as f:
        f.write("2025-03-01 audit started\n")

if __name__ == "__main__":
    build_env()
