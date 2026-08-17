import sys
import json
import os

def verify(workspace: str) -> dict:
    details = []
    total = 0

    # 1) 目录结构（10分）
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "目录 ops/ 已创建"
        })
        total += 10
    else:
        details.append({
            "item": "ops目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到 ops/ 目录"
        })

    # 2) 结果文件存在（10分）
    route_path = os.path.join(workspace, "ops", "route_plan.json")
    if os.path.isfile(route_path):
        details.append({
            "item": "route_plan.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件 ops/route_plan.json 存在"
        })
        total += 10
    else:
        details.append({
            "item": "route_plan.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到 ops/route_plan.json"
        })
        # 后续检查无法进行，直接返回
        return {"total_score": total, "details": details}

    # 3) JSON格式合法 + 结构正确（10分）
    try:
        with open(route_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        details.append({
            "item": "JSON格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不是合法JSON"
        })
        return {"total_score": total, "details": details}

    if not isinstance(data, dict) or "waypoints" not in data:
        details.append({
            "item": "JSON含waypoints字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "根对象缺少 waypoints 字段"
        })
        return {"total_score": total, "details": details}

    waypoints = data["waypoints"]
    if not isinstance(waypoints, list):
        details.append({
            "item": "waypoints为数组",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "waypoints 不是数组"
        })
        return {"total_score": total, "details": details}

    details.append({
        "item": "JSON格式合法 & waypoints字段存在",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "合法JSON，含 waypoints 数组"
    })
    total += 10

    # 4) 剔除脏数据（30分）—— 不能包含不可用的POI
    # 不可用的充电站：charger_02 (charge_rate_kw=0)
    # 不可用的餐厅：rest_02 (available=False)
    # 可以包含其他可用POI（但只期望两个）
    # 检查数组内容
    invalid_found = False
    invalid_reason = []
    available_charging_ids = {"charger_01"}
    available_food_ids = {"rest_01"}

    for idx, wp in enumerate(waypoints):
        if not isinstance(wp, str):
            invalid_found = True
            invalid_reason.append(f"元素{idx}不是字符串")
            continue
        if wp == "charger_02":
            invalid_found = True
            invalid_reason.append("包含不可用的充电站 charger_02")
        if wp == "rest_02":
            invalid_found = True
            invalid_reason.append("包含已关闭的餐厅 rest_02")
        # 额外检查：是否包含其他不相关的POI（虽然不强制，但属于多余扣除一部分分数）
    
    if invalid_found:
        details.append({
            "item": "剔除脏数据（不可用POI）",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "; ".join(invalid_reason)
        })
    else:
        # 检查是否只包含预期可用的POI（charger_01, rest_01）且数量正确
        expected = ["charger_01", "rest_01"]
        if waypoints == expected:
            details.append({
                "item": "剔除脏数据（不可用POI）",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": "只包含可用POI，且顺序待后续判断"
            })
            total += 30
        else:
            # 部分正确但多出或缺失
            score = 0
            reason_parts = []
            # 检查是否包含charger_01
            if "charger_01" in waypoints:
                score += 10
            else:
                reason_parts.append("缺少充电站 charger_01")
            if "rest_01" in waypoints:
                score += 10
            else:
                reason_parts.append("缺少餐厅 rest_01")
            # 检查是否有额外非法POI（超过2个）
            extra = [wp for wp in waypoints if wp not in expected]
            if extra:
                reason_parts.append(f"多余POI: {extra}")
            details.append({
                "item": "剔除脏数据（不可用POI）",
                "score": score,
                "max_score": 30,
                "passed": score == 30,
                "reason": "; ".join(reason_parts) if reason_parts else ""
            })
            total += score

    # 5) 正确顺序（40分）
    correct_order = ["charger_01", "rest_01"]
    if "waypoints" in locals() or "waypoints" in dir():
        if waypoints == correct_order:
            details.append({
                "item": "途经点顺序正确（先充电后吃饭）",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": "顺序符合要求：charger_01 -> rest_01"
            })
            total += 40
        else:
            # 检查是否交换了顺序
            reversed_order = ["rest_01", "charger_01"]
            if waypoints == reversed_order:
                details.append({
                    "item": "途经点顺序正确",
                    "score": 0,
                    "max_score": 40,
                    "passed": False,
                    "reason": "顺序为 rest_01 在前，但应先去充电"
                })
            else:
                details.append({
                    "item": "途经点顺序正确",
                    "score": 0,
                    "max_score": 40,
                    "passed": False,
                    "reason": f"实际顺序 {waypoints} 与预期 {correct_order} 不符"
                })

    # 最终总分
    return {"total_score": total, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
