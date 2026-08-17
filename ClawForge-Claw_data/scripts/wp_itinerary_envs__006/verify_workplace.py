import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查 ops/best_route.json 是否存在（10分）
    path = os.path.join(workspace, "ops", "best_route.json")
    if os.path.isfile(path):
        details.append({"item": "ops/best_route.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "ops/best_route.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续检查无法进行，直接返回
        return finalize(details, total_score)

    # 2. 检查 JSON 是否合法（10分）
    try:
        with open(path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        return finalize(details, total_score)

    # 3. 检查必含字段（20分）：route_id 和 transport
    has_route_id = "route_id" in data and isinstance(data["route_id"], str)
    has_transport = "transport" in data and isinstance(data["transport"], str)
    if has_route_id and has_transport:
        details.append({"item": "包含 route_id 和 transport 字段", "score": 20, "max_score": 20, "passed": True, "reason": "字段齐全"})
        total_score += 20
    else:
        missing = []
        if not has_route_id: missing.append("route_id")
        if not has_transport: missing.append("transport")
        details.append({"item": "包含 route_id 和 transport 字段", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失字段: {', '.join(missing)}"})
        # 即使缺失，继续检查已存在的部分

    # 4. 检查 route_id 是否正确（30分）：必须是 "BJS-SHA-01"
    if has_route_id:
        if data["route_id"] == "BJS-SHA-01":
            details.append({"item": "路由 ID 正确", "score": 30, "max_score": 30, "passed": True, "reason": "匹配预期 BJS-SHA-01"})
            total_score += 30
        else:
            details.append({"item": "路由 ID 正确", "score": 0, "max_score": 30, "passed": False, "reason": f"实际为 {data['route_id']}，期望 BJS-SHA-01"})
    else:
        details.append({"item": "路由 ID 正确", "score": 0, "max_score": 30, "passed": False, "reason": "route_id 字段缺失"})

    # 5. 检查 transport 是否正确（30分）：必须是 "direct_flight"
    if has_transport:
        if data["transport"] == "direct_flight":
            details.append({"item": "交通方式正确", "score": 30, "max_score": 30, "passed": True, "reason": "匹配预期 direct_flight"})
            total_score += 30
        else:
            details.append({"item": "交通方式正确", "score": 0, "max_score": 30, "passed": False, "reason": f"实际为 {data['transport']}，期望 direct_flight"})
    else:
        details.append({"item": "交通方式正确", "score": 0, "max_score": 30, "passed": False, "reason": "transport 字段缺失"})

    return finalize(details, total_score)

def finalize(details, total_score):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
