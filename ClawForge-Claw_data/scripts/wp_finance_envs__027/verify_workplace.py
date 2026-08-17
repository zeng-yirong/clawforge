import sys
import json
from pathlib import Path

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
result_path = Path(workspace) / "briefs" / "tech_summary.json"

details = []
total_score = 0

# 1. File existence (10 points)
if not result_path.exists():
    details.append({
        "item": "File briefs/tech_summary.json exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": "File not found"
    })
else:
    details.append({
        "item": "File briefs/tech_summary.json exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "OK"
    })

    # 2. Valid JSON (10 points)
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "Valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "OK"
        })
    except json.JSONDecodeError as e:
        data = None
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })

    # 3. Required fields present (5 points)
    if data is not None:
        required = ["ticker", "company_name", "sector", "latest_quarter",
                     "revenue_beat_pct", "eps_beat_pct", "revenue_growth_yoy",
                     "news_headline", "news_sentiment", "recommendation"]
        missing = [f for f in required if f not in data]
        if missing:
            details.append({
                "item": "All required fields present",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Missing fields: {missing}"
            })
        else:
            details.append({
                "item": "All required fields present",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "OK"
            })

            # 4. Field values correct (75 points)
            expected = {
                "ticker": "TECH",
                "company_name": "TechVentures Inc",
                "sector": "Technology",
                "latest_quarter": "Q2 2026",
                "revenue_beat_pct": 5.26,
                "eps_beat_pct": 4.17,
                "revenue_growth_yoy": 22.5,
                "news_headline": "TechVentures launches new AI platform",
                "news_sentiment": "bullish",
                "recommendation": "Buy"
            }
            errors = []
            for field, expected_val in expected.items():
                actual_val = data.get(field)
                if field in ("revenue_beat_pct", "eps_beat_pct"):
                    if not isinstance(actual_val, (int, float)):
                        errors.append(f"{field}: expected number, got {type(actual_val).__name__}")
                    elif abs(actual_val - expected_val) > 0.01:
                        errors.append(f"{field}: expected {expected_val}, got {actual_val}")
                else:
                    if actual_val != expected_val:
                        errors.append(f"{field}: expected '{expected_val}', got '{actual_val}'")
            if errors:
                details.append({
                    "item": "Field values correct",
                    "score": 0,
                    "max_score": 75,
                    "passed": False,
                    "reason": "; ".join(errors)
                })
            else:
                details.append({
                    "item": "Field values correct",
                    "score": 75,
                    "max_score": 75,
                    "passed": True,
                    "reason": "All values match expected"
                })
    else:
        # JSON was invalid, cannot check fields
        details.append({
            "item": "All required fields present",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Cannot parse JSON"
        })
        details.append({
            "item": "Field values correct",
            "score": 0,
            "max_score": 75,
            "passed": False,
            "reason": "Cannot parse JSON"
        })

# Compute total
total_score = sum(d["score"] for d in details)
max_total = sum(d["max_score"] for d in details)
# max_total should be 100, but we keep it flexible

# Write score
score_path = Path(workspace) / "workplace_score.json"
with open(score_path, "w") as f:
    json.dump({"total_score": total_score, "details": details}, f, indent=2)
