import json, os, sys, re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # Helper to safely compute path
    def wpath(*parts):
        return os.path.join(workspace, *parts)

    # ------------------------------------------------------------------
    # 1. Directory structure (10 points)
    # ------------------------------------------------------------------
    item = {
        "item": "Directory structure: review/ exists",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": ""
    }
    if os.path.isdir(wpath("review")):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "review directory found"
    else:
        item["reason"] = "review directory missing"
    results.append(item)
    total_score += item["score"]

    # ------------------------------------------------------------------
    # 2. File existence: review.md and roadmap.mmd (10 each = 20)
    # ------------------------------------------------------------------
    for fname, label in [("tool_augmented_reasoning_review.md", "Markdown review"),
                         ("roadmap.mmd", "Mermaid roadmap")]:
        item = {
            "item": f"File exists: review/{fname}",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": ""
        }
        fpath = wpath("review", fname)
        if os.path.isfile(fpath):
            item["score"] = 10
            item["passed"] = True
            item["reason"] = f"{label} found"
        else:
            item["reason"] = f"{label} not found at {fpath}"
        results.append(item)
        total_score += item["score"]

    # ------------------------------------------------------------------
    # 3. Markdown review content (30 points)
    #    Must contain all 5 tool-augmented-reasoning paper_ids in its body
    # ------------------------------------------------------------------
    md_item = {
        "item": "Markdown review contains all 5 required paper IDs (TAR-2020..TAR-2024)",
        "score": 0,
        "max_score": 30,
        "passed": False,
        "reason": ""
    }
    required_ids = ["TAR-2020", "TAR-2021", "TAR-2022", "TAR-2023", "TAR-2024"]
    try:
        with open(wpath("review", "tool_augmented_reasoning_review.md"), "r", encoding="utf-8") as f:
            md_content = f.read()
    except FileNotFoundError:
        md_item["reason"] = "Cannot read file"
        results.append(md_item)
        total_score += 0
    else:
        found_ids = []
        for pid in required_ids:
            if pid in md_content:
                found_ids.append(pid)
        missing = set(required_ids) - set(found_ids)
        if len(missing) == 0:
            md_item["score"] = 30
            md_item["passed"] = True
            md_item["reason"] = "All 5 paper IDs present in review"
        else:
            md_item["score"] = max(0, 30 - 10 * len(missing))  # -10 per missing ID
            md_item["reason"] = f"Missing paper IDs: {missing}"
        results.append(md_item)
        total_score += md_item["score"]

    # ------------------------------------------------------------------
    # 4. Mermaid roadmap content (40 points)
    #    Must have graph TD, all 5 paper_ids as node labels, and chronological order
    # ------------------------------------------------------------------
    mm_item = {
        "item": "Mermaid roadmap valid and contains all 5 papers in chronological order",
        "score": 0,
        "max_score": 40,
        "passed": False,
        "reason": ""
    }
    try:
        with open(wpath("review", "roadmap.mmd"), "r", encoding="utf-8") as f:
            mm_content = f.read()
    except FileNotFoundError:
        mm_item["reason"] = "Cannot read file"
        results.append(mm_item)
        total_score += 0
    else:
        # Check graph TD
        if "graph TD" not in mm_content:
            mm_item["reason"] = "Missing 'graph TD' directive"
            results.append(mm_item)
            total_score += 0
        else:
            # Extract node labels from Mermaid: e.g., TAR-2020[2020]
            node_pattern = re.compile(r'([A-Z]+-\d+)\[(\d{4})\]')
            nodes = node_pattern.findall(mm_content)
            # Check we have exactly 5 nodes, each corresponding to a required paper (by id)
            found_nodes = {pid: year for pid, year in nodes}
            missing_ids = [pid for pid in required_ids if pid not in found_nodes]
            extra_ids = [pid for pid in found_nodes if pid not in required_ids]
            # Check chronological order (by node order in file? We'll check if years are non-decreasing in order of appearance)
            # Get nodes in order they appear in file
            nodes_in_order = node_pattern.findall(mm_content)
            years_in_order = [int(year) for _, year in nodes_in_order]
            is_chronological = all(years_in_order[i] <= years_in_order[i+1] for i in range(len(years_in_order)-1))
            # Score breakdown: 20 for completeness (all 5), 20 for chronological order
            completeness_score = 20 - 4 * len(missing_ids)  # 0 if all missing
            chronological_score = 20 if is_chronological else 0
            mm_item["score"] = max(0, completeness_score + chronological_score)
            if len(missing_ids) == 0 and is_chronological and len(extra_ids) == 0:
                mm_item["passed"] = True
                mm_item["reason"] = "All 5 papers present, chronological, no extra nodes"
            else:
                reasons = []
                if missing_ids:
                    reasons.append(f"missing {missing_ids}")
                if not is_chronological:
                    reasons.append("years not in chronological order")
                if extra_ids:
                    reasons.append(f"extra nodes: {extra_ids}")
                mm_item["reason"] = "; ".join(reasons) if reasons else "unknown issue"
            results.append(mm_item)
            total_score += mm_item["score"]

    # ------------------------------------------------------------------
    # Final score capped to 100
    # ------------------------------------------------------------------
    total_score = min(total_score, max_total)
    final = {
        "total_score": total_score,
        "details": results
    }
    with open(wpath("workplace_score.json"), "w") as f:
        json.dump(final, f, indent=2)
    print(f"Verification complete. Total score: {total_score}/100")

if __name__ == "__main__":
    main()
