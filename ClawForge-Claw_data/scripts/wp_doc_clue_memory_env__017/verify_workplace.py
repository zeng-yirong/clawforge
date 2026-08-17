import os
import sys
import json

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. Check ops directory exists
    ops_path = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_path)
    details.append({
        "item": "ops directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "ops directory found" if dir_exists else "ops directory missing"
    })
    total_score += details[-1]["score"]

    # 2. Check clue_list.json exists
    clue_path = os.path.join(ops_path, "clue_list.json")
    file_exists = os.path.isfile(clue_path)
    details.append({
        "item": "clue_list.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "File missing"
    })
    total_score += details[-1]["score"]
    if not file_exists:
        # Stop here if critical file missing
        details.append({
            "item": "clue_list.json parseable",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not present"
        })
        details.append({
            "item": "clue structure correct",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not present"
        })
        details.append({
            "item": "doc_id matches (3 clues)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "File not present"
        })
        details.append({
            "item": "clue_bullet matches (3 clues)",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "File not present"
        })
        total_score = sum(d["score"] for d in details)
        return {"total_score": total_score, "details": details}

    # 3. Parse JSON
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
        parsed_ok = True
    except (json.JSONDecodeError, Exception) as e:
        parsed_ok = False
        reason = f"JSON parse error: {str(e)}"
    details.append({
        "item": "clue_list.json parseable",
        "score": 10 if parsed_ok else 0,
        "max_score": 10,
        "passed": parsed_ok,
        "reason": "Valid JSON" if parsed_ok else reason
    })
    total_score += details[-1]["score"]
    if not parsed_ok:
        return {"total_score": total_score, "details": details}

    # 4. Check structure: should be a dict with key "clues" which is a list
    structure_ok = isinstance(data, dict) and "clues" in data and isinstance(data["clues"], list)
    if not structure_ok:
        reason = "structure: expected {'clues': [...]}"
    else:
        # Check each item has doc_id and clue_bullet
        all_items_valid = all(
            isinstance(item, dict) and "doc_id" in item and "clue_bullet" in item
            for item in data["clues"]
        )
        if not all_items_valid:
            structure_ok = False
            reason = "Each clue item must have 'doc_id' and 'clue_bullet'"
        else:
            reason = "Structure correct"
    details.append({
        "item": "clue structure correct",
        "score": 10 if structure_ok else 0,
        "max_score": 10,
        "passed": structure_ok,
        "reason": reason
    })
    total_score += details[-1]["score"]
    if not structure_ok:
        return {"total_score": total_score, "details": details}

    # 5. Expected clues (sorted by doc_id for deterministic comparison)
    expected_clues = [
        {"doc_id": "M-001", "clue_bullet": "Podcast discusses the impact of HelioSync Edge Inference Fabric on edge computing."},
        {"doc_id": "P-001", "clue_bullet": "Deck highlights deployment architecture for HelioSync Edge Inference Fabric."},
        {"doc_id": "R-001", "clue_bullet": "Adoption of HelioSync Edge Inference Fabric in manufacturing reduced latency by 40%."}
    ]
    # Sort expected and agent clues by doc_id
    expected_sorted = sorted(expected_clues, key=lambda x: x["doc_id"])
    agent_sorted = sorted(data["clues"], key=lambda x: x["doc_id"])

    # Check doc_id match (length and ids)
    agent_ids = [c["doc_id"] for c in agent_sorted]
    expected_ids = [c["doc_id"] for c in expected_sorted]
    ids_match = (agent_ids == expected_ids)
    details.append({
        "item": "doc_id matches (3 clues)",
        "score": 30 if ids_match else 0,
        "max_score": 30,
        "passed": ids_match,
        "reason": "All doc_ids correct" if ids_match else f"Expected {expected_ids}, got {agent_ids}"
    })
    total_score += details[-1]["score"]
    if not ids_match:
        return {"total_score": total_score, "details": details}

    # 6. Check clue_bullet match (order now aligned by doc_id)
    bullets_match = all(
        a["clue_bullet"] == e["clue_bullet"]
        for a, e in zip(agent_sorted, expected_sorted)
    )
    details.append({
        "item": "clue_bullet matches (3 clues)",
        "score": 30 if bullets_match else 0,
        "max_score": 30,
        "passed": bullets_match,
        "reason": "All clue_bullets correct" if bullets_match else "Some clue_bullet mismatch"
    })
    total_score += details[-1]["score"]

    return {"total_score": min(total_score, max_total), "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    os.makedirs(os.path.join(workspace, "ops"), exist_ok=True)  # ensure ops dir exists for writing score
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
