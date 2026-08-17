import sys
import os
import json
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    os.chdir(workspace)

    score_details = []
    total_score = 0

    # 1. Check cache directory exists (10 points)
    cache_dir = pathlib.Path("cache")
    if cache_dir.is_dir():
        score_details.append({
            "item": "Cache directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found cache/"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "Cache directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing cache/ directory"
        })

    # 2. Check citation_graph.json exists and is valid JSON (10 points)
    graph_path = cache_dir / "citation_graph.json"
    if not graph_path.exists():
        score_details.append({
            "item": "citation_graph.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })
        # Cannot continue, set remaining scores to 0 and write result
        for item in ["JSON structure", "edges list", "edge count", "edge correctness", "no extra fields"]:
            score_details.append({
                "item": item,
                "score": 0,
                "max_score": 10 if item != "edge correctness" else 40,
                "passed": False,
                "reason": "citation_graph.json missing"
            })
        write_score(score_details, sum(d['score'] for d in score_details))
        return

    try:
        with open(graph_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "citation_graph.json is valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON parsed successfully"
        })
        total_score += 10
    except json.JSONDecodeError as e:
        score_details.append({
            "item": "citation_graph.json is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        write_score(score_details, total_score)
        return

    # 3. Check JSON structure: must contain 'edges' list (10 points)
    if not isinstance(data, dict) or "edges" not in data or not isinstance(data["edges"], list):
        score_details.append({
            "item": "JSON structure contains 'edges' list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing 'edges' key or it's not a list"
        })
        write_score(score_details, total_score)
        return
    else:
        score_details.append({
            "item": "JSON structure contains 'edges' list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found 'edges' as list"
        })
        total_score += 10

    edges = data["edges"]

    # 4. Check that each edge is a dict with source/target (5 points) and no extra fields (5 points) = 10 points
    structure_ok = True
    extra_fields = False
    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            structure_ok = False
            break
        if set(edge.keys()) != {"source", "target"}:
            extra_fields = True
    if not structure_ok:
        score_details.append({
            "item": "Edge entries are dicts with source/target",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "One or more edges not dict or missing keys"
        })
        write_score(score_details, total_score)
        return
    if extra_fields:
        score_details.append({
            "item": "Edge entries have no extra fields",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Some edges contain extra fields beyond source/target"
        })
        write_score(score_details, total_score)
        return
    else:
        score_details.append({
            "item": "Edge entries are dicts with only source/target",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All edges are proper {source, target} pairs"
        })
        total_score += 10

    # 5. Check edge count: expected 5 edges (20 points)
    expected_count = 5
    actual_count = len(edges)
    if actual_count == expected_count:
        score_details.append({
            "item": "Edge count matches expected (5)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Exactly {expected_count} edges"
        })
        total_score += 20
    else:
        score_details.append({
            "item": "Edge count matches expected (5)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"Expected {expected_count}, got {actual_count}"
        })

    # 6. Check edge correctness (only valid citations, sorted, deduplicated) (40 points)
    # Build expected set of (source, target) after dedup & sort
    # Valid papers: paper_001, paper_002, paper_003
    valid_ids = {"paper_001", "paper_002", "paper_003"}
    expected_edges = set()
    # Compute from papers.json (we read it again to be independent)
    papers_path = pathlib.Path("data/papers/papers.json")
    if not papers_path.exists():
        score_details.append({
            "item": "Edge content correctness",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "data/papers/papers.json not found, cannot verify"
        })
        write_score(score_details, total_score)
        return
    with open(papers_path, "r") as f:
        papers_data = json.load(f)
    for paper in papers_data.get("papers", []):
        src = paper["paper_id"]
        for tgt in paper["citation_ids"]:
            if tgt in valid_ids:
                expected_edges.add((src, tgt))
    # Sort as required: by source then target
    sorted_expected = sorted(expected_edges, key=lambda x: (x[0], x[1]))

    actual_edges_set = set()
    for e in edges:
        actual_edges_set.add((e["source"], e["target"]))

    # Check duplicates: actual edges should have no duplicates
    if len(actual_edges_set) != len(edges):
        score_details.append({
            "item": "Edge content correctness",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "Edges contain duplicates (should be deduplicated)"
        })
        write_score(score_details, total_score)
        return

    # Check that actual set equals expected set
    if actual_edges_set != expected_edges:
        missing = expected_edges - actual_edges_set
        extra = actual_edges_set - expected_edges
        reason_parts = []
        if missing:
            reason_parts.append(f"Missing edges: {missing}")
        if extra:
            reason_parts.append(f"Extra edges: {extra}")
        score_details.append({
            "item": "Edge content correctness",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": "; ".join(reason_parts)
        })
        write_score(score_details, total_score)
        return

    # Check ordering (must be sorted)
    actual_order = [(e["source"], e["target"]) for e in edges]
    if actual_order != sorted_expected:
        score_details.append({
            "item": "Edge content correctness",
            "score": 10,
            "max_score": 40,
            "passed": False,
            "reason": "Edges not sorted in required order (by source then target)"
        })
        write_score(score_details, total_score)
        return

    # All checks pass for content
    score_details.append({
        "item": "Edge content correctness",
        "score": 40,
        "max_score": 40,
        "passed": True,
        "reason": "All edges correct, deduplicated, and sorted"
    })
    total_score += 40

    # Write final score
    write_score(score_details, total_score)

def write_score(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
