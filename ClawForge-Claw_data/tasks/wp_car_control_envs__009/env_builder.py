import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("report", exist_ok=True)  # 预先创建空目录给 agent 参考，但最终文件由 agent 写出

    # 旧的日志文件 (2025-02-28)
    old_rows = [
        {"zone": "fl", "temp": 25, "fan": 2, "ac_on": "true"},
        {"zone": "fr", "temp": 30, "fan": 5, "ac_on": "true"},
        {"zone": "rl", "temp": 27, "fan": 3, "ac_on": "true"},
        {"zone": "rr", "temp": 29, "fan": 4, "ac_on": "false"},
    ]
    with open("data/logs/log_2025_02_28.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["zone","temp","fan","ac_on"])
        writer.writeheader()
        writer.writerows(old_rows)

    # 新的日志文件 (2025-03-01) – 正确答案来源
    new_rows = [
        {"zone": "fl", "temp": 26, "fan": 3, "ac_on": "false"},
        {"zone": "fr", "temp": 29, "fan": 4, "ac_on": "true"},
        {"zone": "rl", "temp": 30, "fan": 5, "ac_on": "true"},
        {"zone": "rr", "temp": 28, "fan": 2, "ac_on": "true"},   # temp == 28，不满足 >28
        {"zone": "rc", "temp": 30, "fan": 3, "ac_on": "true"},   # 满足条件
    ]
    with open("data/logs/log_2025_03_01.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["zone","temp","fan","ac_on"])
        writer.writeheader()
        writer.writerows(new_rows)

    # 额外干扰文件 – 无关数据
    os.makedirs("data/config", exist_ok=True)
    with open("data/config/ac_presets.json", "w") as f:
        json.dump({"presets": [{"id":"p1","name":"制冷","fan_speed":"high"}]}, f)

if __name__ == "__main__":
    build_env()
