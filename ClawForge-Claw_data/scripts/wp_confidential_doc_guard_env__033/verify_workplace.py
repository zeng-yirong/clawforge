import sys, os, json, re
from pathlib import Path

def verify(workspace):
    details = []
    total = 0
    max_total = 100

    ws = Path(workspace)

    # ------------------------------------------------------------
    # 1. Directory & file existence (10 points)
    # ------------------------------------------------------------
    item = "ops/deny_list.json exists"
    expected_path = ws / "ops" / "deny_list.json"
    if expected_path.exists():
        details.append({"item": item, "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total += 10
    else:
        details.append({"item": item, "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        # Cannot proceed further
        score = {"total_score": total, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score, f, indent=2)
        return

    # ------------------------------------------------------------
    # 2. JSON parse validity (10 points)
    # ------------------------------------------------------------
    item = "deny_list.json is valid JSON and contains a list"
    try:
        with open(expected_path, "r") as f:
            content = json.load(f)
        if isinstance(content, list):
            details.append({"item": item, "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON list"})
            total += 10
        else:
            details.append({"item": item, "score": 0, "max_score": 10, "passed": False, "reason": "Root is not a list"})
            total = 0
            score = {"total_score": total, "details": details}
            with open(ws / "workplace_score.json", "w") as f:
                json.dump(score, f, indent=2)
            return
    except Exception as e:
        details.append({"item": item, "score": 0, "max_score": 10, "passed": False, "reason": f"JSON error: {str(e)}"})
        total = 0
        score = {"total_score": total, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(score, f, indent=2)
        return

    # ------------------------------------------------------------
    # 3. Only request_id strings, no extra fields (10 points)
    # ------------------------------------------------------------
    item = "List contains only string request IDs, no extra keys"
    all_strings = all(isinstance(x, str) for x in content)
    if all_strings:
        details.append({"item": item, "score": 10, "max_score": 10, "passed": True, "reason": "All elements are strings"})
        total += 10
    else:
        details.append({"item": item, "score": 0, "max_score": 10, "passed": False, "reason": "Non-string or extra structure found"})

    # ------------------------------------------------------------
    # 4. Expected IDs: req_001 and req_004 (30 points)
    # ------------------------------------------------------------
    item = "List contains exactly the two required request IDs: req_001, req_004"
    expected_ids = {"req_001", "req_004"}
    actual_set = set(content)
    # Check for no extra IDs
    extra = actual_set - expected_ids
    missing = expected_ids - actual_set
    if not extra and not missing:
        details.append({"item": item, "score": 30, "max_score": 30, "passed": True, "reason": "Exactly req_001, req_004"})
        total += 30
    else:
        penalty = 0
        if missing:
            penalty += 15
        if extra:
            penalty += 15
        score = max(0, 30 - penalty)
        details.append({"item": item, "score": score, "max_score": 30, "passed": False,
                        "reason": f"Missing: {missing if missing else 'none'}; Extra: {extra if extra else 'none'}"})
        total += score

    # ------------------------------------------------------------
    # 5. No duplicates in output (10 points)
    # ------------------------------------------------------------
    item = "No duplicate request IDs in output list"
    if len(content) == len(actual_set):
        details.append({"item": item, "score": 10, "max_score": 10, "passed": True, "reason": "No duplicates"})
        total += 10
    else:
        details.append({"item": item, "score": 0, "max_score": 10, "passed": False, "reason": "Duplicates found"})

    # ------------------------------------------------------------
    # 6. Reject presence of internal/innocent requests (30 points)
    # ------------------------------------------------------------
    item = "Does NOT contain any of these wrong IDs: req_002, req_003, req_005, req_006"
    forbidden = {"req_002", "req_003", "req_005", "req_006"}
    illegal = actual_set & forbidden
    if not illegal:
        details.append({"item": item, "score": 30, "max_score": 30, "passed": True, "reason": "No forbidden IDs"})
        total += 30
    else:
        penalty = len(illegal) * 10
        score = max(0, 30 - penalty)
        details.append({"item": item, "score": score, "max_score": 30, "passed": False,
                        "reason": f"Illegal IDs present: {illegal}"})
        total += score

    # ------------------------------------------------------------
    # Final score
    # ------------------------------------------------------------
    # Cap at 100
    total = min(total, 100)
    result = {"total_score": total, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
