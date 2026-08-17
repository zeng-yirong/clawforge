import json
import os

def build_env():
    # 创建数据目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 空目录，agent 会写入结果

    # 1. regions.json
    regions = {
        "regions": [
            {
                "region_id": "downtown",
                "name": "市中心区域",
                "center": {"lat": 39.9042, "lon": 116.4074},
                "radius_km": 5,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "airport",
                "name": "机场区域",
                "center": {"lat": 40.0799, "lon": 116.6031},
                "radius_km": 10,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "suburb",
                "name": "郊区扩展区域",
                "center": {"lat": 39.7, "lon": 116.2},
                "radius_km": 8,
                "map_version": "2024.05.15"   # 旧版本干扰
            }
        ]
    }
    with open("data/regions.json", "w") as f:
        json.dump(regions, f, ensure_ascii=False, indent=2)

    # 2. pois.json  (含干扰项)
    pois = {
        "pois": [
            {
                "poi_id": "charge_fast",
                "name": "超级充电站",
                "category": "charging",
                "lat": 39.95, "lon": 116.5,
                "address": "市中心东侧",
                "charge_rate_kw": 100
            },
            {
                "poi_id": "charge_slow",
                "name": "慢充站",
                "category": "charging",
                "lat": 39.92, "lon": 116.45,
                "address": "市中心西侧",
                "charge_rate_kw": 30      # 速率低，不应选用
            },
            {
                "poi_id": "food_mcd",
                "name": "麦当劳（朝阳店）",
                "category": "food",
                "lat": 39.94, "lon": 116.48,
                "address": "朝阳区"
            },
            {
                "poi_id": "food_kfc",
                "name": "肯德基",
                "category": "food",
                "lat": 39.93, "lon": 116.47,
                "address": "朝阳区"
            },
            {
                "poi_id": "airport_dest",
                "name": "首都机场T3",
                "category": "attraction",
                "lat": 40.08, "lon": 116.59,
                "address": "机场区域"
            },
            {
                "poi_id": "parking_lot",
                "name": "停车场A",
                "category": "parking",
                "lat": 39.9, "lon": 116.4,
                "address": "某地"
            }
        ]
    }
    with open("data/pois.json", "w") as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)

    # 3. route_preferences.json (干扰多个)
    prefs = {
        "preferences": [
            {"preference_id": "fastest", "name": "最快路线", "description": "优先选择时间最短的路线"},
            {"preference_id": "shortest", "name": "最短路线", "description": "优先选择距离最短的路线"},
            {"preference_id": "avoid_congestion", "name": "避开拥堵", "description": "优先选择交通畅通的路线"},
            {"preference_id": "eco", "name": "经济路线", "description": "优先选择能耗最低的路线"}
        ]
    }
    with open("data/route_preferences.json", "w") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)

    # 4. traffic_data.json (纯干扰，不做使用)
    traffic = {
        "road_segments": [
            {"segment_id": "s1", "name": "中环路", "condition": "congested", "congestion_level": 8},
            {"segment_id": "s2", "name": "外环高速", "condition": "slow", "congestion_level": 5},
            {"segment_id": "s3", "name": "延安高架路", "condition": "smooth", "congestion_level": 2}
        ]
    }
    with open("data/traffic_data.json", "w") as f:
        json.dump(traffic, f, ensure_ascii=False, indent=2)

    # 5. 空 ops 目录 (agent 将写入结果)

if __name__ == "__main__":
    build_env()
