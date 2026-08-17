import os
import json
import random

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)  # 干扰目录

    # ---- 干扰文件：regions.json ----
    regions = {"regions": [
        {"region_id": "reg_01", "name": "北京市中心", "center": {"lat": 39.9042, "lon": 116.4074}, "radius_km": 30},
        {"region_id": "reg_02", "name": "朝阳区", "center": {"lat": 39.9215, "lon": 116.4433}, "radius_km": 20},
        {"region_id": "reg_03", "name": "海淀区", "center": {"lat": 39.9560, "lon": 116.3100}, "radius_km": 25}
    ]}
    with open("data/regions.json", "w", encoding="utf-8") as f:
        json.dump(regions, f, ensure_ascii=False, indent=2)

    # ---- 干扰文件：traffic_data.json ----
    traffic = {"road_segments": [
        {"segment_id": "seg_01", "name": "中环路", "condition": "congested", "congestion_level": 8},
        {"segment_id": "seg_02", "name": "外环高速", "condition": "smooth", "congestion_level": 2},
        {"segment_id": "seg_03", "name": "延安高架路", "condition": "slow", "congestion_level": 5}
    ]}
    with open("data/traffic_data.json", "w", encoding="utf-8") as f:
        json.dump(traffic, f, ensure_ascii=False, indent=2)

    # ---- 干扰文件：route_preferences.json ----
    prefs = {"preferences": [
        {"preference_id": "pref_01", "name": "最快路线", "description": "优先选择时间最短的路线"},
        {"preference_id": "pref_02", "name": "最短路线", "description": "优先选择距离最短的路线"},
        {"preference_id": "pref_03", "name": "避开拥堵", "description": "优先选择交通畅通的路线"}
    ]}
    with open("data/route_preferences.json", "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)

    # ---- 干扰目录及文件：logs/ 下的假日志 ----
    with open("logs/operation.log", "w") as f:
        f.write("2025-02-10 14:23:01 [INFO] Session navi-abc123 started\n")
        f.write("2025-02-10 14:23:15 [ERROR] Waypoint validation failed for poi-003\n")

    # ---- 核心数据：pois.json ----
    pois = {"pois": [
        # 正常干扰 POI（大量）
        {"poi_id": "poi_d01", "name": "正阳门充电站", "category": "charging", "lat": 39.895, "lon": 116.391, "address": "东城区前门大街1号", "charge_rate_kw": 120},
        {"poi_id": "poi_d02", "name": "国贸充电站", "category": "charging", "lat": 39.908, "lon": 116.460, "address": "朝阳区建国门外大街1号", "charge_rate_kw": 150},
        {"poi_id": "poi_d03", "name": "老北京炸酱面馆（分店）", "category": "food", "lat": 39.928, "lon": 116.418, "address": "西城区什刹海胡同5号"},
        {"poi_id": "poi_d04", "name": "天坛公园南门小吃", "category": "food", "lat": 39.882, "lon": 116.406, "address": "东城区天坛路1号"},
        {"poi_id": "poi_d05", "name": "故宫博物院", "category": "attraction", "lat": 39.916, "lon": 116.397, "address": "东城区景山前街4号"},
        {"poi_id": "poi_d06", "name": "颐和园", "category": "attraction", "lat": 39.999, "lon": 116.275, "address": "海淀区新建宫门路19号"},
        # 用户提到的三个途径点
        {"poi_id": "poi-001", "name": "快充站", "category": "charging", "lat": 39.920, "lon": 116.445, "address": "朝阳区望京西路8号", "charge_rate_kw": 200},
        {"poi_id": "poi-002", "name": "老北京炸酱面", "category": "food", "lat": 39.934, "lon": 116.402, "address": "东城区南锣鼓巷99号"},
        # 异常点：address 为空字符串
        {"poi_id": "poi-003", "name": "天坛", "category": "attraction", "lat": 39.882, "lon": 116.407, "address": ""},
        # 干扰：另一个 address 为空但用户没提
        {"poi_id": "poi_d07", "name": "无名荒地", "category": "parking", "lat": 39.850, "lon": 116.350, "address": ""}
    ]}
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)

    # 额外：创建一个空的 ops/ 下文件作为干扰（但 agent 应写入新的）
    with open("ops/old_fix.json", "w") as f:
        f.write('{"old_id": "poi_d01"}\n')

if __name__ == "__main__":
    build_env()
