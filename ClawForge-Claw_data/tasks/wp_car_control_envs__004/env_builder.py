import os
import json

def build_env():
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ac_presets.json – 含6个预设，其中运动的fan_speed故意设为high
    presets = {
        "presets": [
            {
                "preset_id": "preset_01",
                "name": "制冷",
                "description": "快速制冷模式，保持车内凉爽",
                "default_temperature": 22,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": True,
                "defog_enabled": False,
                "defrost_enabled": False
            },
            {
                "preset_id": "preset_02",
                "name": "制热",
                "description": "快速制热模式，保持车内温暖",
                "default_temperature": 28,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": False,
                "defrost_enabled": True
            },
            {
                "preset_id": "preset_03",
                "name": "自动",
                "description": "自动调节温度和风速",
                "default_temperature": 24,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": False,
                "defrost_enabled": False
            },
            {
                "preset_id": "preset_04",
                "name": "运动",
                "description": "运动模式，提供最佳动力响应",
                "default_temperature": 20,
                "fan_speed": "high",      # 异常值
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": False,
                "defrost_enabled": False
            },
            {
                "preset_id": "preset_05",
                "name": "节能",
                "description": "节能模式，降低能耗",
                "default_temperature": 26,
                "fan_speed": "auto",
                "ac_enabled": False,
                "recirculation": True,
                "defog_enabled": False,
                "defrost_enabled": False
            },
            {
                "preset_id": "preset_06",
                "name": "除雾",
                "description": "快速除雾除霜模式",
                "default_temperature": 25,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": True,
                "defrost_enabled": True
            }
        ]
    }
    with open("data/ac_presets.json", "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)

    # 干扰文件
    ambient_lights = {
        "ambient_lights": [
            {"color_id": "cl_01", "name": "关闭", "hex_color": "#000000", "effect": "氛围灯关闭"},
            {"color_id": "cl_02", "name": "橙色", "hex_color": "#FF9933", "effect": "温暖活力"},
        ]
    }
    with open("data/ambient_lights.json", "w", encoding="utf-8") as f:
        json.dump(ambient_lights, f, ensure_ascii=False, indent=2)

    driving_modes = {
        "driving_modes": [
            {"mode_id": "dm_01", "name": "舒适模式", "description": "平衡动力与能耗", "characteristics": {"power": "medium"}},
        ]
    }
    with open("data/driving_modes.json", "w", encoding="utf-8") as f:
        json.dump(driving_modes, f, ensure_ascii=False, indent=2)

    zones = {
        "zones": [
            {"zone_id": "z_01", "name": "左前", "position": "front_left", "seat_type": "ventilated"}
        ]
    }
    with open("data/zones.json", "w", encoding="utf-8") as f:
        json.dump(zones, f, ensure_ascii=False, indent=2)

    # 日志干扰
    with open("log/system_alert.log", "w") as f:
        f.write("2025-03-15 03:00:01 [WARN] AC_FAN_SPEED_MISMATCH: preset_04 fan_speed=high expected=auto\n")
        f.write("2025-03-15 03:00:02 [INFO] AC_TEMP stable\n")

if __name__ == "__main__":
    build_env()
