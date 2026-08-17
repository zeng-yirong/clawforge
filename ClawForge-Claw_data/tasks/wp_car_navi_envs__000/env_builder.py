import os
import json

def build_env():
    # 创建 data 目录
    os.makedirs("data", exist_ok=True)
    # 创建 ops 目录（验证时需要，但 agent 需要自己写入）
    os.makedirs("ops", exist_ok=True)

    # ========== 离线地图数据 ==========
    offline_maps = {
        "regions": [
            {
                "region_id": "region_001",
                "name": "北京市中心",
                "center": {"lat": 39.905, "lon": 116.397},
                "radius_km": 10,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "region_002",
                "name": "朝阳区",
                "center": {"lat": 39.921, "lon": 116.443},
                "radius_km": 8,
                "map_version": "2024.05.15"
            },
            {
                "region_id": "region_003",
                "name": "海淀区",
                "center": {"lat": 39.959, "lon": 116.298},
                "radius_km": 12,
                "map_version": "2024.04.20"
            }
        ]
    }
    with open("data/offline_maps.json", "w", encoding="utf-8") as f:
        json.dump(offline_maps, f, ensure_ascii=False, indent=2)

    # ========== POI 数据（包含干扰项） ==========
    pois = {
        "pois": [
            # 北京市中心区域的有效 POI
            {
                "poi_id": "poi_001",
                "name": "国贸充电站",
                "category": "charging",
                "address": "北京市中心建国路88号",
                "lat": 39.908,
                "lon": 116.460,
                "charge_rate_kw": 120,
                "hourly_rate": 15
            },
            {
                "poi_id": "poi_003",
                "name": "老北京炸酱面馆",
                "category": "food",
                "address": "北京市中心王府井大街200号",
                "lat": 39.913,
                "lon": 116.410,
                "hourly_rate": 0
            },
            # 朝阳区干扰项
            {
                "poi_id": "poi_002",
                "name": "朝阳充电站",
                "category": "charging",
                "address": "朝阳区望京西路1号",
                "lat": 39.988,
                "lon": 116.480,
                "charge_rate_kw": 100,
                "hourly_rate": 12
            },
            {
                "poi_id": "poi_004",
                "name": "望京韩国料理",
                "category": "food",
                "address": "朝阳区广顺北大街",
                "lat": 39.990,
                "lon": 116.475,
                "hourly_rate": 0
            },
            # 海淀区干扰项
            {
                "poi_id": "poi_005",
                "name": "中关村充电站",
                "category": "charging",
                "address": "海淀区中关村大街",
                "lat": 39.982,
                "lon": 116.310,
                "charge_rate_kw": 110,
                "hourly_rate": 14
            },
            {
                "poi_id": "poi_006",
                "name": "清华食堂",
                "category": "food",
                "address": "海淀区清华园",
                "lat": 39.995,
                "lon": 116.326,
                "hourly_rate": 0
            }
        ]
    }
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)

    # ========== 干扰：旧版本地图备份 ==========
    old_maps = {
        "regions": [
            {
                "region_id": "region_001",
                "name": "北京市中心",
                "center": {"lat": 39.9, "lon": 116.4},
                "radius_km": 10,
                "map_version": "2024.03.01"
            }
        ]
    }
    with open("data/old_maps_backup.json", "w", encoding="utf-8") as f:
        json.dump(old_maps, f, ensure_ascii=False, indent=2)

    # ========== 干扰：重复 POI 文件（版本混乱） ==========
    pois_v1 = {
        "pois": [
            {
                "poi_id": "poi_001",
                "name": "国贸充电站(旧)",
                "category": "charging",
                "address": "北京市中心东三环",
                "lat": 39.907,
                "lon": 116.458
            }
        ]
    }
    with open("data/pois_v1.json", "w", encoding="utf-8") as f:
        json.dump(pois_v1, f, ensure_ascii=False, indent=2)

    # ========== 其他区域数据（无关干扰） ==========
    regions = {
        "regions": [
            {"region_id": "region_001", "name": "北京市中心", "center": {"lat": 39.905, "lon": 116.397}, "radius_km": 10},
            {"region_id": "region_002", "name": "朝阳区", "center": {"lat": 39.921, "lon": 116.443}, "radius_km": 8}
        ]
    }
    with open("data/regions.json", "w", encoding="utf-8") as f:
        json.dump(regions, f, ensure_ascii=False, indent=2)

    # ========== 路线偏好文件（无用干扰） ==========
    preferences = {
        "preferences": [
            {"preference_id": "pref_001", "name": "最快路线", "description": "优先选择时间最短的路线"},
            {"preference_id": "pref_002", "name": "最短路线", "description": "优先选择距离最短的路线"}
        ]
    }
    with open("data/route_preferences.json", "w", encoding="utf-8") as f:
        json.dump(preferences, f, ensure_ascii=False, indent=2)

    # ========== 交通数据文件（无用干扰） ==========
    traffic = {
        "road_segments": [
            {"segment_id": "seg_001", "name": "中环路", "condition": "congested", "congestion_level": 8},
            {"segment_id": "seg_002", "name": "延安高架路", "condition": "smooth", "congestion_level": 2}
        ]
    }
    with open("data/traffic_data.json", "w", encoding="utf-8") as f:
        json.dump(traffic, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_env()
