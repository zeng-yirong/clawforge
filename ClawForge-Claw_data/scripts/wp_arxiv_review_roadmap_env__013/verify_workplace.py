import sys
import os
import json
import re

def verify(workspace):
    errors = []
    details = []
    total_score = 0

    # Helper to add detail
    def add_detail(item, score, max_score, passed, reason):
        details.append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score

    # ------------------------------------------------------------------
    # 1. Check review.json exists (10 points)
    review_path = os.path.join(workspace, "review.json")
    if os.path.isfile(review_path):
        total_score += add_detail("review.json exists", 10, 10, True, "File found")
    else:
        total_score += add_detail("review.json exists", 0, 10, False, "File not found")
        # If missing, we cannot check further items under this file, but we continue.

    # 2. Check review.json is valid JSON (10 points)
    review_data = None
    if os.path.isfile(review_path):
        try:
            with open(review_path, "r") as f:
                review_data = json.load(f)
            total_score += add_detail("review.json valid JSON", 10, 10, True, "Parsed successfully")
        except (json.JSONDecodeError, ValueError) as e:
            total_score += add_detail("review.json valid JSON", 0, 10, False, f"Invalid JSON: {e}")
    else:
        total_score += add_detail("review.json valid JSON", 0, 10, False, "File missing")

    # If review_data is available, proceed with content checks
    if review_data is not None:
        # 3. target_direction field (5 points)
        if isinstance(review_data.get("target_direction"), str) and review_data["target_direction"] == "efficient_vision":
            total_score += add_detail("target_direction correct", 5, 5, True, "Value is 'efficient_vision'")
        else:
            total_score += add_detail("target_direction correct", 0, 5, False,
                                      f"Expected 'efficient_vision', got {review_data.get('target_direction')}")

        # 4. papers array length == 3 (10 points)
        papers = review_data.get("papers", [])
        if isinstance(papers, list) and len(papers) == 3:
            total_score += add_detail("papers list length = 3", 10, 10, True, "Found 3 papers")
        else:
            total_score += add_detail("papers list length = 3", 0, 10, False,
                                      f"Expected 3, got {len(papers) if isinstance(papers, list) else 'not a list'}")

        # 5. Each paper has required fields and correct types (10 points)
        field_ok = True
        expected_fields = {"paper_id": str, "title": str, "year": int, "keywords": list}
        for i, p in enumerate(papers):
            for field, ftype in expected_fields.items():
                if field not in p or not isinstance(p[field], ftype):
                    field_ok = False
                    break
            if not field_ok:
                break
        if field_ok:
            total_score += add_detail("paper fields and types", 10, 10, True, "All papers have correct field types")
        else:
            total_score += add_detail("paper fields and types", 0, 10, False, "Missing or wrong type in one or more papers")

        # 6. Papers sorted by year ascending, then by paper_id ascending for same year (5 points)
        sorted_ok = True
        for i in range(len(papers)-1):
            a = papers[i]
            b = papers[i+1]
            if a["year"] > b["year"]:
                sorted_ok = False
                break
            if a["year"] == b["year"] and a["paper_id"] > b["paper_id"]:
                sorted_ok = False
                break
        if sorted_ok:
            total_score += add_detail("papers sorted correctly", 5, 5, True, "Order is ascending by year then ID")
        else:
            total_score += add_detail("papers sorted correctly", 0, 5, False, "Sort order incorrect")

        # 7. Exact content of papers list (20 points)
        expected_papers = [
            {"paper_id": "p001", "title": "Efficient Vision Transformer", "year": 2020, "keywords": ["transformer", "efficiency"]},
            {"paper_id": "p003", "title": "Lightweight CNN for Mobile", "year": 2022, "keywords": ["cnn", "mobile"]},
            {"paper_id": "p005", "title": "Pruning for Edge Deployment", "year": 2023, "keywords": ["pruning", "edge"]}
        ]
        content_ok = True
        if len(papers) == 3:
            for exp, actual in zip(expected_papers, papers):
                if exp != actual:
                    content_ok = False
                    break
        else:
            content_ok = False
        if content_ok:
            total_score += add_detail("papers content matches exactly", 20, 20, True, "All three papers match expected values")
        else:
            total_score += add_detail("papers content matches exactly", 0, 20, False, "Content mismatch")

        # 8. total_papers field (5 points)
        total_papers = review_data.get("total_papers")
        if isinstance(total_papers, int) and total_papers == 3:
            total_score += add_detail("total_papers = 3", 5, 5, True, "Correct")
        else:
            total_score += add_detail("total_papers = 3", 0, 5, False, f"Expected 3, got {total_papers}")

        # 9. total_years_sum field (5 points)
        total_years_sum = review_data.get("total_years_sum")
        if isinstance(total_years_sum, int) and total_years_sum == 6065:
            total_score += add_detail("total_years_sum = 6065", 5, 5, True, "Correct")
        else:
            total_score += add_detail("total_years_sum = 6065", 0, 5, False, f"Expected 6065, got {total_years_sum}")

    else:
        # If no review data, assign 0 to content checks
        for item, max_sc in [("target_direction correct", 5),
                            ("papers list length = 3", 10),
                            ("paper fields and types", 10),
                            ("papers sorted correctly", 5),
                            ("papers content matches exactly", 20),
                            ("total_papers = 3", 5),
                            ("total_years_sum = 6065", 5)]:
            total_score += add_detail(item, 0, max_sc, False, "review.json missing or invalid")

    # ------------------------------------------------------------------
    # 10. roadmap.mmd exists (5 points)
    roadmap_path = os.path.join(workspace, "roadmap.mmd")
    if os.path.isfile(roadmap_path):
        total_score += add_detail("roadmap.mmd exists", 5, 5, True, "File found")
    else:
        total_score += add_detail("roadmap.mmd exists", 0, 5, False, "File not found")

    # 11. roadmap.mmd contains all three paper IDs (15 points)
    if os.path.isfile(roadmap_path):
        with open(roadmap_path, "r") as f:
            content = f.read()
        # Check each required ID appears as a word (not substring of larger word)
        required_ids = ["p001", "p003", "p005"]
        found_all = True
        for pid in required_ids:
            # match whole word (surrounded by non-alphanumeric or start/end)
            if not re.search(r'\b' + pid + r'\b', content):
                found_all = False
                break
        if found_all:
            total_score += add_detail("roadmap.mmd contains all paper IDs", 15, 15, True, "p001, p003, p005 found")
        else:
            total_score += add_detail("roadmap.mmd contains all paper IDs", 0, 15, False, "Missing one or more IDs")
    else:
        total_score += add_detail("roadmap.mmd contains all paper IDs", 0, 15, False, "File missing")

    # ------------------------------------------------------------------
    # Ensure total_score is integer between 0 and 100
    total_score = min(max(total_score, 0), 100)

    result = {
        "total_score": total_score,
        "details": details
    }

    # Write workplace_score.json
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification complete. Total score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
