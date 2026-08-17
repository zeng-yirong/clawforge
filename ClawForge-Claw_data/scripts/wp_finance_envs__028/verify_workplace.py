import sys
import os
import json
import math

def verify(workspace: str) -> dict:
    details = []
    total_score = 0

    # 1. Check reports/average_pe.json exists (10 points)
    report_path = os.path.join(workspace, "reports", "average_pe.json")
    item = {"item": "File reports/average_pe.json exists", "max_score": 10}
    if os.path.isfile(report_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "File found"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "File not found"
    details.append(item)
    total_score += item["score"]

    if not item["passed"]:
        # No file to validate, remaining items get 0
        for name, max_s in [("JSON format & keys", 10), ("Ticker list correctness", 20), ("Average P/E accuracy", 60)]:
            details.append({"item": name, "score": 0, "max_score": max_s, "passed": False, "reason": "Missing input file"})
        return {"total_score": total_score, "details": details}

    # 2. Validate JSON format and required keys (10 points)
    item2 = {"item": "JSON valid and contains 'tickers' and 'average_pe'", "max_score": 10}
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict) and "tickers" in data and "average_pe" in data:
            item2["score"] = 10
            item2["passed"] = True
            item2["reason"] = "Valid JSON with required keys"
        else:
            item2["score"] = 0
            item2["passed"] = False
            item2["reason"] = "Missing required keys or wrong structure"
    except Exception as e:
        item2["score"] = 0
        item2["passed"] = False
        item2["reason"] = f"JSON parse error: {str(e)}"
    details.append(item2)
    total_score += item2["score"]

    if not item2["passed"]:
        for name, max_s in [("Ticker list correctness", 20), ("Average P/E accuracy", 60)]:
            details.append({"item": name, "score": 0, "max_score": max_s, "passed": False, "reason": "Invalid JSON or missing keys"})
        return {"total_score": total_score, "details": details}

    # 3. Verify ticker list (20 points)
    item3 = {"item": "Ticker list contains exactly TECH and NXTC", "max_score": 20}
    tickers = data["tickers"]
    expected_tickers = {"TECH", "NXTC"}
    actual_set = set(tickers)
    if actual_set == expected_tickers:
        item3["score"] = 20
        item3["passed"] = True
        item3["reason"] = "Correct tickers present"
    elif actual_set == expected_tickers and len(tickers) != 2:
        # This catches duplicate entries in list
        item3["score"] = 10
        item3["passed"] = True
        item3["reason"] = "Correct tickers but list may contain duplicates"
    else:
        missing = expected_tickers - actual_set
        extra = actual_set - expected_tickers
        reason_parts = []
        if missing:
            reason_parts.append(f"Missing: {missing}")
        if extra:
            reason_parts.append(f"Extra: {extra}")
        item3["score"] = 0
        item3["passed"] = False
        item3["reason"] = "; ".join(reason_parts)
    details.append(item3)
    total_score += item3["score"]

    # 4. Verify average_pe accuracy (60 points)
    expected_avg = (25.5 + 32.1) / 2  # 28.8
    item4 = {"item": "Average P/E equals 28.8 (±0.01)", "max_score": 60}
    try:
        actual_pe = data["average_pe"]
        if isinstance(actual_pe, (int, float)) and math.isclose(actual_pe, expected_avg, abs_tol=0.01):
            item4["score"] = 60
            item4["passed"] = True
            item4["reason"] = f"average_pe = {actual_pe}, expected ≈ {expected_avg}"
        else:
            item4["score"] = 0
            item4["passed"] = False
            item4["reason"] = f"average_pe = {actual_pe}, expected ≈ {expected_avg}"
    except Exception as e:
        item4["score"] = 0
        item4["passed"] = False
        item4["reason"] = f"Error reading average_pe: {str(e)}"
    details.append(item4)
    total_score += item4["score"]

    return {"total_score": min(total_score, 100), "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {result['total_score']}/100")

if __name__ == "__main__":
    main()
