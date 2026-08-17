import os
import json
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 检查目录结构
    ops_dir = os.path.join(workspace, "ops")
    if not os.path.isdir(ops_dir):
        results.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops dir not found"})
    else:
        results.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ok"})
        total_score += 5

    # 检查目标文件是否存在
    target_path = os.path.join(workspace, "ops", "trip_waypoints.json")
    if not os.path.isfile(target_path):
        results.append({"item": "trip_waypoints.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
        print(json.dumps({"total_score": total_score, "details": results}, ensure_ascii=False))
        return

    # 检查文件合法性（JSON）
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        results.append({"item": "JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        print(json.dumps({"total_score": total_score, "details": results}, ensure_ascii=False))
        return

    results.append({"item": "JSON valid", "score": 10, "max_score": 10, "passed": True, "reason": "valid JSON"})
    total_score += 10

    # 读取正确的 plan.txt 和最新POI数据
    plan_path = os.path.join(workspace, "plan.txt")
    if not os.path.isfile(plan_path):
        results.append({"item": "plan.txt readable", "score": 0, "max_score": 5, "passed": False, "reason": "plan.txt missing"})
        print(json.dumps({"total_score": total_score, "details": results}, ensure_ascii=False))
        return

    with open(plan_path, "r", encoding="utf-8") as f:
        expected_names = [line.strip() for line in f if line.strip()]

    # 读取最新POI（v2）
    poi_v2_path = os.path.join(workspace, "data", "pois_v2.json")
    if not os.path.isfile(poi_v2_path):
        results.append({"item": "pois_v2.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "reference data missing"})
        print(json.dumps({"total_score": total_score, "details": results}, ensure_ascii=False))
        return

    with open(poi_v2_path, "r", encoding="utf-8") as f:
        poi_v2 = json.load(f)

    # 构建名称->ID映射（只从最新版取）
    name_to_id = {poi["name"]: poi["poi_id"] for poi in poi_v2["pois"]}

    # 构建期望的waypoints列表（顺序对应plan.txt，且仅当名称在最新版中存在）
    expected_waypoints = []
    for name in expected_names:
        if name in name_to_id:
            expected_waypoints.append(name_to_id[name])
        else:
            # 如果找不到，期望为空（但设计上所有名称都在v2中）
            pass

    # 检查输出结构
    if isinstance(data, list):
        output_waypoints = data
    elif isinstance(data, dict):
        # 允许包裹在 "waypoints" 键下
        output_waypoints = data.get("waypoints", data.get("poi_ids", []))
        if not isinstance(output_waypoints, list):
            results.append({"item": "output structure", "score": 0, "max_score": 10, "passed": False, "reason": "expected list or dict with waypoints key"})
            print(json.dumps({"total_score": total_score, "details": results}, ensure_ascii=False))
            return
    else:
        results.append({"item": "output structure", "score": 0, "max_score": 10, "passed": False, "reason": "output is not list or dict"})
        print(json.dumps({"total_score": total_score, "details": results}, ensure_ascii=False))
        return

    results.append({"item": "output structure", "score": 10, "max_score": 10, "passed": True, "reason": "valid list structure"})
    total_score += 10

    # 检查元素数量
    if len(output_waypoints) != len(expected_waypoints):
        results.append({"item": "waypoint count", "score": 0, "max_score": 15, "passed": False, "reason": f"expected {len(expected_waypoints)} waypoints, got {len(output_waypoints)}"})
    else:
        results.append({"item": "waypoint count", "score": 15, "max_score": 15, "passed": True, "reason": f"correct count {len(expected_waypoints)}"})
        total_score += 15

    # 检查每个元素是否为字符串且符合预期
    waypoint_mismatch = False
    for i, (got, exp) in enumerate(zip(output_waypoints, expected_waypoints)):
        if not isinstance(got, str) or got != exp:
            waypoint_mismatch = True
            break
    if waypoint_mismatch:
        results.append({"item": "waypoint ids order", "score": 0, "max_score": 30, "passed": False, "reason": f"mismatch at index {i}: expected {exp}, got {got}"})
    else:
        results.append({"item": "waypoint ids order", "score": 30, "max_score": 30, "passed": True, "reason": "all ids correct and in order"})
        total_score += 30

    # 不允许包含多余字段（例如距离等本任务不要求的）
    if isinstance(data, dict) and len(data) != 1:
        results.append({"item": "no extra keys", "score": 0, "max_score": 5, "passed": False, "reason": f"unexpected keys: {list(data.keys())}"})
    else:
        results.append({"item": "no extra keys", "score": 5, "max_score": 5, "passed": True, "reason": "clean output"})
        total_score += 5

    # 写入评分
    final_score = min(100, total_score)
    output = {
        "total_score": final_score,
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)

    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    verify()
