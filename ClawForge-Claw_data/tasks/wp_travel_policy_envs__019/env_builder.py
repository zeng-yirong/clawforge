import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("raw_data/policies", exist_ok=True)
    os.makedirs("raw_data/quotes", exist_ok=True)
    os.makedirs("raw_data/archive", exist_ok=True)

    # 1. 有效的政策 v2（当前版本）
    policy_v2 = {
        "policy_id": "pol_v2",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 2000,
        "max_single_booking_cost": 2000,
        "allowed_cabin_classes": ["economy"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 1500,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": [],
        "required_documents": [],
        "no_refund_cabin_classes": []
    }
    with open("raw_data/policies/policy_v2.json", "w") as f:
        json.dump(policy_v2, f, indent=2)

    # 2. 过时政策 v1（干扰项）
    policy_v1 = {
        "policy_id": "pol_v1",
        "name": "Acme Corp Executive Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 3000,
        "max_single_booking_cost": 3000,
        "allowed_cabin_classes": ["business", "first"],
        "min_advance_booking_days": 1,
        "requires_approval_above": 2500,
        "preferred_vendors": ["FlightPro"],
        "restricted_routes": [],
        "required_documents": [],
        "no_refund_cabin_classes": []
    }
    with open("raw_data/policies/policy_v1.json", "w") as f:
        json.dump(policy_v1, f, indent=2)

    # 3. 报价文件
    # SkyBook 经济舱报价：裸价 $1300，手续费 transaction_fee=20，service_fee=10，促销 SAVE50 减 $50
    skybook_quote = {
        "platform_id": "skybook",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "economy",
        "price": 1300,
        "transaction_fee": 20,
        "service_fee": 10,
        "promotions": [{"code": "SAVE50", "discount_amount": 50}]
    }
    with open("raw_data/quotes/skybook_quote.json", "w") as f:
        json.dump(skybook_quote, f, indent=2)

    # AeroCheap 经济舱报价（干扰，不是首选平台）
    aerocheap_quote = {
        "platform_id": "aerocheap",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "economy",
        "price": 1200,
        "transaction_fee": 15,
        "service_fee": 5,
        "promotions": []
    }
    with open("raw_data/quotes/aerocheap_quote.json", "w") as f:
        json.dump(aerocheap_quote, f, indent=2)

    # FlightPro 商务舱报价（干扰，舱位不符合政策允许的经济舱）
    flightpro_quote = {
        "platform_id": "flightpro",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "business",
        "price": 1800,
        "transaction_fee": 30,
        "service_fee": 15,
        "promotions": []
    }
    with open("raw_data/quotes/flightpro_quote.json", "w") as f:
        json.dump(flightpro_quote, f, indent=2)

    # 4. 预订申请
    booking_request = {
        "trip_id": "TRIP-019",
        "employee": "Alice",
        "origin": "JFK",
        "destination": "LHR",
        "departure_date": "2026-06-15",
        "cabin_class": "economy",
        "passengers": 1,
        "preferred_platform": "SkyBook"
    }
    with open("raw_data/booking_request.json", "w") as f:
        json.dump(booking_request, f, indent=2)

    # 5. 干扰文件：账户信息（无关）
    accounts = {
        "account_id": "acme_corp",
        "company_name": "Acme Corp",
        "travel_budget": 100000,
        "currency": "USD",
        "approvers": ["Emma", "John"]
    }
    with open("raw_data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 6. 干扰：空日志文件
    with open("raw_data/archive/audit.log", "w") as f:
        f.write("")

    # 7. 额外干扰：过期促销优惠（不适用于该行程）
    old_promo = {
        "code": "WINTER20",
        "valid_until": "2026-03-01",
        "discount_amount": 20
    }
    with open("raw_data/archive/old_promotions.json", "w") as f:
        json.dump(old_promo, f, indent=2)

if __name__ == "__main__":
    build_env()
