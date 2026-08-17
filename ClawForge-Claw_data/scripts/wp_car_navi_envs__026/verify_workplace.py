import sys, os, json, math, re

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = {"total_score": 0, "details": []}

    # 1. 检查产出文件是否存在
    waypoints_path = os.path.join(workspace, "plans", "waypoints.json")
    if not os.path.exists(waypoints_path):
        result["details"].append({"item": "产出文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 plans/waypoints.json 不存在"})
        result["total_score"] = 0
        _write_result(workspace, result)
        return
    result["details"].append({"item": "产出文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})

    # 2. 解析产出 JSON
    try:
        with open(waypoints_path, "r") as f:
            agent_output = json.load(f)
    except Exception as e:
        result["details"].append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        result["total_score"] = 10
        _write_result(workspace, result)
        return

    if not isinstance(agent_output, list) or not all(isinstance(x, str) for x in agent_output):
        result["details"].append({"item": "内容格式正确", "score": 0, "max_score": 10, "passed": False, "reason": "产出必须是一个字符串列表"})
        result["total_score"] = 10
        _write_result(workspace, result)
        return
    result["details"].append({"item": "JSON 格式合法且为字符串列表", "score": 10, "max_score": 10, "passed": True, "reason": "格式正确"})

    # 3. 读取请求文件，获取起点和条件
    request_path = os.path.join(workspace, "trips", "charge_plan_request.txt")
    origin_lat, origin_lon, min_power, max_results = None, None, 150, 3
    if os.path.exists(request_path):
        try:
            with open(request_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("User Location:"):
                        parts = line.split(":")[1].strip().split(",")
                        origin_lat = float(parts[0].strip())
                        origin_lon = float(parts[1].strip())
                    elif line.startswith("Preferred Charging Power:"):
                        nums = re.findall(r'\d+', line)
                        if nums:
                            min_power = int(nums[0])
                    elif line.startswith("Max Results:"):
                        max_results = int(line.split(":")[1].strip())
        except Exception as e:
            pass

    if origin_lat is None or origin_lon is None:
        result["details"].append({"item": "请求文件解析", "score": 0, "max_score": 10, "passed": False, "reason": "无法从请求文件解析起点坐标"})
        result["total_score"] = 30  # 已得20+0+? 前面有20分
        _write_result(workspace, result)
        return
    result["details"].append({"item": "请求文件解析成功", "score": 10, "max_score": 10, "passed": True, "reason": f"起点({origin_lat},{origin_lon}) 最小功率{min_power}kW 最多{max_results}个"})

    # 4. 读取 POI 数据
    pois_path = os.path.join(workspace, "data", "pois", "beijing_chargers.json")
    if not os.path.exists(pois_path):
        result["details"].append({"item": "POI 数据文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "beijing_chargers.json 不存在"})
        result["total_score"] = 40
        _write_result(workspace, result)
        return

    try:
        with open(pois_path, "r") as f:
            pois = json.load(f)
    except Exception as e:
        result["details"].append({"item": "POI 数据解析", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        result["total_score"] = 40
        _write_result(workspace, result)
        return
    result["details"].append({"item": "POI 数据解析成功", "score": 10, "max_score": 10, "passed": True, "reason": ""})

    # 5. 筛选、排序、取前 N 个
    valid = []
    for p in pois:
        if p.get("category") == "charging" and p.get("charge_rate_kw", 0) >= min_power:
            lat = p.get("lat")
            lon = p.get("lon")
            if lat is None or lon is None:
                continue
            dist = haversine(origin_lat, origin_lon, lat, lon)
            valid.append((dist, p["poi_id"]))
    valid.sort(key=lambda x: (x[0], x[1]))
    expected_ids = [pid for _, pid in valid[:max_results]]

    # 6. 内容比对
    matched = agent_output == expected_ids
    if matched:
        score = 60
        reason = f"精确匹配，输出 {expected_ids}"
    else:
        # 部分匹配：按共同元素比例给分
        if len(agent_output) <= len(expected_ids):
            common = len(set(agent_output) & set(expected_ids))
            score = int(60 * common / max(len(expected_ids), 1))
        else:
            common = sum(1 for pid in agent_output if pid in expected_ids)
            score = int(60 * common / max(len(agent_output), 1))
        reason = f"预期 {expected_ids}，实际 {agent_output}"

    result["details"].append({
        "item": "内容正确性",
        "score": score,
        "max_score": 60,
        "passed": matched,
        "reason": reason
    })

    total = 10 + 10 + 10 + 10 + score
    result["total_score"] = min(total, 100)
    _write_result(workspace, result)

def _write_result(workspace, result):
    path = os.path.join(workspace, "workplace_score.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
