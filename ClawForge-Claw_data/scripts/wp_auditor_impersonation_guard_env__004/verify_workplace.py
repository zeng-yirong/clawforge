import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    score_details = []
    total = 0

    # 1. ops directory exists (10 points)
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        score_details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found ops directory"
        })
        total += 10
    else:
        score_details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops directory not found"
        })

    # 2. denied_requests.json format (10 points)
    denied_file = ops_dir / "denied_requests.json"
    data = None
    if denied_file.is_file():
        try:
            with open(denied_file, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) and "denied_request_ids" in data and isinstance(data["denied_request_ids"], list):
                score_details.append({
                    "item": "denied_requests.json format",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": "JSON valid and has denied_request_ids list"
                })
                total += 10
            else:
                score_details.append({
                    "item": "denied_requests.json format",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": "JSON structure invalid: missing denied_request_ids or not a list"
                })
        except (json.JSONDecodeError, IOError) as e:
            score_details.append({
                "item": "denied_requests.json format",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Error reading JSON: {e}"
            })
    else:
        score_details.append({
            "item": "denied_requests.json format",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })

    # 3. Correctness of denied IDs (80 points)
    expected_ids = {"req-001", "req-003"}
    if data is not None and "denied_request_ids" in data:
        denied_ids = set(data["denied_request_ids"])
        # perfect match
        if denied_ids == expected_ids:
            score = 80
            reason = "Denied IDs exactly match expected: req-001, req-003"
        else:
            correct = denied_ids & expected_ids
            extra = denied_ids - expected_ids
            missing = expected_ids - denied_ids
            # each correct ID worth 40, each wrong (extra or missing) costs 40
            raw = len(correct) * 40 - (len(extra) + len(missing)) * 40
            score = max(0, raw)
            parts = []
            if correct:
                parts.append(f"Correct IDs: {sorted(correct)}")
            if extra:
                parts.append(f"Extra IDs: {sorted(extra)}")
            if missing:
                parts.append(f"Missing IDs: {sorted(missing)}")
            reason = "; ".join(parts) if parts else "No match"
        score_details.append({
            "item": "denied request IDs correctness",
            "score": score,
            "max_score": 80,
            "passed": (score == 80),
            "reason": reason
        })
        total += score
    else:
        score_details.append({
            "item": "denied request IDs correctness",
            "score": 0,
            "max_score": 80,
            "passed": False,
            "reason": "Cannot evaluate because file missing or invalid"
        })

    total_score = min(100, total)
    result = {
        "total_score": total_score,
        "details": score_details
    }
    output_path = ws / "workplace_score.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total_score}")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
