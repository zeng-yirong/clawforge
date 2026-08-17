import os
import json
import sys
import re
from collections import defaultdict

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
score_details = []

def check_path_exists(relative_path, desc, max_score):
    full = os.path.join(workspace, relative_path)
    exists = os.path.exists(full)
    score = max_score if exists else 0
    score_details.append({
        "item": desc,
        "score": score,
        "max_score": max_score,
        "passed": exists,
        "reason": f"{'Exists' if exists else 'Missing'}: {relative_path}"
    })
    return exists

def parse_markdown_table(filepath):
    """Extract table rows from review.md, return list of dicts with paper_id, title, year, contribution."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Find table lines (lines starting with '|')
    lines = content.split("\n")
    table_rows = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cols = [c.strip() for c in stripped.split("|")[1:-1]]
            if len(cols) >= 4:
                # skip header row if it contains '---'
                if any("---" in col for col in cols):
                    continue
                table_rows.append(cols)
        else:
            if table_rows:  # table ended
                break
    return table_rows

def parse_mermaid_graph(filepath):
    """Extract nodes and edges from Mermaid graph TD block."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Find block between ```mermaid and 
    mermaid_pattern = r"```mermaid\n(.*?)```"
    match = re.search(mermaid_pattern, content, re.DOTALL)
    if not match:
        # try without backticks (strict but we require them)
        return None, None
    block = match.group(1).strip()
    nodes = set()
    edges = []
    for line in block.split("\n"):
        line = line.strip()
        # node: id[label] or id(label)
        node_match = re.match(r"^(\w+)\[\(?(.*?)\)?\]$", line)
        if node_match:
            nodes.add(node_match.group(1))
        # edge: id1 --> id2
        edge_match = re.match(r"^(\w+)\s*-->\s*(\w+)$", line)
        if edge_match:
            edges.append((edge_match.group(1), edge_match.group(2)))
            nodes.add(edge_match.group(1))
            nodes.add(edge_match.group(2))
    return nodes, edges

# --- Scores ---
# 1. Check review.md exists (10 pts)
if not check_path_exists("review.md", "review.md exists", 10):
    # can't proceed
    score_details.append({"item": "Overall structure", "score": 0, "max_score": 90, "passed": False, "reason": "Missing review.md, remaining checks skipped"})
    total = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": score_details}, f, indent=2)
    sys.exit(0)

# 2. Check roadmap.mmd exists (10 pts)
if not check_path_exists("roadmap.mmd", "roadmap.mmd exists", 10):
    score_details.append({"item": "Overall structure", "score": 0, "max_score": 80, "passed": False, "reason": "Missing roadmap.mmd, remaining checks skipped"})
    total = sum(d["score"] for d in score_details)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": score_details}, f, indent=2)
    sys.exit(0)

# 3. Parse review.md table (20 pts)
review_path = os.path.join(workspace, "review.md")
try:
    rows = parse_markdown_table(review_path)
    table_ok = True
    reason = f"Found {len(rows)} data rows"
except Exception as e:
    rows = []
    table_ok = False
    reason = f"Parse error: {str(e)}"
score_details.append({
    "item": "review.md table format",
    "score": 20 if table_ok and len(rows) > 0 else 0,
    "max_score": 20,
    "passed": table_ok and len(rows) > 0,
    "reason": reason
})

# 4. Verify table content: should contain exactly 4 papers from tool_augmented_reasoning
expected_papers = [
    ("tool_001", "Tool-Augmented Reasoning in Language Models", 2023),
    ("tool_004", "Tool-Assisted Fact Verification", 2023),
    ("tool_002", "Learning to Use Tools: A Survey", 2024),
    ("tool_003", "Chain-of-Thought with Tool Grounding", 2025)
]
# order: year asc, then paper_id asc (tool_001, tool_004 both 2023, tool_001 < tool_004)
expected_order = ["tool_001", "tool_004", "tool_002", "tool_003"]
actual_order = [r[0] for r in rows] if len(rows) >= 4 else []
order_correct = (actual_order == expected_order)
paper_ids_in_rows = set(r[0] for r in rows)
all_expected_ids = {p[0] for p in expected_papers}
content_correct = paper_ids_in_rows == all_expected_ids

