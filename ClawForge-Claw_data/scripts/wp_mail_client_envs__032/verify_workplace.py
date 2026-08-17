"""
Verify that the agent produced ops/urgent_ids.json with the correct two email IDs.
Scoring:
- ops directory exists: 5
- ops/urgent_ids.json exists: 10
- valid JSON: 10
- contains exactly 2 IDs: 20
- each ID is correct (25 each): 50
Total: 100
"""
import sys, os, json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_score = 100
    details = []

    # 1. ops directory exists
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ missing"})

    # 2. ops/urgent_ids.json exists
    target_file = os.path.join(workspace, "ops", "urgent_ids.json")
    if os.path.isfile(target_file):
        details.append({"item": "urgent_ids.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
        score += 10
    else:
        details.append({"item": "urgent_ids.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "file missing"})
        # If file missing, we cannot check further; output partial score
        final = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. valid JSON
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        details.append({"item": "valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "JSON parse OK"})
        score += 10
    except Exception as e:
        details.append({"item": "valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse failed: {e}"})
        final = {"total_score": score, "details": details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 4. must be a list of exactly 2 IDs
    if not isinstance(data, list):
        details.append({"item": "content is a list", "score": 0, "max_score": 20, "passed": False, "reason": "not a list"})
        score += 0
        # skip further checks
    else:
        if len(data) == 2:
            details.append({"item": "exactly 2 items", "score": 20, "max_score": 20, "passed": True, "reason": f"contains {len(data)} IDs"})
            score += 20
        else:
            details.append({"item": "exactly 2 items", "score": 0, "max_score": 20, "passed": False, "reason": f"expected 2, got {len(data)}"})

        # 5. Check IDs (order-independent)
        expected = {"e001", "e002"}
        actual = set(str(x) for x in data)
        correct = expected == actual
        if correct:
            details.append({"item": "correct IDs (e001, e002)", "score": 50, "max_score": 50, "passed": True, "reason": "IDs match expected"})
            score += 50
        else:
            details.append({"item": "correct IDs (e001, e002)", "score": 0, "max_score": 50, "passed": False, "reason": f"got {actual}, expected {expected}"})

    # Write out score file
    final = {"total_score": score, "details": details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    main()
