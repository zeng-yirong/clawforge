import os
import json
import shutil

def build_env():
    # 清理并创建目录
    for d in ["data/platforms", "data/policies", "data", "ops"]:
        os.makedirs(d, exist_ok=True)

    # ---------- 平台数据 ----------
    # AeroCheap (有效，最低价)
    aero = {
        "platform_id": "aero_cheap",
        "name": "AeroCheap",
        "region": "North America",
        "is_active": True,
        "transaction_fee": 30,
        "service_fee": 20,
        "payment_methods": ["visa", "mastercard"],
        "cancellation_policy": "non-refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"tier": "silver", "points": 0},
        "flights": [
            {
                "flight_id": "aero-cheap-flt-001",
                "origin": "JFK",
                "destination": "LHR",
                "date": "2026-06-15",
                "cabin_class": "business",
                "price": 1800.0
            }
        ]
    }
    # FlightPro (有效，稍贵)
    flightpro = {
        "platform_id": "flight_pro",
        "name": "FlightPro",
        "region": "Europe",
        "is_active": True,
        "transaction_fee": 25,
        "service_fee": 15,
        "payment_methods": ["amex", "paypal"],
        "cancellation_policy": "flexible",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"tier": "gold", "points": 500},
        "flights": [
            {
                "flight_id": "flightpro-flt-002",
                "origin": "JFK",
                "destination": "LHR",
                "date": "2026-06-15",
                "cabin_class": "business",
                "price": 1900.0
            }
        ]
    }
    # SkyBook (有效，但价格超政策上限)
    skybook = {
        "platform_id": "sky_book",
        "name": "SkyBook",
        "region": "Asia Pacific",
        "is_active": True,
        "transaction_fee": 40,
        "service_fee": 10,
        "payment_methods": ["visa", "mastercard", "amex"],
        "cancellation_policy": "non-refundable",
        "discounts": [{"code": "WELCOME10", "percent": 10}],
        "promotions": [],
        "loyalty_program": {"tier": "platinum", "points": 2000},
        "flights": [
            {
                "flight_id": "skybook-flt-003",
                "origin": "JFK",
                "destination": "LHR",
                "date": "2026-06-15",
                "cabin_class": "business",
                "price": 2050.0
            }
        ]
    }
    # 干扰项：已停用的旧平台（价格更低但不活跃）
    old_platform = {
        "platform_id": "old_express",
        "name": "OldExpress",
        "region": "Europe",
        "is_active": False,
        "transaction_fee": 10,
        "service_fee": 5,
        "payment_methods": ["cash"],
        "cancellation_policy": "non-refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"tier": "bronze", "points": 0},
        "flights": [
            {
                "flight_id": "old-flt-004",
                "origin": "JFK",
                "destination": "LHR",
                "date": "2026-06-15",
                "cabin_class": "business",
                "price": 1700.0
            }
        ]
    }

    for fname, data in [("aero_cheap.json", aero),
                        ("flight_pro.json", flightpro),
                        ("sky_book.json", skybook),
                        ("old_express.json", old_platform)]:
        with open(f"data/platforms/{fname}", "w") as f:
            json.dump(data, f, indent=2)

    # ---------- 政策数据 ----------
    # 适用 Business Travel Policy (唯一符合要求的)
    business_policy = {
        "policy_id": "bus_pol_001",
        "name": "Acme Corp Business Travel Policy",
        "version": "v2",
        "max_cost_per_booking": 2000,
        "max_single_booking_cost": 2000,
        "allowed_cabin_classes": ["business", "economy"],
        "min_advance_booking_days": 0,
        "requires_approval_above": 1500,
        "preferred_vendors": ["AeroCheap", "FlightPro"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["business"]
    }
    # 干扰政策：Executive 版本（不适用于普通员工）
    executive_policy = {
        "policy_id": "exec_pol_002",
        "name": "Acme Corp Executive Travel Policy",
        "version": "v1",
        "max_cost_per_booking": 5000,
        "max_single_booking_cost": 5000,
        "allowed_cabin_classes": ["first", "business"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 3000,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": []
    }
    with open("data/policies/business_policy.json", "w") as f:
        json.dump(business_policy, f, indent=2)
    with open("data/policies/executive_policy.json", "w") as f:
        json.dump(executive_policy, f, indent=2)

    # ---------- 账户数据（仅作背景） ----------
    accounts = [
        {"account_id": "acc_001", "company_name": "Acme Corp", "travel_budget": 50000, "currency": "USD", "approvers": ["boss@acme.com"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---------- 干扰文件 ----------
    with open("data/README.md", "w") as f:
        f.write("# Platform Data\nPlaceholder for platform price dumps.\n")

if __name__ == "__main__":
    build_env()
