import sys
import os
import json
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0

    # helper to check file existence
    def file_path(rel):
        return os.path.join(workspace, rel)

    # ---------- Item 1: review.md exists (5 pts) ----------
    review_path = file_path("review.md")
    exists_review = os.path.isfile(review_path)
    details.append({
        "item": "review.md exists",
        "score": 5 if exists_review else 0,
        "max_score": 5,
        "passed": exists_review,
        "reason": "Found" if exists_review else "Missing"
    })

    # ---------- Item 2: roadmap.mmd exists (5 pts) ----------
    roadmap_path = file_path("roadmap.mmd")
    exists_roadmap = os.path.isfile(roadmap_path)
    details.append({
        "item": "roadmap.mmd exists",
        "score": 5 if exists_roadmap else 0,
        "max_score": 5,
        "passed": exists_roadmap,
        "reason": "Found" if exists_roadmap else "Missing"
    })

    # If either file missing, skip further checks and set max possible score
    if not exists_review or not exists_roadmap:
        total_score = sum(d["score"] for d in details)
        write_score(total_score, details, workspace)
        return

    # ---------- Load ground truth from papers.json ----------
    papers_path = file_path("data/papers/papers.json")
    if not os.path.isfile(papers_path):
        print("FATAL: data/papers/papers.json not found in workspace.", file=sys.stderr)
        sys.exit(1)

    with open(papers_path, "r") as f:
        data = json.load(f)

    raw_papers = data.get("papers", [])
    # Filter correct direction
    correct_papers = [p for p in raw_papers if p.get("direction") == "tool_augmented_reasoning"]
    # Sort by year ascending
    correct_papers.sort(key=lambda p: p["year"])

    expected_titles = [p["title"] for p in correct_papers]
    expected_year_title = [f"{p['year']} – {p['title']}" for p in correct_papers]  # en dash as per prompt example
    n_expected = len(expected_titles)

    # ---------- Item 3: review.md contains introductory elements (5 pts) ----------
    with open(review_path, "r") as f:
        review_text = f.read()

    has_title = bool(re.search(r'^#\s+', review_text, re.MULTILINE))
    has_intro = "tool_augmented_reasoning" in review_text.lower() or "tool augmented reasoning" in review_text.lower()
    intro_ok = has_title and has_intro
    details.append({
        "item": "review.md has a title and introductory sentence",
        "score": 5 if intro_ok else 0,
        "max_score": 5,
        "passed": intro_ok,
        "reason": "Title+intro found" if intro_ok else "Missing title or intro"
    })

    # ---------- Item 4: review.md contains all correct paper titles in order (30 pts, 6 each) ----------
    # We'll check each expected title appears in the review text.
    # Also check order: we can extract all lines that contain "##" or bullet points? Simpler: check titles appear consecutively.
    # For robustness, we check each title's presence and relative order via index.
    review_lower = review_text.lower()
    found_titles = []
    for t in expected_titles:
        if t.lower() in review_lower:
            found_titles.append(t)
    correct_titles_count = len(found_titles)

    # Check order: the indices of first occurrence in the review text
    indices = []
    for t in expected_titles:
        idx = review_text.find(t)
        if idx != -1:
            indices.append(idx)
    order_ok = all(indices[i] < indices[i+1] for i in range(len(indices)-1)) if len(indices) == n_expected else False

    title_score = 0
    if correct_titles_count == n_expected and order_ok:
        title_score = 30
    elif correct_titles_count == n_expected:
        title_score = 20  # correct set but wrong order
    else:
        title_score = correct_titles_count * 6  # partial credit

    title_score = min(title_score, 30)
    details.append({
        "item": "review.md lists all correct papers in ascending year order",
        "score": title_score,
        "max_score": 30,
        "passed": title_score >= 30,
        "reason": f"Found {correct_titles_count}/{n_expected} titles, order {'ok' if order_ok else 'not ok'}"
    })

    # ---------- Item 5: review.md does NOT contain any noise paper title (10 pts) ----------
    noise_titles = ["Wrong Format Paper", "Capitalized Paper", "Missing Direction Paper",
                    "Efficient Vision Transformers", "Another Vision Paper", "Yet Another Vision Paper",
                    "Old Paper", "Ancient Paper"]
    found_noise = [t for t in noise_titles if t.lower() in review_lower]
    noise_penalty = len(found_noise) * 5
    noise_score = max(0, 10 - noise_penalty)
    details.append({
        "item": "review.md excludes noise papers",
        "score": noise_score,
        "max_score": 10,
        "passed": noise_score == 10,
        "reason": f"Found {len(found_noise)} noise paper(s): {found_noise}" if found_noise else "Clean"
    })

    # ---------- Item 6: roadmap.mmd has valid graph LR header (5 pts) ----------
    with open(roadmap_path, "r") as f:
        roadmap_text = f.read()
    has_graph_lr = re.search(r'graph\s+LR', roadmap_text, re.IGNORECASE) is not None
    details.append({
        "item": "roadmap.mmd contains 'graph LR'",
        "score": 5 if has_graph_lr else 0,
        "max_score": 5,
        "passed": has_graph_lr,
        "reason": "Found" if has_graph_lr else "Missing graph LR"
    })

    # ---------- Item 7: roadmap.mmd has exactly the expected nodes (20 pts, 4 per node) ----------
    # Extract node labels (text inside square brackets)
    node_pattern = re.compile(r'\[([^\]]+)\]')
    node_texts = node_pattern.findall(roadmap_text)
    # Normalize whitespace in node texts
    node_texts = [re.sub(r'\s+', ' ', t.strip()) for t in node_texts]

    # Count how many expected year-title strings appear (exact match)
    expected_set = set(expected_year_title)
    node_hits = sum(1 for n in node_texts if n in expected_set)
    # Also check no unexpected node with "tool_augmented_reasoning" or similar? We'll just count expected.
    node_score = node_hits * 4
    node_score = min(node_score, 20)
    node_all_found = node_hits == n_expected
    details.append({
        "item": "roadmap.mmd nodes contain correct year-title pairs",
        "score": node_score,
        "max_score": 20,
        "passed": node_all_found,
        "reason": f"Found {node_hits}/{n_expected} correct nodes"
    })

    # ---------- Item 8: roadmap.mmd arrows connect nodes in chronological order (20 pts) ----------
    # Parse edges: look for patterns like NodeA --> NodeB
    # We'll extract arrows: text before '-->' and after, taking the node label from square brackets.
    # Simple approach: find all arrows and map to node labels.
    arrow_pattern = re.compile(r'([^\]]*)\]?\s*-->+\s*\[?([^\]]*)\]?')
    # Better: use the whole line with --> and extract the two bracketed parts.
    # We'll split on '-->' and then find the last bracketed in left and first bracketed in right.
    lines = roadmap_text.split('\n')
    edges = []
    for line in lines:
        if '-->' in line:
            left, right = line.split('-->', 1)
            left_nodes = node_pattern.findall(left)
            right_nodes = node_pattern.findall(right)
            if left_nodes and right_nodes:
                edges.append((left_nodes[-1].strip(), right_nodes[0].strip()))

    # Build adjacency list from expected order
    expected_edges = []
    for i in range(len(expected_year_title)-1):
        expected_edges.append((expected_year_title[i], expected_year_title[i+1]))

    # Check if the found edges are a superset of expected edges (ignore extra)
    found_edge_set = set(edges)
    expected_edge_set = set(expected_edges)
    correct_edges = len(found_edge_set & expected_edge_set)
    if correct_edges == len(expected_edges) and len(expected_edges) > 0:
        edge_score = 20
    elif correct_edges > 0:
        edge_score = correct_edges * (20 // len(expected_edges)) if len(expected_edges) else 0
    else:
        edge_score = 0
    edge_score = min(edge_score, 20)
    details.append({
        "item": "roadmap.mmd edges follow chronological order",
        "score": edge_score,
        "max_score": 20,
        "passed": edge_score >= 20,
        "reason": f"Correct edges: {correct_edges}/{len(expected_edges)}"
    })

    # ---------- Compute total ----------
    total_score = sum(d["score"] for d in details)
    total_score = min(total_score, 100)

    # Write score file
    write_score(total_score, details, workspace)

def write_score(total_score, details, workspace):
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    main()
