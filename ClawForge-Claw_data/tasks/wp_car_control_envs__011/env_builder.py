import os
import random
import json

def build_env():
    # 确保目录存在
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 创建主日志文件（含干扰项和脏数据）
    log_lines = []
    # 有效 ac-fan 命令（速度在0-5之间，结果success）
    valid_speeds = [1, 2, 3, 4, 5, 2, 3, 4, 5, 1]  # 共10条，平均3.0 → 四舍五入3
    for speed in valid_speeds:
        log_lines.append(f"2025-03-21 08:{random.randint(10,59):02d}:{random.randint(0,59):02d} ac-fan --speed {speed} success")
    # 干扰：ac-temp 成功命令
    for temp in [22, 24, 26]:
        log_lines.append(f"2025-03-21 09:{random.randint(0,59):02d}:{random.randint(0,59):02d} ac-temp --temperature {temp} success")
    # 干扰：ac-fan 失败命令（速度超出范围或参数错误）
    log_lines.append("2025-03-21 09:15:32 ac-fan --speed 6 failure_invalid_speed")
    log_lines.append("2025-03-21 09:18:10 ac-fan --speed -1 failure_invalid_speed")
    log_lines.append("2025-03-21 09:20:44 ac-fan --speed abc failure_bad_argument")
    # 干扰：其他命令
    log_lines.append("2025-03-21 09:22:01 seat --zone fl --position 10 success")
    log_lines.append("2025-03-21 09:25:37 window --window fl --percentage 50 success")
    # 乱序写入，打乱顺序
    random.shuffle(log_lines)
    with open("logs/command_history.log", "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    # 创建背景文件，增加迷惑性
    ac_presets = {
        "presets": [
            {"preset_id": "p1", "name": "制冷", "description": "快速制冷模式", "default_temperature": 22, "fan_speed": "auto", "ac_enabled": True, "recirculation": True},
            {"preset_id": "p2", "name": "制热", "description": "快速制热模式", "default_temperature": 28, "fan_speed": "high", "ac_enabled": True, "recirculation": False},
        ]
    }
    with open("data/ac_presets.json", "w", encoding="utf-8") as f:
        json.dump(ac_presets, f)

    zones = {
        "zones": [
            {"zone_id": "z1", "name": "左前", "position": "front_left", "seat_type": "ventilated"},
            {"zone_id": "z2", "name": "右前", "position": "front_right", "seat_type": "standard"},
        ]
    }
    with open("data/zones.json", "w", encoding="utf-8") as f:
        json.dump(zones, f)

    # 额外空文件干扰
    open("ops/old_report.json", "w").close()

if __name__ == "__main__":
    build_env()
