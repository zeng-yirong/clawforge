import os
import json

def build_env():
    # Create directory structure
    dirs = ["data/alerts", "data/sensors", "data/zones", "ops", "logs", "backups"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # --- Sensors (with distractors) ---
    sensors = [
        {"sensor_id": "S01", "status": "offline", "type": "motion"},
        {"sensor_id": "S02", "status": "active",   "type": "glass_break"},
        {"sensor_id": "S03", "status": "active",   "type": "motion"},
        {"sensor_id": "S04", "status": "error",    "type": "temperature"},
        {"sensor_id": "S05", "status": "active",   "type": "door_contact"},
    ]
    with open("data/sensors/sensors.json", "w") as f:
        json.dump({"sensors": sensors}, f, indent=2)

    # --- Zones (intrusion flags) ---
    zones = [
        {"zone_id": "Z01", "zone_name": "Main Lobby",  "intrusion_detected": False},
        {"zone_id": "Z02", "zone_name": "Basement",     "intrusion_detected": True},
        {"zone_id": "Z03", "zone_name": "Garage",       "intrusion_detected": False},
        {"zone_id": "Z04", "zone_name": "Office Room",  "intrusion_detected": False},
    ]
    with open("data/zones/zones.json", "w") as f:
        json.dump({"zones": zones}, f, indent=2)

    # --- Alerts (one real, many distracting) ---
    alerts = [
        # distractor: offline sensor, critical – invalid
        {"alert_id": "alert-001", "sensor_id": "S01", "zone_id": "Z01",
         "severity": "critical", "timestamp": "2025-04-01T03:15:00Z",
         "acknowledged": False, "description": "Motion spike in lobby (offline sensor ghost)"},
        # distractor: active sensor, low severity – too low
        {"alert_id": "alert-002", "sensor_id": "S02", "zone_id": "Z01",
         "severity": "low", "timestamp": "2025-04-01T03:16:30Z",
         "acknowledged": False, "description": "Glass break anomaly – likely wind"},
        # distractor: error sensor, critical – sensor down
        {"alert_id": "alert-003", "sensor_id": "S04", "zone_id": "Z02",
         "severity": "critical", "timestamp": "2025-04-01T03:17:45Z",
         "acknowledged": False, "description": "Temp spike in basement (error sensor – no confidence)"},
        # distractor: active sensor, high severity, but zone no intrusion
        {"alert_id": "alert-004", "sensor_id": "S05", "zone_id": "Z03",
         "severity": "high", "timestamp": "2025-04-01T03:18:20Z",
         "acknowledged": False, "description": "Door forced open – garage (but zone shows no intrusion)"},
        # distractor: active sensor, critical, but zone has no intrusion
        {"alert_id": "alert-005", "sensor_id": "S02", "zone_id": "Z04",
         "severity": "critical", "timestamp": "2025-04-01T03:19:10Z",
         "acknowledged": False, "description": "Glass break in office – false pattern"},
        # *** REAL ALERT ***
        {"alert_id": "alert-007", "sensor_id": "S03", "zone_id": "Z02",
         "severity": "critical", "timestamp": "2025-04-01T03:20:00Z",
         "acknowledged": False, "description": "Motion triggered in basement restricted area"},
        # extra distractor: duplicate-looking but different sensor
        {"alert_id": "alert-006", "sensor_id": "S03", "zone_id": "Z02",
         "severity": "medium", "timestamp": "2025-04-01T03:21:30Z",
         "acknowledged": False, "description": "Low confidence motion (filtered)"},
    ]
    for i, alert in enumerate(alerts, 1):
        fname = f"alert_{i:03d}.json"
        # overwrite alert_id to match filename but keep unique id
        alert["alert_id"] = f"alert-{i:03d}"
        with open(f"data/alerts/{fname}", "w") as f:
            json.dump(alert, f, indent=2)

    # --- Distractor files (non-JSON) ---
    # An old CSV log that looks like alert data but is irrelevant
    with open("data/alerts/old_alerts.csv", "w") as f:
        f.write("alert_id,sensor_id,zone,severity\nalert-xxx,S99,Z99,critical\n")
    # A backup tarball (empty placeholder)
    with open("backups/alerts_backup_20250331.txt", "w") as f:
        f.write("This is a placeholder backup – ignore.\n")
    # Log file with unrelated entries
    with open("logs/system_events.log", "w") as f:
        f.write("2025-04-01 03:10:00 [INFO] Sensor health check passed\n")
        f.write("2025-04-01 03:11:00 [WARN] Network latency spike\n")
        f.write("2025-04-01 03:22:00 [ERROR] Firewall rule mismatch – not security related\n")

if __name__ == "__main__":
    build_env()
