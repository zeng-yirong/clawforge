import os
import json
import csv

def build_env():
    # 创建目录
    os.makedirs("routes", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 城市码对照表
    with open("cities.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["code", "name"])
        writer.writerow(["BJS", "北京"])
        writer.writerow(["SHA", "上海"])

    # 有效最新路线（含干扰项）
    routes_2024 = {
        "routes": [
            {
                "route_id": "BJS-SHA-001",
                "origin": "BJS",
                "destination": "SHA",
                "distance_km": 1200,
                "high_speed_train": {"cost": 500, "duration_hours": 4.5},
                "direct_flight": {"cost": 1200, "duration_hours": 2.0},
                "普通火车": {"cost": 200, "duration_hours": 10.0}
            },
            {
                "route_id": "BJS-SHA-002",
                "origin": "BJS",
                "destination": "SHA",
                "distance_km": 1200,
                "high_speed_train": {"cost": 550, "duration_hours": 4.5},
                "direct_flight": {"cost": 1300, "duration_hours": 2.0}
            },
            {
                "route_id": "BJ-SHA-003",
                "origin": "BJ",
                "destination": "SHA",
                "distance_km": 1180,
                "high_speed_train": {"cost": 480, "duration_hours": 4.5},
                "direct_flight": {"cost": 1100, "duration_hours": 2.0}
            },
            {
                "route_id": "BJS-SH-004",
                "origin": "BJS",
                "destination": "SH",
                "distance_km": 1150,
                "high_speed_train": {"cost": 520, "duration_hours": 4.0},
                "direct_flight": {"cost": 1000, "duration_hours": 1.5}
            },
            {
                "route_id": "BJS-SHA-005",
                "origin": "BJS",
                "destination": "SHA",
                "distance_km": 1200,
                "direct_flight": {"cost": 800, "duration_hours": 2.0}
            }
        ]
    }
    with open("routes_2024.json", "w") as f:
        json.dump(routes_2024, f, indent=2)

    # 过期档案（诱饵）
    routes_archive = {
        "routes": [
            {
                "route_id": "BJS-SHA-OLD",
                "origin": "BJS",
                "destination": "SHA",
                "high_speed_train": {"cost": 450, "duration_hours": 5.0},  # 更便宜但时间略长，且是归档数据
                "direct_flight": {"cost": 1000, "duration_hours": 2.5}
            }
        ]
    }
    with open("routes_archive.json", "w") as f:
        json.dump(routes_archive, f, indent=2)

    # 格式错误的干扰文件
    with open("routes_error.json", "w") as f:
        f.write('{"routes": [{"route_id": "BAD", "origin": "BJS", "destination": "SHA", "high_speed_train": {"cost": "abc", "duration_hours": "x"}]}')  # 故意破损

    # 无用的文本笔记
    with open("notes.txt", "w") as f:
        f.write("这里是老王备份的旧笔记，没什么用。\n")

if __name__ == "__main__":
    build_env()
