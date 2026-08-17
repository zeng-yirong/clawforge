import json
import os

def build_env():
    # 创建目录结构
    os.makedirs("data/policies", exist_ok=True)
    os.makedirs("data/platforms", exist_ok=True)
    os.makedirs("data/bookings", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- 政策文件 ----
    # 旧政策（v1.0）—— 干扰
    policy_old = {
        "policy_id": "acme_corp_2025",
        "name": "Acme Corp Business Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 5000,
        "max_single_booking_cost": 3000,
        "allowed_cabin_classes": ["economy", "premium_economy"],
        "min_advance_booking_days": 3,
        "requires_approval_above": 2500,
        "preferred_vendors": ["AeroCheap"],
        "restricted_routes": ["JFK-LHR"],
        "required_documents": [],
        "no_refund_cabin_classes": ["economy"]
    }
    with open("data/policies/acme_corp_2025_v1.0.json", "w") as f:
        json.dump(policy_old, f, indent=2)

    # 新政策（v2.0）—— 目标用这个
    policy_new = {
        "policy_id": "acme_corp_2026",
        "name": "Acme Corp Business Travel Policy",
        "version": "2.0",
        "max_cost_per_booking": 6000,
        "max_single_booking_cost": 3500,
        "allowed_cabin_classes": ["economy", "premium_economy", "business"],
        "min_advance_booking_days": 5,
        "requires_approval_above": 2000,
        "preferred_vendors": ["SkyBook", "FlightPro"],
        "restricted_routes": ["JFK-LHR", "CDG-NRT"],
        "required_documents": ["passport", "visa"],
        "no_refund_cabin_classes": ["economy", "business"]
    }
    with open("data/policies/acme_corp_2026_v2.0.json", "w") as f:
        json.dump(policy_new, f, indent=2)

    # 另一个无关政策（干扰）
    policy_exec = {
        "policy_id": "acme_exec_2026",
        "name": "Acme Corp Executive Travel Policy",
        "version": "1.0",
        "max_cost_per_booking": 12000,
        "max_single_booking_cost": 8000,
        "allowed_cabin_classes": ["business", "first"],
        "min_advance_booking_days": 2,
        "requires_approval_above": 5000,
        "preferred_vendors": ["SkyBook"],
        "restricted_routes": [],
        "required_documents": ["passport"],
        "no_refund_cabin_classes": ["first"]
    }
    with open("data/policies/acme_exec_2026_v1.0.json", "w") as f:
        json.dump(policy_exec, f, indent=2)

    # ---- 平台数据 ----
    platforms = [
        {"platform_id": "skybook", "name": "SkyBook", "region": "North America", "is_active": True,
         "transaction_fee": 25.0, "service_fee": 15.0, "payment_methods": ["credit_card", "company_account"],
         "cancellation_policy": "free_before_24h", "discounts": [{"code": "WELCOME10", "percent": 10}],
         "promotions": [{"id": "PROMO_JUN", "description": "Summer sale"}], "loyalty_program": {"name": "SkyMiles", "tier": "gold"}},
        {"platform_id": "aerocheap", "name": "AeroCheap", "region": "Europe", "is_active": True,
         "transaction_fee": 10.0, "service_fee": 5.0, "payment_methods": ["credit_card"],
         "cancellation_policy": "no_refund", "discounts": [], "promotions": [],
         "loyalty_program": {"name": "AeroPoints", "tier": "silver"}},
        {"platform_id": "flightpro", "name": "FlightPro", "region": "Asia Pacific", "is_active": False,  # 干扰：停用平台
         "transaction_fee": 30.0, "service_fee": 20.0, "payment_methods": ["credit_card", "paypal"],
         "cancellation_policy": "partial_refund", "discounts": [{"code": "FLY10", "percent": 10}],
         "promotions": [], "loyalty_program": {"name": "ProPoints", "tier": "platinum"}}
    ]
    for p in platforms:
        with open(f"data/platforms/{p['platform_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    # ---- 账户信息 ----
    account = {
        "account_id": "acme_corp_main",
        "company_name": "Acme Corp",
        "travel_budget": 500000,
        "currency": "USD",
        "approvers": ["alice@acme.com", "bob@acme.com", "charlie@acme.com"]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(account, f, indent=2)

    # ---- 预订记录 ----
    # 每条记录格式：booking_id, route, cabin_class, total_cost, status, platform_id, created_at, departure_date
    # 故意制造多种情况
    bookings = [
        # 违规1: 费用超 max_single_booking_cost (3500) 且超 requires_approval_above (2000)
        {"booking_id": "BK-101", "route": "JFK-LHR", "cabin_class": "business", "total_cost": 4200,
         "status": "confirmed", "platform_id": "skybook", "created_at": "2026-05-01", "departure_date": "2026-06-01"},
        # 违规2: 需要文件但未提供 (但实际上我们只检查政策, 这里标记 violation 为 "missing_required_documents")
        # 但我们在 violations 中表述为 "missing required documents"  (policy requires passport & visa)
        {"booking_id": "BK-202", "route": "CDG-NRT", "cabin_class": "economy", "total_cost": 2800,
         "status": "pending", "platform_id": "aerocheap", "created_at": "2026-05-10", "departure_date": "2026-05-20"},
        # 合规: 总费用2000以下, 舱位允许, 提前天数足够
        {"booking_id": "BK-303", "route": "LHR-JFK", "cabin_class": "economy", "total_cost": 1500,
         "status": "confirmed", "platform_id": "skybook", "created_at": "2026-05-15", "departure_date": "2026-06-10"},
        # 违规3: 预定提前天数不足 (min_advance_booking_days=5, 创建到出发只有4天)
        {"booking_id": "BK-404", "route": "JFK-LHR", "cabin_class": "business", "total_cost": 3100,
         "status": "confirmed", "platform_id": "skybook", "created_at": "2026-05-28", "departure_date": "2026-06-01"},
        # 违规4: 使用了非优选供应商 (AeroCheap 不在 preferred_vendors 里)
        # 但是注意: aerocheap 是停用平台? 但我们政策只关心供应商，平台作为供应商
        {"booking_id": "BK-505", "route": "JFK-LHR", "cabin_class": "economy", "total_cost": 1800,
         "status": "pending", "platform_id": "aerocheap", "created_at": "2026-05-20", "departure_date": "2026-06-15"},
        # 已取消的预订 - 忽略
        {"booking_id": "BK-606", "route": "JFK-LHR", "cabin_class": "business", "total_cost": 5000,
         "status": "cancelled", "platform_id": "skybook", "created_at": "2026-04-01", "departure_date": "2026-05-01"},
        # 合规: 费用恰好等于 max_single_booking_cost? 3500 不允许超过, 等于允许? 政策说 max_single_booking_cost = 3500, 假设 <= 允许
        {"booking_id": "BK-707", "route": "JFK-LHR", "cabin_class": "economy", "total_cost": 3500,
         "status": "confirmed", "platform_id": "flightpro", "created_at": "2026-05-01", "departure_date": "2026-06-10"},
        # 违规5: 舱位不允许 (只允许 economy, premium_economy, business; 现在 first 不允许)
        {"booking_id": "BK-808", "route": "JFK-LHR", "cabin_class": "first", "total_cost": 6000,
         "status": "pending", "platform_id": "skybook", "created_at": "2026-05-10", "departure_date": "2026-06-20"},
        # 违规6: 成本超过 max_cost_per_booking (6000) - 这个 booking 总成本 6200
        {"booking_id": "BK-909", "route": "JFK-LHR", "cabin_class": "business", "total_cost": 6200,
         "status": "confirmed", "platform_id": "skybook", "created_at": "2026-05-05", "departure_date": "2026-06-10"},
    ]

    for b in bookings:
        with open(f"data/bookings/{b['booking_id']}.json", "w") as f:
            json.dump(b, f, indent=2)

    # 额外干扰：一个非JSON文件
    with open("data/bookings/legacy_export.csv", "w") as f:
        f.write("booking_id,status\ntest,unknown\n")

    # 还有一个无关的目录
    os.makedirs("data/backup", exist_ok=True)
    with open("data/backup/old_policy.xml", "w") as f:
        f.write("<policy>dummy</policy>")

if __name__ == "__main__":
    build_env()
