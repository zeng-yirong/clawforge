import sys
import os
import json
from datetime import datetime

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."
TODAY = "2025-03-15"
WINDOW_START = f"{TODAY}T15:00:00"
WINDOW_END = f"{TODAY}T17:00:00"


def parse_iso(tstr: str) -> datetime:
    return datetime.fromisoformat(tstr)


def calculate_expected_conflicts(devices_file: str, schedules_file: str) -> set:
    """从环境数据中计算预期的冲突调度ID集合"""
    with open(devices_file) as f:
        devices_data = json.load(f)
    with open(schedules_file) as f:
        schedules_data = json.load(f)

    device_ids = set(devices_data.get("devices", {}).keys())
    schedules = schedules_data.get("schedules", [])

    # 过滤：时间窗口内 + 设备存在
    valid = []
    for s in schedules:
        try:
            dt = parse_iso(s["time"])
        except (ValueError, KeyError):
            continue
        if not (parse_iso(WINDOW_START) <= dt < parse_iso(WINDOW_END)):
            continue
        if s.get("device_id") not in device_ids:
            continue
        valid.append(s)

    # 按 (device_id, time) 分组，找出组内动作不同的所有调度
    from collections import defaultdict
    groups = defaultdict(list)
    for s in valid:
        key = (s["device_id"], s["time"])
        groups[key].append(s)

    conflict_ids = set()
    for (dev, t), group in groups.items():
        actions = set(s["action"] for s in group)
        if len(actions) > 1:
            # 有冲突
            for s in group:
                conflict_ids.add(s["schedule_id"])

    return conflict_ids


def verify():
    ops_dir = os.path.join(WORKSPACE, "ops")
    score_items = []
    total_score = 0

    # 1. 检查 ops 目录是否存在（5分）
    if os.path.isdir(ops_dir):
        score_items.append({
            "item": "Directory ops/ exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Found ops/ directory"
        })
        total_score += 5
    else:
        score_items.append({
            "item": "Directory ops/ exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Missing ops/ directory"
        })
        # 如果目录不存在，后续文件检查直接失败
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_items}, f, indent=2)
        return

    # 2. 检查冲突结果文件是否存在（5分基础）
    result_path = os.path.join(ops_dir, "conflict_schedules.json")
    if not os.path.isfile(result_path):
        score_items.append({
            "item": "conflict_schedules.json exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "File not found"
        })
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_items}, f, indent=2)
        return
    else:
        score_items.append({
            "item": "conflict_schedules.json exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "File found"
        })
        total_score += 5

    # 3. 解析合法性（10分）
    try:
        with open(result_path) as f:
            result_data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        score_items.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_items}, f, indent=2)
        return
    score_items.append({
        "item": "JSON is valid",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Valid JSON"
    })
    total_score += 10

    # 4. 期望答案（通过环境数据计算）
    devices_path = os.path.join(WORKSPACE, "data/devices/devices.json")
    schedules_path = os.path.join(WORKSPACE, "data/schedules.json")
    try:
        expected = calculate_expected_conflicts(devices_path, schedules_path)
    except Exception as e:
        score_items.append({
            "item": "Calculate expected conflicts",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Error reading env data: {e}"
        })
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_items}, f, indent=2)
        return
    score_items.append({
        "item": "Calculate expected conflicts",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": f"Expected conflicts: {expected}"
    })
    total_score += 10

    # 5. 检查结果列表内容（70分）
    # 确保结果是一个列表
    if not isinstance(result_data, list):
        # 如果是一个 dict 包含列表也行？我们要求必须是 list
        # 为了容错，检查是否包含 'conflicts' 键？但 prompt 要求直接列表，所以严格
        score_items.append({
            "item": "Result format (list of IDs)",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": f"Expected a list, got {type(result_data).__name__}"
        })
    else:
        result_set = set(result_data)
        # 检查是否正好相等
        if result_set == expected:
            score_items.append({
                "item": "Conflict IDs match exactly",
                "score": 70,
                "max_score": 70,
                "passed": True,
                "reason": f"Found {sorted(expected)}"
            })
            total_score += 70
        else:
            # 部分正确：每个多余或缺失扣 10 分，直到 0
            missing = expected - result_set
            extra = result_set - expected
            penalty = (len(missing) + len(extra)) * 10
            base = 70 - penalty
            if base < 0:
                base = 0
            score_items.append({
                "item": "Conflict IDs match exactly",
                "score": base,
                "max_score": 70,
                "passed": False,
                "reason": f"Missing: {missing}, Extra: {extra}"
            })
            total_score += base

    # 写入评分文件
    with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_items}, f, indent=2)


if __name__ == "__main__":
    verify()
