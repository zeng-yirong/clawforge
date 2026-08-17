import sys
import json
import os
from pathlib import Path

def verify(workspace):
    score_details = []
    total_score = 0

    # 1. 检查必要目录和文件存在 (10分)
    required_dirs = ["data/customers", "data/logs", "ops"]
    dirs_ok = True
    for d in required_dirs:
        if not Path(workspace, d).is_dir():
            dirs_ok = False
            break
    if dirs_ok:
        total_score += 10
        score_details.append({"item": "Required directories exist", "score": 10, "max_score": 10, "passed": True, "reason": "All required directories found."})
    else:
        score_details.append({"item": "Required directories exist", "score": 0, "max_score": 10, "passed": False, "reason": "Missing some directories."})

    # 2. 检查 agent 产物 ops/updated_labels.json 是否存在且格式合法 (10分)
    labels_path = Path(workspace, "ops", "updated_labels.json")
    if not labels_path.is_file():
        score_details.append({"item": "Agent output file ops/updated_labels.json", "score": 0, "max_score": 10, "passed": False, "reason": "File not found."})
        # 无法继续，总分写入并退出
        write_score(total_score, score_details, workspace)
        return

    try:
        with open(labels_path, "r") as f:
            labels_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        score_details.append({"item": "Agent output file ops/updated_labels.json", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        write_score(total_score, score_details, workspace)
        return

    if not isinstance(labels_data, list):
        score_details.append({"item": "Agent output file ops/updated_labels.json", "score": 0, "max_score": 10, "passed": False, "reason": "Root element is not a list."})
        write_score(total_score, score_details, workspace)
        return

    for entry in labels_data:
        if not isinstance(entry, dict) or "customer_id" not in entry or "labels" not in entry:
            score_details.append({"item": "Agent output file ops/updated_labels.json", "score": 0, "max_score": 10, "passed": False, "reason": "List items missing required fields (customer_id, labels)."})
            write_score(total_score, score_details, workspace)
            return

    total_score += 10
    score_details.append({"item": "Agent output file ops/updated_labels.json", "score": 10, "max_score": 10, "passed": True, "reason": "File exists, valid JSON, list with required fields."})

    # 3. 读取原始客户、消费、活动数据
    customers_path = Path(workspace, "data/customers", "customers.json")
    with open(customers_path, "r") as f:
        customers_data = json.load(f)
    customers_list = customers_data["customers"]
    customer_ids_expected = {c["customer_id"] for c in customers_list}

    consumption_path = Path(workspace, "data/logs", "consumption_logs.json")
    with open(consumption_path, "r") as f:
        consumption_data = json.load(f)
    consumption_logs = consumption_data["consumption_logs"]

    activity_path = Path(workspace, "data/logs", "activity_logs.json")
    with open(activity_path, "r") as f:
        activity_data = json.load(f)
    activity_logs = activity_data["activity_logs"]

    # 构建预期标签
    # 计算每个客户的正消费总和
    spend_sum = {}
    for log in consumption_logs:
        cid = log["customer_id"]
        amt = log["quarter_spend_usd"]
        if amt > 0:  # 忽略负数
            spend_sum[cid] = spend_sum.get(cid, 0) + amt

    # 获取每个客户的 last_active_days (取最小值，但目前只有一条)
    inactive_days = {}
    for log in activity_logs:
        cid = log["customer_id"]
        days = log["last_active_days"]
        if cid in inactive_days:
            inactive_days[cid] = min(inactive_days[cid], days)
        else:
            inactive_days[cid] = days

    expected_labels = {}
    for c in customers_list:
        cid = c["customer_id"]
        total_spend = spend_sum.get(cid, 0)
        days = inactive_days.get(cid, 999)  # 缺失则视为很久
        if total_spend > 1500 and days <= 30:
            tier = "gold"
        elif total_spend > 800 and total_spend <= 1500 and days <= 60:
            tier = "silver"
        else:
            tier = "bronze"
        expected_labels[cid] = [tier]

    # 4. 比对 (80分, 每个客户约13.33分, 四舍五入取整)
    labels_dict = {entry["customer_id"]: entry["labels"] for entry in labels_data}
    # 检查是否覆盖所有客户
    missing = customer_ids_expected - set(labels_dict.keys())
    extra = set(labels_dict.keys()) - customer_ids_expected
    # 扣分: 每个缺失客户扣13分, 每个多余客户扣13分
    max_per_customer = 80 // len(customer_ids_expected) if customer_ids_expected else 0  # 13
    correct_count = 0
    for cid in customer_ids_expected:
        if cid not in labels_dict:
            continue
        if labels_dict[cid] == expected_labels[cid]:
            correct_count += 1
    # 得分 = 正确数 * 满分/客户数 - 多余扣分
    penalty = len(missing) * max_per_customer + len(extra) * max_per_customer
    raw_score = correct_count * max_per_customer
    final_score = max(0, raw_score - penalty)
    total_score += final_score
    reason_parts = []
    if missing:
        reason_parts.append(f"Missing customers: {missing}")
    if extra:
        reason_parts.append(f"Extra customers: {extra}")
    if correct_count < len(customer_ids_expected):
        incorrect = [cid for cid in customer_ids_expected if cid not in labels_dict or labels_dict.get(cid) != expected_labels[cid]]
        reason_parts.append(f"Incorrect labels for: {incorrect}")
    if not reason_parts:
        reason_parts.append("All customer labels correct.")
    score_details.append({
        "item": "Customer labels accuracy",
        "score": final_score,
        "max_score": 80,
        "passed": final_score == 80,
        "reason": "; ".join(reason_parts)
    })

    # 写入最终评分
    write_score(total_score, score_details, workspace)

def write_score(total, details, workspace):
    output = {
        "total_score": total,
        "details": details
    }
    with open(Path(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
