import sys, json, os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 1. Check ops directory exists (10 pts)
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })
        # If directory missing, fail entire test (but still record)
        # We'll continue to give feedback

    # 2. Check conflicts.json exists and is valid JSON (10 pts)
    conflicts_path = os.path.join(ops_path, "conflicts.json")
    if not os.path.isfile(conflicts_path):
        details.append({
            "item": "conflicts.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "conflicts.json not found in ops/"
        })
        # Can't proceed further; write score and exit
        _write_score(score, details)
        return
    else:
        try:
            with open(conflicts_path, "r") as f:
                data = json.load(f)
            details.append({
                "item": "conflicts.json is valid JSON",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "File is valid JSON"
            })
            score += 10
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "conflicts.json is valid JSON",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Invalid JSON: {str(e)}"
            })
            _write_score(score, details)
            return

    # 3. Check data is a list (10 pts)
    if not isinstance(data, list):
        details.append({
            "item": "data is a list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Root element is not a list"
        })
        _write_score(score, details)
        return
    else:
        details.append({
            "item": "data is a list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Root is a list"
        })
        score += 10

    # 4. Check exactly one conflict item (10 pts)
    if len(data) != 1:
        details.append({
            "item": "exactly one conflict device",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Expected 1 item, found {len(data)}"
        })
    else:
        details.append({
            "item": "exactly one conflict device",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "List contains exactly one conflict entry"
        })
        score += 10

    # 5. Check device_id (20 pts)
    conflict = data[0] if len(data) > 0 else {}
    device_id = conflict.get("device_id", "")
    if device_id == "device_001":
        details.append({
            "item": "device_id is device_001",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Correct device_id"
        })
        score += 20
    else:
        details.append({
            "item": "device_id is device_001",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected 'device_001', got '{device_id}'"
        })

    # 6. Check reason contains key health indicators (20 pts)
    reason = conflict.get("reason", "")
    keywords = ["respiratory", "humidity", "20%"]
    keyword_matches = sum(1 for kw in keywords if kw in reason)
    if keyword_matches == 3:
        details.append({
            "item": "reason contains 'respiratory', 'humidity', '20%'",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Reason includes all three key phrases"
        })
        score += 20
    else:
        missed = [kw for kw in keywords if kw not in reason]
        details.append({
            "item": "reason contains 'respiratory', 'humidity', '20%'",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Missing keywords: {', '.join(missed)}"
        })

    # 7. Check suggested_action suggests increasing humidity (20 pts)
    action = conflict.get("suggested_action", "")
    action_keywords = ["humidifier", "increase humidity", "raise humidity", "add moisture"]
    has_action = any(akw in action.lower() for akw in action_keywords)
    if has_action:
        details.append({
            "item": "suggested_action recommends increasing humidity",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Action suggests humidifier or increasing humidity"
        })
        score += 20
    else:
        details.append({
            "item": "suggested_action recommends increasing humidity",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Action '{action}' does not contain 'humidifier' or 'increase humidity'"
        })

    _write_score(score, details)

def _write_score(total, details):
    output = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    main()
