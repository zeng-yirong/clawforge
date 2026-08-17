import json, csv, os, sys, re
from pathlib import Path

def check_workplace(workspace):
    ws = Path(workspace)
    score = 0
    max_score = 100
    details = []

    def add_detail(item, score_val, max_val, passed, reason):
        details.append({
            "item": item,
            "score": score_val,
            "max_score": max_val,
            "passed": passed,
            "reason": reason
        })
        return score_val if passed else 0

    # 1. 目录结构和必要文件 (10分)
    expected_file = ws / "ops/booking_decision.json"
    if expected_file.exists():
        score += add_detail("ops/booking_decision.json 存在", 10, 10, True, "文件存在")
    else:
        score += add_detail("ops/booking_decision.json 存在", 0, 10, False, "缺失目标文件")

    # 2. JSON格式校验 (10分)
    if expected_file.exists():
        try:
            with open(expected_file, "r") as f:
                decision = json.load(f)
            score += add_detail("JSON格式合法", 10, 10, True, "解析成功")
        except (json.JSONDecodeError, Exception) as e:
            score += add_detail("JSON格式合法", 0, 10, False, f"解析失败: {e}")
            decision = {}
    else:
        decision = {}

    if not decision:
        # 后续检查跳过
        score += add_detail("所有字段检查", 0, 80, False, "无决策数据")
        final = {"total_score": score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. 必须字段存在性 (20分)
    required_fields = ["selected_flight_id", "price", "policy_valid", "needs_approval", "approvers"]
    missing_fields = [f for f in required_fields if f not in decision]
    if missing_fields:
        score += add_detail("必需字段完整", 0, 20, False, f"缺失字段: {missing_fields}")
    else:
        score += add_detail("必需字段完整", 20, 20, True, "所有必需字段都存在")

    # 4. selected_flight_id 必须是合法的航班ID (10分)
    flight_id = decision.get("selected_flight_id", "")
    # 唯一正确答案：SB-20260615-JFK-LHR-001
    if flight_id == "SB-20260615-JFK-LHR-001":
        score += add_detail("selected_flight_id 正确", 10, 10, True, "选中最便宜的可行航班")
    else:
        score += add_detail("selected_flight_id 正确", 0, 10, False, f"得到 {flight_id}, 应 SB-20260615-JFK-LHR-001")

    # 5. price 必须等于1750.00 (20分)
    try:
        price = float(decision.get("price", -1))
    except:
        price = -1
    if abs(price - 1750.00) < 0.01:
        score += add_detail("price 正确", 20, 20, True, f"价格1750.00匹配")
    else:
        score += add_detail("price 正确", 0, 20, False, f"得到 {price}, 应 1750.00")

    # 6. policy_valid 必须为 true (10分)
    if decision.get("policy_valid") is True:
        score += add_detail("policy_valid 正确", 10, 10, True, "合规")
    else:
        score += add_detail("policy_valid 正确", 0, 10, False, f"得到 {decision.get('policy_valid')}, 应为 true")

    # 7. needs_approval 必须为 false (因为价格小于2000) (10分)
    if decision.get("needs_approval") is False:
        score += add_detail("needs_approval 正确", 10, 10, True, "低于$2000无需审批")
    else:
        score += add_detail("needs_approval 正确", 0, 10, False, f"得到 {decision.get('needs_approval')}, 应为 false")

    # 8. approvers 必须为空列表或只包含部门经理 (10分)
    approvers = decision.get("approvers", None)
    # 预期：因为不需要额外审批，可能保留默认部门经理，或者空列表。但按提示“审批人是谁也写明白”，
    # 比较合理的做法是列出部门经理（第一行）。但允许多种合理答案：空列表或["mike.li@acme-corp.com"]。
    # 但为了客观，我们只接受空列表或["mike.li@acme-corp.com"]。
    if isinstance(approvers, list) and (approvers == [] or approvers == ["mike.li@acme-corp.com"]):
        score += add_detail("approvers 合理", 10, 10, True, f"审批人列表: {approvers}")
    else:
        score += add_detail("approvers 合理", 0, 10, False, f"得到 {approvers}, 应为 [] 或 ['mike.li@acme-corp.com']")

    # 最终汇总
    final = {"total_score": score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    check_workplace(workspace)
