import sys
import os
import json

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # ------------------------------------------------------------
    # 1. cache directory exists
    # ------------------------------------------------------------
    cache_dir = os.path.join(workspace, "cache")
    if os.path.isdir(cache_dir):
        details.append({
            "item": "cache directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "cache/ found"
        })
        total_score += 5
    else:
        details.append({
            "item": "cache directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "cache/ directory missing"
        })

    # ------------------------------------------------------------
    # 2. cache/citation_graph.json file exists
    # ------------------------------------------------------------
    graph_path = os.path.join(cache_dir, "citation_graph.json") if os.path.isdir(cache_dir) else os.path.join(workspace, "cache", "citation_graph.json")
    # safe fallback: just try the normal path
    graph_path = os.path.join(workspace, "cache", "citation_graph.json")
    if os.path.isfile(graph_path):
        details.append({
            "item": "citation_graph.json file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found {graph_path}"
        })
        total_score += 10
    else:
        details.append({
            "item": "citation_graph.json file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "cache/citation_graph.json not found"
        })
        # early exit, cannot proceed
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    # ------------------------------------------------------------
    # 3. JSON is valid
    # ------------------------------------------------------------
    try:
        with open(graph_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON is valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully"
        })
        total_score += 10
    except Exception as e:
        details.append({
            "item": "JSON is valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    # ------------------------------------------------------------
    # 4. Contains 'edges' key and it's a list
    # ------------------------------------------------------------
    if isinstance(data, dict) and "edges" in data and isinstance(data["edges"], list):
        details.append({
            "item": "Contains 'edges' list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Found edges key with list value"
        })
        total_score += 10
    else:
        details.append({
            "item": "Contains 'edges' list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Missing or invalid 'edges' field"
        })
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    # ------------------------------------------------------------
    # 5. Each edge is dict with source and target
    # ------------------------------------------------------------
    edges_ok = True
    for i, edge in enumerate(data["edges"]):
        if not isinstance(edge, dict) or "source" not in edge or "target" not in edge:
            edges_ok = False
            break
    if edges_ok:
        details.append({
            "item": "Edge format validity",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All edges contain source and target strings"
        })
        total_score += 10
    else:
        details.append({
            "item": "Edge format validity",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Some edges missing source/target or not dict"
        })
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    # ------------------------------------------------------------
    # 6. Correct total number of edges
    # ------------------------------------------------------------
    expected_count = 7
    actual_count = len(data["edges"])
    if actual_count == expected_count:
        details.append({
            "item": "Total edge count",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": f"Exactly {expected_count} edges"
        })
        total_score += 15
    else:
        score = max(0, int(15 * (1 - abs(actual_count - expected_count) / expected_count)))
        details.append({
            "item": "Total edge count",
            "score": score,
            "max_score": 15,
            "passed": score > 0,
            "reason": f"Expected {expected_count}, got {actual_count}"
        })
        total_score += score

    # ------------------------------------------------------------
    # 7. Exactly the expected edges (set comparison)
    # ------------------------------------------------------------
    expected_edges = {
        ("p001", "p002"),
        ("p001", "p003"),
        ("p001", "p004"),
        ("p003", "p005"),
        ("p005", "p001"),
        ("p005", "p003"),
        ("p006", "p002"),
    }

    actual_edges = set()
    for e in data["edges"]:
        actual_edges.add((e["source"], e["target"]))

    missing = expected_edges - actual_edges
    extra = actual_edges - expected_edges

    if not missing and not extra:
        details.append({
            "item": "Exact edges match",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": "All 7 expected edges present, no extra edges"
        })
        total_score += 40
    else:
        penalty = 0
        if missing:
            penalty += len(missing) * 5
        if extra:
            penalty += len(extra) * 5
        score = max(0, 40 - penalty)
        details.append({
            "item": "Exact edges match",
            "score": score,
            "max_score": 40,
            "passed": score == 40,
            "reason": f"Missing: {missing if missing else 'none'} ; Extra: {extra if extra else 'none'}"
        })
        total_score += score

    # ------------------------------------------------------------
    # Finalize
    # ------------------------------------------------------------
    return {"total_score": total_score, "details": details}

def main() -> None:
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    result_path = os.path.join(workspace, "workplace_score.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {result_path} : {result['total_score']}/100")

if __name__ == "__main__":
    main()
