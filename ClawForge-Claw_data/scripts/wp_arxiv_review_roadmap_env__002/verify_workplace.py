import json
import os
import sys
import re

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_path = os.path.join(workspace, "results.json")
    score_details = []
    total_score = 0

    # 1. results.json exists and is valid JSON
    try:
        if not os.path.isfile(results_path):
            raise FileNotFoundError("results.json not found")
        with open(results_path, 'r') as f:
            data = json.load(f)
        score_details.append({
            "item": "results.json exists and valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found and parsed successfully."
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "results.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": str(e)
        })
        # Cannot proceed further
        final_score = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final_score, f, indent=2)
        return

    # 2. Contains required keys
    required_keys = ["review", "roadmap", "papers_used"]
    missing_keys = [k for k in required_keys if k not in data]
    if missing_keys:
        score_details.append({
            "item": "Contains keys: review, roadmap, papers_used",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Missing keys: {missing_keys}"
        })
    else:
        score_details.append({
            "item": "Contains keys: review, roadmap, papers_used",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "All required keys present."
        })
        total_score += 5

    # 3. papers_used exact match (after sorting)
    try:
        used_list = data.get("papers_used", [])
        if not isinstance(used_list, list):
            raise ValueError("papers_used is not a list")
        
        # Load original papers to compute expected list
        papers_path = os.path.join(workspace, "data/papers/papers.json")
        papers_data = load_json(papers_path)
        all_papers = papers_data.get("papers", [])
        
        # Filter: direction == 'tool_augmented_reasoning'
        target_papers = [p for p in all_papers if p.get("direction") == "tool_augmented_reasoning"]
        # De-duplicate by paper_id, keep the one with highest year
        dedup = {}
        for p in target_papers:
            pid = p["paper_id"]
            if pid not in dedup or p["year"] > dedup[pid]["year"]:
                dedup[pid] = p
        expected_ids = sorted(dedup.keys())
        
        # Check also the used list must contain only valid target papers (no extra)
        normalized_used = sorted(used_list)
        if normalized_used == expected_ids:
            score_details.append({
                "item": "papers_used exact match with expected list",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": f"Matches expected: {expected_ids}"
            })
            total_score += 40
        else:
            score_details.append({
                "item": "papers_used exact match with expected list",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": f"Expected {expected_ids}, got {normalized_used}"
            })
    except Exception as e:
        score_details.append({
            "item": "papers_used exact match with expected list",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": str(e)
        })

    # 4. review non-empty and length > 100
    review_text = data.get("review", "")
    if isinstance(review_text, str) and len(review_text) > 100:
        score_details.append({
            "item": "review non-empty and length > 100",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": f"Length: {len(review_text)}"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "review non-empty and length > 100",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Length: {len(review_text) if isinstance(review_text,str) else 'not string'}"
        })

    # 5. review contains all target paper titles
    try:
        target_titles = [dedup[pid]["title"] for pid in expected_ids]
        missing_titles = [t for t in target_titles if t not in review_text]
        titles_found = len(target_titles) - len(missing_titles)
        titles_score = titles_found * 2  # 2 points per title, max 10
        if titles_score > 10:
            titles_score = 10
        score_details.append({
            "item": "review contains all target paper titles",
            "score": titles_score,
            "max_score": 10,
            "passed": titles_score == 10,
            "reason": f"Found {titles_found}/{len(target_titles)} titles. Missing: {missing_titles}"
        })
        total_score += titles_score
    except Exception as e:
        score_details.append({
            "item": "review contains all target paper titles",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": str(e)
        })

    # 6. review contains "Tool-Augmented Reasoning" phrase
    if "Tool-Augmented Reasoning" in review_text:
        score_details.append({
            "item": "review contains 'Tool-Augmented Reasoning'",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Phrase found."
        })
        total_score += 5
    else:
        score_details.append({
            "item": "review contains 'Tool-Augmented Reasoning'",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Phrase not found."
        })

    # 7. roadmap non-empty and length > 50
    roadmap_text = data.get("roadmap", "")
    if isinstance(roadmap_text, str) and len(roadmap_text) > 50:
        score_details.append({
            "item": "roadmap non-empty and length > 50",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": f"Length: {len(roadmap_text)}"
        })
        total_score += 5
    else:
        score_details.append({
            "item": "roadmap non-empty and length > 50",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": f"Length: {len(roadmap_text) if isinstance(roadmap_text,str) else 'not string'}"
        })

    # 8. roadmap contains "graph TD"
    if "graph TD" in roadmap_text:
        score_details.append({
            "item": "roadmap contains 'graph TD'",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Found."
        })
        total_score += 5
    else:
        score_details.append({
            "item": "roadmap contains 'graph TD'",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Not found."
        })

    # 9. roadmap contains at least one "-->"
    if "-->" in roadmap_text:
        score_details.append({
            "item": "roadmap contains at least one '-->'",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "Found."
        })
        total_score += 5
    else:
        score_details.append({
            "item": "roadmap contains at least one '-->'",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "Not found."
        })

    # 10. roadmap contains at least as many node brackets as target papers
    # Count substrings like [something]
    node_count = len(re.findall(r'\[.*?\]', roadmap_text))
    if node_count >= len(expected_ids):
        score_details.append({
            "item": f"roadmap node count >= target papers ({len(expected_ids)})",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found {node_count} nodes."
        })
        total_score += 10
    else:
        score_details.append({
            "item": f"roadmap node count >= target papers ({len(expected_ids)})",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Found {node_count} nodes, expected at least {len(expected_ids)}."
        })

    # Write final score
    final_score = {"total_score": total_score, "details": score_details}
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(final_score, f, indent=2)

if __name__ == "__main__":
    main()
