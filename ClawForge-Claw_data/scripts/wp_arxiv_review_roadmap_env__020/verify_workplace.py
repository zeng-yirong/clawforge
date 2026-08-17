import sys
import json
import os

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    details = []
    total_score = 0

    # 1. Check directory structure (5 points)
    ops_dir = os.path.join(WORKSPACE, "ops")
    if os.path.isdir(ops_dir):
        details.append({
            "item": "ops directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/ directory found"
        })
        total_score += 5
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    # 2. review_summary.json exists (10 points)
    result_path = os.path.join(ops_dir, "review_summary.json") if os.path.isdir(ops_dir) else None
    if result_path and os.path.isfile(result_path):
        details.append({
            "item": "review_summary.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found at ops/review_summary.json"
        })
        total_score += 10
    else:
        details.append({
            "item": "review_summary.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/review_summary.json not found"
        })
        # Cannot proceed further
        score_info = {"total_score": total_score, "details": details}
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump(score_info, f, indent=2)
        return

    # 3. JSON is valid and contains required top-level fields (10 points)
    try:
        data = load_json(result_path)
        if "papers" in data and "roadmap" in data:
            details.append({
                "item": "JSON has papers and roadmap fields",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Top-level keys 'papers' and 'roadmap' present"
            })
            total_score += 10
        else:
            details.append({
                "item": "JSON has papers and roadmap fields",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Missing required keys; found: {list(data.keys())}"
            })
            # end scoring if structure wrong
            score_info = {"total_score": total_score, "details": details}
            with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
                json.dump(score_info, f, indent=2)
            return
    except (json.JSONDecodeError, ValueError) as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        score_info = {"total_score": total_score, "details": details}
        with open(os.path.join(WORKSPACE, "workplace_score.json"), "w") as f:
            json.dump(score_info, f, indent=2)
        return

    papers = data["papers"]
    roadmap = data["roadmap"]

    # 4. papers array length and content (30 points total)
    expected_papers = [
        {"paper_id": "T001", "title": "Augmented Reasoning with Tool Use", "year": 2021,
         "abstract": "A framework that integrates external tools into reasoning chains."},
        {"paper_id": "T002", "title": "Tool-augmented Language Models", "year": 2022,
         "abstract": "Extends language models with dynamic tool invocation."},
        {"paper_id": "T003", "title": "Scaling Tool-Augmented Reasoning", "year": 2023,
         "abstract": "Explores scaling laws for tool-augmented reasoning systems."}
    ]
    # Check length
    if len(papers) == len(expected_papers):
        details.append({
            "item": "papers length correct",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found {len(papers)} papers (expected {len(expected_papers)})"
        })
        total_score += 10
    else:
        details.append({
            "item": "papers length correct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Found {len(papers)} papers, expected {len(expected_papers)}"
        })

    # Check each paper has required fields and matches expected data
    field_score = 0
    max_field = 20  # 10 for fields + 10 for values
    paper_fields_ok = True
    paper_values_ok = True
    for exp in expected_papers:
        match = [p for p in papers if p.get("paper_id") == exp["paper_id"]]
        if not match:
            paper_values_ok = False
            continue
        p = match[0]
        # Check fields
        for key in ["paper_id", "title", "year", "abstract"]:
            if key not in p:
                paper_fields_ok = False
        # Check values
        for key, val in exp.items():
            if p.get(key) != val:
                paper_values_ok = False
    if paper_fields_ok:
        field_score += 10
        total_score += 10
        details.append({
            "item": "all papers have required fields (paper_id, title, year, abstract)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Every paper object contains all required keys"
        })
    else:
        details.append({
            "item": "all papers have required fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Some paper objects are missing required keys"
        })
    if paper_values_ok:
        field_score += 10
        total_score += 10
        details.append({
            "item": "paper values match expected data (from env_builder)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All three papers have correct paper_id, title, year, abstract"
        })
    else:
        details.append({
            "item": "paper values match expected data",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "One or more papers have mismatched values"
        })

    # 5. papers ordered by year ascending (5 points)
    years = [p["year"] for p in papers if "year" in p]
    if years == sorted(years):
        details.append({
            "item": "papers sorted by year ascending",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Paper order is correct"
        })
        total_score += 5
    else:
        details.append({
            "item": "papers sorted by year ascending",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Years: {years}, expected sorted"
        })

    # 6. roadmap array length (10 points)
    expected_roadmap = [
        {"from": "T001", "to": "T002", "label": "builds upon"},
        {"from": "T002", "to": "T003", "label": "builds upon"}
    ]
    if len(roadmap) == len(expected_roadmap):
        details.append({
            "item": "roadmap length correct",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found {len(roadmap)} edges (expected {len(expected_roadmap)})"
        })
        total_score += 10
    else:
        details.append({
            "item": "roadmap length correct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Found {len(roadmap)} edges, expected {len(expected_roadmap)}"
        })

    # 7. roadmap edge objects have correct fields and values (20 points)
    edge_field_ok = True
    edge_value_ok = True
    # Normalize order: sort by (from, to)
    sorted_roadmap = sorted(roadmap, key=lambda e: (e.get("from", ""), e.get("to", "")))
    expected_sorted = sorted(expected_roadmap, key=lambda e: (e["from"], e["to"]))
    for i, exp_edge in enumerate(expected_sorted):
        if i >= len(sorted_roadmap):
            edge_value_ok = False
            continue
        e = sorted_roadmap[i]
        for key in ["from", "to", "label"]:
            if key not in e:
                edge_field_ok = False
        for key, val in exp_edge.items():
            if e.get(key) != val:
                edge_value_ok = False
    # fields sub-score
    if edge_field_ok:
        details.append({
            "item": "all roadmap edges have required fields (from, to, label)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Every edge object contains from, to, label"
        })
        total_score += 10
    else:
        details.append({
            "item": "all roadmap edges have required fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Some edges missing required keys"
        })
    # values sub-score
    if edge_value_ok:
        details.append({
            "item": "roadmap edge values match expected (from, to, label)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All edges have correct from, to, label"
        })
        total_score += 10
    else:
        details.append({
            "item": "roadmap edge values match expected",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "One or more edges have incorrect values"
        })

    # 8. Exclusion of interference directions (5 points)
    # Check that no paper with direction != 'tool_augmented_reasoning' appears in papers
    interference_found = False
    for p in papers:
        # original env data had T001, T002, T003 only for correct direction; but we also had E001, E002, X001 in source
        # They should not appear in output
        if p.get("paper_id") in ("E001", "E002", "X001"):
            interference_found = True
            break
    if not interference_found:
        details.append({
            "item": "no interference papers (different direction) included",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Only tool_augmented_reasoning papers present"
        })
        total_score += 5
    else:
        details.append({
            "item": "no interference papers included",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Found interference paper in output"
        })

    # Final score
    final_score = min(total_score, 100)  # cap at 100
    summary = {"total_score": final_score, "details": details}
    score_path = os.path.join(WORKSPACE, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
