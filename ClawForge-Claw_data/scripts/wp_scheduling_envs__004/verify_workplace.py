"""
verify_workplace.py – Checks agent output for wp_scheduling_envs__004.
Scoring criteria:
  - ops/clean_devices.json exists (10)
  - File is valid JSON and is a list (10)
  - List has exactly 6 entries (10)
  - Each entry has all required non-empty fields: device_id, device_name, device_type, location (20)
  - No duplicate device_id (10)
  - device_type of each entry is in the allowed list (10)
  - The set of device_id matches the expected set (20)
  - For each expected device, the corresponding entry's fields match (10)
Total: 100
"""

import sys
import json
import os
from pathlib import Path

EXPECTED_DEVICES = {
    "ac_living_01": {"device_name": "Living Room AC", "device_type": "ac", "location": "living_room"},
    "light_bedroom_01": {"device_name": "Bedroom Light", "device_type": "light", "location": "bedroom"},
    "humidifier_bedroom_01": {"device_name": "Bedroom Humidifier", "device_type": "humidifier", "location": "bedroom"},
    "plug_coffee_01": {"device_name": "Coffee Machine Smart Plug", "device_type": "smart_plug", "location": "kitchen"},
    "light_living_01": {"device_name": "Living Room Light", "device_type": "light", "location": "living_room"},
    "tv_plug_01": {"device_name": "TV Smart Plug", "device_type": "smart_plug", "location": "living_room"},
}

ALLOWED_TYPES = {"ac", "humidifier", "light", "smart_plug"}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    result = {"total_score": 0, "details": []}
    score = 0

    # 1. 检查 ops/clean_devices.json 是否存在
    output_path = ws / "ops" / "clean_devices.json"
    if output_path.exists():
        score += 10
        result["details"].append({"item": "File exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/clean_devices.json found"})
    else:
        result["details"].append({"item": "File exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/clean_devices.json not found"})
        # 如果文件不存在，后续检查无法进行，直接输出结果
        result["total_score"] = score
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 2. 解析 JSON 且必须是列表
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        result["details"].append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": "File is not valid JSON"})
        result["total_score"] = score
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    if not isinstance(data, list):
        result["details"].append({"item": "Valid JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": "JSON root is not a list"})
        result["total_score"] = score
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    score += 10
    result["details"].append({"item": "Valid JSON is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Root is a list"})

    # 3. 长度必须为 6
    if len(data) == 6:
        score += 10
        result["details"].append({"item": "List length", "score": 10, "max_score": 10, "passed": True, "reason": "Exactly 6 items"})
    else:
        result["details"].append({"item": "List length", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected 6 items, got {len(data)}"})

    # 4. 检查每个条目必要字段完整（device_id, device_name, device_type, location）
    required_fields = {"device_id", "device_name", "device_type", "location"}
    all_fields_valid = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            all_fields_valid = False
            continue
        for field in required_fields:
            val = entry.get(field)
            if not isinstance(val, str) or val.strip() == "":
                all_fields_valid = False
                break
    if all_fields_valid:
        score += 20
        result["details"].append({"item": "Required fields present and non-empty", "score": 20, "max_score": 20, "passed": True, "reason": "All entries have required fields"})
    else:
        result["details"].append({"item": "Required fields present and non-empty", "score": 0, "max_score": 20, "passed": False, "reason": "Some entries missing or empty required fields"})

    # 5. 无重复 device_id
    ids = [entry.get("device_id") for entry in data if isinstance(entry, dict)]
    if len(ids) == len(set(ids)):
        score += 10
        result["details"].append({"item": "No duplicate device_id", "score": 10, "max_score": 10, "passed": True, "reason": "All device_id unique"})
    else:
        score += 0
        result["details"].append({"item": "No duplicate device_id", "score": 0, "max_score": 10, "passed": False, "reason": "Duplicate device_id found"})

    # 6. device_type 全在允许列表中
    types_ok = all(
        isinstance(entry, dict) and entry.get("device_type") in ALLOWED_TYPES
        for entry in data
    )
    if types_ok:
        score += 10
        result["details"].append({"item": "device_type in allowed set", "score": 10, "max_score": 10, "passed": True, "reason": "All device_type are valid"})
    else:
        result["details"].append({"item": "device_type in allowed set", "score": 0, "max_score": 10, "passed": False, "reason": "Some device_type not in allowed set"})

    # 7. 集合一致性：device_id 集合必须与预期完全一致
    actual_ids = set(ids)
    expected_ids = set(EXPECTED_DEVICES.keys())
    if actual_ids == expected_ids:
        score += 20
        result["details"].append({"item": "device_id set matches expected", "score": 20, "max_score": 20, "passed": True, "reason": "Correct device IDs"})
    else:
        extra = actual_ids - expected_ids
        missing = expected_ids - actual_ids
        reason = f"Extra IDs: {extra}, Missing IDs: {missing}" if extra or missing else "Sets differ"
        result["details"].append({"item": "device_id set matches expected", "score": 0, "max_score": 20, "passed": False, "reason": reason})

    # 8. 对每个预期设备，检查 device_name, device_type, location 是否一致
    # 先构建输出设备的词典
    output_by_id = {}
    for entry in data:
        if isinstance(entry, dict) and "device_id" in entry:
            output_by_id[entry["device_id"]] = entry

    fields_match = True
    for eid, efields in EXPECTED_DEVICES.items():
        out = output_by_id.get(eid)
        if out is None:
            fields_match = False
            break
        for field, expected_val in efields.items():
            if out.get(field) != expected_val:
                fields_match = False
                break
        if not fields_match:
            break

    if fields_match:
        score += 10
        result["details"].append({"item": "Expected device fields match", "score": 10, "max_score": 10, "passed": True, "reason": "All field values correct"})
    else:
        result["details"].append({"item": "Expected device fields match", "score": 0, "max_score": 10, "passed": False, "reason": "Some fields differ from expected"})

    result["total_score"] = score
    # 写入结果
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
