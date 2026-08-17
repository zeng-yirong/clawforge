#!/usr/bin/env python3
import json
import os
import sys

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    errors = []
    details = []
    
    # 1. ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops 目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops 目录已创建"})
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops 目录未找到"})
        # 如果目录不存在，下面无法检查文件，直接返回
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return total

    # 2. final_booking.json 存在且合法 (10分)
    booking_path = os.path.join(ops_dir, "final_booking.json")
    if not os.path.isfile(booking_path):
        details.append({"item": "final_booking.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return total
    try:
        booking = load_json(booking_path)
        details.append({"item": "final_booking.json 合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON解析成功"})
    except Exception as e:
        details.append({"item": "final_booking.json 合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
        total = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": details}, f)
        return total

    # 3. 必要字段存在 (10分)
    required_fields = ["platform", "flight_id", "price", "total_cost", "approval_needed", "approvers"]
    missing = [f for f in required_fields if f not in booking]
    if missing:
        details.append({"item": "必要字段存在", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {missing}"})
    else:
        details.append({"item": "必要字段存在", "score": 10, "max_score": 10, "passed": True, "reason": "所有必要字段都存在"})

    # 4. 基础票价正确 (30分)
    expected_price = 2350.0  # AeroCheap AC-102 商务舱价格
    actual_price = booking.get("price")
    if isinstance(actual_price, (int, float)) and abs(actual_price - expected_price) < 0.01:
        details.append({"item": "基础票价正确", "score": 30, "max_score": 30, "passed": True, "reason": f"基础票价={actual_price} 匹配预期"})
    else:
        details.append({"item": "基础票价正确", "score": 0, "max_score": 30, "passed": False, "reason": f"基础票价={actual_price}，预期={expected_price}"})

    # 5. 总费用正确 (20分)
    # 总费用 = 基础票价 + transaction_fee(50) + service_fee(50) = 2450
    expected_total = 2450.0
    actual_total = booking.get("total_cost")
    if isinstance(actual_total, (int, float)) and abs(actual_total - expected_total) < 0.01:
        details.append({"item": "总费用正确", "score": 20, "max_score": 20, "passed": True, "reason": f"总费用={actual_total} 匹配预期"})
    else:
        details.append({"item": "总费用正确", "score": 0, "max_score": 20, "passed": False, "reason": f"总费用={actual_total}，预期={expected_total}"})

    # 6. approval_needed 正确 (10分)
    expected_approval = True  # 2450 > 2000
    actual_approval = booking.get("approval_needed")
    if isinstance(actual_approval, bool) and actual_approval == expected_approval:
        details.append({"item": "approval_needed 正确", "score": 10, "max_score": 10, "passed": True, "reason": f"approval_needed={actual_approval} 匹配预期"})
    else:
        details.append({"item": "approval_needed 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"approval_needed={actual_approval}，预期={expected_approval}"})

    # 7. approvers 列表正确 (10分)
    # 需审批，所以 approvers 应该来自 accounts.json 中 acme_corp 的 approvers
    expected_approvers = ["Carol (CFO)", "Dave (VP Finance)"]
    actual_approvers = booking.get("approvers")
    if isinstance(actual_approvers, list) and sorted(actual_approvers) == sorted(expected_approvers):
        details.append({"item": "approvers 列表正确", "score": 10, "max_score": 10, "passed": True, "reason": f"approvers={actual_approvers} 匹配预期"})
    else:
        details.append({"item": "approvers 列表正确", "score": 0, "max_score": 10, "passed": False, "reason": f"approvers={actual_approvers}，预期={expected_approvers}"})

    total_score = sum(d["score"] for d in details)
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    return total_score

if __name__ == "__main__":
    verify()
