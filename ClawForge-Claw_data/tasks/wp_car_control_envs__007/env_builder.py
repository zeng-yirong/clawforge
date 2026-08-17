import os
import json

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 主数据：ac_presets.json
    presets = {
        "presets": {
            "preset_1": {
                "preset_id": "preset_1",
                "name": "制冷",
                "description": "快速制冷模式，保持车内凉爽",
                "default_temperature": 22,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": True,
                "defog_enabled": True,
                "defrost_enabled": False
            },
            "preset_2": {
                "preset_id": "preset_2",
                "name": "制热",
                "description": "快速制热模式，保持车内温暖",
                "default_temperature": 28,
                "fan_speed": "high",
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": True,
                "defrost_enabled": False
            },
            "preset_3": {
                "preset_id": "preset_3",
                "name": "自动",
                "description": "自动调节温度和风速",
                "default_temperature": 24,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": True,
                "defog_enabled": False,
                "defrost_enabled": False
            },
            "preset_4": {
                "preset_id": "preset_4",
                "name": "除雾",
                "description": "快速除雾除霜模式",
                "default_temperature": 28,
                "fan_speed": "high",
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": True,
                "defrost_enabled": True
            },
            "preset_5": {
                "preset_id": "preset_5",
                "name": "节能",
                "description": "节能模式，降低能耗",
                "default_temperature": 20,
                "fan_speed": "auto",
                "ac_enabled": False,
                "recirculation": True,
                "defog_enabled": True,
                "defrost_enabled": False
            },
            "preset_6": {
                "preset_id": "preset_6",
                "name": "运动",
                "description": "运动模式，提供最佳动力响应",
                "default_temperature": 30,
                "fan_speed": "high",
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": False,
                "defrost_enabled": False
            }
        }
    }
    with open("data/ac_presets.json", "w") as f:
        json.dump(presets, f, indent=2)

    # 干扰项：ambient_lights.json
    ambient_lights = {
        "ambient_lights": {
            "color_1": {
                "color_id": "color_1",
                "name": "关闭",
                "hex_color": "#000000",
                "effect": "氛围灯关闭"
            },
            "color_2": {
                "color_id": "color_2",
                "name": "蓝色",
                "hex_color": "#0066CC",
                "effect": "冷静舒适"
            }
        }
    }
    with open("data/ambient_lights.json", "w") as f:
        json.dump(ambient_lights, f, indent=2)

    # 干扰项：driving_modes.json
    driving_modes = {
        "driving_modes": {
            "mode_eco": {
                "mode_id": "mode_eco",
                "name": "节能模式",
                "description": "优化能耗，提高续航里程",
                "characteristics": {"power": "low", "suspension": "soft"}
            },
            "mode_sport": {
                "mode_id": "mode_sport",
                "name": "运动模式",
                "description": "最大动力输出，运动调校",
                "characteristics": {"power": "high", "suspension": "hard"}
            }
        }
    }
    with open("data/driving_modes.json", "w") as f:
        json.dump(driving_modes, f, indent=2)

    # 干扰项：zones.json
    zones = {
        "zones": {
            "zone_fl": {
                "zone_id": "zone_fl",
                "name": "左前",
                "position": "front_left",
                "seat_type": "ventilated"
            },
            "zone_fr": {
                "zone_id": "zone_fr",
                "name": "右前",
                "position": "front_right",
                "seat_type": "heated"
            }
        }
    }
    with open("data/zones.json", "w") as f:
        json.dump(zones, f, indent=2)

if __name__ == "__main__":
    build_env()
