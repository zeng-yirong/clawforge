"""
verify_workplace.py - 验证 Agent 产出的 best_route.json 是否正确
评分项：
  1. ops 目录存在 (10分)
  2. best_route.json 文件存在且合法 JSON (10分)
  3. 包含必需字段 route_id 和 total_duration_h (20分)
  4. route_id 正确为 "BJS-NKG-SHA" (30分)
  5. total_duration_h 正确为 5.5 (30分)   (高铁4.0 + 高铁1.5 = 5.5)
满分100，逐项累加。
"""
import sys
import os
import json

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. 检查 ops 目录是否存在
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops目录存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "ops目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到ops目录"})
        # 后续无法检查，直接返回
        return {"total_score": total_score, "details": details}

    # 2. 检查 best_route.json 文件
    json_path = os.path.join(ops_dir, "best_route.json")
    if not os.path.isfile(json_path):
        details.append({"item": "best_route.json存在且合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        return {"total_score": total_score, "details": details}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "best_route.json存在且合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且可解析"})
        total_score += 10
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "best_route.json存在且合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        return {"total_score": total_score, "details": details}

    # 3. 检查必需字段
    required_fields = ["route_id", "total_duration_h"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        details.append({"item": "包含必需字段route_id和total_duration_h", "score": 20, "max_score": 20, "passed": True, "reason": "字段齐全"})
        total_score += 20
    else:
        details.append({"item": "包含必需字段route_id和total_duration_h", "score": 0, "max_score": 20, "passed": False, "reason": f"缺少字段: {', '.join(missing)}"})
        # 后面无法检查具体值，但可以继续检查已存在的字段
        # 但为了公平，若缺失某个字段，则该值检查自动0分
        # 我们仍检查存在的字段，但避免重复扣分？这里简化：若缺失则相关项0分

    # 4. 检查 route_id
    expected_route_id = "BJS-NKG-SHA"
    if "route_id" in data:
        passed = data["route_id"] == expected_route_id
        details.append({"item": f"route_id正确应为'{expected_route_id}'", "score": 30 if passed else 0, "max_score": 30, "passed": passed, "reason": f"实际值: {data.get('route_id')}"})
        if passed:
            total_score += 30
    else:
        details.append({"item": f"route_id正确应为'{expected_route_id}'", "score": 0, "max_score": 30, "passed": False, "reason": "route_id字段缺失"})

    # 5. 检查 total_duration_h
    expected_duration = 5.5  # 高铁4.0 + 高铁1.5 = 5.5
    if "total_duration_h" in data:
        actual = data["total_duration_h"]
        # 允许浮点数微小误差（0.01）
        passed = abs(actual - expected_duration) < 0.01
        details.append({"item": f"total_duration_h正确应为{expected_duration}", "score": 30 if passed else 0, "max_score": 30, "passed": passed, "reason": f"实际值: {actual}"})
        if passed:
            total_score += 30
    else:
        details.append({"item": f"total_duration_h正确应为{expected_duration}", "score": 0, "max_score": 30, "passed": False, "reason": "total_duration_h字段缺失"})

    # 确保总分不超过100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    # 写入 workplace_score.json
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Score written to {score_path}: {result['total_score']}/100")

if __name__ == "__main__":
    main()
