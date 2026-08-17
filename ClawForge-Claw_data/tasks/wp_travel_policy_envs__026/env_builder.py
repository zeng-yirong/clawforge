import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 政策文件（包含干扰项）
    policies = {
        "policy_v1.json": {
            "policy_id": "travel_policy_v1",
            "name": "Acme Corp Business Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 1500,
            "allowed_cabin_classes": ["economy"],
            "requires_approval_above": 1000,
            "preferred_vendors": ["aero_cheap"]
        },
        "policy_v2.json": {
            "policy_id": "travel_policy_v2",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.0",
            "max_cost_per_booking": 5000,
            "allowed_cabin_classes": ["economy", "business"],
            "requires_approval_above": 3000,
            "preferred_vendors": ["aero_cheap"]
        },
        "policy_draft.json": {
            "policy_id": "travel_policy_draft",
            "name": "Draft Policy",
            "version": "2.1-draft",
            "max_cost_per_booking": 6000,
            "allowed_cabin_classes": ["economy", "business", "first"],
            "requires_approval_above": 4000,
            "preferred_vendors": []
        }
    }
    for fname, content in policies.items():
        with open(f"data/policies/{fname}", "w") as f:
            json.dump(content, f, indent=2)

    # 平台报价（包含干扰项：不活跃平台、无效报价）
    platforms = {
        "aero_cheap_quotes.json": {
            "platform_id": "aero_cheap",
            "is_active": True,
            "quotes": [
                {"flight_id": "AC-1234", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "economy", "price": 1800, "currency": "USD"},
                {"flight_id": "AC-5678", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "business", "price": 4800, "currency": "USD"}
            ]
        },
        "flight_pro_quotes.json": {
            "platform_id": "flight_pro",
            "is_active": True,
            "quotes": [
                {"flight_id": "FP-9012", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "economy", "price": 2200, "currency": "USD"},
                {"flight_id": "FP-3456", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "business", "price": 4500, "currency": "USD"}
            ]
        },
        "sky_book_quotes.json": {
            "platform_id": "sky_book",
            "is_active": True,
            "quotes": [
                {"flight_id": "SB-7890", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "economy", "price": 2400, "currency": "USD"},
                {"flight_id": "SB-1112", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "business", "price": 5100, "currency": "USD"}
            ]
        },
        "defunct_platform_quotes.json": {
            "platform_id": "defunct_air",
            "is_active": False,
            "quotes": [
                {"flight_id": "DA-0001", "origin": "JFK", "destination": "LHR", "departure_date": "2026-06-15", "cabin_class": "economy", "price": 1500, "currency": "USD"}
            ]
        }
    }
    for fname, content in platforms.items():
        with open(f"data/platforms/{fname}", "w") as f:
            json.dump(content, f, indent=2)
