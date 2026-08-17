import sys
import os
import json
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    max_total = 100

    def add_item(name, score_val, max_val, passed, reason):
        nonlocal score
        details.append({
            "item": name,
            "score": score_val,
            "max_score": max_val,
            "passed": passed,
            "reason": reason
        })
        score += score_val

    # 1. output/review.json exists
    review_path = os.path.join(workspace, "output", "review.json")
    if not os.path.isfile(review_path):
        add_item("Output file existence", 0, 10, False, "output/review.json not found.")
        # cannot proceed
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return
    else:
        add_item("Output file existence", 10, 10, True, "output/review.json exists.")

    # 2. Valid JSON
    try:
        with open(review_path) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        add_item("Valid JSON", 0, 10, False, "File is not valid JSON.")
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": score, "details": details}, f, indent=2)
        return
    add_item("Valid JSON", 10, 10, True, "File is valid JSON.")

    # 3. Top-level fields present
    required_fields = ["direction", "papers", "roadmap"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        add_item("Top-level fields present", 0, 10, False, f"Missing fields: {missing}")
    else:
        add_item("Top-level fields present", 10, 10, True, "All required fields present.")

    # 4. Direction value
    expected_direction = "tool_augmented_reasoning"
    if data.get("direction") == expected_direction:
        add_item("Direction value", 10, 10, True, f"Direction is '{expected_direction}'.")
    else:
        add_item("Direction value", 0, 10, False, f"Expected '{expected_direction}', got '{data.get('direction')}'.")

    # 5. Papers list – IDs and content
    papers = data.get("papers", [])
    expected_ids = {"p001", "p002", "p003"}
    actual_ids = set(p.get("paper_id") for p in papers)
    missing_ids = expected_ids - actual_ids
    extra_ids = actual_ids - expected_ids
    if missing_ids or extra_ids:
        add_item("Papers list IDs", 0, 15, False,
                 f"Missing IDs: {missing_ids}, Extra IDs: {extra_ids}")
    else:
        # Check each paper has required subfields
        all_have_fields = all(
            all(k in p for k in ("paper_id", "title", "year"))
            for p in papers
        )
        if not all_have_fields:
            add_item("Papers list fields", 0, 15, False,
                     "Some paper objects missing required fields (paper_id, title, year).")
        else:
            # Verify titles and years
            expected_paper_data = {
                "p001": {"title": "Augmenting Language Models with Tools", "year": 2020},
                "p002": {"title": "Toolformer: Teaching Language Models to Use Tools", "year": 2022},
                "p003": {"title": "ReAct: Synergizing Reasoning and Acting in Language Models", "year": 2022}
            }
            errors = []
            for p in papers:
                pid = p["paper_id"]
                if pid in expected_paper_data:
                    exp = expected_paper_data[pid]
                    if p["title"] != exp["title"]:
                        errors.append(f"{pid} title mismatch")
                    if p["year"] != exp["year"]:
                        errors.append(f"{pid} year mismatch")
            if errors:
                add_item("Papers list content", 0, 15, False, "; ".join(errors))
            else:
                add_item("Papers list content", 15, 15, True,
                         "All paper IDs, titles, years correct.")

    # 6. Roadmap citation edges
    roadmap = data.get("roadmap", "")
    roadmap_clean = re.sub(r'\s+', '', roadmap)
    roadmap_clean = re.sub(r'->', '-->', roadmap_clean)
    expected_edges = ["p001-->p002", "p001-->p003", "p002-->p003"]
    missing_edges = [e for e in expected_edges if e not in roadmap_clean]
    if missing_edges:
        add_item("Roadmap citation edges", 0, 20, False,
                 f"Missing edges: {missing_edges}. Cleaned roadmap: {roadmap_clean}")
    else:
        add_item("Roadmap citation edges", 20, 20, True,
                 "All three expected edges found.")

    # Write final score
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
