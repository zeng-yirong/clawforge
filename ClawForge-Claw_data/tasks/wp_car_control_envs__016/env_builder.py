import json
import os

def build_env():
    # 创建主数据目录
    os.makedirs("data", exist_ok=True)
    
    # 空调预设数据，包含干扰项和唯一正确答案
    presets = {
        "presets": [
            {
                "preset_id": "preset_001",
                "name": "制冷",
                "description": "快速制冷模式，保持车内凉爽",
                "default_temperature": 18,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": True,
                "defog_enabled": False,
                "defrost_enabled": False
            },
            {
                "preset_id": "preset_002",
                "name": "制热",
                "description": "快速制热模式，保持车内温暖",
                "default_temperature": 26,
                "fan_speed": "auto",
                "ac_enabled": False,
                "recirculation": True,
                "defog_enabled": True,          # 除雾开启但空调关闭 → 干扰
                "defrost_enabled": False
            },
            {
                "preset_id": "preset_003",
                "name": "自动",
                "description": "自动调节温度和风速",
                "default_temperature": 22,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": False,
                "defrost_enabled": True          # 除霜开启但除雾关闭 → 干扰
            },
            {
                "preset_id": "preset_004",
                "name": "除雾",
                "description": "快速除雾除霜模式",
                "default_temperature": 24,
                "fan_speed": "high",             # ✅ 正确答案：高速
                "ac_enabled": True,
                "recirculation": False,
                "defog_enabled": True,
                "defrost_enabled": False
            },
            {
                "preset_id": "preset_005",
                "name": "节能",
                "description": "节能模式，降低能耗",
                "default_temperature": 20,
                "fan_speed": "auto",
                "ac_enabled": True,
                "recirculation": True,
                "defog_enabled": False,
                "defrost_enabled": False
            },
            {
                "preset_id": "preset_006",
                "name": "运动",
                "description": "运动模式，提供最佳动力响应",
                "default_temperature": 16,
                "fan_speed": "high",
                "ac_enabled": False,
                "recirculation": False,
                "defog_enabled": False,
                "defrost_enabled": True
            }
        ]
    }
    with open("data/ac_presets.json", "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)
    
    # 创建干扰用 ambient_lights.json（agent 不需要碰）
    ambient_lights = {
        "ambient_lights": [
            {"color_id": "off", "name": "关闭", "hex_color": "#000000", "effect": "氛围灯关闭"},
            {"color_id": "orange", "name": "橙色", "hex_color": "#FF9933", "effect": "温暖活力"},
            {"color_id": "white", "name": "白色", "hex_color": "#FFFFFF", "effect": "简约明亮"}
        ]
    }
    with open("data/ambient_lights.json", "w", encoding="utf-8") as f:
        json.dump(ambient_lights, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
