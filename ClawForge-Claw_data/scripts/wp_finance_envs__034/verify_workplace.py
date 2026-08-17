"""
Verifier for wp_finance_envs__034.
Checks that agent produced output/report.json with correct fields and values.
All expected values are derived from the original data files in the workspace.
"""
import sys
import json
import os
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # --- Helper to add score item ---
    def add_item(name, score, max_score, passed, reason):
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        nonlocal total_score
        total_score += score

    # 1. Check output directory exists (5 pts)
    out_dir = os.path.join(workspace, "output")
    if os.path.isdir(out_dir):
        add_item("output/ directory exists", 5, 5, True, "Directory found")
    else:
        add_item("output/ directory exists", 0, 5, False, "Directory missing")
        # short-circuit remaining checks (can't read file)
        _write_score(total_score, details, workspace)
        return

    # 2. Check output/report.json exists (10 pts)
    report_path = os.path.join(out_dir, "report.json")
    if os.path.isfile(report_path):
        add_item("output/report.json exists", 10, 10, True, "File found")
    else:
        add_item("output/report.json exists", 0, 10, False, "File missing")
        _write_score(total_score, details, workspace)
        return

    # 3. Valid JSON (10 pts)
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        add_item("File is valid JSON", 10, 10, True, "Parsed successfully")
    except (json.JSONDecodeError, Exception) as e:
        add_item("File is valid JSON", 0, 10, False, f"Parse error: {e}")
        _write_score(total_score, details, workspace)
        return

    # Required fields
    expected_fields = [
        "ticker", "current_price", "pe_ratio", "latest_quarter",
        "eps_actual", "eps_estimate", "eps_beat_pct", "bullish_news_count"
    ]

    for field in expected_fields:
        if field in report:
            add_item(f"Field '{field}' present", 10, 10, True, f"Found key '{field}'")
        else:
            add_item(f"Field '{field}' present", 0, 10, False, f"Key '{field}' missing")
            # we continue to check others, but field check already failed

    # If any field missing, skip value verification for that field
    all_present = all(f in report for f in expected_fields)
    if not all_present:
        # still give partial credit for existing fields, but skip value checks
        _write_score(total_score, details, workspace)
        return

    # --- Compute expected values from source files ---
    # Load stocks
    stocks_path = os.path.join(workspace, "data", "stocks", "stocks.json")
    with open(stocks_path) as f:
        stocks = json.load(f)
    tech_stock = next(s for s in stocks if s["ticker"] == "TECH")
    expected_price = float(tech_stock["current_price"])
    expected_pe = float(tech_stock["pe_ratio"])

    # Load earnings
    earnings_path = os.path.join(workspace, "data", "earnings", "earnings.json")
    with open(earnings_path) as f:
        earnings = json.load(f)
    tech_earnings = [e for e in earnings if e["ticker"] == "TECH" and e["quarter"] == "Q2 2026"]
    if len(tech_earnings) != 1:
        add_item("Earnings data consistency", 0, 10, False,
                 f"Expected 1 TECH Q2 2026 record, found {len(tech_earnings)}")
        _write_score(total_score, details, workspace)
        return
    earn = tech_earnings[0]
    eps_actual = float(earn["eps_actual"])
    eps_estimate = float(earn["eps_estimate"])
    expected_eps_beat_pct = round((eps_actual - eps_estimate) / eps_estimate * 100, 2)

    # Load news
    news_path = os.path.join(workspace, "data", "news", "news.json")
    with open(news_path) as f:
        news = json.load(f)
    bull_count = sum(1 for n in news if n["sentiment"] == "bullish" and "TECH" in n.get("related_tickers", []))
    expected_bull_count = bull_count

    # --- Verify each field ---
    # ticker
    if isinstance(report.get("ticker"), str) and report["ticker"] == "TECH":
        add_item("ticker value = 'TECH'", 10, 10, True, "Correct")
    else:
        add_item("ticker value = 'TECH'", 0, 10, False, f"Got {report.get('ticker')}")

    # current_price
    r_price = report.get("current_price")
    if isinstance(r_price, (int, float)) and math.isclose(r_price, expected_price, rel_tol=1e-6):
        add_item("current_price correct", 10, 10, True, f"Expected {expected_price}, got {r_price}")
    else:
        add_item("current_price correct", 0, 10, False, f"Expected {expected_price}, got {r_price}")

    # pe_ratio
    r_pe = report.get("pe_ratio")
    if isinstance(r_pe, (int, float)) and math.isclose(r_pe, expected_pe, rel_tol=1e-6):
        add_item("pe_ratio correct", 10, 10, True, f"Expected {expected_pe}, got {r_pe}")
    else:
        add_item("pe_ratio correct", 0, 10, False, f"Expected {expected_pe}, got {r_pe}")

    # latest_quarter
    if isinstance(report.get("latest_quarter"), str) and report["latest_quarter"] == "Q2 2026":
        add_item("latest_quarter = 'Q2 2026'", 10, 10, True, "Correct")
    else:
        add_item("latest_quarter = 'Q2 2026'", 0, 10, False, f"Got {report.get('latest_quarter')}")

    # eps_actual
    r_eps_a = report.get("eps_actual")
    if isinstance(r_eps_a, (int, float)) and math.isclose(r_eps_a, eps_actual, rel_tol=1e-6):
        add_item("eps_actual correct", 10, 10, True, f"Expected {eps_actual}, got {r_eps_a}")
    else:
        add_item("eps_actual correct", 0, 10, False, f"Expected {eps_actual}, got {r_eps_a}")

    # eps_estimate
    r_eps_e = report.get("eps_estimate")
    if isinstance(r_eps_e, (int, float)) and math.isclose(r_eps_e, eps_estimate, rel_tol=1e-6):
        add_item("eps_estimate correct", 10, 10, True, f"Expected {eps_estimate}, got {r_eps_e}")
    else:
        add_item("eps_estimate correct", 0, 10, False, f"Expected {eps_estimate}, got {r_eps_e}")

    # eps_beat_pct
    r_beat = report.get("eps_beat_pct")
    if isinstance(r_beat, (int, float)) and math.isclose(r_beat, expected_eps_beat_pct, rel_tol=1e-4):
        add_item("eps_beat_pct correct", 10, 10, True, f"Expected {expected_eps_beat_pct}, got {r_beat}")
    else:
        add_item("eps_beat_pct correct", 0, 10, False, f"Expected {expected_eps_beat_pct}, got {r_beat}")

    # bullish_news_count
    r_bull = report.get("bullish_news_count")
    if isinstance(r_bull, int) and r_bull == expected_bull_count:
        add_item("bullish_news_count correct", 10, 10, True, f"Expected {expected_bull_count}, got {r_bull}")
    else:
        add_item("bullish_news_count correct", 0, 10, False, f"Expected {expected_bull_count}, got {r_bull}")

    # Write result
    _write_score(total_score, details, workspace)

def _write_score(total, details, workspace):
    final_score = min(total, 100)
    result = {
        "total_score": final_score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {final_score}/100 written to {out_path}")

if __name__ == "__main__":
    main()
