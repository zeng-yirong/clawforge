import os
import json
import random

def build_env():
    # 城市数据
    cities = {
        "BJS": {"name": "北京", "lat": 39.9, "lon": 116.4},
        "SHA": {"name": "上海", "lat": 31.2, "lon": 121.5},
        "HGH": {"name": "杭州", "lat": 30.3, "lon": 120.2},
        "CAN": {"name": "广州", "lat": 23.1, "lon": 113.3},
        "SZX": {"name": "深圳", "lat": 22.5, "lon": 114.1},  # 干扰城市，不在行程中
        "CTU": {"name": "成都", "lat": 30.6, "lon": 104.0}   # 干扰城市
    }
    os.makedirs("data", exist_ok=True)
    with open("data/cities.json", "w") as f:
        json.dump(cities, f, indent=2)

    # 路线数据（包含干扰路线、不完整数据）
    routes = {
        "R1": {"origin": "BJS", "destination": "SHA", "distance_km": 1200,
                "high_speed_train": {"duration_h": 4.5, "cost_cny": 550},
                "direct_flight": {"duration_h": 2.0, "cost_cny": 1200},
                "普通火车": {"duration_h": 12.0, "cost_cny": 180}},
        "R2": {"origin": "SHA", "destination": "HGH", "distance_km": 180,
                "high_speed_train": {"duration_h": 0.8, "cost_cny": 75},
                "direct_flight": {"duration_h": 0.8, "cost_cny": 600},
                "普通火车": {"duration_h": 2.5, "cost_cny": 30}},
        "R3": {"origin": "HGH", "destination": "CAN", "distance_km": 1200,
                "high_speed_train": {"duration_h": 7.5, "cost_cny": 800},
                "direct_flight": {"duration_h": 2.5, "cost_cny": 900},
                "普通火车": {"duration_h": 14.0, "cost_cny": 250}},
        "R4": {"origin": "CAN", "destination": "BJS", "distance_km": 2000,
                "high_speed_train": {"duration_h": 9.0, "cost_cny": 1000},
                "direct_flight": {"duration_h": 3.0, "cost_cny": 1500},
                "普通火车": {"duration_h": 22.0, "cost_cny": 400}},
        # 干扰路线：深圳到北京等
        "R5": {"origin": "SZX", "destination": "BJS", "distance_km": 1900,
                "high_speed_train": {"duration_h": 8.5, "cost_cny": 950},
                "direct_flight": {"duration_h": 3.0, "cost_cny": 1400}},
        # 缺少交通方式（诱饵）
        "R6": {"origin": "SHA", "destination": "CAN", "distance_km": 1400,
                "direct_flight": {"duration_h": 2.5, "cost_cny": 1100},
                "high_speed_train": None}  # 没有高铁选项
    }
    with open("data/routes.json", "w") as f:
        json.dump(routes, f, indent=2)

    # 用户笔记
    notes = (
        "老张的便签：\n"
        "1. 必须按顺序：北京->上海->杭州->广州->北京（别打乱）。\n"
        "2. 时间优先，但太贵的飞机也悠着点，别超总预算5000。\n"
        "3. 杭州到广州这一程我查了，高铁要7个多小时，飞机才2.5小时但贵一点，你看着选。\n"
        "4. 北京到上海、上海到杭州高铁又快又便宜，别整幺蛾子。\n"
        "5. 广州回北京飞机吧，高铁太慢了。\n"
    )
    with open("notes.txt", "w") as f:
        f.write(notes)

    # 额外干扰文件
    with open("data/old_routes_backup.json", "w") as f:
        json.dump({"dummy": "data"}, f)
    with open("data/cities_old.csv", "w") as f:
        f.write("Code,Name\nBJS,Beijing\nSHA,Shanghai\n")

if __name__ == "__main__":
    build_env()
