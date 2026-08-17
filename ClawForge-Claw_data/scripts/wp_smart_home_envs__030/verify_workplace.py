import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace)

    details = []
    total = 0

    # 1. Check that ops/conflicts.json exists and is valid JSON (10 pts)
    conflicts_path = workspace / "ops" / "conflicts.json"
    if not conflicts_path.exists():
        details.append({"item": "ops/conflicts.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        total = 0
        write_score(total, details, workspace)
        return
    try:
        with open(conflicts_path) as f:
            conflicts = json.load(f)
    except Exception as e:
        details.append({"item": "ops/conflicts.json is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse error: {e}"})
        total = 0
        write_score(total, details, workspace)
        return
    details.append({"item": "ops/conflicts.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists and valid JSON"})
    total += 10

    # 2. Conflicts must be a list (5 pts)
    if not isinstance(conflicts, list):
        details.append({"item": "conflicts is a list", "score": 0, "max_score": 5, "passed": False, "reason": "Root element is not a list"})
    else:
        details.append({"item": "conflicts is a list", "score": 5, "max_score": 5, "passed": True, "reason": "Root element is a list"})
        total += 5

    # 3. Must contain exactly 2 entries (the two conflict devices) (10 pts)
    if len(conflicts) != 2:
        details.append({"item": "exactly 2 conflict entries", "score": 0, "max_score": 10, "passed": False, "reason": f"Found {len(conflicts)} entries, expected 2"})
    else:
        details.append({"item": "exactly 2 conflict entries", "score": 10, "max_score": 10, "passed": True, "reason": "Correct number of conflicts"})
        total += 10

    # 4. Validate each conflict entry structure (15 pts)
    # Each must have: device_id, type, current_setting, recommended_setting
    # current_setting and recommended_setting must be dicts with appropriate keys
    entry_schema_points = 15
    if len(conflicts) == 2:
        ok = True
        reasons = []
        for i, entry in enumerate(conflicts):
            if not isinstance(entry, dict):
                ok = False
                reasons.append(f"Entry {i} is not a dict")
                continue
            if "device_id" not in entry or "type" not in entry or "current_setting" not in entry or "recommended_setting" not in entry:
                ok = False
                reasons.append(f"Entry {i} missing required fields")
                continue
            current = entry["current_setting"]
            recommended = entry["recommended_setting"]
            if not isinstance(current, dict) or not isinstance(recommended, dict):
                ok = False
                reasons.append(f"Entry {i} current_setting/recommended_setting must be dicts")
                continue
            # For air conditioner, expect temperature key; for humidifier, humidity key
            # We'll check in a more flexible way later; for now just structure
        if ok:
            details.append({"item": "each conflict entry has correct structure", "score": entry_schema_points, "max_score": entry_schema_points, "passed": True, "reason": "All entries have device_id, type, current_setting, recommended_setting"})
            total += entry_schema_points
        else:
            details.append({"item": "each conflict entry has correct structure", "score": 0, "max_score": entry_schema_points, "passed": False, "reason": "; ".join(reasons)})

    # 5. Check specific content (50 pts)
    # We expect: 
    #   - Bedroom Humidifier (dev_id: hum_bedroom) with current_humidity=60, recommended_humidity=45
    #   - Living Room AC (dev_id: ac_livingroom) with current_temperature=20, recommended_temperature=24
    # Build lookup by device_id
    if len(conflicts) == 2:
        conflict_map = {}
        for c in conflicts:
            if isinstance(c, dict) and "device_id" in c:
                conflict_map[c["device_id"]] = c

        content_score = 0
        content_max = 50
        content_reasons = []

        # Check Bedroom Humidifier
        bh = conflict_map.get("hum_bedroom")
        if bh is None:
            content_reasons.append("Missing hum_bedroom entry")
        else:
            if bh.get("type") != "humidifier":
                content_reasons.append("hum_bedroom type should be humidifier")
            else:
                cs = bh.get("current_setting", {})
                rs = bh.get("recommended_setting", {})
                if cs.get("humidity") != 60:
                    content_reasons.append(f"hum_bedroom current humidity should be 60, got {cs.get('humidity')}")
                if rs.get("humidity") != 45:
                    content_reasons.append(f"hum_bedroom recommended humidity should be 45, got {rs.get('humidity')}")

        # Check Living Room AC
        lrac = conflict_map.get("ac_livingroom")
        if lrac is None:
            content_reasons.append("Missing ac_livingroom entry")
        else:
            if lrac.get("type") != "air_conditioner":
                content_reasons.append("ac_livingroom type should be air_conditioner")
            else:
                cs = lrac.get("current_setting", {})
                rs = lrac.get("recommended_setting", {})
                if cs.get("temperature") != 20:
                    content_reasons.append(f"ac_livingroom current temperature should be 20, got {cs.get('temperature')}")
                if rs.get("temperature") != 24:
                    content_reasons.append(f"ac_livingroom recommended temperature should be 24, got {rs.get('temperature')}")

        # No other devices should appear
        unwanted = set(conflict_map.keys()) - {"hum_bedroom", "ac_livingroom"}
        if unwanted:
            content_reasons.append(f"Unexpected device(s) in conflicts: {unwanted}")

        if content_reasons:
            details.append({"item": "content correctness", "score": 0, "max_score": content_max, "passed": False, "reason": "; ".join(content_reasons)})
        else:
            details.append({"item": "content correctness", "score": content_max, "max_score": content_max, "passed": True, "reason": "All conflict entries correct"})
            total += content_max

    # Additional: ensure recommended_setting contains only the relevant parameter
    # (We already covered that implicitly)

    # Ensure no extra fields in conflict entries? Not required but bonus? Not needed.

    total = min(total, 100)
    write_score(total, details, workspace)

def write_score(total, details, workspace):
    out = {
        "total_score": total,
        "details": details
    }
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
