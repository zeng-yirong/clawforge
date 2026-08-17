import sys
import json
import os
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    wp = Path(workspace)

    details = []
    total_score = 0

    # 1. 检查必需目录结构 (10分)
    dirs_ok = True
    required_dirs = ["data/policies", "data/platforms", "data/bookings", "ops"]
    for d in required_dirs:
        if not (wp / d).is_dir():
            dirs_ok = False
            details.append({"item": f"Directory {d} exists", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing directory: {d}"})
            break
    if dirs_ok:
        details.append({"item": "Directory structure", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories present"})
        total_score += 10

    # 2. 检查ops/violations.json存在且合法 (10分)
    violations_path = wp / "ops" / "violations.json"
    if not violations_path.is_file():
        details.append({"item": "ops/violations.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # 不能继续，总分0
        total_score = 0
        write_score(total_score, details, wp)
        return
    try:
        data = load_json(violations_path)
    except:
        details.append({"item": "ops/violations.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "Invalid JSON"})
        write_score(0, details, wp)
        return
    details.append({"item": "ops/violations.json exists and valid", "score": 10, "max_score": 10, "passed": True, "reason": "File is readable JSON"})
    total_score += 10

    # 3. 验证数据结构：必须包含 violations 列表和 total_excess (10分)
    if "violations" not in data or "total_excess" not in data:
        details.append({"item": "JSON has required keys", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'violations' or 'total_excess'"})
        total_score += 0
    elif not isinstance(data["violations"], list):
        details.append({"item": "violations is a list", "score": 0, "max_score": 10, "passed": False, "reason": "violations is not a list"})
    else:
        details.append({"item": "JSON structure correct", "score": 10, "max_score": 10, "passed": True, "reason": "Has violations list and total_excess"})
        total_score += 10

    # 4. 读取政策v2，获取max_single_booking_cost和allowed_cabin_classes (用于后续判断)
    policy_path = wp / "data" / "policies" / "acme_business_v2.json"
    if not policy_path.is_file():
        details.append({"item": "Policy v2 file accessible", "score": 0, "max_score": 5, "passed": False, "reason": "Policy file not found"})
        total_score += 0
        # 无法继续，但继续运行会报错，提前结束
        write_score(total_score, details, wp)
        return
    policy = load_json(policy_path)
    max_cost = policy["max_single_booking_cost"]  # 2000
    allowed_classes = set(policy["allowed_cabin_classes"])  # {"economy","business"}
    details.append({"item": "Policy v2 loaded", "score": 5, "max_score": 5, "passed": True, "reason": "Read max_single_booking_cost and allowed_cabin_classes"})
    total_score += 5

    # 5. 读取所有预订记录，找出违规项（按最新政策） (55分)
    bookings_path = wp / "data" / "bookings" / "records.json"
    if not bookings_path.is_file():
        details.append({"item": "Bookings file", "score": 0, "max_score": 5, "passed": False, "reason": "Bookings file missing"})
        write_score(total_score, details, wp)
        return
    try:
        all_bookings = load_json(bookings_path)
    except:
        details.append({"item": "Bookings JSON valid", "score": 0, "max_score": 5, "passed": False, "reason": "Invalid JSON"})
        write_score(total_score, details, wp)
        return
    details.append({"item": "Bookings loaded", "score": 5, "max_score": 5, "passed": True, "reason": "Read all bookings"})
    total_score += 5

    # 计算期望的违规项
    expected_violations = []
    for bk in all_bookings:
        booking_id = bk["booking_id"]
        cost = bk["total_cost"]
        cabin = bk["cabin_class"]
        # 违反条件：成本 > max_cost 或 cabin_class not in allowed_classes
        violation = False
        excess = 0
        if cost > max_cost:
            violation = True
            excess = cost - max_cost
        if cabin not in allowed_classes:
            violation = True
            # 如果也超成本，取cost - max_cost；否则excess = cost (因为全部不允许)
            if not cost > max_cost:
                excess = cost  # 整个成本都是违规的，但按题义“超标金额”可能只针对成本超标？题目说“预订成本减去政策允许的最大单次成本”，对于舱位违规，成本可能不超标，但整个预订都是违规，超额怎么算？为了明确，我们定义：如果舱位不允许，超额=总成本（因为根本不允许预订）。但题目中提到“超标金额（预订成本减去政策允许的最大单次成本）”，似乎只针对成本超标。但审计也关心舱位违规。为了统一，我们设定：对于舱位违规但成本不超标的，超额为0？但审计需要清单，超额金额可以为零？为了代码可判定，我们定义：违规条目都列出，超额仅针对成本超标的情况；舱位违规但成本不超的，excess=0。这样verify可以检查。
            # 但agent可能会把舱位违规的成本也视为超额，需要保持一致。在env_builder中我们有两个违规：BK-003成本2500 >2000，excess=500；BK-004舱位first不允许，成本4000>2000? 4000>2000, 所以excess=2000；BK-006成本2100>2000，excess=100。所以三个都超成本。没有纯舱位违规不超成本的例子。为了简单，我们不再设计纯舱位违规不超成本的。所以可以统一：excess = max(0, cost - max_cost) 对所有违规。
        # 但是舱位违规且成本不超的情况，agent可能定义excess=0还是cost？根据题目“超标金额（预订成本减去政策允许的最大单次成本）”只提到成本。所以如果cost<=max_cost但舱位不允许，超额应为0？但这样不太合理。为了消除歧义，我们限制我们的违规预订都是成本超标的（BK-003 2500>2000, BK-004 4000>2000, BK-006 2100>2000）。这样无论哪种解释，excess都是cost-max_cost。
        # 检查是否确实违规（成本超标或舱位不允许）
        if cost > max_cost or cabin not in allowed_classes:
            expected_violations.append({
                "booking_id": booking_id,
                "excess_amount": excess
            })
    # 排序以便比较
    expected_violations.sort(key=lambda x: x["booking_id"])

    # 提取agent的结果
    agent_violations = data.get("violations", [])
    agent_violations_sorted = sorted(agent_violations, key=lambda x: x.get("booking_id", ""))

    # 比较数量 (10分)
    score_violations = 0
    max_violations = 40
    # 先检查数量匹配
    if len(agent_violations_sorted) != len(expected_violations):
        details.append({"item": "Violation count", "score": 0, "max_score": 10, "passed": False,
                        "reason": f"Expected {len(expected_violations)} violations, got {len(agent_violations_sorted)}"})
        total_score += 0
        score_violations = 0
    else:
        details.append({"item": "Violation count", "score": 10, "max_score": 10, "passed": True,
                        "reason": f"Correct count: {len(expected_violations)}"})
        total_score += 10
        score_violations = 10

        # 检查每条记录 (30分)
        all_match = True
        for i, (exp, act) in enumerate(zip(expected_violations, agent_violations_sorted)):
            bid_match = exp["booking_id"] == act.get("booking_id")
            # 允许excess有正负偏差？精确值
            exp_excess = exp["excess_amount"]
            act_excess = act.get("excess_amount", None)
            if act_excess is None:
                all_match = False
                continue
            # 允许浮点误差？都是整数，用int比较
            excess_match = int(act_excess) == exp_excess
            if not (bid_match and excess_match):
                all_match = False
                break
        if all_match:
            details.append({"item": "Violation details", "score": 30, "max_score": 30, "passed": True,
                            "reason": "All booking IDs and excess amounts match expected"})
            total_score += 30
            score_violations += 30
        else:
            details.append({"item": "Violation details", "score": 0, "max_score": 30, "passed": False,
                            "reason": "Mismatch in booking IDs or excess amounts"})
            total_score += 0

    # 检查total_excess (10分)
    expected_total = sum(v["excess_amount"] for v in expected_violations)
    agent_total = data.get("total_excess")
    if agent_total is None:
        details.append({"item": "total_excess present", "score": 0, "max_score": 10, "passed": False, "reason": "Missing key"})
    else:
        # 允许浮点误差，但都是整数
        if abs(agent_total - expected_total) < 0.01:
            details.append({"item": "Total excess correct", "score": 10, "max_score": 10, "passed": True,
                            "reason": f"Expected {expected_total}, got {agent_total}"})
            total_score += 10
        else:
            details.append({"item": "Total excess correct", "score": 0, "max_score": 10, "passed": False,
                            "reason": f"Expected {expected_total}, got {agent_total}"})

    # 计算最终总分（可能还有细节未加，但已加完）。确保总分不超过100
    total_score = min(total_score, 100)
    write_score(total_score, details, wp)

def write_score(total, details, wp):
    score_data = {
        "total_score": total,
        "details": details
    }
    with open(wp / "workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
