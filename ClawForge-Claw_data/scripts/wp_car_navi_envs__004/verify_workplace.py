import json
import sys
import os
import math

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(relative_path):
    path = os.path.join(WORKSPACE, relative_path)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def euclidean_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def main():
    details = []
    total = 0

    # 1. ops/ 目录存在
    ops_dir = os.path.join(WORKSPACE, "ops")
    passed = os.path.isdir(ops_dir)
    details.append({"item": "ops目录存在", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": "ops/目录" + ("存在" if passed else "不存在")})
    if passed:
        total += 10

    # 2. selected_chargers.json 存在
    result_path = os.path.join(ops_dir, "selected_chargers.json")
    passed = os.path.isfile(result_path)
    details.append({"item": "selected_chargers.json存在", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": "文件" + ("存在" if passed else "不存在")})
    if passed:
        total += 10

    # 3. JSON 合法
    result_data = None
    passed = False
    reason = ""
    if os.path.isfile(result_path):
        try:
            with open(result_path, "r", encoding="utf-8") as f:
                result_data = json.load(f)
            passed = True
            reason = "JSON解析成功"
        except (json.JSONDecodeError, Exception) as e:
            reason = f"JSON解析失败: {e}"
    else:
        reason = "文件不存在，无法解析"
    details.append({"item": "JSON格式合法", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": reason})
    if passed:
        total += 10

    # 4. 内容是列表
    passed = isinstance(result_data, list)
    details.append({"item": "内容是列表", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": "类型是" + str(type(result_data)) if not passed else "是列表"})
    if passed:
        total += 10

    if not isinstance(result_data, list):
        # 无法继续，直接输出
        score = {"total_score": total, "details": details}
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump(score, f, indent=2)
        return

    # 5. 列表长度等于3
    passed = len(result_data) == 3
    details.append({"item": "列表长度=3", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": f"长度为{len(result_data)}"})
    if passed:
        total += 10

    # 6. 每个元素是有效的poi_id字符串
    pois_raw = load_json("data/pois.json")
    all_poi_ids = set()
    if pois_raw and "pois" in pois_raw:
        for p in pois_raw["pois"]:
            all_poi_ids.add(p["poi_id"])
    passed = all(isinstance(x, str) and x in all_poi_ids for x in result_data)
    details.append({"item": "所有元素是有效poi_id", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": "检查通过" if passed else "存在无效ID"})
    if passed:
        total += 10

    # 7. 所有poi_id的category均为charging
    passed = True
    if pois_raw:
        cat_map = {p["poi_id"]: p.get("category") for p in pois_raw["pois"]}
        for pid in result_data:
            if cat_map.get(pid) != "charging":
                passed = False
                break
    else:
        passed = False
    details.append({"item": "均为充电站", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": "检查通过" if passed else "存在非充电站"})
    if passed:
        total += 10

    # 8. 排除充电速率低于50的（ch_006不应出现）
    passed = "ch_006" not in result_data
    details.append({"item": "排除充电速率<50", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": "ch_006被排除" if passed else "ch_006出现在结果中"})
    if passed:
        total += 10

    # 9. 去重（ch_001只出现一次）
    passed = result_data.count("ch_001") == 1
    details.append({"item": "去重正确", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": "ch_001出现次数" + str(result_data.count("ch_001"))})
    if passed:
        total += 10

    # 10. 距离排序正确（按到外环高速中心点距离升序）
    # 外环高速中心点：从traffic_data中获取，但固定为(31.2, 121.5)
    center_lat = 31.2
    center_lon = 121.5
    # 加载原始充电站数据，排除重复和速率低的，去重并计算距离
    charger_list = []
    seen_ids = set()
    if pois_raw and "pois" in pois_raw:
        for p in pois_raw["pois"]:
            if p["poi_id"] in seen_ids:
                continue
            if p.get("category") != "charging":
                continue
            if p.get("charge_rate_kw", 0) < 50:
                continue
            seen_ids.add(p["poi_id"])
            dist = euclidean_distance(p["lat"], p["lon"], center_lat, center_lon)
            charger_list.append((p["poi_id"], dist))
    charger_list.sort(key=lambda x: x[1])
    expected_ids = [pid for pid, _ in charger_list[:3]]
    passed = result_data == expected_ids
    details.append({"item": "距离排序正确", "score": 10 if passed else 0, "max_score": 10, "passed": passed, "reason": f"期望顺序{expected_ids}, 实际{result_data}"})
    if passed:
        total += 10

    # 输出最终评分
    score = {"total_score": total, "details": details}
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump(score, f, indent=2)

if __name__ == "__main__":
    main()
