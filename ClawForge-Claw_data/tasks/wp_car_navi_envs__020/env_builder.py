import json
import os
import random
import shutil
from datetime import datetime

def build_env():
    # 清理并创建初始目录
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("backup"):
        shutil.rmtree("backup")
    if os.path.exists("logs"):
        shutil.rmtree("logs")
    if os.path.exists("route"):
        shutil.rmtree("route")

    os.makedirs("data")
    os.makedirs("backup")
    os.makedirs("logs")

    # ----- 核心POI数据（包含干扰项和脏数据） -----
    pois = [
        # 正确的充电站A (version 2，营业)
        {"poi_id": "CHG-001", "name": "超充站A", "category": "charging", "lat": 39.9, "lon": 116.4, "open": True, "version": 2},
        # 旧版本充电站A (version 1，关闭) —— 干扰（重复ID）
        {"poi_id": "CHG-001", "name": "超充站A(旧)", "category": "charging", "lat": 39.9, "lon": 116.4, "open": False, "version": 1},
        # 正确的充电站B (version 2，营业)
        {"poi_id": "CHG-002", "name": "超充站B", "category": "charging", "lat": 39.8, "lon": 116.5, "open": True, "version": 2},
        # 另一个充电站 (营业，但多了一个，顺序不对，agent不能选3个充电站)
        {"poi_id": "CHG-003", "name": "超充站C", "category": "charging", "lat": 39.7, "lon": 116.6, "open": True, "version": 2},
        # 关闭的充电站 (干扰)
        {"poi_id": "CHG-004", "name": "坏掉的充电站", "category": "charging", "lat": 39.95, "lon": 116.35, "open": False, "version": 2},
        # 正确的餐厅 (version 2，营业)
        {"poi_id": "FOO-001", "name": "麦当劳", "category": "food", "lat": 39.85, "lon": 116.45, "open": True, "version": 2},
        # 旧版本餐厅 (version 1，营业但版本低) —— 干扰
        {"poi_id": "FOO-001", "name": "麦当劳旧址", "category": "food", "lat": 39.85, "lon": 116.45, "open": True, "version": 1},
        # 另一个餐厅 (营业，但只能选一个)
        {"poi_id": "FOO-002", "name": "肯德基", "category": "food", "lat": 39.88, "lon": 116.42, "open": True, "version": 2},
        # 坐标异常的餐厅 (经度 > 180) —— 脏数据，需忽略
        {"poi_id": "FOO-003", "name": "幽灵餐厅", "category": "food", "lat": 39.9, "lon": 200.0, "open": True, "version": 2},
        # 坐标异常的充电站 (纬度 > 90) —— 脏数据
        {"poi_id": "CHG-005", "name": "太空充电站", "category": "charging", "lat": 100.0, "lon": 116.0, "open": True, "version": 2},
        # 其他类别干扰 (attraction, shopping等)
        {"poi_id": "ATTR-001", "name": "故宫", "category": "attraction", "lat": 39.92, "lon": 116.39, "open": True, "version": 2},
        {"poi_id": "SHOP-001", "name": "商场", "category": "shopping", "lat": 39.87, "lon": 116.43, "open": True, "version": 2},
        # 缺少关键字段的脏数据 (无poi_id)
        {"name": "缺失ID", "category": "food", "lat": 39.8, "lon": 116.4, "open": True, "version": 1},
        # open字段缺失
        {"poi_id": "CHG-006", "name": "未知状态", "category": "charging", "lat": 39.7, "lon": 116.5, "version": 2},
    ]
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump({"pois": pois}, f, ensure_ascii=False, indent=2)

    # ----- 其他干扰数据文件 -----
    # 备份目录：旧版本完整备份（仅用于迷惑）
    backup_pois = [
        {"poi_id": "CHG-001", "name": "超充站A(backup)", "category": "charging", "lat": 39.9, "lon": 116.4, "open": False, "version": 1},
        {"poi_id": "FOO-001", "name": "麦当劳(backup)", "category": "food", "lat": 39.85, "lon": 116.45, "open": False, "version": 1},
    ]
    with open("backup/pois_backup.json", "w", encoding="utf-8") as f:
        json.dump({"pois": backup_pois}, f, ensure_ascii=False, indent=2)

    # 日志文件（内容无关）
    log_lines = [
        "2025-04-01 08:00:00 INFO Data loaded from pois.json",
        "2025-04-01 08:01:00 WARN Found duplicate poi_id: CHG-001, keeping latest version",
        "2025-04-01 08:02:00 ERROR Invalid coordinate detected for FOO-003",
    ]
    with open("logs/poi_audit.log", "w") as f:
        f.write("\n".join(log_lines))

    # 区域数据（无关）
    regions = [
        {"region_id": "R01", "name": "北京市中心", "center": {"lat": 39.9, "lon": 116.4}, "radius_km": 10},
        {"region_id": "R02", "name": "朝阳区", "center": {"lat": 39.92, "lon": 116.46}, "radius_km": 15},
    ]
    with open("data/regions.json", "w", encoding="utf-8") as f:
        json.dump({"regions": regions}, f, ensure_ascii=False, indent=2)

    # 路线偏好（无关）
    prefs = [
        {"preference_id": "P1", "name": "最快路线", "description": "优先选择时间最短的路线"},
        {"preference_id": "P2", "name": "避开拥堵", "description": "优先选择交通畅通的路线"},
    ]
    with open("data/route_preferences.json", "w", encoding="utf-8") as f:
        json.dump({"preferences": prefs}, f, ensure_ascii=False, indent=2)

    # 放置一个README说明任务背景（仅供agent参考，不强制）
    readme = """# 车载导航规划任务
请参考 data/pois.json 中的POI列表，按要求整理出途径点列表并写入 route/waypoints.json。
"""
    with open("README.txt", "w") as f:
        f.write(readme)

    print("Environment built successfully. Files: data/pois.json, data/regions.json, data/route_preferences.json, backup/pois_backup.json, logs/poi_audit.log, README.txt")

if __name__ == "__main__":
    build_env()
