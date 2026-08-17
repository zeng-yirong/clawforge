import json
import os
import sys
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def check(condition, item_name, score, max_score, reason=""):
    return {
        "item": item_name,
        "score": score if condition else 0,
        "max_score": max_score,
        "passed": condition,
        "reason": reason if not condition else ""
    }

def main():
    result_path = os.path.join(workspace, "ops", "nav_plan.json")
    details = []

    # 1. 文件存在性 (10分)
    exists = os.path.isfile(result_path)
    details.append(check(exists, "文件 ops/nav_plan.json 存在", 10, 10, "文件缺失"))

    if not exists:
        details.append({"item": "后续检查", "score": 0, "max_score": 90, "passed": False, "reason": "前置失败"})
        write_score(details)
        return

    try:
        plan = load_json(result_path)
    except Exception as e:
        details.append(check(False, "JSON 解析合法", 10, 10, f"解析失败: {e}"))
        write_score(details)
        return

    # 2. JSON 结构合法性 (10分)
    is_dict = isinstance(plan, dict)
    details.append(check(is_dict, "JSON 顶层为字典", 10, 10, "不是字典"))

    if not is_dict:
        write_score(details)
        return

    # 3. 必含字段 (10分)
    required_fields = ["start", "waypoints", "destination", "preference"]
    missing = [f for f in required_fields if f not in plan]
    details.append(check(len(missing)==0, "包含所有必需字段: start, waypoints, destination, preference",
                         10, 10, f"缺少字段: {missing}"))

    if missing:
        write_score(details)
        return

    # 4. 检查 start 字段 (10分)
    start = plan["start"]
    expected_start = {"lat": 39.9042, "lon": 116.4074}
    start_ok = isinstance(start, dict) and \
               abs(start.get("lat",-1) - expected_start["lat"]) < 0.001 and \
               abs(start.get("lon",-1) - expected_start["lon"]) < 0.001
    details.append(check(start_ok, "起点坐标正确 (市中心区域 center)", 10, 10,
                         f"期望 ({expected_start['lat']}, {expected_start['lon']}), 实际 {start}"))

    # 5. 检查 destination 字段 (20分)
    dest = plan["destination"]
    expected_dest_poi_id = "airport_dest"
    expected_dest_coord = {"lat": 40.08, "lon": 116.59}
    dest_ok = isinstance(dest, dict) and \
              dest.get("poi_id") == expected_dest_poi_id and \
              abs(dest.get("lat",-1) - expected_dest_coord["lat"]) < 0.001 and \
              abs(dest.get("lon",-1) - expected_dest_coord["lon"]) < 0.001
    details.append(check(dest_ok, "终点正确 (首都机场T3)", 20, 20,
                         f"期望 poi_id={expected_dest_poi_id}, 坐标 ({expected_dest_coord['lat']},{expected_dest_coord['lon']}), 实际 {dest}"))

    # 6. 检查 waypoints (30分)
    waypoints = plan["waypoints"]
    is_list = isinstance(waypoints, list)
    details.append(check(is_list, "waypoints 是数组", 5, 5, "不是数组"))

    if not is_list:
        write_score(details)
        return

    # 应包含两个途经点：充电站和麦当劳，顺序不限
    expected_ids = {"charge_fast", "food_mcd"}
    actual_ids = set()
    for wp in waypoints:
        if isinstance(wp, dict):
            pid = wp.get("poi_id")
            if pid:
                actual_ids.add(pid)
    waypoints_ok = expected_ids == actual_ids
    details.append(check(waypoints_ok, "途经点包含超级充电站和麦当劳", 25, 25,
                         f"期望 ID 集合 {expected_ids}, 实际 {actual_ids}"))

    # 7. 检查 preference (10分)
    pref = plan.get("preference")
    pref_ok = pref == "avoid_congestion"
    details.append(check(pref_ok, "路线偏好为避开拥堵", 10, 10,
                         f"期望 'avoid_congestion', 实际 {pref}"))

    # 8. 检查无多余字段 (5分)
    allowed_keys = {"start", "waypoints", "destination", "preference"}
    extra_keys = set(plan.keys()) - allowed_keys
    extra_ok = len(extra_keys) == 0
    details.append(check(extra_ok, "无多余字段", 5, 5,
                         f"多余字段: {extra_keys}"))

    # 汇总分数
    write_score(details)

def write_score(details):
    total = sum(d["score"] for d in details)
    max_total = sum(d["max_score"] for d in details)
    final = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    print(f"总分: {total}/{max_total}")

if __name__ == "__main__":
    main()
