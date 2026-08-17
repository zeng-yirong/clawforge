import sys
import os
import json
import math

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    details = []
    total_score = 0

    # 1. 检查必要目录是否存在 (10分)
    dirs_ok = all(os.path.isdir(d) for d in ["data", "ops"])
    details.append({
        "item": "必要目录 data/ 和 ops/ 存在",
        "score": 10 if dirs_ok else 0,
        "max_score": 10,
        "passed": dirs_ok,
        "reason": "目录完整" if dirs_ok else "缺少目录"
    })
    if dirs_ok:
        total_score += 10

    # 2. 检查输出文件 ops/energy_plan.json 是否存在 (15分)
    plan_path = "ops/energy_plan.json"
    plan_exists = os.path.isfile(plan_path)
    details.append({
        "item": "输出文件 ops/energy_plan.json 存在",
        "score": 15 if plan_exists else 0,
        "max_score": 15,
        "passed": plan_exists,
        "reason": "文件存在" if plan_exists else "文件未找到"
    })
    if plan_exists:
        total_score += 15
    else:
        # 直接返回，后续无法验证
        total_score = sum(d["score"] for d in details)
        if total_score < 0:
            total_score = 0
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 解析JSON并检查必需字段 (25分)
    try:
        with open(plan_path, "r") as f:
            plan = json.load(f)
        required_fields = ["temperature", "humidity", "start_hour", "end_hour", "devices", "estimated_cost", "rate_used"]
        missing = [k for k in required_fields if k not in plan]
        if not missing:
            details.append({
                "item": "JSON包含所有必需字段",
                "score": 25,
                "max_score": 25,
                "passed": True,
                "reason": "字段完整"
            })
            total_score += 25
        else:
            details.append({
                "item": "JSON必需字段缺失",
                "score": 0,
                "max_score": 25,
                "passed": False,
                "reason": f"缺失字段: {missing}"
            })
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON格式合法",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"解析错误: {str(e)}"
        })
        total_score += sum(d["score"] for d in details)
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. 验证关键数值的准确性 (40分)
    numerical_ok = True
    reason_parts = []

    # 预期数值
    exp_temperature = 23.0
    exp_humidity = 50.0
    exp_start = 0
    exp_end = 7
    exp_rate = 0.12
    # 空调+加湿器总功率 = 2000+300 = 2300W
    total_power_w = 2300
    hours = 7
    expected_energy_kwh = (total_power_w * hours) / 1000.0  # 16.1
    expected_cost = round(expected_energy_kwh * exp_rate, 4)  # 1.932

    # 检查温度 (允许±0.1)
    if abs(plan.get("temperature", -1) - exp_temperature) <= 0.1:
        reason_parts.append("温度正确")
    else:
        numerical_ok = False
        reason_parts.append(f"温度应为{exp_temperature}，实际{plan.get('temperature')}")

    # 检查湿度 (允许±1)
    if abs(plan.get("humidity", -1) - exp_humidity) <= 1:
        reason_parts.append("湿度正确")
    else:
        numerical_ok = False
        reason_parts.append(f"湿度应为{exp_humidity}，实际{plan.get('humidity')}")

    # 检查时间
    if plan.get("start_hour") == exp_start and plan.get("end_hour") == exp_end:
        reason_parts.append("时间区间正确")
    else:
        numerical_ok = False
        reason_parts.append(f"时间区间应为{exp_start}-{exp_end}，实际{plan.get('start_hour')}-{plan.get('end_hour')}")

    # 检查电价
    if abs(plan.get("rate_used", -1) - exp_rate) <= 0.001:
        reason_parts.append("电价正确")
    else:
        numerical_ok = False
        reason_parts.append(f"电价应为{exp_rate}，实际{plan.get('rate_used')}")

    # 检查设备列表是否包含bedroom ac和humidifier
    devices_in_plan = plan.get("devices", [])
    device_ids = [d.get("device_id") for d in devices_in_plan if isinstance(d, dict)]
    if "ac-bedroom" in device_ids and "humid-bedroom" in device_ids:
        reason_parts.append("设备正确")
    else:
        numerical_ok = False
        reason_parts.append("设备列表缺少卧室空调或加湿器")

    # 检查预估电费 (允许 ±0.01)
    actual_cost = plan.get("estimated_cost", 0)
    if abs(actual_cost - expected_cost) <= 0.01:
        reason_parts.append("电费正确")
    else:
        numerical_ok = False
        reason_parts.append(f"电费应为{expected_cost}，实际{actual_cost}")

    score_40 = 40 if numerical_ok else 0
    details.append({
        "item": "关键数值计算准确",
        "score": score_40,
        "max_score": 40,
        "passed": numerical_ok,
        "reason": "; ".join(reason_parts)
    })
    total_score += score_40

    # 5. 检查是否有多余的字段/节点？不强制，但可以加分 (越界就扣分？) 这里不扣分，但记录
    # 6. 检查plan中是否包含必要的子结构 (如devices至少两个对象) (10分)
    device_count_ok = isinstance(devices_in_plan, list) and len(devices_in_plan) >= 2
    details.append({
        "item": "devices列表包含至少两个设备",
        "score": 10 if device_count_ok else 0,
        "max_score": 10,
        "passed": device_count_ok,
        "reason": "设备数量足够" if device_count_ok else "设备数量不足"
    })
    if device_count_ok:
        total_score += 10

    # 最终总分
    total_score = min(total_score, 100)  # 防止溢出
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
