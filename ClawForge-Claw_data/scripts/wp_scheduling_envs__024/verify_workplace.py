import sys
import os
import json
import csv
from pathlib import Path

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    full = os.path.join(WORKSPACE, rel_path)
    if not os.path.exists(full):
        return None
    with open(full, "r") as f:
        return json.load(f)

def parse_time(t_str):
    parts = t_str.strip().split(":")
    return int(parts[0]) * 60 + int(parts[1])

def main():
    details = []
    total = 0

    # 1. 检查 ops/ac_fix.json 是否存在并合法 (10分)
    result_path = os.path.join(WORKSPACE, "ops/ac_fix.json")
    if not os.path.exists(result_path):
        details.append({"item": "ops/ac_fix.json 存在性", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续均无法检查，直接输出
        _write_score(0, details)
        return
    try:
        with open(result_path, "r") as f:
            result = json.load(f)
        details.append({"item": "ops/ac_fix.json 合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "解析成功"})
    except Exception as e:
        details.append({"item": "ops/ac_fix.json 合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        _write_score(10, details)
        return

    # 2. 必需字段检查 (10分)
    required_fields = ["device_id", "schedule"]
    if not all(f in result for f in required_fields):
        missing = [f for f in required_fields if f not in result]
        details.append({"item": "必需字段存在", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段 {missing}"})
        total += 0
    else:
        details.append({"item": "必需字段存在", "score": 10, "max_score": 10, "passed": True, "reason": "包含 device_id 和 schedule"})
        total += 10

    # 3. schedule 子字段检查 (10分)
    sch = result.get("schedule", {})
    sub_fields = ["start_time", "end_time", "temperature"]
    if not all(f in sch for f in sub_fields):
        missing = [f for f in sub_fields if f not in sch]
        details.append({"item": "schedule 子字段", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少 {missing}"})
        total += 0
    else:
        details.append({"item": "schedule 子字段", "score": 10, "max_score": 10, "passed": True, "reason": "包含 start_time, end_time, temperature"})
        total += 10

    # 4. device_id 正确 (10分)
    devices = load_json("devices.json")
    if devices is None:
        details.append({"item": "设备ID正确性", "score": 0, "max_score": 10, "passed": False, "reason": "devices.json 不可读"})
        total += 0
    else:
        bedroom_ids = [d["device_id"] for d in devices["devices"] if d["location"] == "bedroom"]
        if result["device_id"] in bedroom_ids:
            details.append({"item": "设备ID正确性", "score": 10, "max_score": 10, "passed": True, "reason": f"设备ID {result['device_id']} 属于卧室"})
            total += 10
        else:
            details.append({"item": "设备ID正确性", "score": 0, "max_score": 10, "passed": False, "reason": f"设备ID {result['device_id']} 不在卧室设备中"})
            total += 0

    # 5. 温度值符合用户偏好 (20分)
    prefs = load_json("user_preferences.json")
    if prefs is None or "bedroom" not in prefs:
        details.append({"item": "温度值准确性", "score": 0, "max_score": 20, "passed": False, "reason": "user_preferences.json 缺少卧室配置"})
        total += 0
    else:
        target_max = prefs["bedroom"]["target_temp_max"]
        temp_val = sch.get("temperature")
        if temp_val is None or not (22 <= temp_val <= target_max):
            details.append({"item": "温度值准确性", "score": 0, "max_score": 20, "passed": False, "reason": f"温度 {temp_val} 不在 [22, {target_max}] 范围内"})
            total += 0
        else:
            details.append({"item": "温度值准确性", "score": 20, "max_score": 20, "passed": True, "reason": f"温度 {temp_val} 符合偏好上限 {target_max}"})
            total += 20

    # 6. 时间段正确性 (40分) 从传感器数据计算应该覆盖的区间
    sensor_path = os.path.join(WORKSPACE, "sensor_data.csv")
    if not os.path.exists(sensor_path):
        details.append({"item": "时间段正确性", "score": 0, "max_score": 40, "passed": False, "reason": "sensor_data.csv 不存在"})
        total += 0
    else:
        try:
            with open(sensor_path, "r") as f:
                reader = csv.DictReader(f)
                rows = [r for r in reader if r["room"] == "bedroom"]
            # 找温度超过 24 的时间点（严格大于）
            over_times = []
            for r in rows:
                temp = float(r["temperature"])
                if temp > 24.0:
                    over_times.append(r["timestamp"])
            if not over_times:
                details.append({"item": "时间段正确性", "score": 0, "max_score": 40, "passed": False, "reason": "没有超温时刻"})
                total += 0
            else:
                # 期望区间：最早超温到最晚超温（连续区间，假设数据连续覆盖）
                expected_start = min(over_times)
                expected_end = max(over_times)
                # 检查 agent 给出的区间是否覆盖该区间（允许等值或更大，但不能更小）
                start_ok = parse_time(sch["start_time"]) <= parse_time(expected_start)
                end_ok = parse_time(sch["end_time"]) >= parse_time(expected_end)
                if start_ok and end_ok:
                    # 但不能过于扩大（比如超过2小时外）。允许最多1小时的余量，防止胡乱填
                    allowed_start = max(0, parse_time(expected_start) - 60)
                    allowed_end = min(24*60, parse_time(expected_end) + 60)
                    if (parse_time(sch["start_time"]) >= allowed_start) and (parse_time(sch["end_time"]) <= allowed_end):
                        details.append({"item": "时间段正确性", "score": 40, "max_score": 40, "passed": True,
                                        "reason": f"覆盖超温区间 {expected_start}-{expected_end}，agent输出 {sch['start_time']}-{sch['end_time']}"})
                        total += 40
                    else:
                        details.append({"item": "时间段正确性", "score": 10, "max_score": 40, "passed": False,
                                        "reason": f"区间范围过大，超出允许的1小时余量"})
                        total += 10
                else:
                    details.append({"item": "时间段正确性", "score": 0, "max_score": 40, "passed": False,
                                    "reason": f"未覆盖全部超温区间，期望 {expected_start}-{expected_end}，实际 {sch['start_time']}-{sch['end_time']}"})
                    total += 0
        except Exception as e:
            details.append({"item": "时间段正确性", "score": 0, "max_score": 40, "passed": False, "reason": f"解析传感器数据错误: {e}"})
            total += 0

    # 额外：检查是否有多余的无关字段（不扣分，但记录）
    _write_score(total, details)

def _write_score(total, details):
    result = {"total_score": total, "details": details}
    out_path = os.path.join(WORKSPACE, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    # 也打印到stdout方便调试
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
