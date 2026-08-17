import json, os

def build_env():
    # 主配置数据
    presets_data = {
        "presets": {
            "p1": {"preset_id": "p1", "name": "制冷", "description": "快速制冷模式，保持车内凉爽",
                   "default_temperature": 22, "fan_speed": "auto", "ac_enabled": True, "recirculation": True,
                   "defog_enabled": False, "defrost_enabled": False},
            "p2": {"preset_id": "p2", "name": "制热", "description": "快速制热模式，保持车内温暖",
                   "default_temperature": 28, "fan_speed": "auto", "ac_enabled": True, "recirculation": False,
                   "defog_enabled": False, "defrost_enabled": False},
            "p3": {"preset_id": "p3", "name": "自动", "description": "自动调节温度和风速",
                   "default_temperature": 24, "fan_speed": "auto", "ac_enabled": True, "recirculation": True,
                   "defog_enabled": True, "defrost_enabled": False},
            "p4": {"preset_id": "p4", "name": "节能", "description": "节能模式，降低能耗",
                   "default_temperature": 26, "fan_speed": "auto", "ac_enabled": True, "recirculation": True,
                   "defog_enabled": False, "defrost_enabled": False},
            "p5": {"preset_id": "p5", "name": "运动", "description": "运动模式，提供最佳动力响应",
                   "default_temperature": 18, "fan_speed": "high", "ac_enabled": True, "recirculation": False,
                   "defog_enabled": False, "defrost_enabled": False},
            "p6": {"preset_id": "p6", "name": "除雾", "description": "快速除雾除霜模式",
                   "default_temperature": 16, "fan_speed": "high", "ac_enabled": True, "recirculation": True,
                   "defog_enabled": True, "defrost_enabled": True}
        }
    }
    os.makedirs("data", exist_ok=True)
    with open("data/ac_presets.json", "w", encoding="utf-8") as f:
        json.dump(presets_data, f, ensure_ascii=False, indent=2)

    # 干扰文件：备份目录（包含一个满足条件的预设，但不应被采用）
    os.makedirs("data/backup", exist_ok=True)
    backup_presets = {
        "presets": {
            "b1": {"preset_id": "b1", "name": "应急除霜", "description": "旧版应急除霜",
                   "default_temperature": 15, "fan_speed": "high", "ac_enabled": True, "recirculation": False,
                   "defog_enabled": True, "defrost_enabled": True}
        }
    }
    with open("data/backup/ac_presets_bak.json", "w", encoding="utf-8") as f:
        json.dump(backup_presets, f, ensure_ascii=False, indent=2)

    # 干扰文件：其他无关配置文件
    ambient_data = {
        "ambient_lights": {
            "c1": {"color_id": "c1", "name": "白色", "hex_color": "#FFFFFF", "effect": "简约明亮"},
            "c2": {"color_id": "c2", "name": "蓝色", "hex_color": "#0066CC", "effect": "冷静舒适"}
        }
    }
    with open("data/ambient_lights.json", "w", encoding="utf-8") as f:
        json.dump(ambient_data, f, ensure_ascii=False, indent=2)

    driving_data = {
        "driving_modes": {
            "m1": {"mode_id": "m1", "name": "舒适模式", "description": "平衡动力与能耗",
                   "characteristics": {"power": 60, "eco": 40}},
            "m2": {"mode_id": "m2", "name": "运动模式", "description": "最大动力输出",
                   "characteristics": {"power": 100, "eco": 10}}
        }
    }
    with open("data/driving_modes.json", "w", encoding="utf-8") as f:
        json.dump(driving_data, f, ensure_ascii=False, indent=2)

    # 创建一个非JSON干扰文件（文本日志）
    with open("data/system_check.log", "w", encoding="utf-8") as f:
        f.write("2025-04-12 01:23:45 INFO AC fan anomaly detected on zone fl\n")
        f.write("2025-04-12 01:23:46 WARN temperature sensor mismatch\n")

    # 创建 ops 目录（预期输出位置）
    os.makedirs("ops", exist_ok=True)

    # 如果 ops 下有残留文件，清理（确保干净状态）
    if os.path.exists("ops/abnormal_presets.json"):
        os.remove("ops/abnormal_presets.json")

if __name__ == "__main__":
    build_env()