# Check each row has correct title and year (from papers)
title_year_ok = True
for r in rows:
    pid = r[0]
    title = r[1] if len(r) > 1 else ""
    year_str = r[2] if len(r) > 2 else ""
    for exp in expected_papers:
        if exp[0] == pid:
            if exp[1] != title or str(exp[2]) != year_str:
                title_year_ok = False
                break

table_score = 0
if len(rows) == 4:
    if content_correct:
        table_score += 10
    if order_correct:
        table_score += 5
    if title_year_ok:
        table_score += 5
else:
    table_score = 0
score_details.append({
    "item": "review.md table content correctness",
    "score": table_score,
    "max_score": 20,
    "passed": table_score == 20,
    "reason": f"Rows: {len(rows)} (expected 4), IDs: {paper_ids_in_rows}, order correct: {order_correct}, titles/years ok: {title_year_ok}"
})

# 5. Parse roadmap.mmd graph (10 pts)
roadmap_path = os.path.join(workspace, "roadmap.mmd")
try:
    nodes, edges = parse_mermaid_graph(roadmap_path)
    graph_ok = (nodes is not None)
    reason = f"Found {len(nodes)} nodes, {len(edges)} edges"
except Exception as e:
    nodes = set()
    edges = []
    graph_ok = False
    reason = f"Parse error: {str(e)}"
score_details.append({
    "item": "roadmap.mmd graph format",
    "score": 10 if graph_ok else 0,
    "max_score": 10,
    "passed": graph_ok,
    "reason": reason
})

# 6. Verify graph nodes and edges (30 pts)
# Expected nodes: all 4 tool papers
expected_node_ids = {"tool_001", "tool_002", "tool_003", "tool_004"}
# Expected edges (from citation_ids):
# tool_001 -> tool_002, tool_001 -> tool_004
# tool_003 -> tool_001
# tool_004 -> tool_001
# tool_002 has no outbound
# total edges: 4 (but note tool_001 -> tool_002 and tool_001 -> tool_004 and tool_003 -> tool_001 and tool_004 -> tool_001)
# Actually from data: tool_001 cites ["tool_002","tool_004"]; tool_003 cites ["tool_001"]; tool_004 cites ["tool_001"]
# So edges: (tool_001, tool_002), (tool_001, tool_004), (tool_003, tool_001), (tool_004, tool_001)
expected_edges = {("tool_001","tool_002"), ("tool_001","tool_004"), ("tool_003","tool_001"), ("tool_004","tool_001")}

if graph_ok:
    node_score = 0
    edge_score = 0
    # Nodes: must have exactly these 4 nodes (no extra)
    if nodes == expected_node_ids:
        node_score = 15
    elif nodes.issuperset(expected_node_ids) and len(nodes) == len(expected_node_ids):
        node_score = 15  # no extra
    elif nodes.issuperset(expected_node_ids):
        node_score = 10  # has extra
    else:
        missing = expected_node_ids - nodes
        node_score = 5 if len(missing) <= 2 else 0

    # Edges: must contain all expected (order doesn't matter)
    edge_set = set(edges)
    if edge_set == expected_edges:
        edge_score = 15
    elif edge_set.issuperset(expected_edges) and len(edge_set) == len(expected_edges):
        edge_score = 15
    elif edge_set.issuperset(expected_edges):
        edge_score = 10
    else:
        missing_edges = expected_edges - edge_set
        extra = edge_set - expected_edges
        edge_score = 5 if len(missing_edges) <= 2 else 0

    graph_score = node_score + edge_score
    score_details.append({
        "item": "roadmap.mmd graph content",
        "score": graph_score,
        "max_score": 30,
        "passed": graph_score == 30,
        "reason": f"Nodes: {nodes} (expected {expected_node_ids}), Edges: {edge_set} (expected {expected_edges})"
    })
else:
    score_details.append({
        "item": "roadmap.mmd graph content",
        "score": 0,
        "max_score": 30,
        "passed": False,
        "reason": "Graph parsing failed"
    })

# 7. Bonus: no extra files beyond review.md and roadmap.mmd? Actually we don't penalize, but ensure no other required.
# No score for that.

# Compute total
total = sum(d["score"] for d in score_details)
score_details.insert(0, {"item": "Overall score", "score": total, "max_score": 100, "passed": True, "reason": "Computed"})

with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump({"total_score": total, "details": score_details}, f, indent=2)

print(f"Total score: {total}/100")
