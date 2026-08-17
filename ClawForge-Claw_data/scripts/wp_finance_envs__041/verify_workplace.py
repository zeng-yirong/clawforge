import os
import sys
import json
from datetime import datetime

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(rel_path):
    path = os.path.join(workspace, rel_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")
    with open(path, "r") as f:
        return json.load(f)

def get_latest_tech_earnings(earnings_data):
    tech_records = [r for r in earnings_data if r.get("ticker") == "TECH"]
    if not tech_records:
        return None
    # sort by report_date descending
    tech_records.sort(key=lambda x: datetime.strptime(x["report_date"], "%Y-%m-%d"), reverse=True)
    return tech_records[0]

def get_latest_tech_news(news_data):
    tech_news = [n for n in news_data if "TECH" in n.get("related_tickers", [])]
    if not tech_news:
        return None
    tech_news.sort(key=lambda x: datetime.strptime(x["published_at"], "%Y-%m-%dT%H:%M:%SZ"), reverse=True)
    return tech_news[0]

def main():
    details = []
    total_score = 0

    # 1. Check output file exists (10 pts)
    output_path = os.path.join(workspace, "outputs", "brief.json")
    if os.path.exists(output_path):
        details.append({"item": "output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "outputs/brief.json found"})
        total_score += 10
    else:
        details.append({"item": "output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "outputs/brief.json not found"})
        # No point checking further if file missing
        write_score(total_score, details)
        return

    # 2. Validate JSON (10 pts)
    try:
        with open(output_path, "r") as f:
            output = json.load(f)
        details.append({"item": "output JSON valid", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parses correctly"})
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({"item": "output JSON valid", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        write_score(total_score, details)
        return

    # 3. Check required fields exist (10 pts)
    required_fields = ["ticker", "latest_quarter", "revenue_actual", "eps_actual", "latest_news_headline"]
    missing = [f for f in required_fields if f not in output]
    if not missing:
        details.append({"item": "required fields present", "score": 10, "max_score": 10, "passed": True, "reason": "All fields found"})
        total_score += 10
    else:
        details.append({"item": "required fields present", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing fields: {missing}"})
        # still continue checking what we can

    # Load ground truth data from initial environment
    try:
        earnings_data = load_json("data/earnings/earnings.json").get("earnings", [])
        news_data = load_json("data/news/news.json").get("news", [])
    except Exception as e:
        details.append({"item": "load source data", "score": 0, "max_score": 0, "passed": False, "reason": f"Cannot load source data: {e}"})
        write_score(total_score, details)
        return

    latest_earnings = get_latest_tech_earnings(earnings_data)
    latest_news = get_latest_tech_news(news_data)

    if latest_earnings is None:
        details.append({"item": "ground truth earnings", "score": 0, "max_score": 0, "passed": False, "reason": "No TECH earnings found in source"})
    if latest_news is None:
        details.append({"item": "ground truth news", "score": 0, "max_score": 0, "passed": False, "reason": "No TECH news found in source"})

    # 4. Compare ticker (10 pts)
    expected_ticker = "TECH"
    actual_ticker = output.get("ticker")
    if actual_ticker == expected_ticker:
        details.append({"item": "ticker value", "score": 10, "max_score": 10, "passed": True, "reason": "ticker is TECH"})
        total_score += 10
    else:
        details.append({"item": "ticker value", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_ticker}, got {actual_ticker}"})

    # 5. Compare latest_quarter (15 pts)
    expected_quarter = latest_earnings["quarter"] if latest_earnings else "N/A"
    actual_quarter = output.get("latest_quarter")
    if actual_quarter == expected_quarter:
        details.append({"item": "latest_quarter value", "score": 15, "max_score": 15, "passed": True, "reason": f"Correct quarter: {expected_quarter}"})
        total_score += 15
    else:
        details.append({"item": "latest_quarter value", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_quarter}, got {actual_quarter}"})

    # 6. Compare revenue_actual (20 pts)
    expected_revenue = latest_earnings["revenue_actual"] if latest_earnings else None
    actual_revenue = output.get("revenue_actual")
    if expected_revenue is not None and actual_revenue == expected_revenue:
        details.append({"item": "revenue_actual value", "score": 20, "max_score": 20, "passed": True, "reason": f"Correct revenue: {expected_revenue}"})
        total_score += 20
    else:
        details.append({"item": "revenue_actual value", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_revenue}, got {actual_revenue}"})

    # 7. Compare eps_actual (20 pts)
    expected_eps = latest_earnings["eps_actual"] if latest_earnings else None
    actual_eps = output.get("eps_actual")
    # Use math.isclose for float comparison
    import math
    if expected_eps is not None and isinstance(actual_eps, (int, float)) and math.isclose(actual_eps, expected_eps, rel_tol=1e-9):
        details.append({"item": "eps_actual value", "score": 20, "max_score": 20, "passed": True, "reason": f"Correct EPS: {expected_eps}"})
        total_score += 20
    else:
        details.append({"item": "eps_actual value", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_eps}, got {actual_eps}"})

    # 8. Compare latest_news_headline (15 pts)
    expected_headline = latest_news["headline"] if latest_news else "N/A"
    actual_headline = output.get("latest_news_headline")
    if actual_headline == expected_headline:
        details.append({"item": "latest_news_headline value", "score": 15, "max_score": 15, "passed": True, "reason": f"Correct headline: {expected_headline}"})
        total_score += 15
    else:
        details.append({"item": "latest_news_headline value", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_headline}, got {actual_headline}"})

    # Ensure total capped at 100
    total_score = min(total_score, 100)
    write_score(total_score, details)

def write_score(total, details):
    score_data = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(score_data, f, indent=2)
    print(f"Score written: {total}/100")

if __name__ == "__main__":
    main()
