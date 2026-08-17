"""
Verify that the agent produced the correct sector_score.json in the workspace.
Checks: file exists, valid JSON, correct ticker, correct score (within floating tolerance).
Graded on 100 points.
"""
import sys
import json
import math
import os


def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # 1. Check that ops directory exists (10pts)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 10
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory missing"
        })

    # 2. Check that ops/sector_score.json exists (10pts)
    score_file = os.path.join(ops_dir, "sector_score.json")
    if os.path.isfile(score_file):
        details.append({
            "item": "sector_score.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "file present"
        })
        total_score += 10
    else:
        details.append({
            "item": "sector_score.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file not found"
        })
        return {"total_score": total_score, "details": details}

    # 3. Validate JSON content (20pts)
    try:
        with open(score_file, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            details.append({
                "item": "valid JSON object",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "parsed as dict"
            })
            total_score += 20
        else:
            details.append({
                "item": "valid JSON object",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "expected dict, got " + type(data).__name__
            })
            return {"total_score": total_score, "details": details}
    except (json.JSONDecodeError, ValueError) as e:
        details.append({
            "item": "valid JSON",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"JSON decode error: {e}"
        })
        return {"total_score": total_score, "details": details}

    # 4. Check ticker field (25pts)
    expected_ticker = "TECH"
    got_ticker = data.get("ticker")
    if got_ticker == expected_ticker:
        details.append({
            "item": "ticker field is TECH",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": f"ticker = '{got_ticker}'"
        })
        total_score += 25
    else:
        details.append({
            "item": "ticker field is TECH",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"expected '{expected_ticker}', got '{got_ticker}'"
        })

    # 5. Check score field (35pts) – must be 17.5 (allow ±0.01 tolerance)
    expected_score = 12.5 + 5  # eps_beat_pct 12.5 + 1 bullish news * 5
    got_score = data.get("score")
    if isinstance(got_score, (int, float)):
        if math.isclose(float(got_score), expected_score, abs_tol=1e-2):
            details.append({
                "item": "score equals 17.5",
                "score": 35,
                "max_score": 35,
                "passed": True,
                "reason": f"score = {got_score}"
            })
            total_score += 35
        else:
            details.append({
                "item": "score equals 17.5",
                "score": 0,
                "max_score": 35,
                "passed": False,
                "reason": f"expected ~17.5, got {got_score}"
            })
    else:
        details.append({
            "item": "score field numeric",
            "score": 0,
            "max_score": 35,
            "passed": False,
            "reason": f"score not numeric: {got_score}"
        })

    # total capped to 100
    total_score = min(total_score, 100)
    return {"total_score": total_score, "details": details}


def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {result['total_score']}/100")


if __name__ == "__main__":
    main()
