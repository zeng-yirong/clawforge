import os
import sys
import json
import re
import math

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

def load_papers(ws):
    path = os.path.join(ws, "data", "papers", "papers.json")
    with open(path, "r") as f:
        data = json.load(f)
    papers = data.get("papers", [])
    # Filter: only efficient_vision with all required fields
    valid = []
    for p in papers:
        if p.get("direction") != "efficient_vision":
            continue
        pid = p.get("paper_id")
        title = p.get("title")
        year = p.get("year")
        if not pid or not title or year is None:
            continue
        valid.append(p)
    # Sort by year ascending, then paper_id for tie (but years are unique)
    valid.sort(key=lambda p: (p["year"], p["paper_id"]))
    return valid

def parse_markdown_table(content):
    """Return list of (paper_id, title, year) from Markdown table."""
    lines = content.strip().splitlines()
    rows = []
    seen_header = False
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]  # skip empty first/last
        if len(cells) < 3:
            continue
        # Detect header row: if any cell is "paper_id" or "title" etc.
        if not seen_header:
            if any(kw in cells[0].lower() for kw in ["paper_id", "id"]):
                seen_header = True
            continue  # skip header row
        # Skip separator row (contains only dashes)
        if all(re.match(r'^[-:]+$', c) for c in cells):
            continue
        rows.append((cells[0], cells[1], int(cells[2])))
    return rows

def parse_mermaid(content):
    """Return (nodes dict {id: title}, edges list of (src, dst)) from mermaid block."""
    nodes = {}
    edges = []
    # Find mermaid code block
    mermaid_re = re.compile(r'```mermaid\s*\n(.*?)\n```', re.DOTALL)
    match = mermaid_re.search(content)
    if not match:
        return nodes, edges
    block = match.group(1)
    for line in block.strip().splitlines():
        line = line.strip()
        # Node definition: ev01[Title]
        node_match = re.match(r'(\w+)\[(.+?)\]', line)
        if node_match:
            nid, title = node_match.group(1), node_match.group(2)
            nodes[nid] = title
            continue
        # Edge: ev01-->ev02 or ev01 --> ev02
        edge_match = re.match(r'(\w+)\s*-->\s*(\w+)', line)
        if edge_match:
            src, dst = edge_match.group(1), edge_match.group(2)
            edges.append((src, dst))
    return nodes, edges

def build_expected(valid_papers):
    """Return expected table rows and mermaid nodes/edges."""
    table_rows = []
    nodes = {}
    edges = []
    paper_id_to_title = {}
    for p in valid_papers:
        pid = p["paper_id"]
        title = p["title"]
        year = p["year"]
        table_rows.append((pid, title, year))
        nodes[pid] = title
        paper_id_to_title[pid] = title
    # Build edges from citation_ids, only if target exists in valid_papers
    valid_ids = set(p["paper_id"] for p in valid_papers)
    for p in valid_papers:
        src = p["paper_id"]
        for dst in p.get("citation_ids", []):
            if dst in valid_ids:
                edges.append((src, dst))
    return table_rows, nodes, edges

def score_table(actual_rows, expected_rows):
    max_score = 40
    if not actual_rows:
        return 0, max_score, "No table rows found"
    correct = 0
    for i, (exp_pid, exp_title, exp_year) in enumerate(expected_rows):
        if i < len(actual_rows):
            act_pid, act_title, act_year = actual_rows[i]
            if act_pid == exp_pid and act_title == exp_title and act_year == exp_year:
                correct += 1
    score = int(correct / len(expected_rows) * max_score) if expected_rows else 0
    return score, max_score, f"Correct rows: {correct}/{len(expected_rows)}"

