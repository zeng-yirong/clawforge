import sys
import os
import json

def verify_workplace(workspace):
    """
    Evaluate the agent's output for the paper citation graph task.
    Scores from 0 to 100.
    """
    total_score = 0
    details = []

    # 1. Check cache directory exists (10 points)
    cache_path = os.path.join(workspace, "cache")
    if os.path.isdir(cache_path):
        details.append({
            "item": "Cache directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "cache/ directory is present."
        })
        total_score += 10
    else:
        details.append({
            "item": "Cache directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "cache/ directory not found."
        })

    # 2. Check citation_graph.json exists (10 points)
    graph_file = os.path.join(cache_path, "citation_graph.json")
    if os.path.isfile(graph_file):
        details.append({
            "item": "citation_graph.json file exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "cache/citation_graph.json is present."
        })
        total_score += 10
    else:
        details.append({
            "item": "citation_graph.json file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "cache/citation_graph.json not found."
        })
        # If file missing, no further checks possible
        finalize_score(workspace, total_score, details)
        return

    # 3. Parse JSON (10 points)
    try:
        with open(graph_file, "r") as f:
            data = json.load(f)
        details.append({
            "item": "JSON parse valid",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File is valid JSON."
        })
        total_score += 10
    except (json.JSONDecodeError, Exception) as e:
        details.append({
            "item": "JSON parse valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {str(e)}"
        })
        finalize_score(workspace, total_score, details)
        return

    # 4. Check top-level structure has 'nodes' and 'edges' (10 points)
    if isinstance(data, dict) and "nodes" in data and "edges" in data:
        details.append({
            "item": "Graph structure has nodes and edges",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Top-level keys: nodes, edges."
        })
        total_score += 10
    else:
        details.append({
            "item": "Graph structure has nodes and edges",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Missing required keys. Found: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}"
        })

    # 5. Check nodes: exactly 6 AI papers (30 points)
    nodes = data.get("nodes", [])
    expected_paper_ids = {"ai001", "ai002", "ai003", "ai004", "ai005", "ai006"}
    actual_paper_ids = set()
    for node in nodes:
        if isinstance(node, dict) and "paper_id" in node:
            actual_paper_ids.add(node["paper_id"])
    if actual_paper_ids == expected_paper_ids:
        details.append({
            "item": "Nodes contain exactly 6 AI paper IDs (no biology, no duplicates, no old/extra)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"Node IDs: {sorted(actual_paper_ids)}"
        })
        total_score += 30
    else:
        # Partial credit: count of correct IDs
        correct = actual_paper_ids & expected_paper_ids
        wrong = actual_paper_ids - expected_paper_ids
        missing = expected_paper_ids - actual_paper_ids
        score = max(0, int(30 * len(correct) / 6))
        details.append({
            "item": "Nodes contain exactly 6 AI paper IDs",
            "score": score,
            "max_score": 30,
            "passed": len(correct) == 6 and len(wrong) == 0,
            "reason": f"Correct: {len(correct)}, Wrong: {wrong}, Missing: {missing}"
        })
        total_score += score

    # 6. Check edges: correct citation relationships (20 points)
    edges = data.get("edges", [])
    # Expected edges (source_target pairs) from ground truth AI papers only
    expected_edges = {
        ("ai001", "ai003"),
        ("ai001", "ai005"),
        ("ai002", "ai001"),
        ("ai004", "ai001"),
        ("ai004", "ai003"),
        ("ai005", "ai003"),
        ("ai006", "ai003"),
        ("ai006", "ai005")
    }
    actual_edges = set()
    for edge in edges:
        if isinstance(edge, dict) and "source" in edge and "target" in edge:
            actual_edges.add((edge["source"], edge["target"]))
    if actual_edges == expected_edges:
        details.append({
            "item": "Edges match expected AI paper citations",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"Edges count: {len(actual_edges)} (expected {len(expected_edges)})"
        })
        total_score += 20
    else:
        correct_edges = actual_edges & expected_edges
        wrong_edges = actual_edges - expected_edges
        missing_edges = expected_edges - actual_edges
        score = max(0, int(20 * len(correct_edges) / len(expected_edges)))
        details.append({
            "item": "Edges match expected AI paper citations",
            "score": score,
            "max_score": 20,
            "passed": len(correct_edges) == len(expected_edges) and len(wrong_edges) == 0,
            "reason": f"Correct: {len(correct_edges)}, Wrong: {wrong_edges}, Missing: {missing_edges}"
        })
        total_score += score

    # 7. Check node schema: each node must have paper_id, title, year (10 points)
    schema_ok = True
    node_fields_issue = []
    for idx, node in enumerate(nodes):
        if not isinstance(node, dict):
            schema_ok = False
            node_fields_issue.append(f"Node {idx} is not a dict")
            continue
        for field in ["paper_id", "title", "year"]:
            if field not in node:
                schema_ok = False
                node_fields_issue.append(f"Node {idx} missing '{field}'")
    if schema_ok:
        details.append({
            "item": "Each node has paper_id, title, year",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All nodes contain required fields."
        })
        total_score += 10
    else:
        details.append({
            "item": "Each node has paper_id, title, year",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Issues: {node_fields_issue[:3]}"
        })

    # 8. No extra top-level keys (optional, but penalize if present)
    allowed_keys = {"nodes", "edges"}
    extra_keys = set(data.keys()) - allowed_keys
    if extra_keys:
        details.append({
            "item": "No unexpected top-level keys",
            "score": 0,
            "max_score": 0,  # not graded but we log
            "passed": False,
            "reason": f"Extra keys found: {extra_keys}"
        })

    # Ensure total does not exceed 100
    final_total = min(total_score, 100)
    finalize_score(workspace, final_total, details)


def finalize_score(workspace, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    result_file = os.path.join(workspace, "workplace_score.json")
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written to {result_file}: total {total}/100")


if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
