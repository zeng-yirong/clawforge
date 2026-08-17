import os
import json
import math
import random

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def build_env():
    os.makedirs("trips", exist_ok=True)
    os.makedirs("data/pois", exist_ok=True)

    # 用户请求文件
    request = (
        "User Location: 39.9042, 116.4074\n"
        "Preferred Charging Power: >=150 kW\n"
        "Max Results: 3\n"
    )
    with open("trips/charge_plan_request.txt", "w") as f:
        f.write(request)

    # POI 数据（混合充电站、其他类别、功率不足的）
    pois = [
        {"poi_id": "cp01", "name": "天安门充电站", "category": "charging", "lat": 39.905, "lon": 116.408, "address": "东城区东交民巷", "charge_rate_kw": 200},
        {"poi_id": "cp02", "name": "王府井充电站", "category": "charging", "lat": 39.915, "lon": 116.415, "address": "东城区王府井大街", "charge_rate_kw": 180},
        {"poi_id": "cp03", "name": "东单充电站", "category": "charging", "lat": 39.912, "lon": 116.420, "address": "东城区东单北大街", "charge_rate_kw": 150},
        {"poi_id": "cp04", "name": "西单充电站", "category": "charging", "lat": 39.900, "lon": 116.380, "address": "西城区西单北大街", "charge_rate_kw": 160},
        {"poi_id": "cp05", "name": "南锣鼓巷充电站", "category": "charging", "lat": 39.930, "lon": 116.410, "address": "东城区南锣鼓巷", "charge_rate_kw": 140},
        {"poi_id": "cp06", "name": "国贸充电站", "category": "charging", "lat": 39.908, "lon": 116.460, "address": "朝阳区建国门外大街", "charge_rate_kw": 170},
        {"poi_id": "fd01", "name": "全聚德烤鸭店", "category": "food", "lat": 39.907, "lon": 116.409, "address": "东城区前门大街", "charge_rate_kw": 0},
        {"poi_id": "at01", "name": "故宫博物院", "category": "attraction", "lat": 39.916, "lon": 116.397, "address": "东城区景山前街", "charge_rate_kw": 0}
    ]
    random.shuffle(pois)  # 增加迷惑性
    with open("data/pois/beijing_chargers.json", "w") as f:
        json.dump(pois, f, indent=2)

if __name__ == "__main__":
    build_env()
