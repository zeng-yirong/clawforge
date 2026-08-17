import sys
import os
import json
import math

def verify(workspace):
    details = []
    total_score = 0

    # Paths
    output_file = os.path.join(workspace, "output", "investment_brief.json")
    stocks_file = os.path.join(workspace, "data", "stocks", "stocks.json")
    earnings_file = os.path.join(workspace, "data", "earnings", "earnings.json")
    news_file = os.path.join(workspace, "data", "news", "news.json")
    analysts_file = os.path.join(workspace, "data", "analysts", "analysts.json")
    risk_model_file = os.path.join(workspace, "data", "risk_model.md")

    # Helper to read JSON files safely
    def read_json(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            return None

    # 1. Check output file exists (10 pts)
    if os.path.exists(output_file):
        total_score += 10
        details.append({"item": "Output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "output/investment_brief.json present"})
    else:
        details.append({"item": "Output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found at output/investment_brief.json"})
        # Cannot continue without file, finalize
        return _finalize(total_score, details)

    # 2. Check file is valid JSON (10 pts)
    try:
        with open(output_file, "r") as f:
            brief = json.load(f)
        total_score += 10
        details.append({"item": "Valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "File parsed successfully"})
    except Exception as e:
        total_score += 0
        details.append({"item": "Valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {str(e)}"})
        return _finalize(total_score, details)

    # 3. Check required fields (5 pts for ticker)
    required_fields = ["ticker", "current_price", "eps_data", "news", "analysts", "risk_score"]
    missing_fields = [f for f in required_fields if f not in brief]
    if not missing_fields:
        total_score += 5
        details.append({"item": "Required fields present", "score": 5, "max_score": 5, "passed": True, "reason": "All required keys in brief"})
    else:
        total_score += 0
        details.append({"item": "Required fields present", "score": 0, "max_score": 5, "passed": False, "reason": f"Missing fields: {missing_fields}"})
        # Stop if critical fields missing
        return _finalize(total_score, details)

    # 4. Validate ticker (5 pts)
    if brief.get("ticker") == "NXTC":
        total_score += 5
        details.append({"item": "Ticker correct", "score": 5, "max_score": 5, "passed": True, "reason": "ticker is NXTC"})
    else:
        total_score += 0
        details.append({"item": "Ticker correct", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected NXTC, got {brief.get('ticker')}"})

    # 5. Validate current_price (10 pts)
    stocks_data = read_json(stocks_file)
    if stocks_data is None:
        total_score += 0
        details.append({"item": "Current price", "score": 0, "max_score": 10, "passed": False, "reason": "Cannot read stocks.json"})
    else:
        expected_price = None
        for s in stocks_data:
            if s.get("ticker") == "NXTC":
                expected_price = s.get("current_price")
                break
        got_price = brief.get("current_price")
        if expected_price is not None and got_price == expected_price:
            total_score += 10
            details.append({"item": "Current price", "score": 10, "max_score": 10, "passed": True, "reason": f"Price matches {expected_price}"})
        else:
            total_score += 0
            details.append({"item": "Current price", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {expected_price}, got {got_price}"})

    # 6. Validate eps_data (20 pts)
    earnings_data = read_json(earnings_file)
    if earnings_data is None:
        total_score += 0
        details.append({"item": "EPS data", "score": 0, "max_score": 20, "passed": False, "reason": "Cannot read earnings.json"})
    else:
        # Get expected earnings for NXTC (ignore missing eps_beat_pct records)
        expected_eps = []
        for e in earnings_data:
            if e.get("ticker") == "NXTC" and e.get("eps_beat_pct") is not None:
                expected_eps.append({
                    "quarter": e["quarter"],
                    "eps_actual": e["eps_actual"],
                    "eps_estimate": e["eps_estimate"],
                    "eps_beat": e["eps_beat"],
                    "eps_beat_pct": e["eps_beat_pct"]
                })
        # Sort by report_date (use the ordering from the data: Q1 then Q2)
        # We can sort by quarter string, or rely on original order.
        expected_eps.sort(key=lambda x: x["quarter"])
        got_eps = brief.get("eps_data", [])
        # Check length
        if len(got_eps) != len(expected_eps):
            total_score += 0
            details.append({"item": "EPS data count", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {len(expected_eps)} entries, got {len(got_eps)}"})
        else:
            eps_score = 20
            eps_issues = []
            for i, (exp, got) in enumerate(zip(expected_eps, got_eps)):
                for key in ["quarter", "eps_actual", "eps_estimate", "eps_beat", "eps_beat_pct"]:
                    if got.get(key) != exp[key]:
                        eps_score -= 4  # deduct for each mismatch
                        eps_issues.append(f"Entry {i}: {key} expected {exp[key]}, got {got.get(key)}")
                if eps_issues:
                    total_score += 0
                    details.append({"item": "EPS data content", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(eps_issues)})
                    break
            else:
                total_score += 20
                details.append({"item": "EPS data correct", "score": 20, "max_score": 20, "passed": True, "reason": "All EPS entries match"})

    # 7. Validate news (20 pts)
    news_data = read_json(news_file)
    if news_data is None:
        total_score += 0
        details.append({"item": "News data", "score": 0, "max_score": 20, "passed": False, "reason": "Cannot read news.json"})
    else:
        expected_news = []
        for n in news_data:
            if "NXTC" in n.get("related_tickers", []):
                expected_news.append({
                    "headline": n["headline"],
                    "sentiment": n["sentiment"]
                })
        # Agent may limit to up to 3; we expect exactly 3 matching NXTC news.
        expected_news = expected_news[:3]  # in case there are more, but we only have 3.
        got_news = brief.get("news", [])
        if len(got_news) != len(expected_news):
            total_score += 0
            details.append({"item": "News count", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {len(expected_news)} news items, got {len(got_news)}"})
        else:
            news_score = 20
            # Compare each (order may differ, we can match by headline)
            matched = [False] * len(expected_news)
            for got in got_news:
                found = False
                for i, exp in enumerate(expected_news):
                    if not matched[i] and got.get("headline") == exp["headline"] and got.get("sentiment") == exp["sentiment"]:
                        matched[i] = True
                        found = True
                        break
                if not found:
                    news_score -= 7  # severe mismatch
                    total_score += 0
                    details.append({"item": "News content", "score": 0, "max_score": 20, "passed": False, "reason": f"Unexpected news: {got}"})
                    break
            else:
                if all(matched):
                    total_score += 20
                    details.append({"item": "News correct", "score": 20, "max_score": 20, "passed": True, "reason": "All news items match expected"})
                else:
                    total_score += 0
                    details.append({"item": "News correct", "score": 0, "max_score": 20, "passed": False, "reason": "Some expected news missing"})

    # 8. Validate analysts (10 pts)
    analysts_data = read_json(analysts_file)
    if analysts_data is None:
        total_score += 0
        details.append({"item": "Analysts data", "score": 0, "max_score": 10, "passed": False, "reason": "Cannot read analysts.json"})
    else:
        expected_analysts = []
        for a in analysts_data:
            if "NXTC" in a.get("coverage", []):
                expected_analysts.append({
                    "name": a["name"],
                    "firm": a["firm"],
                    "rating": a["rating"]
                })
        got_analysts = brief.get("analysts", [])
        if len(got_analysts) != len(expected_analysts):
            total_score += 0
            details.append({"item": "Analysts count", "score": 0, "max_score": 10, "passed": False, "reason": f"Expected {len(expected_analysts)} analysts, got {len(got_analysts)}"})
        else:
            anal_score = 10
            for i, (exp, got) in enumerate(zip(expected_analysts, got_analysts)):
                for key in ["name", "firm", "rating"]:
                    if got.get(key) != exp[key]:
                        anal_score -= 3
                        total_score += 0
                        details.append({"item": "Analysts content", "score": 0, "max_score": 10, "passed": False, "reason": f"Mismatch on entry {i} {key}: expected {exp[key]}, got {got.get(key)}"})
                        break
            else:
                total_score += 10
                details.append({"item": "Analysts correct", "score": 10, "max_score": 10, "passed": True, "reason": "All analyst info matches"})

    # 9. Validate risk_score (15 pts)
    # Parse the risk model to get the formula (hardcoded but we can recompute)
    # Re-read earnings_data, news_data already read.
    if earnings_data is None or news_data is None:
        total_score += 0
        details.append({"item": "Risk score", "score": 0, "max_score": 15, "passed": False, "reason": "Cannot compute reference: missing earnings or news data"})
    else:
        # Compute expected risk score
        # Step 1: average eps_beat_pct for NXTC (ignore missing)
        beats = []
        for e in earnings_data:
            if e.get("ticker") == "NXTC" and e.get("eps_beat_pct") is not None:
                beats.append(e["eps_beat_pct"])
        avg_beat = sum(beats) / len(beats) if beats else 0.0

        # Step 2: news sentiment sum
        news_score = 0
        for n in news_data:
            if "NXTC" in n.get("related_tickers", []):
                if n["sentiment"] == "bullish":
                    news_score += 1
                elif n["sentiment"] == "bearish":
                    news_score -= 1
                # neutral: 0

        expected_risk = avg_beat + news_score
        # Round to 2 decimals as a reasonable tolerance
        got_risk = brief.get("risk_score")
        if got_risk is not None and math.isclose(got_risk, expected_risk, rel_tol=1e-5):
            total_score += 15
            details.append({"item": "Risk score", "score": 15, "max_score": 15, "passed": True, "reason": f"Risk score {got_risk} matches expected {expected_risk}"})
        else:
            total_score += 0
            details.append({"item": "Risk score", "score": 0, "max_score": 15, "passed": False, "reason": f"Expected {expected_risk}, got {got_risk}"})

    # Finalize
    return _finalize(total_score, details)

def _finalize(total_score, details):
    # Clamp to 0-100
    total_score = max(0, min(total_score, 100))
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
