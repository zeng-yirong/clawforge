import os
import json
import csv
import random

def build_env():
    # 创建目录结构
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 1. 有效 POI 数据库 (data/pois.json)
    pois = [
        {"poi_id": "poi_001", "name": "望京SOHO", "category": "attraction", "lat": 39.980, "lon": 116.480, "address": "北京市朝阳区望京东园四区11号楼"},
        {"poi_id": "poi_002", "name": "雁栖湖", "category": "attraction", "lat": 40.350, "lon": 116.630, "address": "北京市怀柔区雁水路3号"},
        {"poi_id": "poi_004", "name": "古北水镇", "category": "attraction", "lat": 40.640, "lon": 117.200, "address": "北京市密云区古北口镇"},
        {"poi_id": "poi_007", "name": "八达岭长城", "category": "attraction", "lat": 40.350, "lon": 116.020, "address": "北京市延庆区G6京藏高速58号"},
        {"poi_id": "poi_009", "name": "颐和园", "category": "attraction", "lat": 39.990, "lon": 116.270, "address": "北京市海淀区新建宫门路19号"}
    ]
    with open("data/pois.json", "w") as f:
        json.dump({"pois": pois}, f, indent=2)

    # 2. 原始途经点记录 (ops/waypoints_log.csv) 包含有效和无效ID
    waypoints = [
        "poi_001",
        "poi_002",
        "poi_003",   # 无效
        "poi_004",
        "poi_005",   # 无效
        "poi_006",   # 无效
        "poi_007"
    ]
    with open("ops/waypoints_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["poi_id"])
        for wp in waypoints:
            writer.writerow([wp])

    # 3. 干扰文件：过期的POI备份
    old_pois = [
        {"poi_id": "poi_001", "name": "望京SOHO(旧)", "category": "attraction"},
        {"poi_id": "poi_010", "name": "旧版无效POI", "category": "food"}
    ]
    with open("data/pois_backup.json", "w") as f:
        json.dump({"pois": old_pois}, f, indent=2)

    # 4. 额外干扰日志文件
    with open("logs/navigation_20250320.txt", "w") as f:
        f.write("Route: 京郊一日游\n")
        f.write("Waypoints: poi_001, poi_002, poi_003, poi_004, poi_005\n")
    with open("logs/errors.log", "w") as f:
        f.write("2025-03-20 14:22: ERROR - poi_003 not found\n")

    # 5. 无关的区域数据（用于迷惑）
    regions = {"regions": [
        {"region_id": "R1", "name": "京北区", "center": {"lat": 40.2, "lon": 116.4}, "radius_km": 50}
    ]}
    with open("data/regions.json", "w") as f:
        json.dump(regions, f, indent=2)

if __name__ == "__main__":
    build_env()
