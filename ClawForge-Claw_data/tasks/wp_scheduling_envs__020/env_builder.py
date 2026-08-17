import os
import json

def build_env():
    # 创建 config 目录
    os.makedirs("config", exist_ok=True)
    
    # 设备列表
    devices = [
        {
            "device_id": "hum-001",
            "device_name": "Bedroom Humidifier",
            "device_type": "humidifier",
            "location": "bedroom",
            "supported_settings": ["power", "humidity_level"],
            "settings": {"power": "on", "humidity_level": 50}
        },
        {
            "device_id": "ac-001",
            "device_name": "Living Room AC",
            "device_type": "ac",
            "location": "living_room",
            "supported_settings": ["power", "temperature", "mode"],
            "settings": {"power": "off", "temperature": 24, "mode": "cool"}
        },
        {
            "device_id": "light-001",
            "device_name": "Kitchen Light",
            "device_type": "light",
            "location": "kitchen",
            "supported_settings": ["power", "brightness"],
            "settings": {"power": "off", "brightness": 100}
        }
    ]
    with open("config/devices.json", "w") as f:
        json.dump({"devices": devices}, f, indent=2)
    
    # 调度列表（包含干扰项）
    schedules = [
        # 正确开启加湿器
        {
            "schedule_id": "sch-001",
            "device_id": "hum-001",
            "action": "turn_on",
            "time": "07:00",
            "days": ["mon","tue","wed","thu","fri","sat","sun"]
        },
        # 错误关闭加湿器（捣乱的调度）
        {
            "schedule_id": "sch-002",
            "device_id": "hum-001",
            "action": "turn_off",
            "time": "08:00",
            "days": ["mon","tue","wed","thu","fri","sat","sun"]
        },
        # 其他设备正常调度
        {
            "schedule_id": "sch-003",
            "device_id": "ac-001",
            "action": "turn_on",
            "time": "09:00",
            "days": ["mon","tue","wed","thu","fri"]
        },
        {
            "schedule_id": "sch-004",
            "device_id": "ac-001",
            "action": "turn_off",
            "time": "22:00",
            "days": ["mon","tue","wed","thu","fri"]
        },
        {
            "schedule_id": "sch-005",
            "device_id": "light-001",
            "action": "turn_on",
            "time": "18:00",
            "days": ["mon","tue","wed","thu","fri","sat","sun"]
        },
        {
            "schedule_id": "sch-006",
            "device_id": "light-001",
            "action": "turn_off",
            "time": "23:00",
            "days": ["mon","tue","wed","thu","fri","sat","sun"]
        },
        # 干扰项1：缺少 device_id 的无效调度
        {
            "schedule_id": "sch-007",
            "action": "turn_off",
            "time": "12:00",
            "days": ["sat","sun"]
        },
        # 干扰项2：重复调度（但动作相同，不影响）
        {
            "schedule_id": "sch-008",
            "device_id": "ac-001",
            "action": "turn_on",
            "time": "09:00",
            "days": ["mon","tue","wed","thu","fri"]
        },
        # 干扰项3：过期时间（但仍然是合法的turn_off，不过不是卧室加湿器）
        {
            "schedule_id": "sch-009",
            "device_id": "light-001",
            "action": "turn_off",
            "time": "00:00",
            "days": ["mon"]
        }
    ]
    with open("config/schedules.json", "w") as f:
        json.dump({"schedules": schedules}, f, indent=2)
    
    # 创建 ops 目录（Agent 会写入结果）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
