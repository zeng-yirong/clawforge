import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 1. Check that results/candidate.json exists
    candidate_path = os.path.join(workspace, "results", "candidate.json")
    if not os.path.isfile(candidate_path):
        details.append({
            "item": "results/candidate.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found."
        })
    else:
        details.append({
            "item": "results/candidate.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File exists."
        })
        # 2. Validate JSON content
        try:
            with open(candidate_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            details.append({
                "item": "Valid JSON and correct keys",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "File is not valid JSON."
            })
            # Still need to finish scoring; skip further checks
            _write_score(details, 10, max_score, workspace)
            return

        # 3. Check required keys
        if not isinstance(data, dict):
            details.append({
                "item": "Valid JSON and correct keys",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "Root is not a JSON object."
            })
            _write_score(details, 10, max_score, workspace)
            return

        required_keys = ["ticker", "eps_actual"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            details.append({
                "item": "Valid JSON and correct keys",
                "score": 5,
                "max_score": 20,
                "passed": False,
                "reason": f"Missing keys: {missing}"
            })
        else:
            details.append({
                "item": "Valid JSON and correct keys",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "Valid JSON and all required keys present."
            })

        # 4. Check ticker value (expected "TECH")
        ticker_ok = data.get("ticker") == "TECH"
        if not ticker_ok:
            details.append({
                "item": "Correct ticker (TECH)",
                "score": 0,
                "max_score": 30,
                "passed": False,
                "reason": f"Got '{data.get('ticker')}', expected 'TECH'."
            })
        else:
            details.append({
                "item": "Correct ticker (TECH)",
                "score": 30,
                "max_score": 30,
                "passed": True,
                "reason": "Ticker matches TECH."
            })

        # 5. Check eps_actual value (expected 2.45)
        # Allow small floating point tolerance (2 decimal places)
        eps = data.get("eps_actual")
        expected_eps = 2.45
        eps_ok = isinstance(eps, (int, float)) and abs(eps - expected_eps) < 0.005
        if not eps_ok:
            details.append({
                "item": "Correct eps_actual (2.45)",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": f"Got {eps}, expected {expected_eps} (±0.005)."
            })
        else:
            details.append({
                "item": "Correct eps_actual (2.45)",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": f"eps_actual = {eps}, matches expected."
            })

    # Calculate total score
    total = sum(d["score"] for d in details)
    _write_score(details, total, max_score, workspace)

def _write_score(details, total, max_score, workspace):
    result = {
        "total_score": total,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {out_path}: {total}/{max_score}")

if __name__ == "__main__":
    main()
