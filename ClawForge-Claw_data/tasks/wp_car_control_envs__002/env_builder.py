import os
import json

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("sensors", exist_ok=True)
    os.makedirs("status", exist_ok=True)

    # ---------- 真正的 AC 预设 ----------
    presets = [
        {
            "preset_id": "cool_001",
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
            "preset_id": "heat_001",
            "name": "制热",
            "description": "快速制热模式，保持车内温暖",
            "default_temperature": 26,
            "fan_speed": "high",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "auto_001",
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
            "preset_id": "eco_001",
            "name": "节能",
            "description": "节能模式，降低能耗",
            "default_temperature": 25,
            "fan_speed": "auto",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "sport_001",
            "name": "运动",
            "description": "运动模式，提供最佳动力响应",
            "default_temperature": 20,
            "fan_speed": "high",
            "ac_enabled": True,
            "recirculation": True,
            "defog_enabled": False,
            "defrost_enabled": False
        },
        {
            "preset_id": "defog_001",
            "name": "除雾",
            "description": "快速除雾除霜模式",
            "default_temperature": 22,
            "fan_speed": "auto",
            "ac_enabled": True,
            "recirculation": False,
            "defog_enabled": True,
            "defrost_enabled": True
        }
    ]
    with open("data/ac_presets.json", "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)

    # ---------- 干扰文件（备份，但除雾的风扇速度为 high，且缺少 defrost_enabled） ----------
    backup_presets = [
        {
            "preset_id": "cool_backup",
            "name": "制冷",
            "description": "快速制冷",
            "default_temperature": 21,
            "fan_speed": "high",
            "ac_enabled": True,
            "recirculation": True
        },
        {
            "preset_id": "defog_backup",
            "name": "除雾",
            "description": "快速除雾",
            "default_temperature": 20,
            "fan_speed": "high",               # 故意不同
            "ac_enabled": True,
            "recirculation": False,
            "defog_enabled": True
            # 缺少 defrost_enabled
        }
    ]
    with open("data/ac_presets_backup.json", "w", encoding="utf-8") as f:
        json.dump(backup_presets, f, ensure_ascii=False, indent=2)

    # 另一个干扰：旧版设置（格式完全不同）
    with open("data/ac_settings_old.json", "w", encoding="utf-8") as f:
        json.dump({"mode": "comfort", "temp": 24}, f, ensure_ascii=False, indent=2)

    # ---------- 传感器数据 ----------
    with open("sensors/env_temp.txt", "w") as f:
        f.write("8\n")   # 低温

    # 干扰传感器
    with open("sensors/humidity.txt", "w") as f:
        f.write("85%\n")

    # ---------- 维修日志 ----------
    log_content = (
        "车辆保养记录（2025-02-10）\n"
        "问题：空调风扇时转时不转\n"
        "排查：传感器正常，初步判断为控制逻辑异常\n"
        "建议：低温高湿时使用除雾预设（风扇自动）\n"
        "下次保养：2025-05-10\n"
    )
    with open("maintenance_log.txt", "w", encoding="utf-8") as f:
        f.write(log_content)

    # ---------- 其他无关文件 ----------
    with open("status/range.json", "w") as f:
        json.dump({"remaining_km": 320}, f)
    with open("status/energy.csv", "w") as f:
        f.write("time,consumption\n00:00,12.5\n00:10,13.0\n")

    # 注意：不预先创建 ops/ 目录，让 Agent 自己创建
