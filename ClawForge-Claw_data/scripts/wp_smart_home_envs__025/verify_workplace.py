import sys
import json
import os
from datetime import datetime, timezone
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查输出文件是否存在 (10分)
    output_path = os.path.join(workspace, "ops", "energy_plan.json")
    if not os.path.exists(output_path):
        score_details.append({
            "item": "Output file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/energy_plan.json not found"
        })
        total_score = 0
        write_result(workspace, total_score, score_details)
        return
    else:
        score_details.append({
            "item": "Output file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/energy_plan.json found"
        })
        total_score += 10

    # 2. JSON 格式合法 (5分)
    try:
        with open(output_path, "r") as f:
            plan = json.load(f)
        score_details.append({
            "item": "JSON format valid",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Parsed successfully"
        })
        total_score += 5
    except Exception as e:
        score_details.append({
            "item": "JSON format valid",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        write_result(workspace, total_score, score_details)
        return

    # 3. 检查必要字段 (10分)
    required_fields = ["current_time", "current_rate", "essential_device_ids", 
                       "non_essential_device_ids", "non_essential_total_power_watts", "potential_savings_per_hour"]
    missing = [f for f in required_fields if f not in plan]
    if missing:
        score_details.append({
            "item": "Required fields present",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing fields: {missing}"
        })
        write_result(workspace, total_score, score_details)
        return
    else:
        score_details.append({
            "item": "Required fields present",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All required fields present"
        })
        total_score += 10

    # 4. 验证 current_time 从 weather.json 获取 (5分)
    weather_path = os.path.join(workspace, "data", "weather", "weather.json")
    try:
        with open(weather_path) as f:
            weather_data = json.load(f)["weather_data"]
        expected_time = weather_data[-1]["timestamp"]  # 最新一条
        if plan["current_time"] != expected_time:
            score_details.append({
                "item": "current_time matches weather",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Expected {expected_time}, got {plan['current_time']}"
            })
        else:
            score_details.append({
                "item": "current_time matches weather",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Correct"
            })
            total_score += 5
    except Exception as e:
        score_details.append({
            "item": "current_time matches weather",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Error reading weather: {e}"
        })

    # 5. 验证 current_rate 从 rates.json 根据时间计算 (10分)
    try:
        rates_path = os.path.join(workspace, "data", "electricity", "rates.json")
        with open(rates_path) as f:
            rates_data = json.load(f)["rates"]
        # 解析 current_time 得到小时
        dt = datetime.fromisoformat(plan["current_time"].replace("Z", "+00:00"))
        hour = dt.hour
        # 查找匹配时段
        expected_rate = None
        for r in rates_data:
            if r["start_hour"] <= hour < r["end_hour"]:
                expected_rate = r["rate_per_kwh"]
                break
        if expected_rate is None:
            # 处理边界情况如22:00属于off_peak_night
            for r in rates_data:
                if hour >= r["start_hour"] and (r["end_hour"] == 24 or hour < r["end_hour"]):
                    expected_rate = r["rate_per_kwh"]
                    break
        if expected_rate is None:
            score_details.append({
                "item": "current_rate matches schedule",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Could not determine expected rate from schedule"
            })
        elif abs(plan["current_rate"] - expected_rate) > 0.001:
            score_details.append({
                "item": "current_rate matches schedule",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Expected {expected_rate}, got {plan['current_rate']}"
            })
        else:
            score_details.append({
                "item": "current_rate matches schedule",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Correct"
            })
            total_score += 10
    except Exception as e:
        score_details.append({
            "item": "current_rate matches schedule",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Error: {e}"
        })

    # 6. 验证 essential_device_ids (15分)
    # 根据 health.json 中 respiratory_issues==True 的用户，所有 type==humidifier 的设备
    try:
        health_path = os.path.join(workspace, "data", "health", "health.json")
        with open(health_path) as f:
            health_data = json.load(f)["users"]
        target_user = next(u for u in health_data if u["respiratory_issues"] == True)
        devices_path = os.path.join(workspace, "data", "devices", "devices.json")
        with open(devices_path) as f:
            devices_data = json.load(f)["devices"]
        expected_essential = sorted([d["device_id"] for d in devices_data if d["type"] == "humidifier"])
        agent_essential = sorted(plan.get("essential_device_ids", []))
        if agent_essential == expected_essential:
            score_details.append({
                "item": "essential_device_ids correct",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "Correct humidifier devices"
            })
            total_score += 15
        else:
            score_details.append({
                "item": "essential_device_ids correct",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Expected {expected_essential}, got {agent_essential}"
            })
    except Exception as e:
        score_details.append({
            "item": "essential_device_ids correct",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Error: {e}"
        })

    # 7. 验证 non_essential_device_ids (15分)
    try:
        expected_non_essential = sorted([d["device_id"] for d in devices_data if d["type"] == "smart_plug"])
        agent_non_essential = sorted(plan.get("non_essential_device_ids", []))
        if agent_non_essential == expected_non_essential:
            score_details.append({
                "item": "non_essential_device_ids correct",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "Correct smart_plug devices"
            })
            total_score += 15
        else:
            score_details.append({
                "item": "non_essential_device_ids correct",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Expected {expected_non_essential}, got {agent_non_essential}"
            })
    except Exception as e:
        score_details.append({
            "item": "non_essential_device_ids correct",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Error: {e}"
        })

    # 8. 验证 non_essential_total_power_watts (15分)
    try:
        expected_power = sum(d["power_watts"] for d in devices_data if d["type"] == "smart_plug")
        if plan["non_essential_total_power_watts"] == expected_power:
            score_details.append({
                "item": "non_essential_total_power_watts correct",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": f"Correct power {expected_power}W"
            })
            total_score += 15
        else:
            score_details.append({
                "item": "non_essential_total_power_watts correct",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Expected {expected_power}, got {plan['non_essential_total_power_watts']}"
            })
    except Exception as e:
        score_details.append({
            "item": "non_essential_total_power_watts correct",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Error: {e}"
        })

    # 9. 验证 potential_savings_per_hour (15分)
    try:
        # 使用 expected_power 和 current_rate 计算
        power_kw = expected_power / 1000.0
        expected_savings = round(power_kw * expected_rate, 2)
        agent_savings = plan.get("potential_savings_per_hour")
        # 允许 0.01 浮点误差
        if abs(agent_savings - expected_savings) < 0.011:
            score_details.append({
                "item": "potential_savings_per_hour correct",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": f"Correct savings ${expected_savings}"
            })
            total_score += 15
        else:
            score_details.append({
                "item": "potential_savings_per_hour correct",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"Expected {expected_savings}, got {agent_savings}"
            })
    except Exception as e:
        score_details.append({
            "item": "potential_savings_per_hour correct",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": f"Error: {e}"
        })

    # 写入结果
    write_result(workspace, total_score, score_details)

def write_result(workspace, total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
