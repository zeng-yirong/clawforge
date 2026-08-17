import os
import json
import shutil

def build_env():
    # 确保工作区干净
    for d in ["data", "archive", "ops"]:
        os.makedirs(d, exist_ok=True)

    # ---------- 最新有效数据 (data/transportation.json) ----------
    routes = [
        {
            "route_id": "BJS-NKG",
            "origin": "北京",
            "destination": "南京",
            "segments": [
                {"mode": "高铁", "duration_h": 4.0, "status": "active", "timestamp": "2025-04-01T08:00:00"},
                {"mode": "飞机", "duration_h": 3.5, "status": "active", "timestamp": "2025-04-01T08:00:00"},
                {"mode": "普通火车", "duration_h": 8.0, "status": "active", "timestamp": "2025-04-01T08:00:00"}
            ],
            "last_updated": "2025-04-01"
        },
        {
            "route_id": "NKG-SHA",
            "origin": "南京",
            "destination": "上海",
            "segments": [
                {"mode": "高铁", "duration_h": 1.5, "status": "active", "timestamp": "2025-04-01T08:00:00"},
                {"mode": "飞机", "duration_h": 2.0, "status": "active", "timestamp": "2025-04-01T08:00:00"},
                {"mode": "普通火车", "duration_h": 4.0, "status": "active", "timestamp": "2025-04-01T08:00:00"}
            ],
            "last_updated": "2025-04-01"
        },
        # 干扰项：已取消的路线（更短时间，但无效）
        {
            "route_id": "BJS-NKG-CANCELLED",
            "origin": "北京",
            "destination": "南京",
            "segments": [
                {"mode": "磁悬浮", "duration_h": 2.0, "status": "cancelled", "timestamp": "2025-03-15T12:00:00"}
            ],
            "last_updated": "2025-03-15"
        },
        # 干扰项：其他城市路线
        {
            "route_id": "BJS-GZG",
            "origin": "北京",
            "destination": "广州",
            "segments": [
                {"mode": "高铁", "duration_h": 8.0, "status": "active", "timestamp": "2025-04-01T08:00:00"}
            ],
            "last_updated": "2025-04-01"
        }
    ]
    with open("data/transportation.json", "w", encoding="utf-8") as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)

    # ---------- 旧版本数据（干扰，内含废弃但数值更优的记录） ----------
    old_routes = [
        {
            "route_id": "BJS-NKG",
            "origin": "北京",
            "destination": "南京",
            "segments": [
                {"mode": "高铁", "duration_h": 3.5, "status": "deprecated", "timestamp": "2025-03-01T10:00:00"}
            ],
            "last_updated": "2025-03-01"
        },
        {
            "route_id": "NKG-SHA",
            "origin": "南京",
            "destination": "上海",
            "segments": [
                {"mode": "高铁", "duration_h": 1.2, "status": "deprecated", "timestamp": "2025-03-01T10:00:00"}
            ],
            "last_updated": "2025-03-01"
        },
        # 重复的旧版路线（应被最新覆盖）
        {
            "route_id": "BJS-NKG",
            "origin": "北京",
            "destination": "南京",
            "segments": [
                {"mode": "飞机", "duration_h": 3.0, "status": "active", "timestamp": "2025-03-20T14:00:00"}
            ],
            "last_updated": "2025-03-20"
        }
    ]
    with open("archive/transportation_backup.json", "w", encoding="utf-8") as f:
        json.dump(old_routes, f, ensure_ascii=False, indent=2)

    # ---------- 其他无关文件（迷惑） ----------
    with open("data/cities.csv", "w") as f:
        f.write("city,code\n北京,BJS\n南京,NKG\n上海,SHA\n广州,GZG\n")
    with open("archive/old_notes.txt", "w") as f:
        f.write("some old info, irrelevant\n")

if __name__ == "__main__":
    build_env()
