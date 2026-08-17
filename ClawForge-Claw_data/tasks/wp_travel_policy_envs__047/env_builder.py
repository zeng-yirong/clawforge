import os
import json
import datetime

def build_env():
    # 1. 创建 policies 目录，放入多个政策文件（干扰项）
    os.makedirs("policies", exist_ok=True)
    # 旧版本 v1.0
    old_policy_v1 = {
        "policy_id": "acme_corp_policy_v1",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 3000,
        "max_single_booking_cost": 1500,
        "allowed_cabin_classes": ["economy", "premium_economy"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 2000,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": [],
        "required_documents": [],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("policies/acme_corp_policy_v1.json", "w") as f:
        json.dump(old_policy_v1, f, indent=2)

    # 旧版本 v2.0
    old_policy_v2 = {
        "policy_id": "acme_corp_policy_v2",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 4000,
        "max_single_booking_cost": 2000,
        "allowed_cabin_classes": ["economy", "premium_economy", "business"],
        "min_advance_booking_days": 5,
        "requires_approval_above": 2500,
        "preferred_vendors": ["SkyBook", "FlightPro"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("policies/acme_corp_policy_v2.json", "w") as f:
        json.dump(old_policy_v2, f, indent=2)

    # 当前有效政策 v2.1
    current_policy = {
        "policy_id": "acme_corp_policy_v2_1",
        "name": "Acme Corp Executive Travel Policy",
        "version": "2.1",
        "max_cost_per_booking": 3500,
        "max_single_booking_cost": 1800,
        "allowed_cabin_classes": ["economy", "premium_economy", "business"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 2000,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": [["JFK", "LHR"]],  # JFK->LHR 需要特别审批，此处视为合规前提不达标
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("policies/current_policy.json", "w") as f:
        json.dump(current_policy, f, indent=2)

    # 2. 创建 requests 目录，放入10个请求（有合规的和不合规的）
    os.makedirs("requests", exist_ok=True)
    # 参考日期：假设当前日期是 2026-05-20
    today = datetime.date(2026, 5, 20)

    requests_data = [
        # req_001: total cost 1600, cabin business, departure 2026-06-01 (提前12天 > 7), 合规
        {"request_id": "REQ-001", "origin": "SFO", "destination": "ORD", "departure_date": "2026-06-01",
         "cabin_class": "business", "total_cost": 1600, "currency": "USD"},
        # req_002: total cost 2000 > max_single_booking_cost 1800, 违反
        {"request_id": "REQ-002", "origin": "LAX", "destination": "JFK", "departure_date": "2026-06-10",
         "cabin_class": "business", "total_cost": 2000, "currency": "USD"},
        # req_003: cabin economy 允许, total 1500, departure 2026-05-25 (提前5天 < 7), 违反最小提前天数
        {"request_id": "REQ-003", "origin": "ORD", "destination": "DFW", "departure_date": "2026-05-25",
         "cabin_class": "economy", "total_cost": 1500, "currency": "USD"},
        # req_004: total 3500 == max_cost_per_booking 允许, 但这是总价? max_cost_per_booking 是单次预订总价上限，合规
        {"request_id": "REQ-004", "origin": "ATL", "destination": "MIA", "departure_date": "2026-06-05",
         "cabin_class": "economy", "total_cost": 3500, "currency": "USD"},
        # req_005: cabin first_class 不在 allowed_cabin_classes 中, 违反
        {"request_id": "REQ-005", "origin": "SEA", "destination": "DEN", "departure_date": "2026-06-20",
         "cabin_class": "first_class", "total_cost": 2500, "currency": "USD"},
        # req_006: 航线 JFK->LHR 在 restricted_routes, 但政策未明确禁止，只是需要特殊审批？ 严格来说需要额外审批但此处视为合规（因为我们只检查明确的违反项），但根据政策v2.1 restricted_routes 可能意味着不允许? 为了有争议，我们让它合规，不触发错误。
        {"request_id": "REQ-006", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15",
         "cabin_class": "business", "total_cost": 3000, "currency": "USD"},
        # req_007: total 1800 == max_single_booking_cost 允许, 提前10天 > 7, 合规
        {"request_id": "REQ-007", "origin": "BOS", "destination": "SFO", "departure_date": "2026-06-01",
         "cabin_class": "premium_economy", "total_cost": 1800, "currency": "USD"},
        # req_008: 提前天数不足, departure 2026-05-22 (提前2天 < 7), 违反
        {"request_id": "REQ-008", "origin": "MIA", "destination": "ORD", "departure_date": "2026-05-22",
         "cabin_class": "economy", "total_cost": 800, "currency": "USD"},
        # req_009: total 4000 > max_cost_per_booking 3500, 违反
        {"request_id": "REQ-009", "origin": "LAX", "destination": "ORD", "departure_date": "2026-06-10",
         "cabin_class": "business", "total_cost": 4000, "currency": "USD"},
        # req_010: cabin economy 允许, total 1200, 提前8天 > 7, 合规
        {"request_id": "REQ-010", "origin": "DEN", "destination": "SEA", "departure_date": "2026-05-28",
         "cabin_class": "economy", "total_cost": 1200, "currency": "USD"},
    ]

    for req_dict in requests_data:
        with open(f"requests/{req_dict['request_id']}.json", "w") as f:
            json.dump(req_dict, f, indent=2)

    # 3. 创建 ops 目录，放入一个干扰文件
    os.makedirs("ops", exist_ok=True)
    with open("ops/temp_notes.txt", "w") as f:
        f.write("This is a temporary note from Anna's assistant. Ignore this.\n")

    # 4. 创建一些无关文件进一步迷惑
    with open("readme_old.txt", "w") as f:
        f.write("Old readme, not relevant.\n")
    os.makedirs("archives", exist_ok=True)
    with open("archives/backup_policy_v1.json", "w") as f:
        json.dump(old_policy_v1, f, indent=2)

if __name__ == "__main__":
    build_env()
