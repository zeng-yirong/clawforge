import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    
    # ---------- 1. 目录结构检查 ----------
    required_dirs = ["ops", "data/offers/flightpro", "data/offers/skybook", "data/offers/aerocheap", "data/policies"]
    score_dir = 0
    max_dir = 10
    for d in required_dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            score_dir += 10 // len(required_dirs)
        else:
            details.append({"item": f"目录 {d} 存在", "score": 0, "max_score": 10//len(required_dirs), "passed": False, "reason": f"未找到目录 {d}"})
    if score_dir == 10:
        details.append({"item": "目录结构完整性", "score": 10, "max_score": 10, "passed": True, "reason": "所有必需目录均存在"})
    else:
        details.append({"item": "目录结构完整性", "score": score_dir, "max_score": 10, "passed": score_dir==10, "reason": f"部分目录缺失，实际得分 {score_dir}"})
    total_score += score_dir
    
    # ---------- 2. 结果文件存在性及合法性 ----------
    result_path = os.path.join(workspace, "ops", "best_option.json")
    if not os.path.isfile(result_path):
        details.append({"item": "结果文件 ops/best_option.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        total_score += 0
        # 后续检查无法进行，直接输出
        write_score(workspace, total_score, details)
        return
    else:
        details.append({"item": "结果文件 ops/best_option.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已生成"})
        total_score += 10
    
    # 读取并验证 JSON 合法性
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可正常解析"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        write_score(workspace, total_score, details)
        return
    
    # ---------- 3. 字段完整性 ----------
    required_fields = ["flight_id", "platform", "price", "cabin_class"]
    missing = [f for f in required_fields if f not in data]
    extra = [k for k in data if k not in required_fields]
    field_score = 0
    max_field = 20
    if not missing:
        field_score += 15
    if not extra:
        field_score += 5
    else:
        field_score = max(0, field_score - len(extra)*2)
    if field_score == max_field:
        details.append({"item": "字段完整性（无缺失、无多余）", "score": max_field, "max_score": max_field, "passed": True, "reason": "仅包含要求的四个字段"})
    else:
        issues = []
        if missing:
            issues.append(f"缺失字段: {', '.join(missing)}")
        if extra:
            issues.append(f"多余字段: {', '.join(extra)}")
        details.append({"item": "字段完整性", "score": field_score, "max_score": max_field, "passed": False, "reason": "; ".join(issues)})
    total_score += field_score
    
    # ---------- 4. 核心数值正确性 ----------
    correct_answer = {
        "flight_id": "FLP-20260615-001",
        "platform": "FlightPro",
        "price": 2200.00,
        "cabin_class": "business"
    }
    
    core_score = 0
    max_core = 60
    
    # 检查 flight_id
    if data.get("flight_id") == correct_answer["flight_id"]:
        core_score += 20
    else:
        details.append({"item": "flight_id 正确", "score": 0, "max_score": 20, "passed": False, "reason": f"期望 {correct_answer['flight_id']}, 实际 {data.get('flight_id')}"})
    
    # 检查 platform
    if data.get("platform") == correct_answer["platform"]:
        core_score += 15
    else:
        details.append({"item": "platform 正确", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 {correct_answer['platform']}, 实际 {data.get('platform')}"})
    
    # 检查 price（允许浮点误差 0.01）
    expected_price = correct_answer["price"]
    actual_price = data.get("price")
    if isinstance(actual_price, (int, float)) and abs(actual_price - expected_price) < 0.01:
        core_score += 15
    else:
        details.append({"item": "price 正确", "score": 0, "max_score": 15, "passed": False, "reason": f"期望 {expected_price}, 实际 {actual_price}"})
    
    # 检查 cabin_class
    if data.get("cabin_class") == correct_answer["cabin_class"]:
        core_score += 10
    else:
        details.append({"item": "cabin_class 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 {correct_answer['cabin_class']}, 实际 {data.get('cabin_class')}"})
    
    if core_score == max_core:
        details.append({"item": "核心数据完全正确", "score": max_core, "max_score": max_core, "passed": True, "reason": "所有字段均匹配预期答案"})
    else:
        # 如果已添加过单项，无需再添加总结项，但为了细节完整，添加一个汇总
        details.append({"item": "核心数据正确性汇总", "score": core_score, "max_score": max_core, "passed": core_score==max_core, "reason": f"单项得分已记录, 合计 {core_score}/{max_core}"})
    total_score += core_score
    
    # 确保总分不超过100
    total_score = min(total_score, 100)
    write_score(workspace, total_score, details)

def write_score(workspace, total_score, details):
    output = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score written to {score_path}: {total_score}/100")

if __name__ == "__main__":
    main()
