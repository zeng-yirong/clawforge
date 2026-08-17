import json
import os
import sys
from pathlib import Path

def verify_workplace(workspace: str):
    details = []
    total_score = 0
    max_total = 100

    # --- Item 1: Directory structure (10 pts) ---
    score = 0
    max_score = 10
    passed = False
    reasons = []
    data_emails_dir = Path(workspace) / "data" / "emails"
    ops_dir = Path(workspace) / "ops"
    
    if data_emails_dir.is_dir():
        score += 5
        reasons.append("data/emails/ exists")
    else:
        reasons.append("data/emails/ missing")
    
    if ops_dir.is_dir():
        score += 5
        reasons.append("ops/ exists")
    else:
        reasons.append("ops/ missing")
    
    if score == 10:
        passed = True
    details.append({
        "item": "Directory structure (data/emails, ops)",
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": "; ".join(reasons)
    })
    total_score += score

    # --- Item 2: Result file existence (10 pts) ---
    score = 0
    max_score = 10
    passed = False
    reasons = []
    result_file = Path(workspace) / "ops" / "archive_list.json"
    if result_file.is_file():
        score += 10
        reasons.append("ops/archive_list.json exists")
        passed = True
    else:
        reasons.append("ops/archive_list.json not found")
    details.append({
        "item": "Result file ops/archive_list.json exists",
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": "; ".join(reasons)
    })
    total_score += score

    # --- Item 3: File format valid JSON and is a list of strings (10 pts) ---
    score = 0
    max_score = 10
    passed = False
    reasons = []
    data = None
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            if all(isinstance(item, str) for item in data):
                score += 10
                reasons.append("Valid JSON list of strings")
                passed = True
            else:
                reasons.append("List contains non-string elements")
        else:
            reasons.append("Root element is not a list")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        reasons.append(f"Failed to parse JSON: {e}")
    details.append({
        "item": "Result is a valid JSON list of strings",
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": "; ".join(reasons)
    })
    total_score += score

    # --- Item 4: Correct IDs (70 pts) ---
    # Expected: all emails with labels containing "newsletter" and has_read == False.
    # We determine expected by scanning the email files.
    expected_ids = set()
    if data_emails_dir.is_dir():
        for file in data_emails_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    email = json.load(f)
                labels = email.get("labels", [])
                has_read = email.get("has_read", True)
                if "newsletter" in labels and not has_read:
                    expected_ids.add(email["id"])
            except:
                pass

    # Sort for deterministic comparison
    expected_list = sorted(expected_ids)
    actual_list = sorted(data) if data is not None else []

    score = 0
    max_score = 70
    passed = False
    reasons = []
    if set(actual_list) == set(expected_list):
        score = 70
        reasons.append(f"All correct IDs: {expected_list}")
        passed = True
    else:
        missing = [e for e in expected_list if e not in actual_list]
        extra = [e for e in actual_list if e not in expected_list]
        if missing:
            reasons.append(f"Missing IDs: {missing}")
        if extra:
            reasons.append(f"Unexpected IDs: {extra}")
        # Partial credit: match ratio based on intersection size
        if len(expected_list) > 0 or len(actual_list) > 0:
            common = len(set(actual_list) & set(expected_list))
            score = int(70 * common / max(len(expected_list), len(actual_list), 1))
            if score == 0 and common > 0:
                score = 1  # at least some match
        else:
            # both empty – should not happen in this test, but give full score
            if len(expected_list) == 0:
                score = 70
                reasons.append("No newsletter unread emails expected")
                passed = True
    if not passed and score >= 70:
        passed = True
    details.append({
        "item": "IDs match expected newsletter unread emails",
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "reason": "; ".join(reasons)
    })
    total_score += score

    # Write final score
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
