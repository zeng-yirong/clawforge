import json
import os

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ac_presets.json —— 包含多个预设，其中“制冷”的 fan_speed='auto'
    presets = {
        "presets": [
            {
                "preset_id": "p001",
                "name": "制冷",
                "description": "快速制冷模式，保持车内凉爽",
                "default_temperature": 26,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": True,
                "defog_enabled": False,
                "defrost_enabled": False
            },
            {
                "preset_id": "p002",
                "name": "制热",
                "description": "快速制热模式，保持车内温暖",
                "default_temperature": 30,
                "fan_speed": "high",
                "ac_enabled": True,
                "recirculation": True,
                "defog_enabled": False,
                "defrost_enabled": False
            },
            {
                "preset_id": "p003",
                "name": "测试_旧制冷",
                "description": "废弃的测试预设",
                "default_temperature": 24,
                "fan_speed": "auto",
                "ac_enabled": False,
                "recirculation": False
            },
            {
                "preset_id": "p004",
                "name": "节能",
                "description": "节能模式，降低能耗",
                "default_temperature": 24,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": False,
                "defrost_enabled": False
            }
        ]
    }
    with open("data/ac_presets.json", "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)

    # zones.json —— 包含左前座椅 (fl) 类型为通风座椅
    zones = {
        "zones": [
            {
                "zone_id": "fl",
                "name": "左前",
                "position": "front_left",
                "seat_type": "ventilated"
            },
            {
                "zone_id": "fr",
                "name": "右前",
                "position": "front_right",
                "seat_type": "heated"
            },
            {
                "zone_id": "rl",
                "name": "左后",
                "position": "rear_left",
                "seat_type": "standard"
            },
            {
                "zone_id": "rr",
                "name": "右后",
                "position": "rear_right",
                "seat_type": "heated"
            },
            {
                "zone_id": "rc",
                "name": "后排中间",
                "position": "rear_center",
                "seat_type": "standard"
            }
        ]
    }
    with open("data/zones.json", "w", encoding="utf-8") as f:
        json.dump(zones, f, ensure_ascii=False, indent=2)

    # 额外干扰文件（车载驾驶模式等，但本次任务不涉及）
    driving_modes = {
        "driving_modes": [
            {"mode_id": "eco", "name": "节能模式", "description": "优化能耗", "characteristics": {}},
            {"mode_id": "comfort", "name": "舒适模式", "description": "平衡", "characteristics": {}},
            {"mode_id": "sport", "name": "运动模式", "description": "最大动力", "characteristics": {}}
        ]
    }
    with open("data/driving_modes.json", "w", encoding="utf-8") as f:
        json.dump(driving_modes, f, ensure_ascii=False, indent=2)

    # 空的环境灯文件（仅用于丰富目录）
    ambient_lights = {"ambient_lights": []}
    with open("data/ambient_lights.json", "w", encoding="utf-8") as f:
        json.dump(ambient_lights, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
