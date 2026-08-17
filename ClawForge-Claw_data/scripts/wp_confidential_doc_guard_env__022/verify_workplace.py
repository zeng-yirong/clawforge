import sys
import json
import os

def score_workplace(workspace):
    results = []
    total_score = 0

    # Helper to add score item
    def add_item(name, score, max_score, passed, reason):
        nonlocal total_score
        results.append({"item": name, "score": score, "max_score": max_score, "passed": passed, "reason": reason})
        total_score += score

    # 1. Check required directory structure (10 points)
    required_dirs = ["ops", "data", "requests"]
    dir_ok = True
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            dir_ok = False
            break
    add_item("Directory structure", 10 if dir_ok else 0, 10, dir_ok,
             "All required directories exist" if dir_ok else f"Missing directory: {d}")

    # 2. Check that deny_targets.json exists (10 points)
    deny_path = os.path.join(workspace, "ops", "deny_targets.json")
    file_exists = os.path.isfile(deny_path)
    add_item("Deny list file exists", 10 if file_exists else 0, 10, file_exists,
             "ops/deny_targets.json exists" if file_exists else "File not found")

    if not file_exists:
        # No need to continue if file missing
        final = {"total_score": total_score, "details": results}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 3. Check JSON is valid and is a list (10 points)
    try:
        with open(deny_path, "r") as f:
            content = f.read()
        deny_list = json.loads(content)
        is_list = isinstance(deny_list, list)
        add_item("JSON format and type", 10 if is_list else 0, 10, is_list,
                 "Valid JSON array" if is_list else "Not a JSON array or invalid JSON")
    except Exception as e:
        add_item("JSON format and type", 0, 10, False, f"Failed to parse: {str(e)}")
        final = {"total_score": total_score, "details": results}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final, f, indent=2)
        return

    # 4. Check list contains exactly the three correct request IDs (40 points)
    correct_ids = {"REQ-002", "REQ-007", "REQ-011"}
    actual_ids = set(deny_list)
    # Score based on intersection and no extra
    intersection = correct_ids & actual_ids
    correct_count = len(intersection)
    extra_count = len(actual_ids - correct_ids)
    # Scoring: each correct ID gives 10 points, each extra ID or missing deducts
    # But we have a max of 40 for this item
    # Simplification: 10 points per correct ID (max 30), plus 10 for no extra
    score_correct = 10 * correct_count
    if extra_count == 0 and correct_count == 3:
        score_no_extra = 10
    elif extra_count == 0:
        score_no_extra = 5  # missing some but no extra
    else:
        score_no_extra = 0
    score_ids = min(score_correct + score_no_extra, 40)
    passed_ids = (correct_count == 3 and extra_count == 0)
    reason_ids = f"Found {correct_count}/3 correct IDs, {extra_count} extra; list: {sorted(actual_ids)}"
    add_item("Deny list content correctness", score_ids, 40, passed_ids, reason_ids)

    # 5. Additional check: each ID should be a string (bonus? We'll make it 10 pts within the remaining)
    # But we already used 10+10+10+40=70, so we have 30 left for format and consistency.
    # Let's check that the list contains only strings (10 points)
    all_strings = all(isinstance(x, str) for x in deny_list)
    add_item("All elements are strings", 10 if all_strings else 0, 10, all_strings,
             "All entries are strings" if all_strings else "Non-string found")

    # 6. Check no duplicate IDs (10 points)
    no_duplicates = len(deny_list) == len(set(deny_list))
    add_item("No duplicate IDs", 10 if no_duplicates else 0, 10, no_duplicates,
             "No duplicates" if no_duplicates else "Duplicates present")

    # 7. Check that the list is not empty and length <= 5 (10 points) — but we already checked content.
    # Instead check that the file was modified recently (not needed). Let's check that the list is sorted? Not required.
    # We can add a final check that the request IDs exist in the original requests.json (10 points)
    # This ensures agent didn't invent IDs.
    requests_path = os.path.join(workspace, "requests", "requests.json")
    if os.path.isfile(requests_path):
        try:
            with open(requests_path, "r") as f:
                req_data = json.load(f)
            req_ids_orig = {r["request_id"] for r in req_data.get("requests", [])}
            all_in_original = all(rid in req_ids_orig for rid in actual_ids)
            add_item("All IDs exist in original requests", 10 if all_in_original else 0, 10, all_in_original,
                     "All IDs present in requests.json" if all_in_original else f"Some IDs not found: {actual_ids - req_ids_orig}")
        except:
            add_item("All IDs exist in original requests", 0, 10, False, "Could not read requests.json")
    else:
        add_item("All IDs exist in original requests", 0, 10, False, "requests.json not found")

    # Ensure total does not exceed 100 (we have 10+10+10+40+10+10+10 = 100 exactly)
    final_score = min(total_score, 100)
    final = {"total_score": final_score, "details": results}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_workplace(workspace)
