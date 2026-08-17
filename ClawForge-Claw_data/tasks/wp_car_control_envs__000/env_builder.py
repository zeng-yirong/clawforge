import os
import json
import random

def build_env():
    # 确保 data/ 目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 留给 agent 写入

    # 正常预设（有效）
    valid_presets = [
        {
            "preset_id": "preset_001",
            "name": "制冷",
            "description": "快速制冷模式，保持车内凉爽",
            "default_temperature": 20,
            "fan_speed": "high",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "preset_003",
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
            "preset_id": "preset_005",
            "name": "运动",
            "description": "运动模式，提供最佳动力响应",
            "default_temperature": 18,
            "fan_speed": "high",
            "ac_enabled": True,
            "recirculation": False,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "preset_007",
            "name": "制热",
            "description": "快速制热模式，保持车内温暖",
            "default_temperature": 28,
            "fan_speed": "high",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        }
    ]

    # 干扰项：fan_speed 不是 high 的预设
    interference_presets = [
        {
            "preset_id": "preset_002",
            "name": "节能",
            "description": "节能模式，降低能耗",
            "default_temperature": 22,
            "fan_speed": "auto",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "preset_004",
            "name": "除雾",
            "description": "快速除雾除霜模式",
            "default_temperature": 25,
            "fan_speed": "auto",
            "ac_enabled": True,
            "recirculation": False,
            "defog_enabled": True,
            "defrost_enabled": True
        },
        {
            "preset_id": "preset_006",
            "name": "制冷",
            "description": "快速制冷模式，保持车内凉爽",
            "default_temperature": 20,
            "fan_speed": "auto",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        }
    ]

    # 脏数据：重复的 preset_id（故意引入重复但 fan_speed 不同，增加迷惑性）
    duplicate_preset = {
        "preset_id": "preset_001",
        "name": "制冷",
        "description": "测试副本，忽略",
        "default_temperature": 20,
        "fan_speed": "auto",
        "ac_enabled": False,
        "recirculation": False,
        "defog_enabled": False,
        "defrost_enabled": False
    }

    # 过期版本/格式错误数据（非标准字段）
    old_format_presets = [
        {
            "id": "preset_008",
            "title": "旧版节能",
            "speed": "high"
        },
        {
            "preset_id": "preset_009",
            "name": "测试",
            "description": "测试用",
            "default_temperature": 24,
            "fan_speed": "high",
            "ac_enabled": "on",   # 类型异常，但保留
            "recirculation": "off"
        }
    ]

    # 合并所有预设
    all_presets = valid_presets + interference_presets + [duplicate_preset] + old_format_presets
    random.shuffle(all_presets)

    # 写入主文件（wrapper 为 "presets"）
    with open("data/ac_presets.json", "w", encoding="utf-8") as f:
        json.dump({"presets": all_presets}, f, ensure_ascii=False, indent=2)

    # 创建额外的诱饵文件（无关）
    with open("data/ambient_lights.json", "w", encoding="utf-8") as f:
        json.dump({"ambient_lights": []}, f, ensure_ascii=False, indent=2)

    # 创建一个临时备份目录，里面放一个旧版预设（干扰）
    os.makedirs("backup", exist_ok=True)
    with open("backup/ac_presets_old.json", "w", encoding="utf-8") as f:
        json.dump({"presets": []}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
