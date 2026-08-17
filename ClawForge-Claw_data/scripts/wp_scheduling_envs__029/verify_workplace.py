import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    details = []
    total_score = 0

    # 1. Check data/accounts.json exists and is valid JSON (10 pts)
    acc_path = ws / "data" / "accounts.json"
    if acc_path.exists():
        try:
            with open(acc_path) as f:
                data = json.load(f)
                if "accounts" in data and len(data["accounts"]) > 0:
                    details.append({"item": "data/accounts.json exists and valid", "score": 10, "max_score": 10, "passed": True, "reason": "File found and structure OK"})
                else:
                    details.append({"item": "data/accounts.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'accounts' key or empty"})
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "data/accounts.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
    else:
        details.append({"item": "data/accounts.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})

    # 2. Check data/devices.json exists and valid (10 pts)
    dev_path = ws / "data" / "devices.json"
    if dev_path.exists():
        try:
            with open(dev_path) as f:
                data = json.load(f)
                if "devices" in data and len(data["devices"]) > 0:
                    details.append({"item": "data/devices.json exists and valid", "score": 10, "max_score": 10, "passed": True, "reason": "File found and structure OK"})
                else:
                    details.append({"item": "data/devices.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'devices' key or empty"})
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "data/devices.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
    else:
        details.append({"item": "data/devices.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})

    # 3. Check schedules/schedules.json exists and valid (10 pts)
    sched_path = ws / "schedules" / "schedules.json"
    if sched_path.exists():
        try:
            with open(sched_path) as f:
                data = json.load(f)
                if "schedules" in data and len(data["schedules"]) >= 3:
                    details.append({"item": "schedules/schedules.json exists and valid", "score": 10, "max_score": 10, "passed": True, "reason": "File found and structure OK"})
                else:
                    details.append({"item": "schedules/schedules.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": "Missing 'schedules' key or fewer than 3 entries"})
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "schedules/schedules.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
    else:
        details.append({"item": "schedules/schedules.json exists and valid", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})

    # 4. Check ops/ directory exists (10 pts)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory present"})
    else:
        details.append({"item": "ops/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory not found"})

    # 5. Check ops/fix_target.json exists and is valid JSON (10 pts)
    fix_path = ws / "ops" / "fix_target.json"
    if fix_path.exists():
        try:
            with open(fix_path) as f:
                content = json.load(f)
                if isinstance(content, list):
                    details.append({"item": "ops/fix_target.json exists and valid JSON array", "score": 10, "max_score": 10, "passed": True, "reason": "File is valid JSON array"})
                else:
                    details.append({"item": "ops/fix_target.json exists and valid JSON array", "score": 0, "max_score": 10, "passed": False, "reason": "Content is not a JSON array"})
        except (json.JSONDecodeError, Exception) as e:
            details.append({"item": "ops/fix_target.json exists and valid JSON array", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
    else:
        details.append({"item": "ops/fix_target.json exists and valid JSON array", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})

    # 6. Check fix_target.json content contains exactly ["sch_003"] (50 pts)
    content_passed = False
    reason = ""
    if fix_path.exists():
        try:
            with open(fix_path) as f:
                content = json.load(f)
            if isinstance(content, list) and len(content) == 1 and content[0] == "sch_003":
                content_passed = True
                reason = "Contains exactly the duplicate schedule ID 'sch_003'"
            elif isinstance(content, list) and "sch_003" in content and len(content) == 1:
                # safety
                content_passed = True
                reason = "Contains exactly the duplicate schedule ID 'sch_003'"
            else:
                reason = f"Expected ['sch_003'], got {content}"
        except Exception as e:
            reason = f"Error reading file: {e}"
    else:
        reason = "File missing"
    details.append({"item": "fix_target.json content correct (duplicate ID)", "score": 50 if content_passed else 0, "max_score": 50, "passed": content_passed, "reason": reason})

    # Compute total
    total_score = sum(d["score"] for d in details)

    result = {
        "total_score": total_score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
