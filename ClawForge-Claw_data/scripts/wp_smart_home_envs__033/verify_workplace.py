import os
import sys
import json
from datetime import datetime

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # ---------- 1. 目录结构检查 (10分) ----------
    required_dirs = [
        "data/devices",
        "data/electricity",
        "data/health",
        "data/weather",
        "ops"
    ]
    dirs_ok = True
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dirs_ok = False
            details.append({
                "item": f"目录 {d} 存在",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"缺少目录 {d}"
            })
            break
    if dirs_ok:
        details.append({
            "item": "必要目录结构完整",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有必需目录均存在"
        })
        total_score += 10
    else:
        total_score += 0

    # ---------- 2. 必要数据文件可读 & 格式合法 (10分) ----------
    data_files = {
        "data/devices/devices.json": "devices",
        "data/electricity/rates.json": "rates",
        "data/health/health.json": "users",
        "data/weather/weather.json": "weather_data"
    }
    all_data = {}
    format_ok = True
    for fpath, key in data_files.items():
        full = os.path.join(workspace, fpath)
        if not os.path.isfile(full):
            format_ok = False
            details.append({
                "item": f"文件 {fpath} 存在",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"缺少 {fpath}"
            })
            break
        try:
            obj = load_json(full)
            if key not in obj or not isinstance(obj[key], list):
                format_ok = False
                details.append({
                    "item": f"文件 {fpath} 包含合法 {key} 列表",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"{fpath} 中未找到数组字段 '{key}'"
                })
                break
            all_data[key] = obj[key]
        except Exception as e:
            format_ok = False
            details.append({
                "item": f"文件 {fpath} 可解析",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"JSON 解析失败: {str(e)}"
            })
            break
    if format_ok:
        details.append({
            "item": "所有数据文件合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "4 个数据文件均存在且 JSON 格式正确"
        })
        total_score += 10
    else:
        total_score += 0

    # 如果数据读取失败，直接返回
    if not format_ok:
        final_score = total_score
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": final_score, "details": details}, f, indent=2)
        print(f"Score written: {final_score}")
        sys.exit(0)

    # ---------- 3. 计算期望答案 ----------
    # 解析时间
    weather_list = all_data["weather_data"]
    # 取第一条（只有一个）
    ts_str = weather_list[0]["timestamp"]  # "2025-06-12T15:00:00"
    current_hour = datetime.fromisoformat(ts_str).hour  # 15

    # 找到当前时段
    rates = all_data["rates"]
    current_period = None
    for r in rates:
        if r["start_hour"] <= current_hour < r["end_hour"]:
            current_period = r["period"]
            break
    if current_period is None:
        current_period = "off_peak"  # fallback

    # 设备列表
    devices = all_data["devices"]
    # 用户列表
    users = all_data["users"]
    # 房间 -> 用户映射
    room_to_user = {u["room"]: u for u in users}

    expected_adjustments = []
    for dev in devices:
        # 只处理空调和加湿器，且状态为 on
        if dev["type"] not in ("air_conditioner", "humidifier"):
            continue
        if dev["status"] != "on":
            continue
        location = dev["location"]
        if location not in room_to_user:
            continue
        user = room_to_user[location]
        current = dev["current_settings"]
        recommended = {}
        need_adjust = False

        if dev["type"] == "air_conditioner":
            temp = current.get("temperature")
            pref = user["temperature_preference"]
            if temp is not None and (temp < pref["min"] or temp > pref["max"]):
                # 推荐中位值?
                recommended["temperature"] = (pref["min"] + pref["max"]) // 2
                need_adjust = True
            # 保留 mode
            if "mode" in current:
                recommended["mode"] = current["mode"]
        elif dev["type"] == "humidifier":
            hum = current.get("humidity")
            pref = user["humidity_preference"]
            if hum is not None and (hum < pref["min"] or hum > pref["max"]):
                recommended["humidity"] = (pref["min"] + pref["max"]) // 2
                need_adjust = True

        if need_adjust:
            expected_adjustments.append({
                "device_id": dev["device_id"],
                "current_settings": current,
                "recommended_settings": recommended
            })

    # ---------- 4. 检查 agent 输出 ops/override_settings.json (80分) ----------
    output_path = os.path.join(workspace, "ops/override_settings.json")
    if not os.path.isfile(output_path):
        details.append({
            "item": "产出文件 ops/override_settings.json",
            "score": 0,
            "max_score": 80,
            "passed": False,
            "reason": "文件不存在"
        })
        total_score += 0
    else:
        try:
            with open(output_path, 'r') as f:
                agent_output = json.load(f)
        except Exception as e:
            details.append({
                "item": "产出文件 JSON 合法",
                "score": 0,
                "max_score": 80,
                "passed": False,
                "reason": f"JSON 解析失败: {str(e)}"
            })
            total_score += 0
            final_score = total_score
            with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
                json.dump({"total_score": final_score, "details": details}, f, indent=2)
            print(f"Score written: {final_score}")
            sys.exit(0)

        # 必须是一个列表
        if not isinstance(agent_output, list):
            details.append({
                "item": "输出是列表格式",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"预期列表，实际 {type(agent_output)}"
            })
            total_score += 0
        else:
            details.append({
                "item": "输出是列表格式",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "输出为列表"
            })
            total_score += 10

            # 检查数量
            expected_ids = {adj["device_id"] for adj in expected_adjustments}
            actual_ids = {item.get("device_id") for item in agent_output if isinstance(item, dict)}
            # 数量正确性 (10分)
            if actual_ids == expected_ids:
                details.append({
                    "item": "设备ID集合正确",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": f"完全匹配期望设备: {sorted(expected_ids)}"
                })
                total_score += 10
            else:
                missing = expected_ids - actual_ids
                extra = actual_ids - expected_ids
                reason_parts = []
                if missing:
                    reason_parts.append(f"缺少设备: {sorted(missing)}")
                if extra:
                    reason_parts.append(f"多余设备: {sorted(extra)}")
                details.append({
                    "item": "设备ID集合正确",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "; ".join(reason_parts)
                })
                total_score += 0

            # 逐个设备检查字段 (每个20分，最多2个设备 => 40分)
            # 但为了细粒度，对每个期望设备检查
            max_device_score = 40  # 总分
            device_score = 0
            for exp in expected_adjustments:
                exp_id = exp["device_id"]
                actual_item = None
                for item in agent_output:
                    if isinstance(item, dict) and item.get("device_id") == exp_id:
                        actual_item = item
                        break
                if actual_item is None:
                    device_score -= 0  # 已经在上面扣了集合分，这里不再重复
                    continue
                # 检查必要字段
                fields_ok = True
                missing_fields = []
                for field in ["device_id", "current_settings", "recommended_settings"]:
                    if field not in actual_item:
                        missing_fields.append(field)
                        fields_ok = False
                if not fields_ok:
                    reason = f"设备 {exp_id} 缺少字段: {missing_fields}"
                    # 扣分该设备得分
                    # 不直接在这里加，最后统一扣
                else:
                    # 检查推荐设置数值
                    exp_rec = exp["recommended_settings"]
                    act_rec = actual_item["recommended_settings"]
                    if act_rec != exp_rec:
                        fields_ok = False
                        reason = f"设备 {exp_id} 推荐设置不符，期望 {exp_rec}，实际 {act_rec}"
                    else:
                        reason = f"设备 {exp_id} 字段完整且推荐值正确"
                if fields_ok:
                    device_score += 20  # 每个设备20分
            # 实际可能只有2个设备，所以满分40
            details.append({
                "item": "各个设备字段正确性",
                "score": min(device_score, 40),
                "max_score": 40,
                "passed": device_score == 40,
                "reason": f"通过 {device_score//20} 个设备检查"
            })
            total_score += min(device_score, 40)

            # 额外检查：确保没有非空调/加湿器设备出现 (10分)
            valid_types = ["air_conditioner", "humidifier"]
            # 需要知道设备类型，可以反向查找devices
            dev_map = {d["device_id"]: d for d in devices}
            illegal_devices = []
            for item in agent_output:
                did = item.get("device_id")
                if did and did in dev_map:
                    if dev_map[did]["type"] not in valid_types:
                        illegal_devices.append(did)
            if illegal_devices:
                details.append({
                    "item": "未包含非气候设备",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"包含了不允许的设备: {illegal_devices}"
                })
                total_score += 0
            else:
                details.append({
                    "item": "未包含非气候设备",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "所有设备类型正确"
                })
                total_score += 10

    # 计算最终总分（确保0-100）
    final_score = min(int(total_score), 100)

    result = {
        "total_score": final_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score written: {final_score}")

if __name__ == "__main__":
    main()
