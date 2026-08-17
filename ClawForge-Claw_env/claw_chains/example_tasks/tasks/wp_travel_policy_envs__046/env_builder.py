import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ----- 有效政策（版本2，当前生效） -----
    policy_v2 = {
        "policy_id": "acme_business_travel_v2",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "is_active": True,
        "max_cost_per_booking": 10000,
        "max_single_booking_cost": 10000,
        "allowed_cabin_classes": ["business"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 8000,
        "preferred_vendors": ["sky_book"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/policies/acme_business_travel_v2.json", "w") as f:
        json.dump(policy_v2, f, indent=2)

    # ----- 干扰政策（旧版本）-----
    policy_v1 = {
        "policy_id": "acme_business_travel_v1",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "is_active": False,
        "max_cost_per_booking": 5000,
        "max_single_booking_cost": 5000,
        "allowed_cabin_classes": ["economy", "business"],
        "min_advance_booking_days": 5,
        "requires_approval_above": 4000,
        "preferred_vendors": ["aero_cheap"],
        "restricted_routes": ["LHR"],
        "required_documents": ["visa"],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/policies/acme_business_travel_v1.json", "w") as f:
        json.dump(policy_v1, f, indent=2)

    # ----- 干扰政策（草稿，未生效）-----
    policy_draft = {
        "policy_id": "acme_business_travel_draft",
        "name": "Acme Corp Business Travel Policy (Draft)",
        "version": "draft",
        "is_active": False,
        "max_cost_per_booking": 12000,
        "max_single_booking_cost": 12000,
        "allowed_cabin_classes": ["first", "business"],
        "min_advance_booking_days": 1,
        "requires_approval_above": 10000,
        "preferred_vendors": ["flight_pro", "sky_book"],
        "restricted_routes": [],
        "required_documents": [],
        "no_refund_cabin_classes": []
    }
    with open("data/policies/acme_business_travel_draft.json", "w") as f:
        json.dump(policy_draft, f, indent=2)

    # ----- 平台：SkyBook（首选供应商）-----
    sky_book = {
        "platform_id": "sky_book",
        "name": "SkyBook",
        "region": "North America",
        "is_active": True,
        "transaction_fee": 20.0,
        "service_fee": 15.0,
        "payment_methods": ["credit_card", "company_account"],
        "cancellation_policy": "free up to 24h",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"points_rate": 0.05},
        "flights": [
            {
                "flight_id": "SB-123",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "price": 8500
            },
            {
                "flight_id": "SB-456",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "economy",
                "price": 3200
            }
        ]
    }
    with open("data/platforms/sky_book.json", "w") as f:
        json.dump(sky_book, f, indent=2)

    # ----- 平台：AeroCheap（非首选，价格低但超过政策预算？实际9500在10000以内，但非首选，且政策要求首选）-----
    aero_cheap = {
        "platform_id": "aero_cheap",
        "name": "AeroCheap",
        "region": "Europe",
        "is_active": True,
        "transaction_fee": 10.0,
        "service_fee": 5.0,
        "payment_methods": ["credit_card"],
        "cancellation_policy": "no refund after 48h",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"points_rate": 0.02},
        "flights": [
            {
                "flight_id": "AC-789",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "price": 9500
            }
        ]
    }
    with open("data/platforms/aero_cheap.json", "w") as f:
        json.dump(aero_cheap, f, indent=2)

    # ----- 平台：FlightPro（非首选，超预算）-----
    flight_pro = {
        "platform_id": "flight_pro",
        "name": "FlightPro",
        "region": "Asia Pacific",
        "is_active": True,
        "transaction_fee": 25.0,
        "service_fee": 20.0,
        "payment_methods": ["credit_card", "paypal"],
        "cancellation_policy": "non-refundable",
        "discounts": [],
        "promotions": [],
        "loyalty_program": {"points_rate": 0.08},
        "flights": [
            {
                "flight_id": "FP-001",
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2026-06-15",
                "cabin_class": "business",
                "price": 12000
            }
        ]
    }
    with open("data/platforms/flight_pro.json", "w") as f:
        json.dump(flight_pro, f, indent=2)

if __name__ == "__main__":
    build_env()
