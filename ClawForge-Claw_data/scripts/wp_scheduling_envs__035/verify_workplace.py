import sys
import json
import os
from collections import defaultdict

def verify(workspace):
    score_details = []
    total = 0

    # 1. 检查目录结构 (10分)
    dirs_ok = True
    for d in ["data", "logs", "ops"]:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_ok = False
    if dirs_ok:
        score_details.append({"item": "目录结构完整", "score": 10, "max_score": 10, "passed": True, "reason": "data, logs, ops 目录均存在"})
        total += 10
    else:
        score_details.append({"item": "目录结构完整", "score": 0, "max_score": 10, "passed": False, "reason": "缺少必需目录"})

    # 2. 检查 ops/conflicts.json 是否存在且合法JSON (10分)
    conflicts_path = os.path.join(workspace, "ops", "conflicts.json")
    if not os.path.isfile(conflicts_path):
        score_details.append({"item": "报告文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "ops/conflicts.json 未找到"})
        total += 0
        # 无法继续，但保持结构
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return
    try:
        with open(conflicts_path) as f:
            conflicts = json.load(f)
        if not isinstance(conflicts, list):
            raise ValueError("不是列表")
        score_details.append({"item": "报告文件合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "ops/conflicts.json 是合法JSON列表"})
        total += 10
    except Exception as e:
        score_details.append({"item": "报告文件合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    # 3. 计算期望的冲突（从env_builder的逻辑推导） (50分)
    # 从工作区读取devices和schedules，模拟agent应当做的过滤
    devices_path = os.path.join(workspace, "data", "devices.json")
    schedules_path = os.path.join(workspace, "data", "schedules.json")
    if not os.path.isfile(devices_path) or not os.path.isfile(schedules_path):
        score_details.append({"item": "冲突计算准确", "score": 0, "max_score": 50, "passed": False, "reason": "缺少依赖文件"})
        total += 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": score_details}, f)
        return

    with open(devices_path) as f:
        devices_data = json.load(f)
    valid_device_ids = {d["device_id"] for d in devices_data["devices"]}

    with open(schedules_path) as f:
        schedules_data = json.load(f)
    # 过滤条件: valid=True, 日期在2025年（简单检查年份），设备ID有效
    valid_schedules = []
    for s in schedules_data["schedules"]:
        if not s.get("valid", False):
            continue
        if not s["datetime"].startswith("2025"):
            continue
        if s["device_id"] not in valid_device_ids:
            continue
        valid_schedules.append(s)

    # 分组：按 (datetime, room)
    groups = defaultdict(list)
    for s in valid_schedules:
        key = (s["datetime"], s["room"])
        groups[key].append(s["device_id"])

    expected_conflicts = []
    for (dt, room), dev_ids in groups.items():
        if len(dev_ids) >= 2:
            expected_conflicts.append({
                "timestamp": dt,
                "room": room,
                "device_ids": sorted(dev_ids)  # 排序便于比较
            })
    # 按 timestampt, room 排序
    expected_conflicts.sort(key=lambda x: (x["timestamp"], x["room"]))

    # 比较实际冲突
    # 先整理实际冲突：要求每个冲突有 timestamp, room, device_ids
    # 允许字段名略有不同，但必须包含这三个信息
    actual_normalized = []
    for c in conflicts:
        # 尝试找 timestamp/time/datetime/日期字段；room；device_ids/devices/ids
        ts = c.get("timestamp") or c.get("time") or c.get("datetime")
        room = c.get("room") or c.get("location")
        devs = c.get("device_ids") or c.get("devices") or c.get("ids")
        if ts and room and devs:
            actual_normalized.append({
                "timestamp": ts,
                "room": room,
                "device_ids": sorted(devs)
            })
    actual_normalized.sort(key=lambda x: (x["timestamp"], x["room"]))

    if actual_normalized == expected_conflicts:
        score_details.append({"item": "冲突计算准确", "score": 50, "max_score": 50, "passed": True, "reason": "冲突列表与预期完全一致"})
        total += 50
    else:
        # 部分得分：计算匹配比例
        # 用集合比较
        exp_set = { (e["timestamp"], e["room"], tuple(e["device_ids"])) for e in expected_conflicts }
        act_set = { (a["timestamp"], a["room"], tuple(a["device_ids"])) for a in actual_normalized }
        common = exp_set & act_set
        if len(expected_conflicts) == 0:
            match_ratio = 0
        else:
            match_ratio = len(common) / len(expected_conflicts)
        # 同时罚分如果有多余的
        extra = len(act_set) - len(common)
        missing = len(expected_conflicts) - len(common)
        score = max(0, int(50 * match_ratio - 5 * extra - 5 * missing))
        score_details.append({"item": "冲突计算准确", "score": score, "max_score": 50, "passed": score >= 40,
                              "reason": f"预期 {len(expected_conflicts)} 个冲突，匹配 {len(common)} 个，多余 {extra} 个，缺少 {missing} 个"})
        total += score

    # 4. 检查报告格式（每个条目必须有三个关键字段） (15分)
    format_ok = True
    for i, c in enumerate(conflicts):
        if not any(k in c for k in ["timestamp","time","datetime"]):
            format_ok = False
        if not any(k in c for k in ["room","location"]):
            format_ok = False
        if not any(k in c for k in ["device_ids","devices","ids"]):
            format_ok = False
    if format_ok and len(conflicts) > 0:
        score_details.append({"item": "报告格式正确", "score": 15, "max_score": 15, "passed": True, "reason": "每条记录包含时间、房间、设备ID列表"})
        total += 15
    elif len(conflicts) == 0:
        # 如果冲突为空，格式不扣分（但之前计算可能扣了）
        score_details.append({"item": "报告格式正确", "score": 15, "max_score": 15, "passed": True, "reason": "无冲突，格式不适用"})
        total += 15
    else:
        score_details.append({"item": "报告格式正确", "score": 0, "max_score": 15, "passed": False, "reason": "部分记录缺少必需字段"})

    # 5. 检查是否包含任何干扰项（过期、无效设备等） (15分)
    # 干扰项不应出现在冲突中：
    invalid_timestamps = ["2024-12-01 02:00", "2025-03-15 04:00", "2025-03-15 05:00"]
    invalid_devices = ["d999"]
    has_interference = False
    for c in conflicts:
        ts = c.get("timestamp") or c.get("time") or c.get("datetime")
        if ts in invalid_timestamps:
            has_interference = True
        devs = c.get("device_ids") or c.get("devices") or c.get("ids")
        if devs and any(d in invalid_devices for d in devs):
            has_interference = True
    if not has_interference:
        score_details.append({"item": "排除干扰项", "score": 15, "max_score": 15, "passed": True, "reason": "未包含过期或无效设备"})
        total += 15
    else:
        score_details.append({"item": "排除干扰项", "score": 0, "max_score": 15, "passed": False, "reason": "报告中包含了不应有的干扰条目"})

    # 总分不能超过100
    total = min(total, 100)
    # 写入结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
