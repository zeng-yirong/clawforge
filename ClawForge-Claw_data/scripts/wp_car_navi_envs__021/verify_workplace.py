import os
import sys
import json
import math
import numbers

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # 1. 检查 ops/navi_021_chargers.json 是否存在
    result_path = os.path.join(workspace, "ops", "navi_021_chargers.json")
    if not os.path.isfile(result_path):
        details.append({
            "item": "产物文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/navi_021_chargers.json 文件不存在"
        })
        total_score = sum(d["score"] for d in details)
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        print(f"Total: {total_score}")
        return

    details.append({
        "item": "产物文件存在",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "ops/navi_021_chargers.json 已找到"
    })

    # 2. 解析 JSON 格式
    try:
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        total_score = 10  # 文件存在已得分
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        print(f"Total: {total_score}")
        return

    if not isinstance(data, list):
        details.append({
            "item": "JSON 是数组格式",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "结果应为数组，实际类型: " + str(type(data))
        })
        total_score = 10
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        print(f"Total: {total_score}")
        return

    details.append({
        "item": "JSON 格式合法",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "数组格式正确"
    })

    # 3. 检查数组长度是否为3（只有3个合格充电站）
    if len(data) != 3:
        details.append({
            "item": "筛选出的充电站数量正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望3条记录，实际{len(data)}条"
        })
    else:
        details.append({
            "item": "筛选出的充电站数量正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "共3条记录"
        })

    # 4. 逐条检查字段、类别、功率、距离
    # 先读取 scenarios.json 获取起点
    scenarios_path = os.path.join(workspace, "data", "scenarios.json")
    if not os.path.isfile(scenarios_path):
        details.append({
            "item": "data/scenarios.json 存在",
            "score": 0,
            "max_score": 0,  # 不加分，但用于后续计算
            "passed": False,
            "reason": "缺少 scenarios.json，无法验证距离"
        })
        # 仍然尝试用预设起点
        start_lat, start_lon = 39.9042, 116.4074
    else:
        with open(scenarios_path, "r", encoding="utf-8") as f:
            scenarios_data = json.load(f)
        scenarios_list = scenarios_data.get("scenarios", [])
        target = None
        for s in scenarios_list:
            if s.get("id") == "navi_021":
                target = s
                break
        if target is None:
            start_lat, start_lon = 39.9042, 116.4074
        else:
            start_lat = target["start"]["lat"]
            start_lon = target["start"]["lon"]

    # 准备预期结果（根据实际距离排序的 poi_id）
    # 预计算合格充电站的距离
    qualifiers = {
        "ch_001": {"lat": 39.9200, "lon": 116.4100, "kw": 120},
        "ch_002": {"lat": 39.8800, "lon": 116.3800, "kw": 60},
        "ch_003": {"lat": 39.9500, "lon": 116.4500, "kw": 150}
    }
    expected_order = sorted(qualifiers.keys(),
                            key=lambda pid: haversine(start_lat, start_lon,
                                                      qualifiers[pid]["lat"],
                                                      qualifiers[pid]["lon"]))

    field_ok = True
    distance_ok = True
    order_ok = True
    category_ok = True
    power_ok = True
    for idx, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_ok = False
            continue
        # 检查必要字段
        req_fields = ["poi_id", "name", "category", "charge_rate_kw", "distance"]
        for fld in req_fields:
            if fld not in entry:
                field_ok = False
                break
        if not field_ok:
            break
        # 检查类别
        if entry.get("category") != "charging":
            category_ok = False
        # 检查功率
        kw = entry.get("charge_rate_kw")
        if not isinstance(kw, numbers.Number) or kw < 60:
            power_ok = False
        # 检查距离（允许±0.5km误差）
        expected_dist = haversine(start_lat, start_lon,
                                  entry.get("lat", 0), entry.get("lon", 0))
        actual_dist = entry.get("distance")
        if not isinstance(actual_dist, numbers.Number):
            distance_ok = False
        elif abs(actual_dist - expected_dist) > 0.5:
            distance_ok = False
        # 记录排序预期
        if idx < len(expected_order):
            if entry.get("poi_id") != expected_order[idx]:
                order_ok = False
        else:
            order_ok = False

    # 汇总得分
    # 字段完整性
    if field_ok:
        details.append({
            "item": "字段完整性 (poi_id, name, category, charge_rate_kw, distance)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有记录包含必要字段"
        })
    else:
        details.append({
            "item": "字段完整性 (poi_id, name, category, charge_rate_kw, distance)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "部分记录缺少必要字段"
        })

    # 类别正确性
    if category_ok:
        details.append({
            "item": "类别均为 charging",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有记录 category 为 charging"
        })
    else:
        details.append({
            "item": "类别均为 charging",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在非 charging 类别的记录"
        })

    # 功率合格
    if power_ok:
        details.append({
            "item": "充电功率 >= 60 kW",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有记录功率 >=60kW"
        })
    else:
        details.append({
            "item": "充电功率 >= 60 kW",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在功率低于60kW的记录"
        })

    # 距离计算正确性（逐条检查，每条5分，共15分）
    dist_correct_count = 0
    for idx, entry in enumerate(data):
        expected_dist = haversine(start_lat, start_lon,
                                  entry.get("lat", 0), entry.get("lon", 0))
        actual_dist = entry.get("distance")
        if isinstance(actual_dist, numbers.Number) and abs(actual_dist - expected_dist) <= 0.5:
            dist_correct_count += 1
    if dist_correct_count == 3:
        details.append({
            "item": "每条记录的距离值计算正确",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "3条距离均偏差≤0.5km"
        })
    else:
        details.append({
            "item": "每条记录的距离值计算正确",
            "score": dist_correct_count * 5,
            "max_score": 15,
            "passed": False,
            "reason": f"只有{dist_correct_count}条距离正确"
        })

    # 排序正确性
    if order_ok:
        details.append({
            "item": "按距离升序排列",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "顺序与预期一致 (ch_001, ch_002, ch_003)"
        })
    else:
        details.append({
            "item": "按距离升序排列",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "排序错误"
        })

    # 计算总分
    total_score = sum(d["score"] for d in details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f)
    print(f"Total: {total_score}")

if __name__ == "__main__":
    main()
