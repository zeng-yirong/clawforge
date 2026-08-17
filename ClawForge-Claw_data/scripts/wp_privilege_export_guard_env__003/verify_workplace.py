import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

score_details = []
total_score = 0

def add_detail(item, score, max_score, passed, reason):
    global total_score
    score_details.append({"item": item, "score": score, "max_score": max_score, "passed": passed, "reason": reason})
    total_score += score

# ---------- 1. 文件存在 ----------
target_path = os.path.join(workspace, "ops", "breach_deny.json")
if os.path.exists(target_path):
    add_detail("文件存在", 10, 10, True, "ops/breach_deny.json 存在")
else:
    add_detail("文件存在", 0, 10, False, "ops/breach_deny.json 不存在")
    # 直接写评分结果退出
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# ---------- 2. JSON 合法性 ----------
try:
    with open(target_path, "r") as f:
        data = json.load(f)
    add_detail("JSON 合法性", 10, 10, True, "合法 JSON")
except Exception as e:
    add_detail("JSON 合法性", 0, 10, False, f"JSON 解析失败: {e}")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

# ---------- 3. 结构及字段 ----------
denied_list = None
if isinstance(data, list):
    denied_list = data
elif isinstance(data, dict):
    for key in ("denied", "requests", "violations", "blocked"):
        if key in data:
            denied_list = data[key]
            break
if denied_list is None:
    add_detail("数据结构", 0, 10, False, "需要顶层数组或含有 'denied' 键的对象")
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
    sys.exit(0)

all_have_fields = True
for i, entry in enumerate(denied_list):
    if not isinstance(entry, dict) or "request_id" not in entry or "actor_name" not in entry:
        all_have_fields = False
        break
if all_have_fields:
    add_detail("字段完整性", 10, 10, True, "每条记录包含 request_id 和 actor_name")
else:
    add_detail("字段完整性", 0, 10, False, "缺少必要字段")

# ---------- 4. 读取环境数据，计算 ground truth ----------
try:
    with open(os.path.join(workspace, "data/accounts.json")) as f:
        accounts = json.load(f)
    with open(os.path.join(workspace, "data/assets/assets.json")) as f:
        assets = json.load(f)
    with open(os.path.join(workspace, "data/requests/requests.json")) as f:
        requests_data = json.load(f)
except Exception as e:
    add_detail("环境数据读取", 0, 0, False, f"无法读取环境数据: {e}")
    ground_truth_ids = set()
else:
    account_perms = {acc["account_id"]: acc.get("permissions", []) for acc in accounts}
    asset_policy = {ast["asset_id"]: ast.get("read_policy", "") for ast in assets}

    def needed_permissions(policy_str):
        return [p.strip() for p in policy_str.split(",") if p.strip()]

    ground_truth_ids = set()
    for req in requests_data:
        rid = req["request_id"]
        actor = req["actor_name"]
        aid = req["target_asset_id"]
        if actor not in account_perms:
            ground_truth_ids.add(rid)
            continue
        if aid not in asset_policy:
            ground_truth_ids.add(rid)
            continue
        needed = needed_permissions(asset_policy[aid])
        if not needed:   # 空策略视为需要某种权限（拒绝）
            ground_truth_ids.add(rid)
            continue
        perms = set(account_perms[actor])
        if not all(np in perms for np in needed):
            ground_truth_ids.add(rid)

# ---------- 5. 准确度评分 ----------
agent_ids = set(entry["request_id"] for entry in denied_list)
correct = len(ground_truth_ids & agent_ids)
false_positive = agent_ids - ground_truth_ids
false_negative = ground_truth_ids - agent_ids

if len(ground_truth_ids) == 0:
    accuracy_score = 30
else:
    accuracy_score = int(30 * correct / len(ground_truth_ids))
add_detail("正确识别越权请求", accuracy_score, 30,
           accuracy_score >= 15,
           f"正确 {correct}/{len(ground_truth_ids)}, 误报 {len(false_positive)}, 漏报 {len(false_negative)}")

if len(false_negative) == 0:
    add_detail("无遗漏", 10, 10, True, "所有应拒绝请求均已包含")
else:
    add_detail("无遗漏", 0, 10, False, f"遗漏: {false_negative}")

if len(false_positive) == 0:
    add_detail("无多余", 10, 10, True, "没有包含不应拒绝的请求")
else:
    add_detail("无多余", 0, 10, False, f"多余: {false_positive}")

# ---------- 写入最终评分 ----------
with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
