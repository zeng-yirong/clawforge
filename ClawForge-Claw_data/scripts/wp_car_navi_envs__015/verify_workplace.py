#!/usr/bin/env python3
"""
Verify that the agent produced the correct charging stations list.
Score 0-100.
"""
import sys
import json
import os

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return None

def main():
    results = []
    total_score = 0

    # 1. Check ops/charging_stations.json exists (10 points)
    target_path = os.path.join(workspace, "ops", "charging_stations.json")
    exists = os.path.isfile(target_path)
    if exists:
        total_score += 10
        results.append({"item": "ops/charging_stations.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
    else:
        results.append({"item": "ops/charging_stations.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found."})
        # If file missing, no further checks possible, assign 0 and finish
        total_score = 0
        write_score(total_score, results)
        return

    # 2. File is valid JSON (10 points)
    data = load_json(target_path)
    if data is not None:
        total_score += 10
        results.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parsed successfully."})
    else:
        results.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "Failed to parse JSON."})
        write_score(total_score, results)
        return

    # 3. Content is a list of objects (10 points)
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        total_score += 10
        results.append({"item": "Content is array of objects", "score": 10, "max_score": 10, "passed": True, "reason": "Top-level list and each element is dict."})
    else:
        results.append({"item": "Content is array of objects", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected list of dicts, got {type(data).__name__}"})
        write_score(total_score, results)
        return

    # Build expected data from env_builder's original pois.json
    # Load the source data file (assuming it's in workspace/data/pois.json)
    source_path = os.path.join(workspace, "data", "pois.json")
    source_pois = load_json(source_path)
    if source_pois is None:
        results.append({"item": "Source data exist", "score": 0, "max_score": 0, "passed": False, "reason": "Cannot load data/pois.json for reference."})
        write_score(total_score, results)
        return

    pois_list = source_pois.get("pois", [])
    expected_stations = []
    for poi in pois_list:
        if poi.get("category") == "charging":
            # Include POI even if address is empty string
            name = poi.get("name", "")
            address = poi.get("address", "")
            expected_stations.append({"name": name, "address": address})
    # Sort by name alphabetically (case-sensitive, same as Python default)
    expected_stations.sort(key=lambda x: x["name"])

    # 4. Check length (20 points)
    if len(data) == len(expected_stations):
        total_score += 20
        results.append({"item": "Array length matches expected charging station count", "score": 20, "max_score": 20, "passed": True, "reason": f"Length {len(data)} correct."})
    else:
        results.append({"item": "Array length matches expected charging station count", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {len(expected_stations)} items, got {len(data)}."})

    # 5. Each object has name and address fields (10 points)
    all_have_fields = all("name" in item and "address" in item for item in data)
    if all_have_fields:
        total_score += 10
        results.append({"item": "Each object has 'name' and 'address'", "score": 10, "max_score": 10, "passed": True, "reason": "All required fields present."})
    else:
        missing_fields = [item for item in data if "name" not in item or "address" not in item]
        total_score += 0
        results.append({"item": "Each object has 'name' and 'address'", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing fields in {len(missing_fields)} item(s)."})

    # 6. Exact content match (including order) (40 points)
    # Compare after ensuring we have same length and fields
    if len(data) == len(expected_stations) and all_have_fields:
        # Build tuples for comparison
        data_sorted = sorted(data, key=lambda x: x["name"])  # sort just in case but we also check order
        if data_sorted == expected_stations and data == data_sorted:
            total_score += 40
            results.append({"item": "Exact content and order match", "score": 40, "max_score": 40, "passed": True, "reason": "All names and addresses match expected sorted order."})
        else:
            # Check if sorted version matches (order issue)
            if data_sorted == expected_stations:
                total_score += 20
                results.append({"item": "Exact content and order match", "score": 20, "max_score": 40, "passed": False, "reason": "Content matches but order is incorrect."})
            else:
                # Find mismatches
                mismatches = []
                for i, (exp, got) in enumerate(zip(expected_stations, data_sorted)):
                    if exp != got:
                        mismatches.append(f"Index {i}: expected {exp}, got {got}")
                total_score += 0
                results.append({"item": "Exact content and order match", "score": 0, "max_score": 40, "passed": False, "reason": f"Content mismatch. {len(mismatches)} errors. Example: {mismatches[0] if mismatches else 'unknown'}"})
    else:
        total_score += 0
        results.append({"item": "Exact content and order match", "score": 0, "max_score": 40, "passed": False, "reason": "Length or field check failed; cannot compare content."})

    # Write final score
    total_score = min(total_score, 100)
    write_score(total_score, results)

def write_score(total_score, details):
    output = {
        "total_score": total_score,
        "details": details
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
