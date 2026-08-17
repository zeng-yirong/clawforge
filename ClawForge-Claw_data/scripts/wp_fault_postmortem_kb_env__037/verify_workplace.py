import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查目录结构 (10 分)
    # 期望 ops/ 目录存在
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({
            "item": "ops 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    # 2. 检查产出文件 ops/postmortem_F037.json 是否存在 (10 分)
    expected_file = os.path.join(ops_dir, "postmortem_F037.json")
    if os.path.isfile(expected_file):
        score_details.append({
            "item": "产出文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "postmortem_F037.json found in ops/"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "产出文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected file {expected_file} not found"
        })
        # 后续检查跳过，如果文件不存在则总分不扣完？但我们继续检查可能会导致错误，所以提前返回？
        # 为了稳健，如果文件不存在，我们直接返回当前分数并说明。
        # 但为了细粒度，我们仍然继续，但后续项可能因为无法读取而报错，这里处理为异常捕获
        # 简化：如果文件不存在，直接输出当前分数并返回
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": score_details}, f, indent=2)
        print(f"Score: {final_score}/100")
        return

    # 3. 读取文件，检查 JSON 合法性 (10 分)
    try:
        with open(expected_file, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON"
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": score_details}, f, indent=2)
        print(f"Score: {final_score}/100")
        return

    # 4. 检查必要字段是否存在 (20 分)
    required_fields = ["fault_id", "root_cause", "affected_tables", "transaction_id", "recommended_action"]
    missing_fields = [f for f in required_fields if f not in data]
    if not missing_fields:
        score_details.append({
            "item": "必要字段存在",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"All required fields present: {required_fields}"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "必要字段存在",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing fields: {missing_fields}"
        })

    # 5. 检查故障 ID 是否等于 F037 (10 分)
    if data.get("fault_id") == "F037":
        score_details.append({
            "item": "故障 ID 正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "fault_id is F037"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "故障 ID 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"fault_id is {data.get('fault_id')}, expected F037"
        })

    # 6. 检查 transaction_id 必须是从日志中提取的 'txn_8899' (25 分)
    expected_txn = "txn_8899"
    actual_txn = data.get("transaction_id")
    if actual_txn == expected_txn:
        score_details.append({
            "item": "事务 ID 正确",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"transaction_id is {expected_txn}"
        })
        total_score += 25
    else:
        score_details.append({
            "item": "事务 ID 正确",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"transaction_id is {actual_txn}, expected {expected_txn}"
        })

    # 7. 检查 affected_tables 是否包含 'inventory_lock' (10 分)
    tables = data.get("affected_tables", [])
    if isinstance(tables, list) and "inventory_lock" in tables:
        score_details.append({
            "item": "受影响表包含 inventory_lock",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "inventory_lock found in affected_tables"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "受影响表包含 inventory_lock",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"affected_tables does not contain inventory_lock: {tables}"
        })

    # 8. 检查 recommended_action 存在且非空 (5 分)
    if data.get("recommended_action") and isinstance(data.get("recommended_action"), str) and len(data["recommended_action"]) > 0:
        score_details.append({
            "item": "推荐操作非空",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "recommended_action is provided"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "推荐操作非空",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "recommended_action missing or empty"
        })

    # 写入最终分数
    final_score = min(total_score, 100)  # 确保不超过100
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": score_details}, f, indent=2)
    print(f"Score: {final_score}/100")

if __name__ == "__main__":
    main()
