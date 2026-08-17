import json
import os
import math

def build_env():
    # 创建数据目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 预创建目录，但让agent覆盖文件（也可不预创建，但为使目录存在更合理，这里创建空目录）
    
    # 1. POI 数据（含干扰项：重复、充电速率不足、其他类别）
    pois = {
        "pois": [
            # 充电站（含充电速率）
            {"poi_id": "ch_001", "name": "超充站-A", "category": "charging", "lat": 31.21, "lon": 121.51, "address": "外环路1号", "charge_rate_kw": 120, "hourly_rate": 15},
            # 重复条目（相同poi_id，故意不同name）
            {"poi_id": "ch_001", "name": "超充站-1号", "category": "charging", "lat": 31.21, "lon": 121.51, "address": "外环路1号", "charge_rate_kw": 120, "hourly_rate": 15},
            {"poi_id": "ch_002", "name": "城东充电站", "category": "charging", "lat": 31.20, "lon": 121.52, "address": "城东路8号", "charge_rate_kw": 90, "hourly_rate": 10},
            {"poi_id": "ch_003", "name": "南郊快充", "category": "charging", "lat": 31.19, "lon": 121.48, "address": "南郊路12号", "charge_rate_kw": 100, "hourly_rate": 12},
            {"poi_id": "ch_004", "name": "滨江充电站", "category": "charging", "lat": 31.22, "lon": 121.53, "address": "滨江大道20号", "charge_rate_kw": 80, "hourly_rate": 8},
            {"poi_id": "ch_005", "name": "远郊电站", "category": "charging", "lat": 31.15, "lon": 121.45, "address": "远郊路99号", "charge_rate_kw": 60, "hourly_rate": 5},
            # 充电速率不足50的诱饵
            {"poi_id": "ch_006", "name": "老旧充电桩", "category": "charging", "lat": 31.25, "lon": 121.50, "address": "老街1号", "charge_rate_kw": 45, "hourly_rate": 2},
            # 其他类别POI（干扰）
            {"poi_id": "fd_001", "name": "老上海餐厅", "category": "food", "lat": 31.23, "lon": 121.49, "address": "南京路100号"},
            {"poi_id": "at_001", "name": "东方明珠", "category": "attraction", "lat": 31.24, "lon": 121.50, "address": "浦东新区世纪大道1号"},
        ]
    }
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)

    # 2. 交通数据（实时路况）
    traffic = {
        "road_segments": [
            {"segment_id": "seg_001", "name": "外环高速", "condition": "slow", "congestion_level": 3},
            {"segment_id": "seg_002", "name": "延安高架路", "condition": "congested", "congestion_level": 5}
        ]
    }
    with open("data/traffic_data.json", "w", encoding="utf-8") as f:
        json.dump(traffic, f, ensure_ascii=False, indent=2)

    # 3. 干扰性数据文件（region, route_preferences等）
    regions = {
        "regions": [
            {"region_id": "reg_001", "name": "上海市中心", "center": {"lat": 31.23, "lon": 121.47}, "radius_km": 10},
            {"region_id": "reg_002", "name": "浦东新区", "center": {"lat": 31.25, "lon": 121.54}, "radius_km": 8}
        ]
    }
    with open("data/regions.json", "w", encoding="utf-8") as f:
        json.dump(regions, f, ensure_ascii=False, indent=2)

    route_prefs = {
        "preferences": [
            {"preference_id": "pref_001", "name": "最快路线", "description": "优先选择时间最短的路线"},
            {"preference_id": "pref_002", "name": "避开拥堵", "description": "优先选择交通畅通的路线"}
        ]
    }
    with open("data/route_preferences.json", "w", encoding="utf-8") as f:
        json.dump(route_prefs, f, ensure_ascii=False, indent=2)

    # 4. 离线地图（只作背景）
    offline_maps = {
        "regions": [
            {"region_id": "map_001", "name": "市中心区域", "center": {"lat": 31.23, "lon": 121.47}, "radius_km": 5, "map_version": "2024.05.15"},
            {"region_id": "map_002", "name": "机场区域", "center": {"lat": 31.14, "lon": 121.80}, "radius_km": 8, "map_version": "2024.06.01"}
        ]
    }
    with open("data/offline_maps.json", "w", encoding="utf-8") as f:
        json.dump(offline_maps, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
