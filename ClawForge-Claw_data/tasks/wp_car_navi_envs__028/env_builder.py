import os
import json
import math

def build_env():
    # 创建目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. 最新的区域数据（市中心区域）
    new_regions = {
        "regions": [
            {
                "region_id": "region_center",
                "name": "市中心区域",
                "center": {"lat": 39.908, "lon": 116.397},
                "radius_km": 10,
                "map_version": "2024.06.01"
            }
        ]
    }
    with open("data/regions.json", "w", encoding="utf-8") as f:
        json.dump(new_regions, f, ensure_ascii=False, indent=2)

    # 2. 旧区域数据（干扰项，半径小、中心偏移）
    old_regions = {
        "regions": [
            {
                "region_id": "region_center_old",
                "name": "市中心区域",
                "center": {"lat": 39.92, "lon": 116.38},
                "radius_km": 5,
                "map_version": "2024.05.15"
            },
            {
                "region_id": "region_suburb",
                "name": "郊区扩展区域",
                "center": {"lat": 39.80, "lon": 116.50},
                "radius_km": 8,
                "map_version": "2024.05.15"
            }
        ]
    }
    with open("data/old_regions.json", "w", encoding="utf-8") as f:
        json.dump(old_regions, f, ensure_ascii=False, indent=2)

    # 3. POI 数据（包含充电站和其他类别）
    # 市中心区域内充电站（按距离排序）：
    # ch_001  (39.910, 116.400)  ~0.34km
    # ch_003  (39.915, 116.410)  ~1.20km
    # ch_002  (39.920, 116.390)  ~1.50km
    # ch_004  (39.950, 116.350)  ~5.50km (也在区域内，但较远)
    # 区域外充电站：ch_005, ch_006
    pois = [
        {"poi_id": "ch_001", "name": "天安门充电站", "category": "charging", "lat": 39.910, "lon": 116.400, "address": "东城区东交民巷", "charge_rate_kw": 120},
        {"poi_id": "ch_002", "name": "王府井充电站", "category": "charging", "lat": 39.920, "lon": 116.390, "address": "东城区王府井大街", "charge_rate_kw": 90},
        {"poi_id": "ch_003", "name": "东单充电站", "category": "charging", "lat": 39.915, "lon": 116.410, "address": "东城区东单北大街", "charge_rate_kw": 100},
        {"poi_id": "ch_004", "name": "建国门充电站", "category": "charging", "lat": 39.950, "lon": 116.350, "address": "朝阳区建国门外大街", "charge_rate_kw": 80},
        {"poi_id": "ch_005", "name": "郊区充电站", "category": "charging", "lat": 39.800, "lon": 116.500, "address": "通州区永乐店", "charge_rate_kw": 60},
        {"poi_id": "ch_006", "name": "远郊充电站", "category": "charging", "lat": 40.000, "lon": 116.200, "address": "延庆区康庄镇", "charge_rate_kw": 50},
        # 干扰项：其他类别
        {"poi_id": "food_001", "name": "全聚德烤鸭", "category": "food", "lat": 39.912, "lon": 116.398, "address": "东城区前门大街"},
        {"poi_id": "park_001", "name": "东单停车场", "category": "parking", "lat": 39.913, "lon": 116.399, "address": "东单路口", "hourly_rate": 15},
        {"poi_id": "shop_001", "name": "王府井百货", "category": "shopping", "lat": 39.918, "lon": 116.395, "address": "东城区王府井大街"}
    ]
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump({"pois": pois}, f, ensure_ascii=False, indent=2)

    # 4. 装饰性干扰文件（不影响结果）
    traffic = {
        "road_segments": [
            {"segment_id": "seg_001", "name": "中环路", "condition": "congested", "congestion_level": 8},
            {"segment_id": "seg_002", "name": "外环高速", "condition": "smooth", "congestion_level": 2}
        ]
    }
    with open("data/traffic_data.json", "w", encoding="utf-8") as f:
        json.dump(traffic, f, ensure_ascii=False, indent=2)

    offline_maps = {
        "regions": [
            {"region_id": "region_center", "name": "市中心区域", "center": [116.397, 39.908], "radius_km": 10, "map_version": "2024.06.01"}
        ]
    }
    with open("data/offline_maps.json", "w", encoding="utf-8") as f:
        json.dump(offline_maps, f, ensure_ascii=False, indent=2)

    route_prefs = {
        "preferences": [
            {"preference_id": "pref_01", "name": "最快路线", "description": "优先选择时间最短的路线"},
            {"preference_id": "pref_02", "name": "经济路线", "description": "优先选择能耗最低的路线"}
        ]
    }
    with open("data/route_preferences.json", "w", encoding="utf-8") as f:
        json.dump(route_prefs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
