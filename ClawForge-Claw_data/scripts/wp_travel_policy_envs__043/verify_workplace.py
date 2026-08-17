import sys
import json
import os
import pathlib

def verify(workspace: str):
    score_details = []
    total_score = 0

    # 1. 检查目录 ops 是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        score_details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    # 2. 检查 booking_confirmation.json 存在且合法 (10分)
    target_file = os.path.join(workspace, "ops", "booking_confirmation.json")
    if not os.path.isfile(target_file):
        score_details.append({
            "item": "ops/booking_confirmation.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # 无法继续，后续所有项得0分
        # 但为了完整性继续执行并记录
    else:
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            score_details.append({
                "item": "ops/booking_confirmation.json exists and valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Valid JSON file"
            })
            total_score += 10
        except (json.JSONDecodeError, Exception) as e:
            score_details.append({
                "item": "ops/booking_confirmation.json exists and valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {e}"
            })
            data = None

    if data is None:
        # 如果文件缺失或损坏，后面全部0分，直接输出
        # 但需要继续生成details，每个项置0
        # 简化：跳过检查，但为了完整性，手动添加剩余项为0
        missing_items = [
            ("flight_id field", 5),
            ("selected_platform field", 5),
            ("total_cost calculated correctly", 20),
            ("base_price field", 5),
            ("transaction_fee field", 5),
            ("service_fee field", 5),
            ("policy_id field", 5),
            ("policy_compliant field", 5),
            ("requires_approval field", 5),
            ("approver_email field", 10),
            ("no incorrect flight selected", 20)
        ]
        for item_name, max_s in missing_items:
            score_details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "Target file missing or invalid"
            })
        # 写出结果并退出
        output = {"total_score": 0, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(output, f, indent=2)
        return

    # 3. 检查必要字段存在性 (35分)
    required_fields = {
        "flight_id": 5,
        "selected_platform": 5,
        "base_price": 5,
        "transaction_fee": 5,
        "service_fee": 5,
        "total_cost": 5,
        "policy_id": 5,
        "policy_compliant": 5,
        "requires_approval": 5,
        "approver_email": 10
    }
    # 注意权重：approver_email 10分，其他各5分，但总共60？我们调整一下：上面列了10项总权重5*9+10=55，但为了总分100，后面还有计算和过滤分。
    # 这里先按55分，但实际 total_cost 计算正确性另外20分，选择正确性20分，加起来95，加上目录结构10=105？不对。
    # 重新规划：目录10，文件存在10，字段存在40，计算正确20，选择正确20，合计100。这里字段存在包括total_cost但不检查数值，数值在计算里。
    # 所以调整：flight_id, selected_platform, base_price, transaction_fee, service_fee, policy_id, policy_compliant, requires_approval, approver_email 共9项，其中approver_email 10分，其余各5分，总计 8*5+10=50。然后额外加 total_cost 字段存在5分（因为数值计算另外20分），所以字段存在部分55分。但之前已有目录+文件20分，加上55+20+20=115不对。我们需要调整。
    # 修正：目录10，文件合法10，字段存在(9项)共50，数值计算20，选择正确10，总分100？其实选择正确可并入字段存在中的flight_id检查。简化：我们按以下权重重写。
    
    # 重新整理评分结构（避免overlap）：
    score_details = []  # 清空之前添加的，重新构建
    total_score = 0

    # 1. ops目录 (10)
    if os.path.isdir(ops_dir):
        score_details.append({"item":"ops directory exists","score":10,"max_score":10,"passed":True,"reason":"found"})
        total_score+=10
    else:
        score_details.append({"item":"ops directory exists","score":0,"max_score":10,"passed":False,"reason":"not found"})

    # 2. 文件存在且合法 (10)
    score_details.append({"item":"ops/booking_confirmation.json exists","score":10,"max_score":10,"passed":True,"reason":"valid JSON"})
    total_score+=10

    # 3. 字段存在性 (40分)
    field_checks = [
        ("flight_id", 5),
        ("selected_platform", 5),
        ("base_price", 5),
        ("transaction_fee", 5),
        ("service_fee", 5),
        ("total_cost", 5),  # 只检查存在，数值后面算
        ("policy_id", 5),
        ("policy_compliant", 5),
        ("requires_approval", 5),
        ("approver_email", 10)  # 总共 5*9+10 = 55? 太多。调整：保留10个字段总权重40，其中approver_email 10，其余各约3.33，取整：flight_id 5, selected_platform 5, base_price 5, transaction_fee 5, service_fee 5, total_cost 5, policy_id 5, policy_compliant 5, requires_approval 5, approver_email 10，总共55。超过40了。我们改为：flight_id 4, selected_platform 4, base_price 4, transaction_fee 4, service_fee 4, total_cost 4, policy_id 4, policy_compliant 4, requires_approval 4, approver_email 4，共40。然后后面计算20，选择正确20，目录10，文件10，共100。好。
    ]
    # 重新定义字段权重
    field_weights = {
        "flight_id": 4,
        "selected_platform": 4,
        "base_price": 4,
        "transaction_fee": 4,
        "service_fee": 4,
        "total_cost": 4,
        "policy_id": 4,
        "policy_compliant": 4,
        "requires_approval": 4,
        "approver_email": 4
    }
    for field, weight in field_weights.items():
        if field in data and data[field] is not None:
            score_details.append({
                "item": f"Field '{field}' present",
                "score": weight,
                "max_score": weight,
                "passed": True,
                "reason": f"found with value {data[field]}"
            })
            total_score += weight
        else:
            score_details.append({
                "item": f"Field '{field}' present",
                "score": 0,
                "max_score": weight,
                "passed": False,
                "reason": f"missing or null"
            })

    # 4. 数值计算正确 (20分)
    # 需要从原始数据重新计算预期 total_cost
    # 预期: selected_platform 必须是 skybook，flight_id 必须是 SKY-2026-0615-JFK-LHR-001，base_price=1800, transaction_fee=50, service_fee=30 => total=1880.0
    expected_platform = "skybook"
    expected_flight_id = "SKY-2026-0615-JFK-LHR-001"
    expected_base = 1800.00
    expected_txn_fee = 50.0
    expected_svc_fee = 30.0
    expected_total = 1880.0
    # 检查 flight_id 是否正确，如果错误则计算分数为0
    if data.get("flight_id") == expected_flight_id and data.get("selected_platform") == expected_platform:
        base_ok = abs(data.get("base_price", 0) - expected_base) < 0.01
        txn_ok = abs(data.get("transaction_fee", 0) - expected_txn_fee) < 0.01
        svc_ok = abs(data.get("service_fee", 0) - expected_svc_fee) < 0.01
        total_ok = abs(data.get("total_cost", 0) - expected_total) < 0.01
        if base_ok and txn_ok and svc_ok and total_ok:
            score_details.append({
                "item": "Numerical calculation correctness",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": f"base={data.get('base_price')}, txn_fee={data.get('transaction_fee')}, svc_fee={data.get('service_fee')}, total={data.get('total_cost')}"
            })
            total_score += 20
        else:
            # 部分正确？给部分分
            part_score = 0
            reasons = []
            if base_ok: part_score += 5
            else: reasons.append(f"base_price expected {expected_base}, got {data.get('base_price')}")
            if txn_ok: part_score += 5
            else: reasons.append(f"transaction_fee expected {expected_txn_fee}, got {data.get('transaction_fee')}")
            if svc_ok: part_score += 5
            else: reasons.append(f"service_fee expected {expected_svc_fee}, got {data.get('service_fee')}")
            if total_ok: part_score += 5
            else: reasons.append(f"total_cost expected {expected_total}, got {data.get('total_cost')}")
            score_details.append({
                "item": "Numerical calculation correctness",
                "score": part_score,
                "max_score": 20,
                "passed": part_score > 0,
                "reason": "; ".join(reasons) if reasons else "partial"
            })
            total_score += part_score
    else:
        score_details.append({
            "item": "Numerical calculation correctness",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Flight or platform mismatch: flight_id={data.get('flight_id')}, platform={data.get('selected_platform')}"
        })

    # 5. 选择正确性 (20分) —— 确保没有选错航班/平台
    if data.get("flight_id") == expected_flight_id and data.get("selected_platform") == expected_platform:
        score_details.append({
            "item": "Correct flight and platform selection",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Selected {expected_flight_id} on {expected_platform}"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "Correct flight and platform selection",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected {expected_flight_id} on {expected_platform}, got {data.get('flight_id')} on {data.get('selected_platform')}"
        })

    # 确保 total_score 不超过100
    total_score = min(total_score, 100)
    output = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
