import os
import sys
import json
import re

def extract_ids(text):
    """Extract all paper IDs matching pattern like TAR01, EFF02 etc."""
    pattern = r'\b[A-Z]{3}\d{2}\b'
    return re.findall(pattern, text)

def score_check(condition, max_score):
    """Return (score, passed, reason) tuple."""
    if condition:
        return max_score, True, "Passed"
    return 0, False, "Failed"

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    max_total = 100

    # Expected IDs (sorted by year then paper_id)
    expected_ids = ['TAR05', 'TAR01', 'TAR02', 'TAR04', 'TAR03']

    # Check output directory exists
    output_dir = os.path.join(workspace, "output")
    dir_exists = os.path.isdir(output_dir)
    s, p, r = score_check(dir_exists, 5)
    total_score += s
    details.append({"item": "output directory exists", "score": s, "max_score": 5, "passed": p, "reason": r})

    # Check review.md exists
    review_path = os.path.join(output_dir, "review.md")
    review_exists = os.path.isfile(review_path)
    s, p, r = score_check(review_exists, 10)
    total_score += s
    details.append({"item": "review.md exists", "score": s, "max_score": 10, "passed": p, "reason": r})

    # Check roadmap.md exists
    roadmap_path = os.path.join(output_dir, "roadmap.md")
    roadmap_exists = os.path.isfile(roadmap_path)
    s, p, r = score_check(roadmap_exists, 10)
    total_score += s
    details.append({"item": "roadmap.md exists", "score": s, "max_score": 10, "passed": p, "reason": r})

    # If both files exist, analyze content
    review_ids = []
    roadmap_ids = []
    if review_exists:
        with open(review_path, 'r') as f:
            review_content = f.read()
        review_ids = extract_ids(review_content)
    if roadmap_exists:
        with open(roadmap_path, 'r') as f:
            roadmap_content = f.read()
        roadmap_ids = extract_ids(roadmap_content)

    # Review ID set correctness (ignoring order)
    review_set_correct = set(review_ids) == set(expected_ids)
    s, p, r = score_check(review_set_correct, 15)
    total_score += s
    details.append({"item": "review.md contains exactly expected IDs (set)", "score": s, "max_score": 15, "passed": p, "reason": r})

    # Review ID order correctness
    review_order_correct = review_ids == expected_ids
    s, p, r = score_check(review_order_correct, 20)
    total_score += s
    details.append({"item": "review.md IDs in correct chronological order", "score": s, "max_score": 20, "passed": p, "reason": r})

    # Roadmap ID set correctness
    roadmap_set_correct = set(roadmap_ids) == set(expected_ids)
    s, p, r = score_check(roadmap_set_correct, 15)
    total_score += s
    details.append({"item": "roadmap.md contains exactly expected IDs (set)", "score": s, "max_score": 15, "passed": p, "reason": r})

    # Roadmap ID order correctness
    roadmap_order_correct = roadmap_ids == expected_ids
    s, p, r = score_check(roadmap_order_correct, 20)
    total_score += s
    details.append({"item": "roadmap.md IDs in correct chronological order", "score": s, "max_score": 20, "passed": p, "reason": r})

    # Bonus: review and roadmap IDs match exactly (order and set)
    both_match = review_ids == roadmap_ids
    s, p, r = score_check(both_match, 5)
    total_score += s
    details.append({"item": "review.md and roadmap.md ID lists are identical", "score": s, "max_score": 5, "passed": p, "reason": r})

    # Ensure total does not exceed max
    total_score = min(total_score, max_total)

    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
