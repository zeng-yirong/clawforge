import json
import os
import sys
from datetime import datetime, timedelta

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def check_path(path):
    return os.path.exists(os.path.join(workspace, path))

def load_json(rel_path):
    with open(os.path.join(workspace, rel_path), "r") as f:
        return json.load(f)

score_details = []
total_score = 0
max_total = 100

# 1. 目录结构检查 (10分)
def check_dir_structure():
    required_dirs = ["data/policies", "data/platforms", "data/bookings", "ops"]
    all_ok = True
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            all_ok = False
            break
    if all_ok:
        score_details.append({"item": "Required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "All 4 required directories found."})
        return 10
    else:
        score_details.append({"item": "Required directories exist", "score": 0, "max_score": 10, "passed": False, "reason": "Missing one or more directories under data/ or ops/."})
        return 0
total_score += check_dir_structure()

# 2. 文件存在性 (10分)
def check_files_exist():
    required_files = [
        "data/policies/acme_corp_2026_v2.0.json",
        "data/accounts.json",
        "ops/approval_required.json"
    ]
    missing = []
    for f in required_files:
        if not check_path(f):
            missing.append(f)
    if not missing:
        score_details.append({"item": "Required output file ops/approval_required.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "All files present."})
        return 10
    else:
        score_details.append({"item": "Required output file ops/approval_required.json exists", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing files: {missing}"})
        return 0
total_score += check_files_exist()

# 3. JSON 格式合法性 (10分)
def check_json_validity():
    try:
        data = load_json("ops/approval_required.json")
        if not isinstance(data, list):
            raise ValueError("Not a list")
        for entry in data:
            if not isinstance(entry, dict):
                raise ValueError("Entry not dict")
            if "booking_id" not in entry or "violations" not in entry:
                raise ValueError("Missing booking_id or violations")
            if not isinstance(entry["violations"], list):
                raise ValueError("Violations not list")
        score_details.append({"item": "Output JSON format is valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON array with required fields."})
        return 10
    except Exception as e:
        score_details.append({"item": "Output JSON format is valid", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        return 0
total_score += check_json_validity()

# 4. 内容精确匹配 (70分)
def check_content():
    # 预期违规预订列表 (唯一答案)
    expected_violations = {
        "BK-101": ["total_cost exceeds max_single_booking_cost (3500)", "total_cost exceeds requires_approval_above (2000)"],
        "BK-202": ["missing required documents (passport, visa)"],
        "BK-404": ["advance booking less than min_advance_booking_days (5)"],
        "BK-505": ["platform is not a preferred vendor"],
        "BK-808": ["cabin class 'first' not allowed by policy"],
        "BK-909": ["total_cost exceeds max_cost_per_booking (6000)"]
    }
    # 注意：BK-202 还可能有其他违规？min_advance_booking_days? 创建于2026-05-10，出发2026-05-20，提前10天，满足。cabin class economy允许。total_cost 2800 > 2000 所以也需要审批？但政策中 requires_approval_above 2000 意味着超过2000需要审批，但这不是违规，只是需要审批。但我们的剧情是“找出违背政策的预订”，而需要审批本身不算违规，只是需要走流程。我们严格按政策条款：超max_cost、舱位不允许、提前天数不足、非优选供应商、缺文件、超max_single_booking_cost才是违规。BK-202 的 max_single_booking_cost 是3500，2800没超；max_cost_per_booking 6000没超；需要审批不算违规。但缺文件是违规。所以BK-202只应列出缺文件。
    # 同样地，BK-101 既有超 single 也有超 approval threshold，但超 approval threshold 不算违规，只是触发审批。这里我们视为违规原因是超费用。但为简化，我们接受两种原因都列或只列其中之一。但是必须符合预期。为了唯一性，我们规定预期结果：只列出明显违反政策条款的，不把“需要审批”当作违规。BK-101 超过 max_single_booking_cost 是明确违规，超过 requires_approval_above 不算违规（只是阈值）。所以我们在 expected_violations 中只放 "total_cost exceeds max_single_booking_cost (3500)"。同样 BK-202 只有缺文件。BK-404 提前天数不足。BK-505 非优选供应商。BK-808 舱位不允许。BK-909 超总预算。
    # 重新定义预期：
    expected = {
        "BK-101": ["total_cost exceeds max_single_booking_cost (3500)"],
        "BK-202": ["missing required documents (passport, visa)"],
        "BK-404": ["advance booking less than min_advance_booking_days (5)"],
        "BK-505": ["platform is not a preferred vendor"],
        "BK-808": ["cabin class 'first' not allowed by policy"],
        "BK-909": ["total_cost exceeds max_cost_per_booking (6000)"]
    }

    try:
        data = load_json("ops/approval_required.json")
    except:
        score_details.append({"item": "Output content matches expected violations", "score": 0, "max_score": 70, "passed": False, "reason": "Cannot load JSON"})
        return 0

    # 检查是否有额外或缺失的 booking_id
    result_ids = set(entry["booking_id"] for entry in data)
    expected_ids = set(expected.keys())
    if result_ids != expected_ids:
        extra = result_ids - expected_ids
        missing = expected_ids - result_ids
        reason = f"Booking IDs mismatch. extra={extra}, missing={missing}"
        score_details.append({"item": "Output content matches expected violations", "score": 0, "max_score": 70, "passed": False, "reason": reason})
        return 0

    # 检查每个 booking 的 violations
    violations_ok = True
    for entry in data:
        bid = entry["booking_id"]
        actual_violations = set(entry["violations"])
        expected_violations_set = set(expected[bid])
        if actual_violations != expected_violations_set:
            violations_ok = False
            break
    if violations_ok:
        score_details.append({"item": "Output content matches expected violations", "score": 70, "max_score": 70, "passed": True, "reason": "All 6 violations correctly identified."})
        return 70
    else:
        # 给出部分分？要求严格一致
        score_details.append({"item": "Output content matches expected violations", "score": 0, "max_score": 70, "passed": False, "reason": "Violations list mismatch for one or more bookings."})
        return 0
total_score += check_content()

# 计算总分（可能超过100？其实加起来100）
final_score = min(total_score, 100)
result = {
    "total_score": final_score,
    "details": score_details
}
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"Total score: {final_score}/100")
