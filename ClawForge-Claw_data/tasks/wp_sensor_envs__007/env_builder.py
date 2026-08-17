import os
import json
import csv

def build_env():
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/locations", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # accounts.json
    accounts = [
        {"account_id": "acc_alpha", "account_name": "Alpha Corp", "location": "", "sensors": ["S001", "S003"], "locations": [], "notification_contacts": []},
        {"account_id": "acc_beta", "account_name": "Beta Ltd", "location": "", "sensors": ["S002", "S004", "S007"], "locations": [], "notification_contacts": []},
        {"account_id": "acc_gamma", "account_name": "Gamma Inc", "location": "", "sensors": ["S005", "S006"], "locations": [], "notification_contacts": []}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # locations.json
    locations = [
        {"location_id": "L001", "location_name": "Main Lobby", "floor": 1, "sensors": ["S001", "S002"]},
        {"location_id": "L002", "location_name": "Office Area", "floor": 2, "sensors": ["S003", "S007"]},
        {"location_id": "L003", "location_name": "Server Room", "floor": 1, "sensors": ["S004"]},
        {"location_id": "L004", "location_name": "Warehouse", "floor": 0, "sensors": ["S005"]},
        {"location_id": "L005", "location_name": "Backup Room", "floor": -1, "sensors": ["S006"]}
    ]
    with open("data/locations/locations.json", "w") as f:
        json.dump({"locations": locations}, f, indent=2)

    # sensors.json
    sensors = [
        {"sensor_id": "S001", "sensor_name": "Temp-A", "sensor_type": "temperature", "location_id": "L001", "unit": "celsius", "threshold_low": -10, "threshold_high": 50, "current_value": 45.2, "status": "critical"},
        {"sensor_id": "S002", "sensor_name": "Humidity-Main", "sensor_type": "humidity", "location_id": "L001", "unit": "percent", "threshold_low": 20, "threshold_high": 80, "current_value": 85.0, "status": "critical"},
        {"sensor_id": "S003", "sensor_name": "Energy-1", "sensor_type": "energy", "location_id": "L002", "unit": "kwh", "threshold_low": 0, "threshold_high": 100, "current_value": 55.0, "status": "active"},
        {"sensor_id": "S004", "sensor_name": "AQI-Lobby", "sensor_type": "air_quality", "location_id": "L003", "unit": "aqi", "threshold_low": 0, "threshold_high": 100, "current_value": 150.0, "status": "critical"},
        {"sensor_id": "S005", "sensor_name": "Temp-Backup", "sensor_type": "temperature", "location_id": "L004", "unit": "celsius", "threshold_low": -10, "threshold_high": 40, "current_value": 15.0, "status": "faulty"},
        {"sensor_id": "S006", "sensor_name": "Humidity-Server", "sensor_type": "humidity", "location_id": "L005", "unit": "percent", "threshold_low": 30, "threshold_high": 70, "current_value": 65.0, "status": "inactive"},
        {"sensor_id": "S007", "sensor_name": "Energy-Backup", "sensor_type": "energy", "location_id": "L002", "unit": "kwh", "threshold_low": 0, "threshold_high": 120, "current_value": 80.0, "status": "active"}
    ]
    with open("data/sensors/sensors.json", "w") as f:
        json.dump({"sensors": sensors}, f, indent=2)

    # incidents.csv
    incidents = [
        ["sensor_id", "status", "timestamp", "description"],
        ["S001", "open", "2024-01-15 08:00:00", "High temperature detected"],
        ["S002", "resolved", "2024-01-14 10:30:00", "Replaced sensor"],
        ["S005", "resolved", "2024-01-13 09:00:00", "Calibrated"],
        ["S003", "open", "2024-01-15 09:00:00", "Energy spike"],
        ["S999", "open", "2024-01-15 12:00:00", "Ghost sensor"],
        ["S007", "open", "2024-01-15 14:00:00", "Normal check"]
    ]
    with open("raw_logs/incidents.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(incidents)

if __name__ == "__main__":
    build_env()
