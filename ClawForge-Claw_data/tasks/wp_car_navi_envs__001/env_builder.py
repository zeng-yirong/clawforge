import os
import json

def build_env():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # ---- offline_maps.json (contains map versions and region definitions) ----
    offline_maps = {
        "regions": [
            {
                "region_id": "region_center",
                "name": "市中心区域",
                "center": {"lat": 39.9042, "lon": 116.4074},
                "radius_km": 10,
                "map_version": "2024.06.01"   # latest
            },
            {
                "region_id": "region_airport",
                "name": "机场区域",
                "center": {"lat": 40.0799, "lon": 116.6031},
                "radius_km": 8,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "region_suburb",
                "name": "郊区扩展区域",
                "center": {"lat": 39.8, "lon": 116.4},
                "radius_km": 15,
                "map_version": "2024.05.15"   # outdated version
            }
        ]
    }
    with open("data/offline_maps.json", "w", encoding="utf-8") as f:
        json.dump(offline_maps, f, indent=2, ensure_ascii=False)

    # ---- pois.json (contains many POIs with distractors) ----
    pois = {
        "pois": [
            # Valid waypoints (in region_center, latest map version)
            {
                "poi_id": "food-001",
                "name": "老北京炸酱面馆",
                "category": "food",
                "lat": 39.905,
                "lon": 116.41,
                "address": "北京市东城区前门大街1号",
                "region_id": "region_center"
            },
            {
                "poi_id": "chrg-001",
                "name": "超充站A",
                "category": "charging",
                "lat": 39.908,
                "lon": 116.42,
                "address": "北京市东城区建国门内大街10号",
                "charge_rate_kw": 150,
                "region_id": "region_center"
            },
            {
                "poi_id": "hotel-001",
                "name": "如家快捷酒店",
                "category": "hotel",
                "lat": 39.902,
                "lon": 116.39,
                "address": "北京市西城区金融街5号",
                "hourly_rate": 180,
                "region_id": "region_center"
            },
            # Distractors: same category but wrong region or wrong version
            {
                "poi_id": "food-002",
                "name": "机场快餐",
                "category": "food",
                "lat": 40.08,
                "lon": 116.60,
                "address": "首都机场T3航站楼",
                "region_id": "region_airport"
            },
            {
                "poi_id": "chrg-002",
                "name": "慢充站B",
                "category": "charging",
                "lat": 39.80,
                "lon": 116.45,
                "address": "北京市大兴区黄村",
                "charge_rate_kw": 60,
                "region_id": "region_center"
            },
            {
                "poi_id": "hotel-002",
                "name": "五星级大酒店",
                "category": "hotel",
                "lat": 39.91,
                "lon": 116.38,
                "address": "北京市东城区王府井大街",
                "hourly_rate": 500,
                "region_id": "region_center"
            },
            # Distractor: outdated version (map_version == 2024.05.15) but in region_center
            {
                "poi_id": "food-003",
                "name": "老店炸酱面（旧版）",
                "category": "food",
                "lat": 39.904,
                "lon": 116.408,
                "address": "北京市东城区前门大街2号",
                "region_id": "region_center"
            },
            {
                "poi_id": "chrg-003",
                "name": "旧充电站",
                "category": "charging",
                "lat": 39.909,
                "lon": 116.419,
                "address": "旧地址",
                "charge_rate_kw": 150,
                "region_id": "region_center"
            },
            {
                "poi_id": "hotel-003",
                "name": "旧经济旅馆",
                "category": "hotel",
                "lat": 39.903,
                "lon": 116.395,
                "address": "旧地址",
                "hourly_rate": 180,
                "region_id": "region_center"
            }
        ]
    }
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump(pois, f, indent=2, ensure_ascii=False)

    # ---- regions.json (separate file, but might be redundant; used for some queries) ----
    regions = {
        "regions": [
            {
                "region_id": "region_center",
                "name": "北京市中心",
                "center": {"lat": 39.9042, "lon": 116.4074},
                "radius_km": 10
            },
            {
                "region_id": "region_airport",
                "name": "朝阳区",
                "center": {"lat": 40.0799, "lon": 116.6031},
                "radius_km": 8
            },
            {
                "region_id": "region_suburb",
                "name": "海淀区",
                "center": {"lat": 39.8, "lon": 116.4},
                "radius_km": 15
            }
        ]
    }
    with open("data/regions.json", "w", encoding="utf-8") as f:
        json.dump(regions, f, indent=2, ensure_ascii=False)

    # ---- route_preferences.json (irrelevant, just for world consistency) ----
    prefs = {
        "preferences": [
            {"preference_id": "pref-001", "name": "最快路线", "description": "优先选择时间最短的路线"},
            {"preference_id": "pref-002", "name": "最短路线", "description": "优先选择距离最短的路线"},
            {"preference_id": "pref-003", "name": "经济路线", "description": "优先选择能耗最低的路线"}
        ]
    }
    with open("data/route_preferences.json", "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2, ensure_ascii=False)

    # ---- traffic_data.json (irrelevant, but present as distractor) ----
    traffic = {
        "road_segments": [
            {"segment_id": "seg-001", "name": "中环路", "condition": "congested", "congestion_level": 8},
            {"segment_id": "seg-002", "name": "外环高速", "condition": "smooth", "congestion_level": 2}
        ]
    }
    with open("data/traffic_data.json", "w", encoding="utf-8") as f:
        json.dump(traffic, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    build_env()
