import sys, os, json, math

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    details = []

    # Helper to construct full path
    def wpath(*parts):
        return os.path.join(workspace, *parts)

    # 1. Check reports directory exists (10 pts)
    reports_dir = wpath("reports")
    if os.path.isdir(reports_dir):
        details.append({"item": "reports directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "reports/ found"})
        total_score += 10
    else:
        details.append({"item": "reports directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "reports/ missing"})

    # 2. Check analysis_TECH.json exists (10 pts)
    target = wpath("reports", "analysis_TECH.json")
    if os.path.isfile(target):
        details.append({"item": "analysis_TECH.json present", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        total_score += 10
    else:
        details.append({"item": "analysis_TECH.json present", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # short-circuit if file missing, rest will fail
        with open(wpath("workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. JSON validity (10 pts)
    try:
        with open(target, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON is valid", "score": 10, "max_score": 10, "passed": True, "reason": "parse succeeded"})
        total_score += 10
    except (json.JSONDecodeError, ValueError) as e:
        details.append({"item": "JSON is valid", "score": 0, "max_score": 10, "passed": False, "reason": f"parse failed: {e}"})
        with open(wpath("workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. Required fields present (20 pts)
    required_fields = ["ticker", "company_name", "latest_earnings_date", "eps_beat_pct", "bullish_news_headlines"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        details.append({"item": "all required fields present", "score": 20, "max_score": 20, "passed": True, "reason": f"fields: {required_fields}"})
        total_score += 20
    else:
        details.append({"item": "all required fields present", "score": 0, "max_score": 20, "passed": False, "reason": f"missing fields: {missing}"})
        # still continue to give partial on other checks

    # 5. Exact ticker and company_name (10 pts)
    ticker_ok = data.get("ticker") == "TECH"
    company_ok = data.get("company_name") == "TechVentures Inc"
    if ticker_ok and company_ok:
        details.append({"item": "ticker and company_name correct", "score": 10, "max_score": 10, "passed": True, "reason": "TECH / TechVentures Inc"})
        total_score += 10
    else:
        score_here = 0
        if ticker_ok: score_here += 5
        if company_ok: score_here += 5
        details.append({"item": "ticker and company_name correct", "score": score_here, "max_score": 10, "passed": ticker_ok and company_ok, "reason": f"ticker={data.get('ticker')}, company={data.get('company_name')}"})
        total_score += score_here

    # 6. latest_earnings_date exact (15 pts)
    expected_date = "2026-07-20"
    date_ok = data.get("latest_earnings_date") == expected_date
    if date_ok:
        details.append({"item": "latest_earnings_date correct", "score": 15, "max_score": 15, "passed": True, "reason": f"date={expected_date}"})
        total_score += 15
    else:
        details.append({"item": "latest_earnings_date correct", "score": 0, "max_score": 15, "passed": False, "reason": f"got={data.get('latest_earnings_date')}, expected={expected_date}"})

    # 7. eps_beat_pct exact value (20 pts)
    expected_beat = 0.1475
    eps = data.get("eps_beat_pct")
    if isinstance(eps, (int, float)) and math.isclose(eps, expected_beat, rel_tol=1e-4):
        details.append({"item": "eps_beat_pct correct", "score": 20, "max_score": 20, "passed": True, "reason": f"value={expected_beat}"})
        total_score += 20
    else:
        details.append({"item": "eps_beat_pct correct", "score": 0, "max_score": 20, "passed": False, "reason": f"got={eps}, expected={expected_beat}"})

    # 8. bullish_news_headlines correct (15 pts)
    expected_headlines = ["TECH Launches AI-Driven Platform, Analysts Upgrade"]
    headlines = data.get("bullish_news_headlines", [])
    if isinstance(headlines, list) and len(headlines) == 1 and headlines[0] == expected_headlines[0]:
        details.append({"item": "bullish_news_headlines correct", "score": 15, "max_score": 15, "passed": True, "reason": f"headline={expected_headlines[0]}"})
        total_score += 15
    else:
        details.append({"item": "bullish_news_headlines correct", "score": 0, "max_score": 15, "passed": False, "reason": f"got={headlines}, expected={expected_headlines}"})

    # 9. Check no extra unexpected files in reports/ (10 pts) – only analysis_TECH.json allowed
    extra_files = [f for f in os.listdir(reports_dir) if f != "analysis_TECH.json"]
    if not extra_files:
        details.append({"item": "no extra files in reports/", "score": 10, "max_score": 10, "passed": True, "reason": "only expected file"})
        total_score += 10
    else:
        details.append({"item": "no extra files in reports/", "score": 0, "max_score": 10, "passed": False, "reason": f"extra files: {extra_files}"})

    # Write final score
    final_score = min(total_score, 100)
    with open(wpath("workplace_score.json"), "w") as f:
        json.dump({"total_score": final_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    verify()
