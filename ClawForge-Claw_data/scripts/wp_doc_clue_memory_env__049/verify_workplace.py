import sys
import json
import os
import math

def verify(workspace):
    # Expected results (hardcoded from env_builder design)
    expected = {
        "ms-001": {"source_type": "media", "clue": "Explores deployment patterns for HelioSync Edge Inference Fabric in edge environments."},
        "ms-004": {"source_type": "media", "clue": "Detailed guide for HelioSync Edge Inference Fabric deployment."},
        "pres-001": {"source_type": "presentation", "clue": "Highlights the HelioSync Edge Inference Fabric roadmap."}
    }
    expected_ids = set(expected.keys())
    expected_len = len(expected_ids)

    details = []
    total_score = 0

    # 1. ops directory exists (5 points)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops directory exists", "score": 5, "max_score": 5, "passed": True, "reason": "ops/ found"})
        total_score += 5
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 5, "passed": False, "reason": "ops/ missing"})
        # Cannot continue if directory missing
        finish(total_score, details)
        return

    # 2. collected_clues.json exists (5 points)
    clues_path = os.path.join(ops_dir, "collected_clues.json")
    if os.path.isfile(clues_path):
        details.append({"item": "collected_clues.json exists", "score": 5, "max_score": 5, "passed": True, "reason": "file found"})
        total_score += 5
    else:
        details.append({"item": "collected_clues.json exists", "score": 0, "max_score": 5, "passed": False, "reason": "file missing"})
        finish(total_score, details)
        return

    # 3. Parse JSON and check it's a list (10 points)
    try:
        with open(clues_path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            details.append({"item": "JSON is a list", "score": 10, "max_score": 10, "passed": True, "reason": f"list of length {len(data)}"})
            total_score += 10
        else:
            details.append({"item": "JSON is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"type is {type(data).__name__}"})
            finish(total_score, details)
            return
    except Exception as e:
        details.append({"item": "JSON parse", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
        finish(total_score, details)
        return

    # 4. List length equals expected (15 points)
    if len(data) == expected_len:
        details.append({"item": "list length", "score": 15, "max_score": 15, "passed": True, "reason": f"length {expected_len}"})
        total_score += 15
    else:
        details.append({"item": "list length", "score": 0, "max_score": 15, "passed": False, "reason": f"expected {expected_len}, got {len(data)}"})
        # Continue checking what we have (partial credit lost only for length)

    # 5. Each entry has required fields (15 points, 5 per entry)
    field_score = 0
    for entry in data:
        if isinstance(entry, dict) and "source_type" in entry and "id" in entry and "clue" in entry:
            field_score += 5
    details.append({"item": "entries have required fields", "score": field_score, "max_score": 15, "passed": field_score == 15, "reason": f"{field_score}/15"})
    total_score += field_score

    # 6. ID and source_type correctness (30 points, 10 per expected entry)
    id_score = 0
    found_ids = set()
    for entry in data:
        eid = entry.get("id")
        st = entry.get("source_type")
        if eid in expected:
            if st == expected[eid]["source_type"]:
                id_score += 10
                found_ids.add(eid)
    details.append({"item": "id and source_type match", "score": id_score, "max_score": 30, "passed": id_score == 30, "reason": f"matched {len(found_ids)} expected entries with correct source_type"})
    total_score += id_score

    # 7. Clue correctness (15 points, 5 per expected entry)
    clue_score = 0
    for entry in data:
        eid = entry.get("id")
        clue = entry.get("clue")
        if eid in expected and clue == expected[eid]["clue"]:
            clue_score += 5
    details.append({"item": "clue values correct", "score": clue_score, "max_score": 15, "passed": clue_score == 15, "reason": f"{clue_score}/15"})
    total_score += clue_score

    # 8. No extra unexpected IDs (5 points)
    extra_ids = [entry.get("id") for entry in data if entry.get("id") not in expected_ids]
    if len(extra_ids) == 0:
        details.append({"item": "no extra entries", "score": 5, "max_score": 5, "passed": True, "reason": "all IDs in expected set"})
        total_score += 5
    else:
        details.append({"item": "no extra entries", "score": 0, "max_score": 5, "passed": False, "reason": f"unexpected IDs: {extra_ids}"})
        total_score += 0

    # Cap total at 100 (should be exactly 100 if all perfect)
    total_score = min(total_score, 100)
    finish(total_score, details)

def finish(score, details):
    result = {"total_score": score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {score}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
