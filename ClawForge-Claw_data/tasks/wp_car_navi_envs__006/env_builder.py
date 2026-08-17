import os
import json
import shutil

def build_env():
    # 确保 data 目录
    os.makedirs("data", exist_ok=True)
    
    # ===== 最新离线地图 (2024.06.01) =====
    offline_maps = {
        "wrapper": "regions",
        "regions": [
            {
                "region_id": "downtown",
                "name": "市中心区域",
                "center": {"lat": 39.9, "lon": 116.4},
                "radius_km": 15,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "airport",
                "name": "机场区域",
                "center": {"lat": 40.1, "lon": 116.6},
                "radius_km": 10,
                "map_version": "2024.06.01"
            },
            {
                "region_id": "suburb",
                "name": "郊区扩展区域",
                "center": {"lat": 40.3, "lon": 116.2},
                "radius_km": 25,
                "map_version": "2024.06.01"
            }
        ]
    }
    with open("data/offline_maps.json", "w", encoding="utf-8") as f:
        json.dump(offline_maps, f, ensure_ascii=False, indent=2)
    
    # ===== 旧备份地图 (仅用于干扰) =====
    os.makedirs("data/backup", exist_ok=True)
    old_maps = {
        "wrapper": "regions",
        "regions": [
            {
                "region_id": "suburb",
                "name": "郊区扩展区域(旧版)",
                "center": {"lat": 40.3, "lon": 116.2},
                "radius_km": 25,
                "map_version": "2024.05.15"
            }
        ]
    }
    with open("data/backup/old_offline_maps.json", "w", encoding="utf-8") as f:
        json.dump(old_maps, f, ensure_ascii=False, indent=2)
    
    # ===== POI 数据 =====
    pois = {
        "wrapper": "pois",
        "pois": [
            # 郊区扩展区域的充电站 (符合条件)
            {
                "poi_id": "chg-001",
                "name": "城郊超充站A",
                "category": "charging",
                "lat": 40.35, "lon": 121.0,
                "address": "郊区高速出口",
                "charge_rate_kw": 100
            },
            {
                "poi_id": "chg-002",
                "name": "乡镇快充站B",
                "category": "charging",
                "lat": 40.25, "lon": 120.5,
                "address": "乡镇中心",
                "charge_rate_kw": 60
            },
            # 郊区扩展区域的充电站 (功率不足)
            {
                "poi_id": "chg-003",
                "name": "老旧充电桩C",
                "category": "charging",
                "lat": 40.28, "lon": 120.8,
                "address": "老街道",
                "charge_rate_kw": 40
            },
            # 市中心区域的充电站 (功率足够但区域错误)
            {
                "poi_id": "chg-004",
                "name": "市中心快充D",
                "category": "charging",
                "lat": 39.92, "lon": 116.4,
                "address": "市中心广场",
                "charge_rate_kw": 80,
                "region_id": "downtown"
            },
            # 郊区扩展区域的餐厅
            {
                "poi_id": "rst-001",
                "name": "农家乐一号",
                "category": "food",
                "lat": 40.30, "lon": 121.2,
                "address": "东郊村",
                "hourly_rate": 0
            },
            {
                "poi_id": "rst-002",
                "name": "路旁小吃店",
                "category": "food",
                "lat": 40.32, "lon": 119.8,
                "address": "西路村",
                "hourly_rate": 0
            },
            # 郊区扩展区域的餐厅 (缺失 region_id，但默认属于suburb? 我们显式设置 region_id)
            # 注意：下面这个餐厅缺失 region_id，为了测试，我们不给它 region_id，但默认不加入？或者加入但视为干扰？
            # 为保证唯一答案，我们给它一个不属于suburb的region_id
            {
                "poi_id": "rst-003",
                "name": "机场餐厅",
                "category": "food",
                "lat": 40.05, "lon": 116.6,
                "address": "机场T2",
                "region_id": "airport"
            },
            # 另一个郊区扩展区域的充电站 (功率足够但category是hospital)
            {
                "poi_id": "chg-005",
                "name": "医院充电桩",
                "category": "hospital",
                "lat": 40.33, "lon": 119.5,
                "address": "镇医院",
                "charge_rate_kw": 120,
                "region_id": "suburb"
            },
            # 重复poi_id (干扰)
            {
                "poi_id": "chg-001",
                "name": "城郊超充站A(重复)",
                "category": "charging",
                "lat": 40.35, "lon": 121.0,
                "address": "郊区高速出口重复",
                "charge_rate_kw": 100,
                "region_id": "suburb"
            }
        ]
    }
    # 为多数POI补充region_id (默认suburb)
    for p in pois["pois"]:
        if "region_id" not in p:
            p["region_id"] = "suburb"
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump(pois, f, ensure_ascii=False, indent=2)
    
    # ===== 额外干扰文件 =====
    with open("data/notes.txt", "w") as f:
        f.write("这是无关笔记")
    with open("data/pois_backup.json", "w") as f:
        json.dump({"pois": []}, f)

if __name__ == "__main__":
    build_env()
