import os
import json
from datetime import datetime, timedelta

def build_env():
    # 创建目录结构
    os.makedirs("logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # 构造干扰文件：其他AC温度指令
    temp_logs = [
        {"timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(), "cmd": "ac-temp", "args": {"temperature": 24}},
        {"timestamp": (datetime.now() - timedelta(minutes=4)).isoformat(), "cmd": "ac-temp", "args": {"temperature": 26}},
    ]
    # 构造风扇指令序列（带干扰顺序）
    fan_logs = [
        {"timestamp": (datetime.now() - timedelta(minutes=3)).isoformat(), "cmd": "ac-fan", "args": {"speed": 2}},
        {"timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(), "cmd": "ac-fan", "args": {"speed": 4}},
        {"timestamp": (datetime.now() - timedelta(minutes=1)).isoformat(), "cmd": "ac-fan", "args": {"speed": 3}},  # 最后一条，答案
    ]
    # 包含一些无关指令（干扰）
    other_logs = [
        {"timestamp": (datetime.now() - timedelta(minutes=6)).isoformat(), "cmd": "ac-mode", "args": {"mode": "auto"}},
        {"timestamp": (datetime.now() - timedelta(minutes=7)).isoformat(), "cmd": "driving-mode", "args": {"mode": "eco"}},
    ]
    
    all_logs = temp_logs + fan_logs + other_logs
    # 乱序写入，增加难度
    import random
    random.shuffle(all_logs)
    
    with open("logs/command_history.json", "w") as f:
        json.dump(all_logs, f, indent=2)
    
    # 额外干扰文件：不相关的预设数据
    with open("data/ac_presets.json", "w") as f:
        json.dump({"presets": [{"preset_id": "cool", "name": "制冷", "fan_speed": "high"}]}, f)
    
    with open("data/zones.json", "w") as f:
        json.dump({"zones": [{"zone_id": "fl", "name": "左前", "seat_type": "ventilated"}]}, f)

if __name__ == "__main__":
    build_env()
