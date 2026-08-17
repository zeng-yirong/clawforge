import os
import json
from datetime import datetime, timedelta

def build_env():
    # Ensure base directories exist
    os.makedirs("data/alerts", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # pre-create empty ops dir (optional, agent may use it)

    # Base timestamp for realistic data
    base = datetime(2025, 3, 14, 2, 30, 0)

    alerts = [
        {
            "alert_id": "ALERT-001",
            "timestamp": (base + timedelta(hours=-2)).isoformat(),
            "zone_id": "zone-backyard",
            "door_id": "door-back",
            "status": "acknowledged"
        },
        {
            "alert_id": "ALERT-002",
            "timestamp": (base + timedelta(hours=-1, minutes=45)).isoformat(),
            "zone_id": "zone-garage",
            "door_id": "door-garage",
            "status": "resolved"
        },
        {
            "alert_id": "ALERT-003",
            "timestamp": (base + timedelta(hours=-1)).isoformat(),
            "zone_id": "zone-main-lobby",
            "door_id": "door-front",
            "status": "new"
        },
        {
            "alert_id": "ALERT-004",
            "timestamp": (base + timedelta(hours=-0, minutes=30)).isoformat(),
            "zone_id": "zone-basement",
            "door_id": "door-basement",
            "status": "acknowledged"
        },
        {
            "alert_id": "ALERT-005",
            "timestamp": (base + timedelta(hours=-0, minutes=15)).isoformat(),
            "zone_id": "zone-office",
            "door_id": "door-office",
            "status": "new"
        },
        {
            "alert_id": "ALERT-006",
            "timestamp": base.isoformat(),
            "zone_id": "zone-backyard",
            "door_id": "door-back",
            "status": "resolved"
        },
        {
            "alert_id": "ALERT-007",
            "timestamp": (base + timedelta(hours=0, minutes=10)).isoformat(),
            "zone_id": "zone-garage",
            "door_id": "door-garage",
            "status": "new"
        },
        # 干扰项：重复的 ALERT-003（过时的旧数据，status 是 acknowledged）
        {
            "alert_id": "ALERT-003",
            "timestamp": (base + timedelta(hours=-3)).isoformat(),
            "zone_id": "zone-main-lobby",
            "door_id": "door-front",
            "status": "acknowledged"
        },
        # 干扰项：缺少 door_id 的 malformed 记录
        {
            "alert_id": "ALERT-008",
            "timestamp": (base + timedelta(hours=0, minutes=20)).isoformat(),
            "zone_id": "zone-backyard",
            "status": "new"
        }
    ]

    with open("data/alerts/alerts.json", "w") as f:
        json.dump(alerts, f, indent=2)

if __name__ == "__main__":
    build_env()
