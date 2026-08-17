import sys, os, json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # 1. 检查 ops/ 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "目录 ops/ 存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ 目录存在"})
        score += 10
    else:
        details.append({"item": "目录 ops/ 存在", "score": 0, "max_score": 10, "passed": False, "reason": "找不到 ops/ 目录"})

    # 2. 检查 ops/booking_request.json 是否存在且可解析 (10分)
    result_path = os.path.join(ops_dir, "booking_request.json")
    if os.path.isfile(result_path):
        try:
            with open(result_path, "r") as f:
                data = json.load(f)
            details.append({"item": "booking_request.json 合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且 JSON 解析成功"})
            score += 10
        except json.JSONDecodeError as e:
            details.append({"item": "booking_request.json 合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析错误: {str(e)}"})
            data = {}
    else:
        details.append({"item": "booking_request.json 合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        data = {}

    # 3. 检查必需字段是否存在 (20分)
    required_keys = ["flight_id", "total_cost", "policy_compliant"]
    missing_keys = [k for k in required_keys if k not in data]
    if not missing_keys:
        details.append({"item": "必需字段完整", "score": 20, "max_score": 20, "passed": True, "reason": f"包含 {required_keys}"})
        score += 20
    else:
        details.append({"item": "必需字段完整", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {missing_keys}"})
        # 后续检查仅在有字段时进行，否则跳过
        data = {k: None for k in required_keys}  # 防止后续 AttributeError

    # 4. 检查 flight_id 是否为正确值 "SKB-001" (30分)
    if data.get("flight_id") == "SKB-001":
        details.append({"item": "flight_id 正确", "score": 30, "max_score": 30, "passed": True, "reason": "flight_id = SKB-001"})
        score += 30
    else:
        details.append({"item": "flight_id 正确", "score": 0, "max_score": 30, "passed": False, "reason": f"flight_id = {data.get('flight_id')!r}，期望 'SKB-001'"})

    # 5. 检查 total_cost 是否为 3200 (20分)
    try:
        cost = data.get("total_cost")
        if isinstance(cost, (int, float)) and abs(cost - 3200) < 0.001:
            details.append({"item": "total_cost 正确", "score": 20, "max_score": 20, "passed": True, "reason": "total_cost = 3200"})
            score += 20
        else:
            details.append({"item": "total_cost 正确", "score": 0, "max_score": 20, "passed": False, "reason": f"total_cost = {cost!r}，期望 3200"})
    except:
        details.append({"item": "total_cost 正确", "score": 0, "max_score": 20, "passed": False, "reason": "total_cost 字段异常"})

    # 6. 检查 policy_compliant 是否为 True (10分)
    if data.get("policy_compliant") is True:
        details.append({"item": "policy_compliant 为 true", "score": 10, "max_score": 10, "passed": True, "reason": "policy_compliant = true"})
        score += 10
    else:
        details.append({"item": "policy_compliant 为 true", "score": 0, "max_score": 10, "passed": False, "reason": f"policy_compliant = {data.get('policy_compliant')!r}，期望 True"})

    # 总分
    total = min(score, 100)
    result = {"total_score": total, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
