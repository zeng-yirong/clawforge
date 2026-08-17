import os
import json
import shutil
from pathlib import Path

def build_env():
    # 清理并重建工作目录
    cwd = Path(".")
    for item in cwd.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # 创建目录结构
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/bookings", exist_ok=True)
    os.makedirs("data/platforms", exist_ok=True)  # 干扰项
    os.makedirs("ops", exist_ok=True)  # 目标输出目录

    # === 政策文件（两个）===
    policies = {
        "acme_business_v2": {
            "policy_id": "acme_business_v2",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.0",
            "max_cost_per_booking": 5000,
            "max_single_booking_cost": 4000,
            "allowed_cabin_classes": ["economy", "business"],
            "min_advance_booking_days": 7,
            "requires_approval_above": 2000,
            "preferred_vendors": ["SkyBook", "AeroCheap"],
            "restricted_routes": [],
            "required_documents": ["boarding_pass", "invoice"],
            "no_refund_cabin_classes": ["economy"]
        },
        "acme_exec_v1": {
            "policy_id": "acme_exec_v1",
            "name": "Acme Corp Executive Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 10000,
            "max_single_booking_cost": 8000,
            "allowed_cabin_classes": ["business", "first"],
            "min_advance_booking_days": 3,
            "requires_approval_above": 5000,
            "preferred_vendors": ["FlightPro"],
            "restricted_routes": ["JFK-LHR"],
            "required_documents": ["boarding_pass", "visa"],
            "no_refund_cabin_classes": ["business"]
        }
    }
    for pid, data in policies.items():
        with open(f"data/policies/{pid}.json", "w") as f:
            json.dump(data, f, indent=2)

    # === 账户文件 ===
    accounts = {
        "acme_corp": {
            "account_id": "acme_corp",
            "company_name": "Acme Corp",
            "travel_budget": 50000,
            "currency": "USD",
            "approvers": ["Alice Smith", "Bob Johnson"]
        },
        "global_tech": {
            "account_id": "global_tech",
            "company_name": "Global Tech Inc.",
            "travel_budget": 80000,
            "currency": "USD",
            "approvers": ["Charlie Davis", "Eve White"]
        }
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # === 预订记录（5条，含干扰项）===
    bookings = {
        "booking_001": {
            "booking_id": "booking_001",
            "account_id": "acme_corp",
            "policy_id": "acme_business_v2",
            "total_cost": 2500,
            "status": "confirmed",
            "created_at": "2026-06-10"
        },
        "booking_002": {
            "booking_id": "booking_002",
            "account_id": "acme_corp",
            "policy_id": "acme_business_v2",
            "total_cost": 1500,
            "status": "confirmed",
            "created_at": "2026-06-11"
        },
        "booking_003": {
            "booking_id": "booking_003",
            "account_id": "global_tech",
            "policy_id": "acme_exec_v1",
            "total_cost": 8000,
            "status": "pending",
            "created_at": "2026-06-12"
        },
        "booking_004": {
            "booking_id": "booking_004",
            "account_id": "acme_corp",
            "policy_id": "acme_business_v2",
            "total_cost": 2200,
            "status": "cancelled",
            "created_at": "2026-06-09"
        },
        "booking_005": {
            "booking_id": "booking_005",
            "account_id": "global_tech",
            "policy_id": "acme_business_v2",
            "total_cost": 3000,
            "status": "confirmed",
            "created_at": "2026-06-13"
        }
    }
    for bid, data in bookings.items():
        with open(f"data/bookings/{bid}.json", "w") as f:
            json.dump(data, f, indent=2)

    # === 干扰项：平台记录（不参与核心任务）===
    platforms = [
        {"platform_id": "skybook", "name": "SkyBook", "region": "North America", "is_active": True, "transaction_fee": 15.0, "service_fee": 5.0, "payment_methods": ["credit_card", "paypal"], "cancellation_policy": "flexible", "discounts": [], "promotions": [], "loyalty_program": {"tier": "gold"}},
        {"platform_id": "aerocheap", "name": "AeroCheap", "region": "Europe", "is_active": False, "transaction_fee": 10.0, "service_fee": 3.0, "payment_methods": ["credit_card"], "cancellation_policy": "non_refundable", "discounts": [{"code": "SAVE10", "percent": 10}], "promotions": [], "loyalty_program": {"tier": "silver"}}
    ]
    for pl in platforms:
        with open(f"data/platforms/{pl['platform_id']}.json", "w") as f:
            json.dump(pl, f, indent=2)

if __name__ == "__main__":
    build_env()
