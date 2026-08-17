import sys
import os
import json
import re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."
scores = []

def check_file(path):
    return os.path.isfile(os.path.join(workspace, path))

def read_file(path):
    with open(os.path.join(workspace, path), 'r', encoding='utf-8') as f:
        return f.read()

# --- Scoring ---

# 1. outputs directory exists (10 pts)
if os.path.isdir(os.path.join(workspace, "outputs")):
    scores.append({"item": "outputs directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "outputs directory found"})
else:
    scores.append({"item": "outputs directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "outputs directory not found"})

# 2. review_and_roadmap.md exists (10 pts)
fpath = "outputs/review_and_roadmap.md"
if check_file(fpath):
    scores.append({"item": "review_and_roadmap.md exists", "score": 10, "max_score": 10, "passed": True, "reason": "file found"})
    content = read_file(fpath)
else:
    scores.append({"item": "review_and_roadmap.md exists", "score": 0, "max_score": 10, "passed": False, "reason": "file not found"})
    # cannot continue without file
    total = sum(s["score"] for s in scores)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total, "details": scores}, f)
    sys.exit(0)

# 3. Contains target paper IDs (5 pts each, total 15)
target_ids = ["paper_001", "paper_002", "paper_003"]
for pid in target_ids:
    if pid in content:
        scores.append({"item": f"Contains {pid} in review", "score": 5, "max_score": 5, "passed": True, "reason": f"{pid} found"})
    else:
        scores.append({"item": f"Contains {pid} in review", "score": 0, "max_score": 5, "passed": False, "reason": f"{pid} not found"})

# 4. Excludes distractor IDs (max 10 pts, -2 per distractor)
distractor_ids = ["paper_004", "paper_005", "paper_006", "paper_007", "paper_008"]
distractor_count = sum(1 for pid in distractor_ids if pid in content)
distractor_score = max(0, 10 - 2 * distractor_count)
if distractor_count == 0:
    scores.append({"item": "No distractor paper IDs present", "score": 10, "max_score": 10, "passed": True, "reason": "All distractors excluded"})
else:
    scores.append({"item": "No distractor paper IDs present", "score": distractor_score, "max_score": 10, "passed": False, "reason": f"Found {distractor_count} distractor(s): {[pid for pid in distractor_ids if pid in content]}"})

# 5. Mermaid code block present (15 pts)
mermaid_pattern = re.compile(r'```(?:mermaid)?\s*\n(.*?)```', re.DOTALL)
mermaid_blocks = mermaid_pattern.findall(content)
if mermaid_blocks:
    mermaid_block = mermaid_blocks[0]
    if 'graph' in mermaid_block or 'flowchart' in mermaid_block:
        scores.append({"item": "Mermaid code block present with graph/flowchart", "score": 15, "max_score": 15, "passed": True, "reason": "Valid Mermaid block found"})
    else:
        scores.append({"item": "Mermaid code block present but missing graph/flowchart", "score": 5, "max_score": 15, "passed": False, "reason": "Block found but does not contain graph/flowchart"})
else:
    mermaid_block = None
    scores.append({"item": "Mermaid code block present", "score": 0, "max_score": 15, "passed": False, "reason": "No Mermaid code block found"})

# 6. Mermaid block contains target paper IDs (5 pts each, total 15)
if mermaid_block is not None:
    for pid in target_ids:
        if pid in mermaid_block:
            scores.append({"item": f"Mermaid contains {pid}", "score": 5, "max_score": 5, "passed": True, "reason": f"{pid} in Mermaid block"})
        else:
            scores.append({"item": f"Mermaid contains {pid}", "score": 0, "max_score": 5, "passed": False, "reason": f"{pid} not in Mermaid block"})
else:
    for pid in target_ids:
        scores.append({"item": f"Mermaid contains {pid}", "score": 0, "max_score": 5, "passed": False, "reason": "No Mermaid block to check"})

# 7. Markdown heading present (5 pts)
if content.startswith("#") or content.startswith("##"):
    scores.append({"item": "Markdown heading present", "score": 5, "max_score": 5, "passed": True, "reason": "Starts with # or ##"})
else:
    scores.append({"item": "Markdown heading present", "score": 0, "max_score": 5, "passed": False, "reason": "No heading at start"})

# 8. Content length > 200 (5 pts)
if len(content) > 200:
    scores.append({"item": "Content length > 200 characters", "score": 5, "max_score": 5, "passed": True, "reason": f"Length {len(content)}"})
else:
    scores.append({"item": "Content length > 200 characters", "score": 0, "max_score": 5, "passed": False, "reason": "Content too short"})

# 9. Contains at least one paper title keyword (10 pts)
if "EfficientNet" in content or "MobileNets" in content or "EfficientDet" in content:
    scores.append({"item": "Contains at least one paper title keyword", "score": 10, "max_score": 10, "passed": True, "reason": "Found EfficientNet, MobileNets, or EfficientDet"})
else:
    scores.append({"item": "Contains at least one paper title keyword", "score": 0, "max_score": 10, "passed": False, "reason": "No recognized title keyword"})

# 10. Mermaid block contains arrow (5 pts)
if mermaid_block is not None and '-->' in mermaid_block:
    scores.append({"item": "Mermaid block contains arrow (-->)", "score": 5, "max_score": 5, "passed": True, "reason": "Arrow found"})
else:
    scores.append({"item": "Mermaid block contains arrow (-->)", "score": 0 if mermaid_block is None else 0, "max_score": 5, "passed": False, "reason": "No arrow or no Mermaid block"})

# 11. Overall file quality (5 pts) – if all previous Mermaid-related checks passed, give bonus
mermaid_related_passed = all(
    s["item"] in ["Mermaid code block present with graph/flowchart"] or 
    s["item"].startswith("Mermaid contains") for s in scores
) and mermaid_block is not None
if mermaid_related_passed:
    scores.append({"item": "Overall Mermaid quality", "score": 5, "max_score": 5, "passed": True, "reason": "All Mermaid checks passed"})
else:
    scores.append({"item": "Overall Mermaid quality", "score": 0, "max_score": 5, "passed": False, "reason": "One or more Mermaid checks failed"})

# Calculate total
total_score = sum(s["score"] for s in scores)
# Ensure total ≤ 100 (it should be exactly 100 if all max_scores sum)
# but we leave as is, then cap at 100
total_score = min(total_score, 100)
results = {
    "total_score": total_score,
    "details": scores
}

with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
    json.dump(results, f, indent=2)
