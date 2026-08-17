import os
import json
import shutil

def build_env():
    # Ensure working directory is clean (cwd is already .)
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Define POI data with intentional interference
    pois = [
        # Charging stations (4 entries, names intentionally not sorted in file)
        {"poi_id": "CS002", "name": "City Charge Hub", "category": "charging", "lat": 39.9042, "lon": 116.4074, "address": "朝阳区望京路10号"},
        {"poi_id": "CS001", "name": "Alpha Charge Station", "category": "charging", "lat": 39.9100, "lon": 116.4100, "address": "海淀区知春路100号"},
        {"poi_id": "CS004", "name": "West Side Charger", "category": "charging", "lat": 39.8900, "lon": 116.3800, "address": "西城区金融街5号"},
        {"poi_id": "CS003", "name": "Green Power Point", "category": "charging", "lat": 39.9200, "lon": 116.4000, "address": "东城区建国门内大街20号"},
        # Distractors: other categories
        {"poi_id": "POI010", "name": "Peking Duck Restaurant", "category": "food", "lat": 39.9150, "lon": 116.3970, "address": "东城区王府井大街88号"},
        {"poi_id": "POI011", "name": "PetroChina Gas Station", "category": "food", "lat": 39.9050, "lon": 116.4200, "address": "朝阳区建国路99号"},  # mis-tagged but not charging
        {"poi_id": "POI012", "name": "Forbidden City", "category": "attraction", "lat": 39.9163, "lon": 116.3972, "address": "东城区景山前街4号"},
        {"poi_id": "POI013", "name": "Chaoyang Hospital", "category": "hospital", "lat": 39.9210, "lon": 116.4350, "address": "朝阳区工体南路8号"},
        # Interference: POI with category string in different case (not 'charging')
        {"poi_id": "POI020", "name": "Fast Charge Express", "category": "CHARGE", "lat": 39.9120, "lon": 116.4050, "address": "朝阳区东三环中路1号"},
        # Interference: missing address (but category not charging)
        {"poi_id": "POI030", "name": "Mystery POI", "category": "shopping", "lat": 39.9000, "lon": 116.3950},
        # Additional charging station with incomplete fields (address empty string)
        {"poi_id": "CS005", "name": "Downtown Charger", "category": "charging", "lat": 39.9080, "lon": 116.4120, "address": ""},  # empty address – still valid but address is ""
    ]
    # Note: "Downtown Charger" has empty address, it's still a valid charging station.
    # The agent should include it. For verification we treat "" as is.

    # Correct charging POIs: CS001,CS002,CS003,CS004,CS005 (5 entries)
    # Write pois.json
    with open("data/pois.json", "w", encoding="utf-8") as f:
        json.dump({"pois": pois}, f, ensure_ascii=False, indent=2)

    # Also create a dummy old_data directory with outdated version to mislead
    os.makedirs("backup", exist_ok=True)
    old_pois = [
        {"poi_id": "CS001", "name": "Alpha Charge Station", "category": "charging", "lat": 39.91, "lon": 116.41, "address": "旧版本地址海淀区"},
        {"poi_id": "CS002", "name": "City Charge Hub", "category": "charging", "lat": 39.90, "lon": 116.40, "address": "旧版本地址朝阳区"},
    ]
    with open("backup/pois_old.json", "w", encoding="utf-8") as f:
        json.dump({"pois": old_pois}, f, ensure_ascii=False, indent=2)

    # Create a dummy ops file to ensure it's not leftover from previous runs
    with open("ops/README.txt", "w") as f:
        f.write("Place generated files here.\n")

if __name__ == "__main__":
    build_env()
