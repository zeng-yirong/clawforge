import json, os

def build_env():
    # 创建数据目录
    os.makedirs("data", exist_ok=True)

    # 生成 ac_presets.json（干扰项丰富，答案唯一）
    presets = [
        {
            "preset_id": "eco_default",
            "name": "节能",
            "description": "节能模式，降低能耗",
            "default_temperature": 24,
            "fan_speed": "auto",
            "ac_enabled": True,
            "recirculation": False,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "eco_winter",
            "name": "节能（冬季）",
            "description": "节能模式下提高暖风效率",
            "default_temperature": 26,
            "fan_speed": "high",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": True
        },
        {
            "preset_id": "cool",
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
            "preset_id": "auto_mode",
            "name": "自动",
            "description": "自动调节温度和风速",
            "default_temperature": 22,
            "fan_speed": "auto",
            "ac_enabled": True,
            "recirculation": False,
            "defog_enabled": True,
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
        json.dump({"presets": presets}, f, ensure_ascii=False, indent=2)

    # 生成 ambient_lights.json（干扰项，不影响答案）
    lights = [
        {"color_id": "off", "name": "关闭", "hex_color": "#000000", "effect": "氛围灯关闭"},
        {"color_id": "orange", "name": "橙色", "hex_color": "#FF9933", "effect": "温暖活力"},
        {"color_id": "blue", "name": "蓝色", "hex_color": "#0066CC", "effect": "冷静舒适"}
    ]
    with open("data/ambient_lights.json", "w", encoding="utf-8") as f:
        json.dump({"ambient_lights": lights}, f, ensure_ascii=False, indent=2)

    # 生成 driving_modes.json（干扰项）
    modes = [
        {"mode_id": "eco", "name": "节能模式", "description": "优化能耗，提高续航里程", "characteristics": {"ac_power_save": True, "fan_limit": "auto"}},
        {"mode_id": "sport", "name": "运动模式", "description": "最大动力输出，运动调校", "characteristics": {"ac_power_save": False, "fan_limit": "high"}}
    ]
    with open("data/driving_modes.json", "w", encoding="utf-8") as f:
        json.dump({"driving_modes": modes}, f, ensure_ascii=False, indent=2)

    # 生成 zones.json（干扰项）
    zones = [
        {"zone_id": "fl", "name": "左前", "position": "front_left", "seat_type": "heated"},
        {"zone_id": "fr", "name": "右前", "position": "front_right", "seat_type": "ventilated"}
    ]
    with open("data/zones.json", "w", encoding="utf-8") as f:
        json.dump({"zones": zones}, f, ensure_ascii=False, indent=2)

    # 创建 ops/ 目录，并放入一个无关文件作为干扰
    os.makedirs("ops", exist_ok=True)
    with open("ops/irrelevant.log", "w") as f:
        f.write("2025-01-15 08:23: temperature check done\n")

if __name__ == "__main__":
    build_env()
