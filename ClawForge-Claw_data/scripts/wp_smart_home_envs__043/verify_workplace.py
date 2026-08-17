import sys
import os
import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # ========== 目录与文件存在性 (15分) ==========
    # 检查 ops 目录
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops 目录存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops 目录已创建"
        })
        total_score += 5
    else:
        details.append({
            "item": "ops 目录存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "未找到 ops 目录"
        })

    plan_path = os.path.join(ops_dir, "climate_plan.json")
    if os.path.isfile(plan_path):
        details.append({
            "item": "climate_plan.json 文件存在",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "计划文件已生成"
        })
        total_score += 5
    else:
        details.append({
            "item": "climate_plan.json 文件存在",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "未找到 climate_plan.json"
        })
        # 后续检查无法进行，直接写入结果返回
        write_score(details, total_score)
        return

    # ========== JSON 合法性 (10分) ==========
    try:
        plan = load_json(plan_path)
        details.append({
            "item": "JSON 语法正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件可正常解析为 JSON"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON 语法正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        write_score(details, total_score)
        return

    # ========== 计划结构检查 (15分) ==========
    # 必须包含三个时段标签：Peak, Mid-Peak, Off-Peak
    required_periods = ["Peak", "Mid-Peak", "Off-Peak"]
    plan_periods = list(plan.keys())
    missing_periods = [p for p in required_periods if p not in plan_periods]
    if not missing_periods:
        details.append({
            "item": "计划包含所有三个电价时段 (Peak, Mid-Peak, Off-Peak)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"包含时段: {plan_periods}"
        })
        total_score += 10
    else:
        details.append({
            "item": "计划包含所有三个电价时段 (Peak, Mid-Peak, Off-Peak)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"缺少时段: {missing_periods}"
        })

    # 检查每个时段是否为列表
    all_list = all(isinstance(plan[p], list) for p in required_periods if p in plan)
    if all_list:
        details.append({
            "item": "每个时段的值都是列表",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "结构正确"
        })
        total_score += 5
    else:
        details.append({
            "item": "每个时段的值都是列表",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "部分时段的值不是列表"
        })

    # ========== 加载参考数据 ==========
    try:
        devices_data = load_json(os.path.join(workspace, "data/devices/devices.json"))
        devices = devices_data["devices"]
        health_data = load_json(os.path.join(workspace, "data/health/health.json"))
        users = health_data["users"]
    except Exception as e:
        details.append({
            "item": "加载参考数据",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": f"无法加载 data/ 下的文件: {e}"
        })
        write_score(details, total_score)
        return

    # 找出所有空调和加湿器
    climate_devices = [d for d in devices if d["type"] in ("air_conditioner", "humidifier")]
    # 找出所有智能插头
    smart_plugs = [d for d in devices if d["type"] == "smart_plug"]

    # 找出有呼吸道问题的用户 (Jane)
    jane = [u for u in users if u.get("respiratory_issues") and u["name"] == "Jane Smith"]
    if not jane:
        details.append({
            "item": "健康数据异常",
            "score": 0,
            "max_score": 0,
            "passed": False,
            "reason": "未找到 Jane Smith 的健康数据"
        })
        write_score(details, total_score)
        return
    jane = jane[0]
    target_temp = (jane["temperature_preference"]["min"] + jane["temperature_preference"]["max"]) // 2  # 23
    target_humidity = (jane["humidity_preference"]["min"] + jane["humidity_preference"]["max"]) // 2  # 50

    # ========== 设备数量与时段完整性 (10分) ==========
    total_devices = len(devices)
    for period in required_periods:
        if period not in plan:
            continue
        period_list = plan[period]
        if len(period_list) != total_devices:
            details.append({
                "item": f"{period} 时段设备数量正确",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"期望 {total_devices} 个设备, 实际 {len(period_list)}"
            })
            total_score += 0
        else:
            details.append({
                "item": f"{period} 时段设备数量正确",
                "score": 10 // 3,  # 约3.33分, 总分10
                "max_score": 10 // 3,
                "passed": True,
                "reason": f"包含 {total_devices} 个设备"
            })
            total_score += 10 // 3

    # ========== 核心逻辑检查 (45分) ==========
    # 对于高峰时段 Peak:
    # - Bedroom AC (DEV-AC-BR-002) 必须 on, target_temp = 23
    # - Bedroom Humidifier (DEV-HU-BR-004) 必须 on, target_humidity = 50
    # - Living Room AC (DEV-AC-LR-001) 必须 off (或 action 为 off)
    # - Living Room Humidifier (DEV-HU-LR-003) 必须 off
    # - 所有智能插头必须 on (action = on)
    # 对于非高峰时段 (Mid-Peak, Off-Peak):
    # - 所有空调和加湿器必须 on, target 同上
    # - 所有智能插头必须 on

    peak_items = plan.get("Peak", [])
    mid_peak_items = plan.get("Mid-Peak", [])
    off_peak_items = plan.get("Off-Peak", [])

    # 辅助函数：根据 device_id 在列表中查找条目
    def find_entry(entry_list, device_id):
        for e in entry_list:
            if e.get("device_id") == device_id:
                return e
        return None

    def check_climate_device(entry, expected_action, expected_target, device_name, period_label):
        # entry: dict with keys device_id, action, target (optional)
        if not entry:
            return (False, f"{period_label} 缺少 {device_name} 条目")
        if entry.get("action") != expected_action:
            return (False, f"{period_label} {device_name} action 应为 {expected_action}, 实际 {entry.get('action')}")
        if expected_action == "on":
            target_key = "target_temp" if "AC" in device_name else "target_humidity"
            actual_target = entry.get(target_key)
            if actual_target is None:
                # 尝试 target 字段
                if "target" in entry:
                    actual_target = entry["target"]
            if actual_target != expected_target:
                return (False, f"{period_label} {device_name} {target_key} 应为 {expected_target}, 实际 {actual_target}")
        return (True, "")

    # 高峰时段检查
    peak_score = 0
    peak_max = 20
    checks = [
        ("DEV-AC-LR-001", "off", None, "Living Room AC"),
        ("DEV-AC-BR-002", "on", target_temp, "Bedroom AC"),
        ("DEV-HU-LR-003", "off", None, "Living Room Humidifier"),
        ("DEV-HU-BR-004", "on", target_humidity, "Bedroom Humidifier"),
    ]
    for dev_id, exp_action, exp_target, dev_name in checks:
        entry = find_entry(peak_items, dev_id)
        ok, reason = check_climate_device(entry, exp_action, exp_target, dev_name, "Peak")
        if ok:
            peak_score += 5
        else:
            details.append({
                "item": f"Peak 时段 {dev_name} 状态正确",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": reason
            })
    # 智能插头在 peak 必须 on
    for plug in smart_plugs:
        entry = find_entry(peak_items, plug["device_id"])
        if entry and entry.get("action") == "on":
            peak_score += 1  # 每个插头1分，共3分
        else:
            details.append({
                "item": f"Peak 时段 {plug['name']} 应为 on",
                "score": 0,
                "max_score": 1,
                "passed": False,
                "reason": "状态错误或缺失"
            })
    if peak_score > peak_max:
        peak_score = peak_max
    details.append({
        "item": "Peak 时段核心设备调度正确",
        "score": peak_score,
        "max_score": peak_max,
        "passed": peak_score == peak_max,
        "reason": f"得分 {peak_score}/{peak_max}"
    })
    total_score += peak_score

    # 非高峰时段检查 (Mid-Peak, Off-Peak)
    non_peak_score = 0
    non_peak_max = 15
    for period_label, period_items in [("Mid-Peak", mid_peak_items), ("Off-Peak", off_peak_items)]:
        if not period_items:
            continue
        period_ok = True
        # 检查所有气候设备必须 on，target 正确
        for dev in climate_devices:
            entry = find_entry(period_items, dev["device_id"])
            if entry is None:
                period_ok = False
                break
            if entry.get("action") != "on":
                period_ok = False
                break
            if dev["type"] == "air_conditioner":
                target_val = entry.get("target_temp") or entry.get("target")
                if target_val != target_temp:
                    period_ok = False
                    break
            elif dev["type"] == "humidifier":
                target_val = entry.get("target_humidity") or entry.get("target")
                if target_val != target_humidity:
                    period_ok = False
                    break
        # 检查智能插头 on
        for plug in smart_plugs:
            entry = find_entry(period_items, plug["device_id"])
            if entry is None or entry.get("action") != "on":
                period_ok = False
                break
        if period_ok:
            non_peak_score += 7.5
        else:
            details.append({
                "item": f"{period_label} 时段设备状态正确",
                "score": 0,
                "max_score": 7.5,
                "passed": False,
                "reason": "部分设备状态或目标不符合预期"
            })
    if non_peak_score > non_peak_max:
        non_peak_score = non_peak_max
    details.append({
        "item": "非高峰时段 (Mid-Peak, Off-Peak) 设备调度正确",
        "score": int(non_peak_score),
        "max_score": non_peak_max,
        "passed": non_peak_score == non_peak_max,
        "reason": f"得分 {non_peak_score}/{non_peak_max}"
    })
    total_score += int(non_peak_score)

    # ========== 额外字段检查 (5分) ==========
    # 检查每个条目是否包含 device_id, action
    extra_ok = True
    for period in required_periods:
        for entry in plan.get(period, []):
            if not isinstance(entry, dict):
                extra_ok = False
                break
            if "device_id" not in entry or "action" not in entry:
                extra_ok = False
                break
    if extra_ok:
        details.append({
            "item": "所有条目包含 device_id 和 action 字段",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "基础字段完整"
        })
        total_score += 5
    else:
        details.append({
            "item": "所有条目包含 device_id 和 action 字段",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "存在缺失字段的条目"
        })

    # 总分为整数
    total_score = min(total_score, 100)
    write_score(details, total_score)

def write_score(details, total_score):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workplace_score.json"), "w") as f:
        json.dump(score_data, f, indent=2)
    # 也输出到当前工作目录以便调试
    with open("workplace_score.json", "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    main()
