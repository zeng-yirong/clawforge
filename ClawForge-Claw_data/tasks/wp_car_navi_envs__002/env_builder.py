import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # 留给Agent输出

    # ========== 区域数据 (offline_maps.json) ==========
    offline_maps = {
        "regions": [
            {
                "region_id": "region_downtown",
                "name": "市中心区域",
                "center": {"lat": 39.9042, "lon": 116.4074},
                "radius_km": 10,
                "map_version": "2024.05.15"
            },
            {
                "region_id": "region_suburb",
                "name": "郊区扩展区域",
                "center": {"lat": 40.0510, "lon": 116.2910},
                "radius_km": 20,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "region_airport",
                "name": "机场区域",
                "center": {"lat": 40.0799, "lon": 116.6031},
                "radius_km": 8,
                "map_version": "2024.05.15"
            }
        ]
    }
    with open("data/offline_maps.json", "w", encoding="utf-8") as f:
        json.dump(offline_maps, f, ensure_ascii=False, indent=2)

    # ========== POI数据 (pois.json) ==========
    # 唯一正确答案：poi-charge-suburb-02 (郊区扩展区域, 充电功率60kW)
    pois = {
        "pois": [
            {
                "poi_id": "poi-charge-downtown-01",
                "name": "市中心快充站",
                "category": "charging",
                "lat": 39.9042,
                "lon": 116.4074,
                "address": "北京市中心东城区",
                "charge_rate_kw": 80,
                "region_id": "region_downtown"
            },
            {
                "poi_id": "poi-charge-suburb-01",
                "name": "郊区慢充站",
                "category": "charging",
                "lat": 40.0510,
                "lon": 116.2910,
                "address": "郊区扩展区域北侧",
                "charge_rate_kw": 40,  # 功率不足
                "region_id": "region_suburb"
            },
            {
                "poi_id": "poi-charge-suburb-02",
                "name": "郊区快充站",
                "category": "charging",
                "lat": 40.0520,
                "lon": 116.2920,
                "address": "郊区扩展区域南侧",
                "charge_rate_kw": 60,  # 唯一符合条件
                "region_id": "region_suburb"
            },
            {
                "poi_id": "poi-charge-airport-01",
                "name": "机场快充站",
                "category": "charging",
                "lat": 40.0799,
                "lon": 116.6031,
                "address": "机场停车场",
                "charge_rate_kw": 120,
                "region_id": "region_airport"
            },
            {
                "poi_id": "poi-restaurant-01",
                "name": "高速服务区餐厅",
                "category": "food",
                "lat": 39.9000,
                "lon": 116.4000,
                "address": "G6高速服务区",
                "region_id": "region_downtown"
            },
            {
                "poi_id": "poi-gas-01",
                "name": "加油站",
                "category": "rest_area",
                "lat": 40.0500,
                "lon": 116.2900,
                "address": "郊区加油站",
                "region_id": "region_suburb"
            }
        ]
    }
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)

    # ========== 额外干扰文件 (route_preferences.json) ==========
    prefs = {
        "preferences": [
            {"preference_id": "pref_fastest", "name": "最快路线", "description": "优先选择时间最短的路线"},
            {"preference_id": "pref_shortest", "name": "最短路线", "description": "优先选择距离最短的路线"},
            {"preference_id": "pref_eco", "name": "经济路线", "description": "优先选择能耗最低的路线"}
        ]
    }
    with open("data/route_preferences.json", "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)

    # ========== 脏数据：损坏的CSV文件（干扰） ==========
    with open("data/old_pois_backup.csv", "w", encoding="utf-8") as f:
        f.write("poi_id,name,category,charge_rate_kw\npoi_old1,老充电站,charging,55\n")

    # ========== 遗留错误JSON（诱饵） ==========
    with open("data/legacy_plan.json", "w", encoding="utf-8") as f:
        f.write('{"poi_id": "poi-charge-downtown-01", "type": "wrong"}')

if __name__ == "__main__":
    build_env()
