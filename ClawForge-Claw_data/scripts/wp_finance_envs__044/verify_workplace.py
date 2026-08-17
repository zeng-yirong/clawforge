import json
import os
import sys
import math

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    full = os.path.join(workspace, path)
    try:
        with open(full, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None

def check():
    details = []
    total_score = 0

    # 1. Directory existence (briefs/)
    briefs_dir = os.path.join(workspace, "briefs")
    dir_ok = os.path.isdir(briefs_dir)
    details.append({
        "item": "briefs directory exists",
        "score": 5 if dir_ok else 0,
        "max_score": 5,
        "passed": dir_ok,
        "reason": "Directory found" if dir_ok else "Missing briefs/ directory"
    })
    if dir_ok:
        total_score += 5

    # 2. briefs/tech_summary.json exists and is valid JSON
    summary = load_json("briefs/tech_summary.json")
    json_ok = summary is not None
    details.append({
        "item": "briefs/tech_summary.json valid JSON",
        "score": 5 if json_ok else 0,
        "max_score": 5,
        "passed": json_ok,
        "reason": "JSON parsed successfully" if json_ok else "File missing or invalid JSON"
    })
    if json_ok:
        total_score += 5
    else:
        # Cannot proceed with further checks
        return finalize(total_score, details)

    # 3. Required fields present
    required_fields = ["ticker", "company_name", "latest_news_headline", "latest_earnings_quarter",
                       "eps_beat_pct", "target_price", "recommendation"]
    missing = [f for f in required_fields if f not in summary]
    fields_ok = len(missing) == 0
    details.append({
        "item": "All required fields present",
        "score": 10 if fields_ok else 0,
        "max_score": 10,
        "passed": fields_ok,
        "reason": f"Missing fields: {missing}" if missing else "All required fields found"
    })
    if fields_ok:
        total_score += 10

    # 4. ticker == "TECH"
    ticker_ok = summary.get("ticker") == "TECH"
    details.append({
        "item": "ticker is TECH",
        "score": 10 if ticker_ok else 0,
        "max_score": 10,
        "passed": ticker_ok,
        "reason": f"Got '{summary.get('ticker')}'" if not ticker_ok else "Correct ticker"
    })
    if ticker_ok:
        total_score += 10

    # 5. company_name == "TechVentures Inc"
    name_ok = summary.get("company_name") == "TechVentures Inc"
    details.append({
        "item": "company_name is TechVentures Inc",
        "score": 10 if name_ok else 0,
        "max_score": 10,
        "passed": name_ok,
        "reason": f"Got '{summary.get('company_name')}'" if not name_ok else "Correct company name"
    })
    if name_ok:
        total_score += 10

    # 6. latest_news_headline == the most recent TECH news headline
    expected_headline = "TechVentures announces new AI partnership with GlobalTech"
    headline_ok = summary.get("latest_news_headline") == expected_headline
    details.append({
        "item": "latest_news_headline correct",
        "score": 10 if headline_ok else 0,
        "max_score": 10,
        "passed": headline_ok,
        "reason": f"Got '{summary.get('latest_news_headline')}'" if not headline_ok else "Correct headline"
    })
    if headline_ok:
        total_score += 10

    # 7. latest_earnings_quarter == "Q2 2026"
    quarter_ok = summary.get("latest_earnings_quarter") == "Q2 2026"
    details.append({
        "item": "latest_earnings_quarter is Q2 2026",
        "score": 10 if quarter_ok else 0,
        "max_score": 10,
        "passed": quarter_ok,
        "reason": f"Got '{summary.get('latest_earnings_quarter')}'" if not quarter_ok else "Correct quarter"
    })
    if quarter_ok:
        total_score += 10

    # 8. eps_beat_pct == 12.5
    eps_ok = math.isclose(summary.get("eps_beat_pct", 0), 12.5, abs_tol=0.01)
    details.append({
        "item": "eps_beat_pct is 12.5",
        "score": 10 if eps_ok else 0,
        "max_score": 10,
        "passed": eps_ok,
        "reason": f"Got {summary.get('eps_beat_pct')}" if not eps_ok else "Correct eps_beat_pct"
    })
    if eps_ok:
        total_score += 10

    # 9. target_price calculation: 245.75 * (1 + 12.5/100) * (1 + 0.18) * 1.05 (bullish sentiment)
    # Expected: 245.75 * 1.125 * 1.18 * 1.05 = 245.75 * 1.393875 = 342.66 (rounded to 2 decimals)
    expected_target = round(245.75 * 1.125 * 1.18 * 1.05, 2)
    target_ok = math.isclose(summary.get("target_price", 0), expected_target, abs_tol=0.01)
    details.append({
        "item": "target_price correct (342.66)",
        "score": 20 if target_ok else 0,
        "max_score": 20,
        "passed": target_ok,
        "reason": f"Got {summary.get('target_price')}, expected {expected_target}" if not target_ok else "Correct target price"
    })
    if target_ok:
        total_score += 20

    # 10. recommendation == "Buy" (since target_price > current_price)
    rec_ok = summary.get("recommendation") == "Buy"
    details.append({
        "item": "recommendation is Buy",
        "score": 10 if rec_ok else 0,
        "max_score": 10,
        "passed": rec_ok,
        "reason": f"Got '{summary.get('recommendation')}'" if not rec_ok else "Correct recommendation"
    })
    if rec_ok:
        total_score += 10

    return finalize(total_score, details)

def finalize(total_score, details):
    # Ensure total_score doesn't exceed 100
    total_score = min(total_score, 100)
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")
    return result

if __name__ == "__main__":
    check()
