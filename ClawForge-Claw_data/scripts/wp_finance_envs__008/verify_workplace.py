import sys
import json
import os
from pathlib import Path

def verify(workspace):
    ws = Path(workspace)
    result_file = ws / "ops" / "tech_picks.json"

    details = []
    total_score = 0

    # 1. File exists (10 points)
    if result_file.exists():
        details.append({"item": "File existence", "score": 10, "max_score": 10, "passed": True, "reason": "ops/tech_picks.json exists"})
        total_score += 10
    else:
        details.append({"item": "File existence", "score": 0, "max_score": 10, "passed": False, "reason": "ops/tech_picks.json not found"})
        _write_score(total_score, details, workspace)
        return total_score

    # 2. Valid JSON array (10 points)
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({"item": "Valid JSON array", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON array"})
            total_score += 10
        else:
            details.append({"item": "Valid JSON array", "score": 0, "max_score": 10, "passed": False, "reason": "JSON root is not a list"})
            _write_score(total_score, details, workspace)
            return total_score
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "Valid JSON array", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {str(e)}"})
        _write_score(total_score, details, workspace)
        return total_score

    # 3. Array length (20 points)
    expected_length = 2
    if len(data) == expected_length:
        details.append({"item": "Array length", "score": 20, "max_score": 20, "passed": True, "reason": f"Length {len(data)} matches expected {expected_length}"})
        total_score += 20
    else:
        details.append({"item": "Array length", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected length {expected_length}, got {len(data)}"})

    # 4. Required fields present and non-empty (20 points)
    required_fields = ["ticker", "company_name", "pe_ratio", "revenue_growth_yoy", "news_headline", "reason"]
    field_ok = True
    for idx, item in enumerate(data):
        for field in required_fields:
            if field not in item or (isinstance(item[field], str) and len(item[field].strip()) == 0):
                field_ok = False
                break
        if not field_ok:
            break
    if field_ok and len(data) > 0:
        details.append({"item": "Required fields present and non-empty", "score": 20, "max_score": 20, "passed": True, "reason": "All required fields present"})
        total_score += 20
    else:
        details.append({"item": "Required fields present and non-empty", "score": 0, "max_score": 20, "passed": False, "reason": "Missing or empty required field in one or more entries"})

    # 5. Value correctness and ordering (40 points)
    expected_items = [
        {
            "ticker": "TEC1",
            "company_name": "TechOne Inc.",
            "pe_ratio": 15.0,
            "revenue_growth_yoy": 18.0,
            "news_headline": "TEC1 Announces Breakthrough Chip"
        },
        {
            "ticker": "TECH",
            "company_name": "TechVentures Inc",
            "pe_ratio": 22.5,
            "revenue_growth_yoy": 12.3,
            "news_headline": "TECH Partners with Global Leader"
        }
    ]
    exact_ok = True
    if len(data) >= len(expected_items):
        for i, expected in enumerate(expected_items):
            actual = data[i]
            for key in expected:
                if key == "news_headline":
                    if actual.get(key) != expected[key]:
                        exact_ok = False
                        break
                else:
                    if isinstance(expected[key], float):
                        if abs(actual.get(key, None) - expected[key]) > 1e-6:
                            exact_ok = False
                            break
                    else:
                        if actual.get(key) != expected[key]:
                            exact_ok = False
                            break
            if not exact_ok:
                break
    else:
        exact_ok = False

    # Check ascending PE order
    sorted_pe = sorted([item["pe_ratio"] for item in data])
    sort_ok = all(data[i]["pe_ratio"] == sorted_pe[i] for i in range(len(data)))

    if exact_ok and sort_ok:
        details.append({"item": "Value correctness and ordering", "score": 40, "max_score": 40, "passed": True, "reason": "Values match expected and sorted by PE ascending"})
        total_score += 40
    else:
        details.append({"item": "Value correctness and ordering", "score": 0, "max_score": 40, "passed": False, "reason": "Values or sorting incorrect"})

    # Write score
    _write_score(total_score, details, workspace)
    return total_score

def _write_score(total_score, details, workspace):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    score_path = Path(workspace) / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
