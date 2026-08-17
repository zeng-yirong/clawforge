import sys
import os
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. Check that outputs directory exists (5 pts)
    outputs_dir = os.path.join(workspace, "outputs")
    if os.path.isdir(outputs_dir):
        score_details.append({
            "item": "outputs directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Found outputs/ directory"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "outputs directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "outputs/ directory missing"
        })

    # 2. Check output file exists (10 pts)
    brief_path = os.path.join(workspace, "outputs", "investment_brief.json")
    if os.path.isfile(brief_path):
        score_details.append({
            "item": "investment_brief.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File present"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "investment_brief.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File missing"
        })
        # Cannot continue
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. Validate JSON structure (10 pts)
    try:
        with open(brief_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON decode error: {e}"
        })
        total_score += 0
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    score_details.append({
        "item": "Valid JSON",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON parsed successfully"
    })
    total_score += 10

    # 4. Required top-level keys (15 pts)
    required_keys = ["ticker", "company_name", "sector", "current_price", "pe_ratio",
                     "revenue_growth_yoy", "eps_growth_yoy", "dividend_yield",
                     "latest_earnings", "bullish_news_count", "combined_score"]
    missing_keys = [k for k in required_keys if k not in data]
    extra_keys = set(data.keys()) - set(required_keys)
    if missing_keys or extra_keys:
        reason = ""
        if missing_keys:
            reason += f"Missing: {missing_keys}. "
        if extra_keys:
            reason += f"Unexpected: {extra_keys}. "
        score_details.append({
            "item": "Required top-level keys",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": reason.strip()
        })
    else:
        score_details.append({
            "item": "Required top-level keys",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "All required keys present, no extras"
        })
        total_score += 15

    # 5. Validate specific field values (core computation, 60 pts total)

    # Sub-checks with penalties
    sub_scores = {}

    # 5a. ticker, company_name, sector
    if data.get("ticker") == "TECH" and data.get("company_name") == "TechVentures Inc" and data.get("sector") == "Technology":
        sub_scores["identity"] = {"score": 5, "max": 5, "reason": "Correct identity fields"}
    else:
        sub_scores["identity"] = {"score": 0, "max": 5, "reason": f"Got ticker={data.get('ticker')}, company={data.get('company_name')}, sector={data.get('sector')}"}

    # 5b. current_price, pe_ratio, revenue_growth_yoy, eps_growth_yoy, dividend_yield from stocks
    # Expected from env_builder for TECH: 245.30, 28.45, 15.2, 22.4, 0.65
    price = data.get("current_price")
    pe = data.get("pe_ratio")
    rev_g = data.get("revenue_growth_yoy")
    eps_g = data.get("eps_growth_yoy")
    div_y = data.get("dividend_yield")
    if (price == 245.30 and pe == 28.45 and rev_g == 15.2 and eps_g == 22.4 and div_y == 0.65):
        sub_scores["stock_fields"] = {"score": 10, "max": 10, "reason": "All stock fields match"}
    else:
        sub_scores["stock_fields"] = {"score": 0, "max": 10, "reason": f"Got price={price}, pe={pe}, rev_g={rev_g}, eps_g={eps_g}, div_y={div_y}"}

    # 5c. latest_earnings structure
    le = data.get("latest_earnings", {})
    le_required = ["quarter", "revenue_actual", "eps_actual", "revenue_beat_pct", "eps_beat_pct"]
    le_ok = all(k in le for k in le_required)
    # Check values: must be Q2 2026, revenue_actual=890000000, eps_actual=2.10, beat_pcts = 8.5 and 7.7
    le_values_ok = (
        le.get("quarter") == "Q2 2026" and
        le.get("revenue_actual") == 890000000 and
        le.get("eps_actual") == 2.10 and
        abs(le.get("revenue_beat_pct", -1) - 8.5) < 0.01 and
        abs(le.get("eps_beat_pct", -1) - 7.7) < 0.01
    )
    if le_ok and le_values_ok:
        sub_scores["latest_earnings"] = {"score": 15, "max": 15, "reason": "Correct latest earnings (Q2 2026, actual beats)"}
    else:
        sub_scores["latest_earnings"] = {"score": 0, "max": 15, "reason": f"Structure ok={le_ok}, values ok={le_values_ok}, got {le}"}

    # 5d. bullish_news_count: should be 2 (two bullish news about TECH: n_001 and n_002)
    bnc = data.get("bullish_news_count")
    if bnc == 2:
        sub_scores["bullish_news_count"] = {"score": 10, "max": 10, "reason": "Bullish news count = 2"}
    else:
        sub_scores["bullish_news_count"] = {"score": 0, "max": 10, "reason": f"Got {bnc}, expected 2"}

    # 5e. combined_score: calculation
    # Combined = 1/pe + rev_growth/100 + eps_growth/100 - div_yield/100
    # Using the correct stock values: 1/28.45 + 15.2/100 + 22.4/100 - 0.65/100
    expected_score = 1.0 / 28.45 + 15.2/100.0 + 22.4/100.0 - 0.65/100.0
    expected_score_rounded = round(expected_score, 4)
    agent_score = data.get("combined_score")
    if isinstance(agent_score, (int, float)) and abs(agent_score - expected_score_rounded) < 0.0001:
        sub_scores["combined_score"] = {"score": 20, "max": 20, "reason": f"Combined score correct ({expected_score_rounded})"}
    else:
        sub_scores["combined_score"] = {"score": 0, "max": 20, "reason": f"Got {agent_score}, expected {expected_score_rounded}"}

    # Aggregate sub scores
    for key, val in sub_scores.items():
        score_details.append({
            "item": f"Field correctness: {key}",
            "score": val["score"],
            "max_score": val["max"],
            "passed": val["score"] == val["max"],
            "reason": val["reason"]
        })
        total_score += val["score"]

    # Final score
    # Cap at 100
    total_score = min(total_score, 100)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
