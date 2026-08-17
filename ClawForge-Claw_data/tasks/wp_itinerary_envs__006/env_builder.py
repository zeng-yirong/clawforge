import os
import json

def build_env():
    # 创建 data 目录及干扰文件
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)

    # 主数据文件 transportation.json
    transportation_data = {
        "routes": [
            {
                "route_id": "BJS-SHA-01",
                "origin": "BJS",
                "destination": "SHA",
                "distance_km": 1178,
                "options": [
                    {"type": "high_speed_train", "travel_time_hours": 4.5, "cost_usd": 80},
                    {"type": "direct_flight", "travel_time_hours": 2.0, "cost_usd": 150},
                    {"type": "普通火车", "travel_time_hours": 12.0, "cost_usd": 30}
                ]
            },
            {
                "route_id": "BJS-SHA-02",
                "origin": "BJS",
                "destination": "SHA",
                "distance_km": 1178,
                "options": [
                    {"type": "high_speed_train", "travel_time_hours": 5.0, "cost_usd": 75},
                    {"type": "direct_flight", "travel_time_hours": 2.5, "cost_usd": 140},
                    {"type": "普通火车", "travel_time_hours": 13.0, "cost_usd": 28}
                ]
            },
            {
                "route_id": "BJS-SHA-03",   # 诱饵：最快的选项 missing travel_time
                "origin": "BJS",
                "destination": "SHA",
                "distance_km": 1178,
                "options": [
                    {"type": "high_speed_train", "travel_time_hours": 3.8, "cost_usd": 90},
                    {"type": "direct_flight", "travel_time_hours": 1.8, "cost_usd": 200},  # 理论上最快，但故意设成干扰？实际最快是1.8，但我们要验证是否选这条？我们要让唯一正确答案是 route BJS-SHA-01 的 direct_flight? 等等，需要确保唯一性。
                    # 为了唯一，可以设置 BJS-SHA-03 的 direct_flight 是1.8，但另一条路线也有1.9? 为了有唯一最快，我们让 BJS-SHA-01 的 direct_flight 2.0，BJS-SHA-02 的 direct_flight 2.5，BJS-SHA-03 的 direct_flight 1.8 但缺少 travel_time_hours? 不，我们可以在选项里故意缺失字段。
                    # 我们需要一个明确的最快且完整选项。设 BJS-SHA-03 的 direct_flight 字段缺失 travel_time_hours 导致不可用。那么真正最快完整的是 BJS-SHA-01 direct_flight (2.0h)
                ]
            },
            {
                "route_id": "BJS-SHA-04",   # 不同目的地，干扰
                "origin": "BJS",
                "destination": "CAN",
                "distance_km": 1880,
                "options": [
                    {"type": "direct_flight", "travel_time_hours": 3.0, "cost_usd": 250}
                ]
            }
        ]
    }

    # 修改 BJS-SHA-03 使其 options 中 direct_flight 缺少 travel_time_hours 字段
    transportation_data["routes"][2]["options"][1] = {"type": "direct_flight", "cost_usd": 200}  # 缺 travel_time

    with open("data/transportation.json", "w") as f:
        json.dump(transportation_data, f, indent=2)

    # 干扰文件：旧版备份
    old_data = {
        "routes": [
            {
                "route_id": "BJS-SHA-01",
                "origin": "BJS",
                "destination": "SHA",
                "distance_km": 1178,
                "options": [
                    {"type": "high_speed_train", "travel_time_hours": 6.0, "cost_usd": 70},
                    {"type": "direct_flight", "travel_time_hours": 3.0, "cost_usd": 180}
                ]
            }
        ]
    }
    with open("data/backup/transportation_old.json", "w") as f:
        json.dump(old_data, f, indent=2)

    # 另一个干扰文件：用户偏好，无关
    with open("data/user_preferences.txt", "w") as f:
        f.write("prefer speed over cost\n")

    # 创建 ops 目录下可能存在的脏数据（诱饵）
    with open("ops/best_route.json", "w") as f:
        f.write('{"route_id": "BJS-SHA-02", "transport": "high_speed_train"}\n')  # 故意占用，agent应覆盖

if __name__ == "__main__":
    build_env()
