import os
import json
import random
import math

BASE = "."
DATA_DIR = os.path.join(BASE, "data")
SENSORS_DIR = os.path.join(DATA_DIR, "sensors")
LOCATIONS_DIR = os.path.join(DATA_DIR, "locations")
OPS_DIR = os.path.join(BASE, "ops")
DUMP_DIR = os.path.join(BASE, "db_dumps")

def build_env():
    # 创建目录结构
    for d in [DATA_DIR, SENSORS_DIR, LOCATIONS_DIR, OPS_DIR, DUMP_DIR]:
        os.makedirs(d, exist_ok=True)

    # 定义 accounts（简单写，作为干扰项）
    accounts = [
        {"account_id": "acc_001", "account_name": "Main Office", "location": "NYC",
         "sensors": ["sensor_temp_01", "sensor_temp_02", "sensor_hum_01"],
         "locations": ["loc_server", "loc_lobby"], "notification_contacts": ["alice@co.com"]},
        {"account_id": "acc_002", "account_name": "Warehouse", "location": "NJ",
         "sensors": ["sensor_temp_03", "sensor_energy_01"],
         "locations": ["loc_wh"], "notification_contacts": ["bob@co.com"]}
    ]
    with open(os.path.join(DATA_DIR, "accounts.json"), "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 定义 locations
    locations = [
        {"location_id": "loc_server", "location_name": "Server Room", "floor": 2,
         "sensors": ["sensor_temp_01", "sensor_temp_02", "sensor_hum_01"]},
        {"location_id": "loc_lobby", "location_name": "Main Lobby", "floor": 1,
         "sensors": ["sensor_temp_03"]},
        {"location_id": "loc_wh", "location_name": "Warehouse", "floor": 0,
         "sensors": ["sensor_energy_01"]}
    ]
    with open(os.path.join(LOCATIONS_DIR, "locations.json"), "w") as f:
        json.dump({"locations": locations}, f, indent=2)

    # 定义 sensors（关键数据，包含干扰和脏数据）
    sensors = [
        # 正确格式：正常 active 且超标（目标）
        {"sensor_id": "sensor_temp_01", "sensor_name": "Server Rack A Top",
         "sensor_type": "temperature", "location_id": "loc_server",
         "unit": "celsius", "threshold_low": 15.0, "threshold_high": 28.0,
         "current_value": 34.5, "status": "active"},

        # active 但未超标（不应包含）
        {"sensor_id": "sensor_temp_02", "sensor_name": "Server Rack B Mid",
         "sensor_type": "temperature", "location_id": "loc_server",
         "unit": "celsius", "threshold_low": 15.0, "threshold_high": 30.0,
         "current_value": 27.2, "status": "active"},

        # inactive 但超标（不应包含）
        {"sensor_id": "sensor_temp_03", "sensor_name": "Warehouse Temp",
         "sensor_type": "temperature", "location_id": "loc_wh",
         "unit": "celsius", "threshold_low": 5.0, "threshold_high": 25.0,
         "current_value": 33.8, "status": "inactive"},

        # active 湿度传感器，阈值不同但未超标（不应包含）
        {"sensor_id": "sensor_hum_01", "sensor_name": "Server Room Humidity",
         "sensor_type": "humidity", "location_id": "loc_server",
         "unit": "percent", "threshold_low": 30.0, "threshold_high": 70.0,
         "current_value": 45.0, "status": "active"},

        # active 能量传感器，超标（应包含？注意目标是温度告警，但prompt没有限制sensor_type，只说所有活跃且超阈值的传感器）
        # 根据业务上下文“机房温度告警”，但工程师指令是“所有活跃且读数超过高限阈值”，所以不应限制类型
        # 这个能量传感器 active 且 current_value=95 超过 threshold_high=80，应包含
        {"sensor_id": "sensor_energy_01", "sensor_name": "UPS Power",
         "sensor_type": "energy", "location_id": "loc_wh",
         "unit": "kwh", "threshold_low": 0.0, "threshold_high": 80.0,
         "current_value": 95.2, "status": "active"},

        # 故意引入缺失字段的脏数据（不应被解析）
        {"sensor_id": "sensor_bad_01", "sensor_name": "Broken Sensor",
         "sensor_type": "temperature", "location_id": "loc_lobby",
         "unit": "celsius", "threshold_low": 10.0, "threshold_high": None,
         "current_value": 40.0, "status": "active"},

        # 非 JSON 行的文本干扰（在同一个文件中插入非标准行？但 JSON 文件标准要求全部是JSON，不能混行。
        # 我们可以在 sensors.json 中加入一个额外的非标准条目，比如用字符串代替对象？会导致 json.load 失败。
        # 更好的办法：再生成一个同名的旧版本文件作为诱饵，但 prompt 明确说数据在 data/sensors/sensors.json
        # 我们可以在 data/sensors/ 里放一个旧版本 sensors_backup.json 干扰，但主要文件是 sensors.json。
        # 为了增加难度，我们在 sensors.json 中故意加入一个字段名拼写错误：thresh_high 而非 threshold_high
        # 但这样会导致无法正确识别阈值，agent 需要处理异常。下面我们加一个具有错误字段的传感器：
        {"sensor_id": "sensor_temp_04", "sensor_name": "Rack C Bottom",
         "sensor_type": "temperature", "location_id": "loc_server",
         "unit": "celsius", "thresh_low": 15.0, "thresh_high": 28.0,
         "current_value": 36.1, "status": "active"},

        # 另外正常但无status字段（缺失关键字段）
        {"sensor_id": "sensor_hum_02", "sensor_name": "Lobby Humidity",
         "sensor_type": "humidity", "location_id": "loc_lobby",
         "unit": "percent", "threshold_low": 20.0, "threshold_high": 80.0,
         "current_value": 85.3}
    ]

    with open(os.path.join(SENSORS_DIR, "sensors.json"), "w") as f:
        json.dump({"sensors": sensors}, f, indent=2)

    # 创建一些额外的干扰文件
    # 旧版本备份
    old_sensors = [
        {"sensor_id": "sensor_temp_01", "sensor_name": "Server Rack A Top",
         "sensor_type": "temperature", "location_id": "loc_server",
         "unit": "celsius", "threshold_low": 15.0, "threshold_high": 28.0,
         "current_value": 22.0, "status": "active"}
    ]
    with open(os.path.join(SENSORS_DIR, "sensors_backup.json"), "w") as f:
        json.dump({"sensors": old_sensors}, f, indent=2)

    # 在 ops 目录放一个空文件作为诱饵
    open(os.path.join(OPS_DIR, ".gitkeep"), "w").close()

    # 在 db_dumps 放一些无关文件
    with open(os.path.join(DUMP_DIR, "slow_query.log"), "w") as f:
        f.write("# nothing here\n")

    # 确保 ops/alarm_sensors.json 不存在（初始状态）
    alarm_path = os.path.join(OPS_DIR, "alarm_sensors.json")
    if os.path.exists(alarm_path):
        os.remove(alarm_path)

if __name__ == "__main__":
    build_env()
