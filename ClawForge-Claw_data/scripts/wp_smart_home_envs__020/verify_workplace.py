import json
import os
import re
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    total_score = 0
    details = []

    # ---------- 1. 检查 analysis 目录和 report.json 是否存在 (10 分) ----------
    report_path = "analysis/optimization_report.json"
    if os.path.isdir("analysis") and os.path.isfile(report_path):
        total_score += 10
        details.append({
            "item": "分析报告文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "analysis/optimization_report.json 存在"
        })
    else:
        details.append({
            "item": "分析报告文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "analysis 目录或 optimization_report.json 不存在"
        })
        # 如果文件不存在，后续无意义，直接输出结果
        write_score(total_score, details)
        return

    # ---------- 2. 检查 JSON 语法合法性 (10 分) ----------
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        total_score += 10
        details.append({
            "item": "JSON 语法合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
    except Exception as e:
        details.append({
            "item": "JSON 语法合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        write_score(total_score, details)
        return

    # ---------- 3. 检查顶层字段 health_conflicts 和 rate_conflicts 存在 (10 分) ----------
    expected_keys = {"health_conflicts", "rate_conflicts"}
    actual_keys = set(report.keys())
    if expected_keys.issubset(actual_keys):
        total_score += 10
        details.append({
            "item": "报告包含两个必要列表",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "health_conflicts 和 rate_conflicts 均存在"
        })
    else:
        missing = expected_keys - actual_keys
        total_score += 0
        details.append({
            "item": "报告包含两个必要列表",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"缺少字段: {missing}"
        })

    # ---------- 4. 加载原始数据，准备精确比对的依据 ----------
    with open("data/devices/devices.json") as f:
        devices_data = json.load(f)["devices"]
    device_map = {d["device_id"]: d for d in devices_data}
    with open("data/devices/status.json") as f:
        status_data = json.load(f)["device_statuses"]
    with open("data/health/health.json") as f:
        health_data = json.load(f)["users"]
    with open("data/weather/weather.json") as f:
        weather_data = json.load(f)["weather_data"][0]
    # 当前小时
    current_hour = int(weather_data["timestamp"][11:13])  # 10

    # 构建健康用户所在房间偏好
    health_prefs = {}
    for u in health_data:
        if u["respiratory_issues"]:
            health_prefs[u["room"]] = {
                "temp_min": u["temperature_preference"]["min"],
                "temp_max": u["temperature_preference"]["max"],
                "hum_min": u["humidity_preference"]["min"],
                "hum_max": u["humidity_preference"]["max"]
            }

    # 判断当前时段是否为高峰 (9-12 或 18-21)
    is_peak = (9 <= current_hour < 12) or (18 <= current_hour < 21)

    # 构建期望的健康冲突列表
    expected_health = []
    # 只处理有呼吸问题的用户所在房间
    for room, prefs in health_prefs.items():
        for dev in devices_data:
            if dev["location"] != room:
                continue
            dev_id = dev["device_id"]
            if dev_id not in status_data:
                continue
            st = status_data[dev_id]
            if dev["type"] == "air_conditioner" and st.get("on"):
                temp = st.get("temperature_setting")
                if temp is not None and (temp < prefs["temp_min"] or temp > prefs["temp_max"]):
                    expected_health.append({
                        "device_id": dev_id,
                        "issue": f"温度设置{temp}°C超出健康偏好{prefs['temp_min']}-{prefs['temp_max']}°C",
                        "suggestion": f"将温度调整至{(prefs['temp_min'] + prefs['temp_max']) // 2}°C"
                    })
            elif dev["type"] == "humidifier" and st.get("on"):
                hum = st.get("humidity_setting")
                if hum is not None and (hum < prefs["hum_min"] or hum > prefs["hum_max"]):
                    expected_health.append({
                        "device_id": dev_id,
                        "issue": f"湿度设置{hum}%低于健康偏好{prefs['hum_min']}-{prefs['hum_max']}%",
                        "suggestion": f"将湿度调整至{(prefs['hum_min'] + prefs['hum_max']) // 2}%"
                    })

    # 构建期望的电价冲突列表（排除有健康冲突的设备）
    health_device_ids = {h["device_id"] for h in expected_health}
    expected_rate = []
    for dev in devices_data:
        dev_id = dev["device_id"]
        if dev_id not in status_data:
            continue
        st = status_data[dev_id]
        if st.get("on") and dev_id not in health_device_ids and is_peak:
            expected_rate.append({
                "device_id": dev_id,
                "issue": f"该设备在高峰时段({current_hour}:00)运行",
                "suggestion": "建议关闭或将运行时间调整至非高峰时段"
            })

    # ---------- 5. 检查 health_conflicts (30 分) ----------
    actual_health = report.get("health_conflicts", [])
    # 5a. 设备数量正确 (10 分)
    if len(actual_health) == len(expected_health):
        total_score += 10
        details.append({
            "item": "健康冲突设备数量",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"数量正确: {len(expected_health)}"
        })
    else:
        total_score += 0
        details.append({
            "item": "健康冲突设备数量",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 {len(expected_health)} 个，实际 {len(actual_health)} 个"
        })

    # 5b. 每个设备必须包含 device_id, issue, suggestion 字段 (5 分)
    field_ok = True
    for item in actual_health:
        if not all(k in item for k in ("device_id", "issue", "suggestion")):
            field_ok = False
            break
    if field_ok and len(actual_health) > 0:
        total_score += 5
        details.append({
            "item": "健康冲突条目字段完整性",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "所有条目均包含 device_id, issue, suggestion"
        })
    else:
        total_score += 0
        details.append({
            "item": "健康冲突条目字段完整性",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "存在条目缺少必要字段"
        })

    # 5c. 设备ID 必须全部在设备清单中且 match 期望 (5 分)
    actual_health_ids = {item["device_id"] for item in actual_health}
    expected_health_ids = {e["device_id"] for e in expected_health}
    # 同时检查没有使用干扰文件中的设备
    all_legit_ids = set(device_map.keys())
    if actual_health_ids.issubset(all_legit_ids) and actual_health_ids == expected_health_ids:
        total_score += 5
        details.append({
            "item": "健康冲突设备ID合法性",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": f"设备ID集合正确: {expected_health_ids}"
        })
    else:
        total_score += 0
        details.append({
            "item": "健康冲突设备ID合法性",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"实际ID: {actual_health_ids}, 期望: {expected_health_ids}, 合法设备: {all_legit_ids}"
        })

    # 5d. 检查建议中的数字是否准确 (10 分)
    suggestion_ok = True
    for exp in expected_health:
        # 找到对应的实际条目
        act = next((x for x in actual_health if x["device_id"] == exp["device_id"]), None)
        if act is None:
            suggestion_ok = False
            break
        # 从 suggestion 中提取数字
        nums = re.findall(r'\d+', act["suggestion"])
        # 期望数字
        exp_nums = re.findall(r'\d+', exp["suggestion"])
        # 检查是否包含所有期望数字（比如23 或45）
        if not all(exp_n in nums for exp_n in exp_nums):
            suggestion_ok = False
            break
    if suggestion_ok:
        total_score += 10
        details.append({
            "item": "健康冲突建议数值",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有建议包含正确的调整数值"
        })
    else:
        total_score += 0
        details.append({
            "item": "健康冲突建议数值",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "存在建议数值不符合预期"
        })

    # ---------- 6. 检查 rate_conflicts (25 分) ----------
    actual_rate = report.get("rate_conflicts", [])
    # 6a. 数量 (10 分)
    if len(actual_rate) == len(expected_rate):
        total_score += 10
        details.append({
            "item": "电价冲突设备数量",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"数量正确: {len(expected_rate)}"
        })
    else:
        total_score += 0
        details.append({
            "item": "电价冲突设备数量",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 {len(expected_rate)} 个，实际 {len(actual_rate)} 个"
        })

    # 6b. 字段完整性 (5 分)
    field_ok2 = True
    for item in actual_rate:
        if not all(k in item for k in ("device_id", "issue", "suggestion")):
            field_ok2 = False
            break
    if field_ok2 and len(actual_rate) > 0:
        total_score += 5
        details.append({
            "item": "电价冲突条目字段完整性",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "所有条目均包含必需字段"
        })
    else:
        total_score += 0
        details.append({
            "item": "电价冲突条目字段完整性",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "存在条目缺少字段或列表为空"
        })

    # 6c. 设备ID 合法性 (10 分)
    actual_rate_ids = {item["device_id"] for item in actual_rate}
    expected_rate_ids = {e["device_id"] for e in expected_rate}
    if actual_rate_ids.issubset(all_legit_ids) and actual_rate_ids == expected_rate_ids:
        total_score += 10
        details.append({
            "item": "电价冲突设备ID合法性",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"设备ID集合正确: {expected_rate_ids}"
        })
    else:
        total_score += 0
        details.append({
            "item": "电价冲突设备ID合法性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"实际ID: {actual_rate_ids}, 期望: {expected_rate_ids}"
        })

    # ---------- 7. 额外加分：检查报告未包含未定义的字段 (5 分) ----------
    # 不允许出现与任务无关的额外顶层字段（如 "summary" 等）
    allowed_top = {"health_conflicts", "rate_conflicts"}
    extra = actual_keys - allowed_top
    if not extra:
        total_score += 5
        details.append({
            "item": "无多余顶层字段",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "报告仅包含要求的两个列表"
        })
    else:
        total_score += 0
        details.append({
            "item": "无多余顶层字段",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"发现额外字段: {extra}"
        })

    # 总分封顶100
    total_score = min(total_score, 100)
    write_score(total_score, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    # 同时标准输出结果（可选）
    print(f"总分: {total}/100")
    for d in details:
        print(f"{d['item']}: {'通过' if d['passed'] else '未通过'} ({d['score']}/{d['max_score']}) - {d['reason']}")

if __name__ == "__main__":
    verify()
