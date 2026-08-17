import os
import json
import csv
from datetime import date

def build_env():
    # 创建目录
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/legacy_policies", exist_ok=True)  # 干扰目录
    os.makedirs("ops", exist_ok=True)                   # 无用目录

    # 平台数据 (3个)
    platforms = {
        "SKY001": {
            "platform_id": "SKY001",
            "name": "SkyBook",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 15.0,
            "service_fee": 10.0,
            "payment_methods": ["credit_card", "invoice"],
            "cancellation_policy": "free within 24h",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"tier": "silver"}
        },
        "AER001": {
            "platform_id": "AER001",
            "name": "AeroCheap",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 12.0,
            "service_fee": 8.0,
            "payment_methods": ["credit_card", "paypal"],
            "cancellation_policy": "non-refundable",
            "discounts": [{"code": "WELCOME10", "percent": 10}],
            "promotions": [],
            "loyalty_program": {"tier": "bronze"}
        },
        "FLP001": {
            "platform_id": "FLP001",
            "name": "FlightPro",
            "region": "Asia Pacific",
            "is_active": False,  # 已停用，干扰
            "transaction_fee": 20.0,
            "service_fee": 5.0,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "strict",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"tier": "gold"}
        }
    }
    for pid, pdata in platforms.items():
        with open(f"data/platforms/{pid}.json", "w") as f:
            json.dump(pdata, f, indent=2)

    # 政策数据 (3个版本)
    policies = {
        "acme_biz_v1": {
            "policy_id": "acme_biz",
            "name": "Acme Corp Business Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 5000,
            "max_single_booking_cost": 5000,
            "allowed_cabin_classes": ["economy", "premium_economy"],
            "min_advance_booking_days": 14,
            "requires_approval_above": 3000,
            "preferred_vendors": ["SkyBook", "AeroCheap"],
            "restricted_routes": [],
            "required_documents": [],
            "no_refund_cabin_classes": []
        },
        "acme_biz_v2": {
            "policy_id": "acme_biz",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.0",
            "max_cost_per_booking": 3000,
            "max_single_booking_cost": 3000,
            "allowed_cabin_classes": ["economy"],
            "min_advance_booking_days": 7,
            "requires_approval_above": 2000,
            "preferred_vendors": ["SkyBook", "AeroCheap"],
            "restricted_routes": [],
            "required_documents": [],
            "no_refund_cabin_classes": []
        },
        "acme_exec_v1": {
            "policy_id": "acme_exec",
            "name": "Acme Corp Executive Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 8000,
            "max_single_booking_cost": 8000,
            "allowed_cabin_classes": ["economy", "business", "first"],
            "min_advance_booking_days": 3,
            "requires_approval_above": 5000,
            "preferred_vendors": ["SkyBook"],
            "restricted_routes": [],
            "required_documents": [],
            "no_refund_cabin_classes": []
        }
    }
    for pid, pdata in policies.items():
        with open(f"data/policies/{pid}.json", "w") as f:
            json.dump(pdata, f, indent=2)

    # 旧政策干扰（放在legacy_policies目录下）
    legacy = {
        "acme_biz_v0.9": {
            "policy_id": "acme_biz",
            "name": "Acme Corp Business Travel Policy",
            "version": "0.9",
            "max_cost_per_booking": 4000,
            "allowed_cabin_classes": ["economy"],
            "min_advance_booking_days": 5
        }
    }
    for pid, pdata in legacy.items():
        with open(f"data/legacy_policies/{pid}.json", "w") as f:
            json.dump(pdata, f, indent=2)

    # 账户数据（无用，仅作背景）
    accounts = {
        "ACC001": {
            "account_id": "ACC001",
            "company_name": "Acme Corp",
            "travel_budget": 500000,
            "currency": "USD",
            "approvers": ["anna@acme.com"]
        }
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 预订记录CSV (包含重复、干扰)
    bookings = [
        # (booking_id, platform_id, cabin_class, total_cost, departure_date, booking_date)
        ("B001", "SKY001", "economy", 2500, "2026-06-20", "2026-06-10"),   # OK
        ("B002", "SKY001", "business", 4500, "2026-06-25", "2026-06-20"),  # 违规：舱位, 成本
        ("B002", "SKY001", "business", 4500, "2026-06-25", "2026-06-20"),  # 重复
        ("B003", "AER001", "economy", 3200, "2026-07-05", "2026-07-01"),   # 违规：成本, 提前天数
        ("B004", "FLP001", "economy", 2000, "2026-06-15", "2026-06-01"),   # 平台停用，但政策不检查平台状态，所以合规（成本<3000，经济舱，提前14天>=7）
        ("B005", "SKY001", "economy", 2800, "2026-07-10", "2026-07-01"),   # OK
        ("B006", "AER001", "premium_economy", 2900, "2026-06-30", "2026-06-25"), # 违规：舱位
        ("B007", "SKY001", "economy", 1500, "2026-06-05", "2026-05-01"),   # OK
        ("B008", "SKY001", "economy", 3500, "2026-08-01", "2026-07-15"),   # 违规：成本
    ]
    with open("data/bookings.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["booking_id", "platform_id", "cabin_class", "total_cost", "departure_date", "booking_date"])
        writer.writerows(bookings)

    # 一些额外的干扰文件
    with open("ops/daily_summary.txt", "w") as f:
        f.write("Q2 report pending\n")

if __name__ == "__main__":
    build_env()