def score_mermaid(actual_nodes, actual_edges, expected_nodes, expected_edges):
    max_total = 40
    # Node score (20 points)
    node_score_max = 20
    correct_nodes = 0
    for nid, title in expected_nodes.items():
        if nid in actual_nodes and actual_nodes[nid] == title:
            correct_nodes += 1
    node_score = int(correct_nodes / max(len(expected_nodes), 1) * node_score_max) if expected_nodes else 0
    # Edge score (20 points)
    edge_score_max = 20
    exp_edge_set = set(expected_edges)
    act_edge_set = set(actual_edges)
    correct_edges = len(exp_edge_set & act_edge_set)
    edge_score = int(correct_edges / max(len(exp_edge_set), 1) * edge_score_max) if exp_edge_set else 0
    total = node_score + edge_score
    reason = f"Nodes: {correct_nodes}/{len(expected_nodes)} correct; Edges: {correct_edges}/{len(expected_edges)} correct"
    return total, max_total, reason

def main():
    ws = WORKSPACE
    details = []

    # --- 1. Directory structure (10 pts) ---
    output_dir = os.path.join(ws, "output")
    dir_exists = os.path.isdir(output_dir)
    details.append({
        "item": "output/ directory exists",
        "score": 5 if dir_exists else 0,
        "max_score": 5,
        "passed": dir_exists,
        "reason": "Found" if dir_exists else "Missing"
    })

    review_file = os.path.join(ws, "output", "review.md")
    review_exists = os.path.isfile(review_file)
    details.append({
        "item": "output/review.md exists",
        "score": 3 if review_exists else 0,
        "max_score": 3,
        "passed": review_exists,
        "reason": "Found" if review_exists else "Missing"
    })

    roadmap_file = os.path.join(ws, "output", "roadmap.md")
    roadmap_exists = os.path.isfile(roadmap_file)
    details.append({
        "item": "output/roadmap.md exists",
        "score": 2 if roadmap_exists else 0,
        "max_score": 2,
        "passed": roadmap_exists,
        "reason": "Found" if roadmap_exists else "Missing"
    })

    # If critical files missing, early exit with partial score
    if not (review_exists and roadmap_exists):
        total = sum(d["score"] for d in details)
        result = {"total_score": total, "details": details}
        with open(os.path.join(ws, "workplace_score.json"), "w") as f:
            json.dump(result, f, indent=2)
        print(f"Score: {total}/100")
        return

    # --- 2. Format validity (10 pts) ---
    with open(review_file, "r") as f:
        review_content = f.read()
    table_rows = parse_markdown_table(review_content)
    table_valid = len(table_rows) >= 3  # expect at least 3 data rows
    details.append({
        "item": "review.md contains valid Markdown table",
        "score": 5 if table_valid else 0,
        "max_score": 5,
        "passed": table_valid,
        "reason": "Valid table" if table_valid else "No data rows found in table"
    })

    with open(roadmap_file, "r") as f:
        roadmap_content = f.read()
    nodes_dict, edges_list = parse_mermaid(roadmap_content)
    mermaid_valid = (len(nodes_dict) > 0)  # at least one node
    details.append({
        "item": "roadmap.md contains valid Mermaid graph",
        "score": 5 if mermaid_valid else 0,
        "max_score": 5,
        "passed": mermaid_valid,
        "reason": "Mermaid block detected with nodes" if mermaid_valid else "No mermaid block or nodes"
    })

    # --- Load reference data ---
    valid_papers = load_papers(ws)
    expected_rows, expected_nodes, expected_edges = build_expected(valid_papers)

    # --- 3. Table content correctness (40 pts) ---
    tbl_score, tbl_max, tbl_reason = score_table(table_rows, expected_rows)
    details.append({
        "item": "review.md table content (paper_id, title, year, sorted by year ascending)",
        "score": tbl_score,
        "max_score": tbl_max,
        "passed": tbl_score >= tbl_max * 0.8,  # 80% threshold for pass
        "reason": tbl_reason
    })

    # --- 4. Mermaid graph correctness (40 pts) ---
    mermaid_score, mermaid_max, mermaid_reason = score_mermaid(nodes_dict, edges_list, expected_nodes, expected_edges)
    details.append({
        "item": "roadmap.md nodes and edges (direction efficient_vision only)",
        "score": mermaid_score,
        "max_score": mermaid_max,
        "passed": mermaid_score >= mermaid_max * 0.8,
        "reason": mermaid_reason
    })

    total_score = sum(d["score"] for d in details)
    result = {"total_score": total_score, "details": details}
    with open(os.path.join(ws, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    main()
