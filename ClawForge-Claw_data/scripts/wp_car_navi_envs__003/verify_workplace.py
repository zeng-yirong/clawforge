import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    output_path = os.path.join(workspace, "output", "updated_sessions.json")
    
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查输出文件是否存在 (10分)
    item = {"item": "输出文件存在", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if os.path.isfile(output_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "output/updated_sessions.json 存在"
    else:
        item["reason"] = f"文件不存在: {output_path}"
        details.append(item)
        # 后续检查无法进行
        write_score(total_score, details)
        return
    details.append(item)
    total_score += 10

    # 2. JSON格式合法 (10分)
    item = {"item": "JSON格式合法", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            item["score"] = 10
            item["passed"] = True
            item["reason"] = "是有效的JSON对象"
        else:
            item["reason"] = f"JSON顶层应为字典，实际为 {type(data).__name__}"
    except Exception as e:
        item["reason"] = f"JSON解析失败: {e}"
    details.append(item)
    total_score += item["score"]
    if not item["passed"]:
        write_score(total_score, details)
        return

    # 期望结果：只包含 session_001 和 session_002，且waypoints正确
    expected_waypoints = {
        "session_001": ["poi_charge_01"],
        "session_002": ["poi_charge_03"]
    }

    # 3. 检查包含的会话ID集合 (10分)
    item = {"item": "会话ID集合正确", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    actual_keys = set(data.keys())
    expected_keys = set(expected_waypoints.keys())
    if actual_keys == expected_keys:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = f"仅包含期望的会话: {expected_keys}"
    else:
        missing = expected_keys - actual_keys
        extra = actual_keys - expected_keys
        parts = []
        if missing:
            parts.append(f"缺失: {missing}")
        if extra:
            parts.append(f"多余: {extra}")
        item["reason"] = "；".join(parts) if parts else "集合不匹配"
    details.append(item)
    total_score += item["score"]

    # 4. 逐会话检查waypoints (40分 = session_001 20分 + session_002 20分)
    for sess_id, expected_wp in expected_waypoints.items():
        item = {"item": f"会话 {sess_id} waypoints 正确", "max_score": 20, "score": 0, "passed": False, "reason": ""}
        if sess_id not in data:
            item["reason"] = f"会话 {sess_id} 缺失"
        else:
            sess = data[sess_id]
            actual_wp = sess.get("waypoints", [])
            if isinstance(actual_wp, list) and actual_wp == expected_wp:
                item["score"] = 20
                item["passed"] = True
                item["reason"] = f"waypoints={actual_wp}"
            else:
                item["reason"] = f"期望 waypoints={expected_wp}，实际得到 {actual_wp}"
        details.append(item)
        total_score += item["score"]

    # 5. 确保没有包含未受影响的会话 (10分) —— 实际已通过第3项检查，但作为冗余
    item = {"item": "未包含不应出现的会话", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    forbidden = {"session_003", "session_004", "session_005"}
    extra_sessions = actual_keys - expected_keys
    if not extra_sessions:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "没有额外会话"
    else:
        item["reason"] = f"包含了不应出现的会话: {extra_sessions}"
    details.append(item)
    total_score += item["score"]

    # 6. waypoints中的POI ID均为字符串且属于charging类别 (10分)
    item = {"item": "waypoints元素均为字符串且存在于POI列表中", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    # 读取POI列表验证（可选），但简化：检查waypoints中的ID是否都是以"poi_charge_"开头
    all_wp_ok = True
    for sess_id, sess in data.items():
        for wp_id in sess.get("waypoints", []):
            if not isinstance(wp_id, str) or not wp_id.startswith("poi_charge_"):
                all_wp_ok = False
                break
    if all_wp_ok:
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "所有waypoint ID符合充电站命名规范"
    else:
        item["reason"] = "存在不符合充电站命名的waypoint"
    details.append(item)
    total_score += item["score"]

    # 写入最终得分
    write_score(total_score, details, max_total)

def write_score(score, details, max_total=100):
    result = {
        "total_score": min(score, max_total),
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
