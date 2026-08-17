import sys
import os
import json
import math

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def check_path_exists(path):
    return os.path.exists(os.path.join(WORKSPACE, path))

def main():
    details = []
    total = 0

    # 1. 目录结构检查 (10分)
    score = 0
    max_score = 10
    required_dirs = ["data", "data/platforms", "data/policies", "ops"]
    all_dirs_exist = True
    for d in required_dirs:
        if not check_path_exists(d):
            all_dirs_exist = False
    if all_dirs_exist:
        score = max_score
        details.append({"item": "目录结构完整性", "score": score, "max_score": max_score, "passed": True, "reason": "所有必需目录均存在"})
    else:
        details.append({"item": "目录结构完整性", "score": 0, "max_score": max_score, "passed": False, "reason": "缺少必需目录"})
    total += score

    # 2. 产物文件存在性 (10分)
    score = 0
    max_score = 10
    result_path = "ops/booking_recommendation.json"
    if check_path_exists(result_path):
        score = max_score
        details.append({"item": "产物文件存在", "score": score, "max_score": max_score, "passed": True, "reason": f"文件 {result_path} 存在"})
    else:
        details.append({"item": "产物文件存在", "score": 0, "max_score": max_score, "passed": False, "reason": f"文件 {result_path} 不存在"})
        total += score
        # 如果关键文件不存在，后续检查跳过并记0分
        total += sum([20, 20, 20, 10, 10])  # 剩余分直接归零，但细节里标记未检查
        for item_name, weight in [("JSON格式合法性",10), ("必填字段存在",10), ("选择平台正确性",20), ("价格计算正确性",30), ("合规性验证",20)]:
            details.append({"item": item_name, "score": 0, "max_score": weight, "passed": False, "reason": "产物文件缺失，无法检查"})
        # 输出分数
        result = {"total_score": total, "details": details}
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. JSON格式合法性 (10分)
    score = 0
    max_score = 10
    try:
        data = load_json(os.path.join(WORKSPACE, result_path))
        if isinstance(data, dict):
            score = max_score
            details.append({"item": "JSON格式合法性", "score": score, "max_score": max_score, "passed": True, "reason": "合法JSON对象"})
        else:
            details.append({"item": "JSON格式合法性", "score": 0, "max_score": max_score, "passed": False, "reason": "JSON根元素不是对象"})
    except Exception as e:
        details.append({"item": "JSON格式合法性", "score": 0, "max_score": max_score, "passed": False, "reason": f"JSON解析失败: {str(e)}"})
    total += score

    # 4. 必填字段存在 (10分)
    score = 0
    max_score = 10
    required_fields = ["platform_id", "flight_id", "total_price", "cabin_class", "is_policy_compliant"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        score = max_score
        details.append({"item": "必填字段存在", "score": score, "max_score": max_score, "passed": True, "reason": "所有必填字段存在"})
    else:
        details.append({"item": "必填字段存在", "score": 0, "max_score": max_score, "passed": False, "reason": f"缺少字段: {missing}"})
    total += score

    # 5. 选择平台正确性 (20分)
    score = 0
    max_score = 20
    # 预期答案: 根据trip_request和政策，有效平台只有skybook（active且允许商务舱），且skybook下有SB-601航班商务舱4200+税费=4270 <=5000，且是唯一合规最便宜。
    # 必须检查platform_id为"skybook"，flight_id为"SB-601"。
    correct_platform = "skybook"
    correct_flight = "SB-601"
    if data.get("platform_id") == correct_platform and data.get("flight_id") == correct_flight:
        score = max_score
        details.append({"item": "选择平台正确性", "score": score, "max_score": max_score, "passed": True, "reason": f"选定了正确的平台和航班: {correct_platform}/{correct_flight}"})
    else:
        details.append({"item": "选择平台正确性", "score": 0, "max_score": max_score, "passed": False, "reason": f"预期平台={correct_platform},航班={correct_flight}; 实际平台={data.get('platform_id')},航班={data.get('flight_id')}"})
    total += score

    # 6. 价格计算正确性 (30分)
    score = 0
    max_score = 30
    # 计算预期总价：SB-601 base_price=4200, SkyBook transaction_fee=50, service_fee=20 => total=4270
    expected_total = 4200 + 50 + 20  # 4270
    actual_total = data.get("total_price")
    if actual_total is not None and abs(actual_total - expected_total) < 0.01:
        score = max_score
        details.append({"item": "价格计算正确性", "score": score, "max_score": max_score, "passed": True, "reason": f"总价正确: {actual_total} USD"})
    else:
        details.append({"item": "价格计算正确性", "score": 0, "max_score": max_score, "passed": False, "reason": f"预期总价{expected_total}, 实际{actual_total}"})
    total += score

    # 7. 合规性验证 (20分)
    score = 0
    max_score = 20
    # 应标记为true，且max_cost_per_booking=5000，商务舱允许，日期满足提前1天等
    if data.get("is_policy_compliant") is True:
        score = max_score
        details.append({"item": "合规性验证", "score": score, "max_score": max_score, "passed": True, "reason": "标记为符合政策"})
    else:
        details.append({"item": "合规性验证", "score": 0, "max_score": max_score, "passed": False, "reason": f"is_policy_compliant应为True, 实际为{data.get('is_policy_compliant')}"})
    total += score

    # 8. 额外检查：记录扣分（可选，但不影响总分，这里不设额外项）
    # 写入最终分数
    result = {"total_score": total, "details": details}
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
