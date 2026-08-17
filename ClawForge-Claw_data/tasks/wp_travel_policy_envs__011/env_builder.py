import os
import json
import random
import shutil

def build_env():
    # 清理残留（如果之前运行过）
    for d in ["data", "ops", "logs", "temp", "backup"]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)
    
    # ---------- 政策文件 ----------
    # 有效政策
    current_policy = {
        "policy_id": "POL_ACM_2026",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "effective_date": "2026-01-01",
        "max_cost_per_booking": 5000,
        "max_single_booking_cost": 2500,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 1500,
        "preferred_vendors": ["FlightPro"],
        "restricted_routes": [],
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["economy"]
    }
    os.makedirs("data/policies", exist_ok=True)
    with open("data/policies/current_policy.json", "w") as f:
        json.dump(current_policy, f, indent=2)
    
    # 干扰的过期政策
    obsolete_policy = {
        "policy_id": "POL_ACM_2025",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "effective_date": "2025-01-01",
        "max_single_booking_cost": 2000,
        "allowed_cabin_classes": ["business", "premium_economy"],
        "min_advance_booking_days": 7,
        "requires_approval_above": 1000,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": []
    }
    os.makedirs("data/policies/archived", exist_ok=True)
    with open("data/policies/archived/obsolete_policy.json", "w") as f:
        json.dump(obsolete_policy, f, indent=2)
    
    # ---------- 平台与报价 ----------
    # 定义三个平台（一个停运）
    platforms = {
        "flightpro": {
            "platform_id": "FlightPro",
            "name": "FlightPro",
            "region": "North America",
            "is_active": True,
            "transaction_fee": 15.0,
            "service_fee": 20.0,
            "payment_methods": ["credit_card", "invoice"],
            "cancellation_policy": "free cancellation 24h before departure",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"name": "ProRewards", "tier": "Gold"}
        },
        "skybook": {
            "platform_id": "SkyBook",
            "name": "SkyBook",
            "region": "Europe",
            "is_active": True,
            "transaction_fee": 25.0,
            "service_fee": 30.0,
            "payment_methods": ["credit_card"],
            "cancellation_policy": "50% refund if cancelled 48h before",
            "discounts": [{"code": "WELCOME10", "percent": 10}],
            "promotions": [{"desc": "Summer Sale", "discount": 100}],
            "loyalty_program": {"name": "SkyMiles", "tier": "Silver"}
        },
        "aerocheap": {
            "platform_id": "AeroCheap",
            "name": "AeroCheap",
            "region": "Asia Pacific",
            "is_active": False,  # 已停运
            "transaction_fee": 5.0,
            "service_fee": 10.0,
            "payment_methods": ["debit_card"],
            "cancellation_policy": "no refund",
            "discounts": [],
            "promotions": [],
            "loyalty_program": {"name": "AeroPoints", "tier": "Bronze"}
        }
    }
    
    # 为每个平台创建报价（每个平台只放一个航班，代表该平台最低商务舱报价）
    offers = {
        "flightpro": {
            "flight_id": "FLP-20260615-001",
            "platform_id": "FlightPro",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-15",
            "cabin_class": "business",
            "price": 2200.00,
            "currency": "USD",
            "seats_available": 4,
            "platform_is_active": True
        },
        "skybook": {
            "flight_id": "SKB-20260615-003",
            "platform_id": "SkyBook",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-15",
            "cabin_class": "business",
            "price": 2400.00,
            "currency": "USD",
            "seats_available": 2,
            "platform_is_active": True
        },
        "aerocheap": {
            "flight_id": "ACH-20260615-007",
            "platform_id": "AeroCheap",
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2026-06-15",
            "cabin_class": "business",
            "price": 1800.00,
            "currency": "USD",
            "seats_available": 0,
            "platform_is_active": False  # 与平台停运一致
        }
    }
    
    # 为每个平台创建目录和报价 JSON
    for plat_id, plat_info in platforms.items():
        plat_dir = f"data/offers/{plat_id}"
        os.makedirs(plat_dir, exist_ok=True)
        # 平台元数据（干扰项，但 agent 不需要读这个）
        with open(f"{plat_dir}/platform_info.json", "w") as f:
            json.dump(plat_info, f, indent=2)
        # 报价文件
        if plat_id in offers:
            with open(f"{plat_dir}/offer.json", "w") as f:
                json.dump(offers[plat_id], f, indent=2)
    
    # ---------- 干扰文件 ----------
    # logs 目录下放一些无关日志
    os.makedirs("logs", exist_ok=True)
    with open("logs/server.log", "w") as f:
        f.write("2026-06-10 08:00:00 INFO Server started\n")
        f.write("2026-06-10 08:05:00 WARN Connection timeout\n")
    
    # temp 目录下放临时备份（带旧报价）
    os.makedirs("temp/offers_backup", exist_ok=True)
    old_offer = {
        "flight_id": "FLP-20250615-001",
        "platform_id": "FlightPro",
        "origin": "JFK",
        "destination": "LHR",
        "cabin_class": "economy",
        "price": 800.00,
        "platform_is_active": True
    }
    with open("temp/offers_backup/old_offer.json", "w") as f:
        json.dump(old_offer, f, indent=2)
    
    # 创建 ops 目录（空，等 agent 写结果）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
