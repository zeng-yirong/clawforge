import json, csv, os

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)
    # 创建 ops 目录
    os.makedirs("ops", exist_ok=True)

    # 生成 ac_presets.json（当前状态，已包含一次错误修改）
    presets = [
        {
            "preset_id": "cool",
            "name": "制冷",
            "description": "快速制冷模式，保持车内凉爽",
            "default_temperature": 22,
            "fan_speed": "high",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "heat",
            "name": "制热",
            "description": "快速制热模式，保持车内温暖",
            "default_temperature": 28,
            "fan_speed": "auto",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "auto",
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
            "preset_id": "eco",
            "name": "节能",
            "description": "节能模式，降低能耗",
            "default_temperature": 26,
            "fan_speed": "auto",
            "ac_enabled": True,
            "recirculation": False,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "sport",
            "name": "运动",
            "description": "运动模式，提供最佳动力响应",
            "default_temperature": 20,
            "fan_speed": "high",          # 当前错误值（原本是 auto）
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "defog",
            "name": "除雾",
            "description": "快速除雾除霜模式",
            "default_temperature": 24,
            "fan_speed": "high",
            "ac_enabled": True,
            "recirculation": False,
            "defog_enabled": True,
            "defrost_enabled": True
        }
    ]
    with open("data/ac_presets.json", "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)

    # 生成 modifications.csv（包括多次修改，仅一条涉及 fan_speed）
    modifications = [
        ["timestamp", "operator", "preset_id", "affected_field", "original_value", "new_value"],
        ["2025-04-01T10:00:00", "alice", "sport", "fan_speed", "auto", "high"],
        ["2025-04-01T10:05:00", "bob",   "cool",  "default_temperature", "26", "24"],
        ["2025-04-01T10:10:00", "alice", "eco",   "recirculation", "false", "true"],
        ["2025-04-01T10:15:00", "charlie", "defog", "defog_enabled", "true", "false"]
    ]
    with open("ops/modifications.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(modifications)

if __name__ == "__main__":
    build_env()
