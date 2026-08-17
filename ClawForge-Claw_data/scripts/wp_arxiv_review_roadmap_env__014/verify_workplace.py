import sys
import os
import json

def compute_expected_ids(workspace):
    """Read papers.json from workspace and apply the same selection rules as the prompt."""
    papers_path = os.path.join(workspace, "data", "papers", "papers.json")
    if not os.path.isfile(papers_path):
        return None
    with open(papers_path, "r") as f:
        data = json.load(f)
    papers = data.get("papers", [])
    valid = []
    for p in papers:
        if p.get("direction") != "tool_augmented_reasoning":
            continue
        year = p.get("year")
        if not (2022 <= year <= 2024):
            continue
        keywords = p.get("keywords", [])
        if any("obsolete" in kw.lower() for kw in keywords):
            continue
        valid.append(p["paper_id"])
    # deduplicate while preserving order
    seen = set()
    unique = []
    for pid in valid:
        if pid not in seen:
            seen.add(pid)
            unique.append(pid)
    return unique

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = {"total_score": 0, "details": []}

    # Helper to add a detail
    def add_detail(item, score, max_score, passed, reason):
        results["details"].append({
            "item": item,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # 1. Directory existence (10 points)
    report_dir = os.path.join(workspace, "report")
    if os.path.isdir(report_dir):
        add_detail("report/ directory exists", 10, 10, True, "Found report/")
    else:
        add_detail("report/ directory exists", 0, 10, False, "Missing report/")

    # 2. review.md exists (10 points)
    review_path = os.path.join(report_dir, "review.md")
    if os.path.isfile(review_path):
        add_detail("report/review.md exists", 10, 10, True, "Found review.md")
    else:
        add_detail("report/review.md exists", 0, 10, False, "Missing review.md")

    # 3. roadmap.md exists (10 points)
    roadmap_path = os.path.join(report_dir, "roadmap.md")
    if os.path.isfile(roadmap_path):
        add_detail("report/roadmap.md exists", 10, 10, True, "Found roadmap.md")
    else:
        add_detail("report/roadmap.md exists", 0, 10, False, "Missing roadmap.md")

    # 4. paper_ids.json exists and is valid JSON (10 points)
    ids_path = os.path.join(report_dir, "paper_ids.json")
    ids_loaded = None
    if os.path.isfile(ids_path):
        try:
            with open(ids_path, "r") as f:
                ids_loaded = json.load(f)
            add_detail("report/paper_ids.json exists and valid JSON", 10, 10, True, "Parsed successfully")
        except (json.JSONDecodeError, ValueError):
            add_detail("report/paper_ids.json exists and valid JSON", 0, 10, False, "Invalid JSON")
    else:
        add_detail("report/paper_ids.json exists and valid JSON", 0, 10, False, "Missing file")

    # 5. Correct ID set (60 points - main)
    expected_ids = compute_expected_ids(workspace)
    if expected_ids is None:
        add_detail("Correct paper ID set", 0, 60, False, "Cannot read data/papers/papers.json to compute expected IDs")
    elif ids_loaded is None:
        add_detail("Correct paper ID set", 0, 60, False, "Agent ID list not available")
    else:
        # Convert both to sets for comparison
        expected_set = set(expected_ids)
        actual_set = set(ids_loaded) if isinstance(ids_loaded, list) else set()
        if actual_set == expected_set:
            add_detail("Correct paper ID set", 60, 60, True,
                       f"Agent produced exactly the {len(expected_set)} expected IDs")
        elif actual_set == expected_set:
            pass
        else:
            missing = expected_set - actual_set
            extra = actual_set - expected_set
            # Partial score: max 60, lose 30 for wrong count or content
            base = 30  # half for having a list at all
            if len(actual_set) == 0:
                add_detail("Correct paper ID set", 0, 60, False,
                           "Agent produced empty list")
            else:
                # penalty for missing/extra: 30 points lost if any mismatch, otherwise keep 30-60
                if missing or extra:
                    msg = f"IDs differ. Missing {len(missing)}, Extra {len(extra)}"
                    add_detail("Correct paper ID set", base, 60, False, msg)
                else:
                    # same set (should be caught above, but for safety)
                    add_detail("Correct paper ID set", 60, 60, True, "Sets match")

    # Calculate total
    total = sum(d["score"] for d in results["details"])
    results["total_score"] = min(total, 100)  # cap at 100

    # Write output
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Verification complete. Score: {results['total_score']}/100")

if __name__ == "__main__":
    main()
