import sys
import os
import json
import math

def verify(workspace):
    details = []
    total_score = 0

    # Helper to add score item
    def add_item(item_name, score, max_score, passed, reason):
        details.append({
            "item": item_name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # 1. Check that reports directory exists (5 pts)
    reports_path = os.path.join(workspace, "reports")
    if os.path.isdir(reports_path):
        total_score += add_item("reports directory exists", 5, 5, True, "Directory found.")
    else:
        total_score += add_item("reports directory exists", 0, 5, False, "Directory 'reports' not found.")

    # 2. Check that tech_analysis.json exists in reports (10 pts)
    target_file = os.path.join(reports_path, "tech_analysis.json")
    if os.path.isfile(target_file):
        total_score += add_item("tech_analysis.json exists", 10, 10, True, "File found.")
    else:
        total_score += add_item("tech_analysis.json exists", 0, 10, False, "File not found.")
        # If file missing, we cannot proceed further checks
        write_score(workspace, total_score, details)
        return

    # 3. Parse JSON (10 pts)
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        total_score += add_item("JSON syntax", 10, 10, True, "Valid JSON.")
    except (json.JSONDecodeError, Exception) as e:
        total_score += add_item("JSON syntax", 0, 10, False, f"Invalid JSON: {e}")
        write_score(workspace, total_score, details)
        return

    # 4. Check required fields (ticker, latest_quarter, eps_beat_pct, bullish_high_impact_news, pe_ratio)
    required_fields = ["ticker", "latest_quarter", "eps_beat_pct", "bullish_high_impact_news", "pe_ratio"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        total_score += add_item("Required fields present", 10, 10, True, "All fields found.")
    else:
        total_score += add_item("Required fields present", 0, 10, False, f"Missing fields: {missing}")
        # Can still check existing fields but skip missing ones; we'll still attempt partial
        # For simplicity, stop if any missing
        write_score(workspace, total_score, details)
        return

    # 5. ticker must be "TECH" (10 pts)
    if data["ticker"] == "TECH":
        total_score += add_item("ticker value", 10, 10, True, "Correct.")
    else:
        total_score += add_item("ticker value", 0, 10, False, f"Expected 'TECH', got '{data['ticker']}'.")

    # 6. latest_quarter must be "Q2 2026" (15 pts)
    expected_quarter = "Q2 2026"
    if data["latest_quarter"] == expected_quarter:
        total_score += add_item("latest_quarter", 15, 15, True, "Correct.")
    else:
        total_score += add_item("latest_quarter", 0, 15, False, f"Expected '{expected_quarter}', got '{data['latest_quarter']}'.")

    # 7. eps_beat_pct must be 15.7 (20 pts)
    expected_eps = 15.7
    actual_eps = data["eps_beat_pct"]
    if isinstance(actual_eps, (int, float)) and math.isclose(actual_eps, expected_eps, abs_tol=1e-9):
        total_score += add_item("eps_beat_pct", 20, 20, True, "Correct.")
    else:
        total_score += add_item("eps_beat_pct", 0, 20, False, f"Expected {expected_eps}, got {actual_eps}.")

    # 8. bullish_high_impact_news must be 2 (20 pts)
    expected_news_count = 2
    actual_news = data["bullish_high_impact_news"]
    if isinstance(actual_news, int) and actual_news == expected_news_count:
        total_score += add_item("bullish_high_impact_news", 20, 20, True, "Correct.")
    else:
        total_score += add_item("bullish_high_impact_news", 0, 20, False, f"Expected {expected_news_count}, got {actual_news}.")

    # 9. pe_ratio must be 22.5 (20 pts)
    expected_pe = 22.5
    actual_pe = data["pe_ratio"]
    if isinstance(actual_pe, (int, float)) and math.isclose(actual_pe, expected_pe, abs_tol=1e-9):
        total_score += add_item("pe_ratio", 20, 20, True, "Correct.")
    else:
        total_score += add_item("pe_ratio", 0, 20, False, f"Expected {expected_pe}, got {actual_pe}.")

    write_score(workspace, total_score, details)

def write_score(workspace, total, details):
    score_obj = {
        "total_score": total,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(score_obj, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
