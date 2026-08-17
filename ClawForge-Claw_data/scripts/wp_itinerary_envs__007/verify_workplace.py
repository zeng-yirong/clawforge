import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score_details = []
    total_score = 0

    # 1. 检查必需文件是否存在（10分）
    required_files = ["itinerary.json"]
    for f in required_files:
        if (ws / f).exists():
            score_details.append({"item": f"文件 {f} 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
            total_score += 10
        else:
            score_details.append({"item": f"文件 {f} 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})

    # 2. 解析 itinerary.json 并验证结构（20分）
    it_path = ws / "itinerary.json"
    if it_path.exists():
        try:
            with open(it_path, "r") as f:
                itinerary = json.load(f)
        except json.JSONDecodeError:
            score_details.append({"item": "JSON解析", "score": 0, "max_score": 20, "passed": False, "reason": "JSON格式错误"})
            total_score += 0
            write_result(total_score, score_details)
            return

        # 结构要求：必须是一个列表，每个元素是包含 origin, destination, transport, cost, duration 的字典
        if not isinstance(itinerary, list):
            score_details.append({"item": "行程结构", "score": 0, "max_score": 10, "passed": False, "reason": "根节点不是列表"})
            total_score += 0
            write_result(total_score, score_details)
            return

        if len(itinerary) != 4:
            score_details.append({"item": "行程段数", "score": 0, "max_score": 10, "passed": False, "reason": f"段数为{len(itinerary)}，期望4"})
            total_score += 0
        else:
            score_details.append({"item": "行程段数", "score": 10, "max_score": 10, "passed": True, "reason": "4段行程"})
            total_score += 10

        # 检查每一段必须字段
        structure_ok = True
        for i, leg in enumerate(itinerary):
            required_keys = ["origin", "destination", "transport", "cost", "duration"]
            missing = [k for k in required_keys if k not in leg]
            if missing:
                structure_ok = False
                score_details.append({"item": f"第{i+1}段字段完整", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少{missing}"})
                total_score += 0
                break
        if structure_ok:
            score_details.append({"item": "所有段字段完整", "score": 10, "max_score": 10, "passed": True, "reason": "每个leg包含必需字段"})
            total_score += 10
    else:
        score_details.append({"item": "itinerary.json解析", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        write_result(total_score, score_details)
        return

    # 3. 验证行程顺序和交通方式（60分）
    expected_sequence = [
        {"origin": "BJS", "destination": "SHA", "transport": "high_speed_train"},
        {"origin": "SHA", "destination": "HGH", "transport": "high_speed_train"},
        {"origin": "HGH", "destination": "CAN", "transport": "direct_flight"},
        {"origin": "CAN", "destination": "BJS", "transport": "direct_flight"}
    ]
    # 允许交通方式：high_speed_train, direct_flight, 普通火车
    # 正确答案：
    # 北京-上海：高铁 (快速+便宜，符合笔记)
    # 上海-杭州：高铁
    # 杭州-广州：飞机（笔记明确让选飞机）
    # 广州-北京：飞机（笔记说飞机）
    # 如果选别的交通方式，扣分

    sequence_correct = True
    for i, (leg, exp) in enumerate(zip(itinerary, expected_sequence)):
        if leg.get("origin") != exp["origin"] or leg.get("destination") != exp["destination"]:
            sequence_correct = False
            score_details.append({"item": f"第{i+1}段城市顺序", "score": 0, "max_score": 15, "passed": False, "reason": f"期望{exp['origin']}->{exp['destination']}，实际{leg.get('origin')}->{leg.get('destination')}"})
            total_score += 0
            break
    if sequence_correct:
        score_details.append({"item": "城市顺序", "score": 15, "max_score": 15, "passed": True, "reason": "顺序正确"})
        total_score += 15

    # 交通方式匹配
    transport_correct = True
    for i, (leg, exp) in enumerate(zip(itinerary, expected_sequence)):
        if leg.get("transport") != exp["transport"] and not (i==2 and leg.get("transport")=="direct_flight"):  # 简单检查
            transport_correct = False
            score_details.append({"item": f"第{i+1}段交通方式", "score": 0, "max_score": 20, "passed": False, "reason": f"期望{exp['transport']}，实际{leg.get('transport')}"})
            total_score += 0
            break
    if transport_correct:
        score_details.append({"item": "交通方式", "score": 20, "max_score": 20, "passed": True, "reason": "所有交通方式符合预期"})
        total_score += 20

    # 数值合理性（15分）
    # 从路由数据中获取期望的成本和时间
    # 加载路由数据以验证准确性
    routes_path = ws / "data" / "routes.json"
    if routes_path.exists():
        with open(routes_path) as f:
            routes = json.load(f)
    else:
        routes = {}

    cost_total_expected = 0
    duration_total_expected = 0.0
    ref_segments = [
        ("R1", "high_speed_train"),
        ("R2", "high_speed_train"),
        ("R3", "direct_flight"),
        ("R4", "direct_flight")
    ]
    for route_id, transport_key in ref_segments:
        route = routes.get(route_id)
        if route and transport_key in route and route[transport_key]:
            cost_total_expected += route[transport_key]["cost_cny"]
            duration_total_expected += route[transport_key]["duration_h"]
    # 允许±10%误差
    tolerance = 0.10
    cost_total_actual = sum(leg.get("cost", 0) for leg in itinerary)
    duration_total_actual = sum(leg.get("duration", 0) for leg in itinerary)

    if cost_total_actual < 0:
        cost_ok = False
    else:
        cost_diff = abs(cost_total_actual - cost_total_expected) / cost_total_expected if cost_total_expected else 1
        cost_ok = cost_diff <= tolerance
    if duration_total_actual < 0:
        dur_ok = False
    else:
        dur_diff = abs(duration_total_actual - duration_total_expected) / duration_total_expected if duration_total_expected else 1
        dur_ok = dur_diff <= tolerance

    if cost_ok and dur_ok:
        score_details.append({"item": "总成本与总时间合理", "score": 15, "max_score": 15, "passed": True, "reason": f"成本={cost_total_actual}(期望{cost_total_expected}),时间={duration_total_actual}(期望{duration_total_expected})"})
        total_score += 15
    else:
        score_details.append({"item": "总成本与总时间合理", "score": 0, "max_score": 15, "passed": False, "reason": f"成本={cost_total_actual}(期望{cost_total_expected}),时间={duration_total_actual}(期望{duration_total_expected})"})
        total_score += 0

    # 总预算检查（笔记说不超过5000）：5分
    if cost_total_actual <= 5000:
        score_details.append({"item": "预算符合要求", "score": 5, "max_score": 5, "passed": True, "reason": f"总成本{cost_total_actual}<=5000"})
        total_score += 5
    else:
        score_details.append({"item": "预算符合要求", "score": 0, "max_score": 5, "passed": False, "reason": f"总成本{cost_total_actual}>5000"})
        total_score += 0

    # 最终总分取整
    total_score = min(total_score, 100)
    write_result(total_score, score_details)

def write_result(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {score}")

if __name__ == "__main__":
    main()
