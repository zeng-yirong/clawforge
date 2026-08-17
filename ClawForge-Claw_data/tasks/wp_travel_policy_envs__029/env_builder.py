import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # accounts.json
    accounts = {
        "account_id": "acme_corp_main",
        "company_name": "Acme Corp",
        "travel_budget": 500000,
        "currency": "USD",
        "approvers": ["alice@acme.com", "bob@acme.com"]
    }
    os.makedirs(".", exist_ok=True)
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # policies/ 包含多个版本，最新版本 v2.0 has requires_approval_above = 2500
    policies = [
        {
            "policy_id": "pol_acme_v1",
            "name": "Acme Corp Business Travel Policy",
            "version": "1.0",
            "max_cost_per_booking": 3000,
            "max_single_booking_cost": 3000,
            "allowed_cabin_classes": ["economy", "premium_economy"],
            "min_advance_booking_days": 3,
            "requires_approval_above": 1500,
            "preferred_vendors": ["AeroCheap", "SkyBook"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": ["economy"]
        },
        {
            "policy_id": "pol_acme_v2",
            "name": "Acme Corp Business Travel Policy",
            "version": "2.0",
            "max_cost_per_booking": 5000,
            "max_single_booking_cost": 5000,
            "allowed_cabin_classes": ["economy", "premium_economy", "business"],
            "min_advance_booking_days": 5,
            "requires_approval_above": 2500,
            "preferred_vendors": ["AeroCheap", "FlightPro", "SkyBook"],
            "restricted_routes": ["JFK-LHR"],
            "required_documents": ["passport", "visa"],
            "no_refund_cabin_classes": ["economy", "premium_economy"]
        },
        {
            "policy_id": "pol_acme_v1_obsolete",
            "name": "Acme Corp Business Travel Policy (OBSOLETE)",
            "version": "1.5",
            "max_cost_per_booking": 2500,
            "max_single_booking_cost": 2500,
            "allowed_cabin_classes": ["economy", "premium_economy"],
            "min_advance_booking_days": 2,
            "requires_approval_above": 2000,
            "preferred_vendors": ["AeroCheap"],
            "restricted_routes": [],
            "required_documents": ["passport"],
            "no_refund_cabin_classes": ["economy"]
        }
    ]
    os.makedirs("policies", exist_ok=True)
    for p in policies:
        with open(f"policies/{p['policy_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    # platforms/ 三个平台，供场景背景
    platforms = [
        {"platform_id": "ac", "name": "AeroCheap", "region": "North America", "is_active": True, "transaction_fee": 15.0, "service_fee": 10.0, "payment_methods": ["credit_card"], "cancellation_policy": "non-refundable", "discounts": [], "promotions": [], "loyalty_program": {}},
        {"platform_id": "fp", "name": "FlightPro", "region": "Europe", "is_active": True, "transaction_fee": 20.0, "service_fee": 12.0, "payment_methods": ["credit_card", "paypal"], "cancellation_policy": "partial", "discounts": [], "promotions": [], "loyalty_program": {}},
        {"platform_id": "sb", "name": "SkyBook", "region": "Asia Pacific", "is_active": False, "transaction_fee": 18.0, "service_fee": 8.0, "payment_methods": ["credit_card", "bank_transfer"], "cancellation_policy": "full", "discounts": [], "promotions": [], "loyalty_program": {}}
    ]
    os.makedirs("platforms", exist_ok=True)
    for pl in platforms:
        with open(f"platforms/{pl['platform_id']}.json", "w") as f:
            json.dump(pl, f, indent=2)

    # bookings/ 生成一批预订记录，一些有效、一些作废、一些状态无效、一些重复、一些测试
    # 有效且 cost > 2500 (requires_approval_above) 的 booking_id 应被选出
    # 干扰项：cost小于等于2500的，状态为cancelled/deleted的，标记为test的记录
    bookings = []
    # 符合条件的目标记录（4条）
    targets = [
        {"booking_id": "BK-1001", "platform_id": "ac", "cost": 2800, "total_amount": 3000, "status": "confirmed", "tags": []},
        {"booking_id": "BK-1003", "platform_id": "fp", "cost": 3100, "total_amount": 3200, "status": "pending", "tags": []},
        {"booking_id": "BK-1007", "platform_id": "sb", "cost": 2599, "total_amount": 2600, "status": "confirmed", "tags": []},
        {"booking_id": "BK-1010", "platform_id": "ac", "cost": 4500, "total_amount": 4700, "status": "pending", "tags": []}
    ]
    # 干扰记录：低于阈值、取消状态、测试数据
    decoys = [
        {"booking_id": "BK-1002", "platform_id": "ac", "cost": 1800, "total_amount": 1900, "status": "confirmed", "tags": []},
        {"booking_id": "BK-1004", "platform_id": "fp", "cost": 2500, "total_amount": 2600, "status": "cancelled", "tags": []},
        {"booking_id": "BK-1005", "platform_id": "sb", "cost": 3000, "total_amount": 3100, "status": "deleted", "tags": ["archived"]},
        {"booking_id": "BK-1006", "platform_id": "ac", "cost": 1500, "total_amount": 1600, "status": "confirmed", "tags": ["test"]},
        {"booking_id": "BK-1008", "platform_id": "fp", "cost": 2600, "total_amount": 2700, "status": "pending", "tags": ["duplicate"]},
        {"booking_id": "BK-1009", "platform_id": "sb", "cost": 2400, "total_amount": 2500, "status": "confirmed", "tags": []},
        # 重复 ID（仅出现一次）
        {"booking_id": "BK-1011", "platform_id": "ac", "cost": 3000, "total_amount": 3100, "status": "confirmed", "tags": []},
    ]
    # 注意：BK-1008 虽然 cost=2600 >2500，但是 tag 包含 "duplicate"，按角色要求 "有效预订"？角色说 "未被删除标记"，duplicate 不算删除标记，实际上应该算。但为了增加混淆，我们可以在 prompt 中说 "未被删除标记"，但 duplicate 是另一个问题。然而 agent 可能会误解。但要确保唯一答案，我们可以让 duplicate 记录的成本也大于阈值，但如果不排除则答案多一条。更好的方式：将 decoys 中的 duplicate 的 status 设为 "cancelled" 或其他。我们调整一下：让 BK-1008 的 status 为 cancelled 或者将其 cost 设为 2300。为了简单，我把 BK-1008 的 cost 改为 2300，这样它不满足阈值，不会干扰。同时确保只有 targets 满足条件。
    decoys[4]["cost"] = 2300  # BK-1008 now 2300

    # 把 decoys 中可能意外满足条件的也调整：BK-1011 cost=3000，status=confirmed，没有特殊tag，这个会多一个目标。我们将其设为已取消？或者将 status 设为 "pending" 但加一个 tag "test"。修改：BK-1011 的 status 改为 "cancelled" 以排除。
    decoys[6]["status"] = "cancelled"

    # 最终满足条件的 booking_id 列表: BK-1001, BK-1003, BK-1007, BK-1010
    os.makedirs("bookings", exist_ok=True)
    all_bookings = targets + decoys
    # 打乱顺序
    random.shuffle(all_bookings)
    for b in all_bookings:
        with open(f"bookings/{b['booking_id']}.json", "w") as f:
            json.dump(b, f, indent=2)

    # 额外干扰：其他格式的日志
    os.makedirs("logs", exist_ok=True)
    with open("logs/booking_audit.log", "w") as f:
        f.write("2026-01-15 12:00:00 INFO Processed BK-1001\n2026-01-15 12:01:00 ERROR Retry BK-1005\n")

    # ops 目录留空，agent 需要创建
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
