import sys
import os
import json

def load_json(path):
    if not os.path.exists(path):
        return None, "File not found"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except (json.JSONDecodeError, ValueError) as e:
        return None, f"JSON parse error: {e}"

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0
    max_total = 100

    # 1. Check directories (10 points)
    required_dirs = ["ops"]
    dir_score = 0
    for d in required_dirs:
        if os.path.isdir(os.path.join(workspace, d)):
            dir_score += 5
    results.append({
        "item": "Required directories exist",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": f"Found {dir_score//5}/1 required directories"
    })
    total_score += dir_score

    # 2. Check clue_list.json existence and structure (15 points)
    clue_path = os.path.join(workspace, "ops/clue_list.json")
    exists = os.path.exists(clue_path)
    if not exists:
        results.append({
            "item": "clue_list.json exists",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "File not found"
        })
        # remaining checks won't pass, but we continue to give partial scores
    else:
        data, err = load_json(clue_path)
        if err:
            results.append({
                "item": "clue_list.json is valid JSON",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": err
            })
        else:
            results.append({
                "item": "clue_list.json is valid JSON",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": "JSON parsed successfully"
            })
            total_score += 15

            # 3. Structure: must be a list of objects (10 points)
            if isinstance(data, list):
                results.append({
                    "item": "clue_list is a list",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": f"List with {len(data)} items"
                })
                total_score += 10
            else:
                results.append({
                    "item": "clue_list is a list",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"Expected list, got {type(data).__name__}"
                })

            # 4. Correct entries count and content (55 points)
            if isinstance(data, list):
                # Expected entries (order doesn't matter)
                # From reports: R-2025-001, R-2025-003
                # From presentations: P-2025-101, P-2025-102
                # From media_samples: M-2025-201, M-2025-202
                expected_entries = [
                    {"source_type": "report", "doc_id": "R-2025-001", "summary": "Explores edge deployment of AetherMind Synaptic Core in factory settings."},
                    {"source_type": "report", "doc_id": "R-2025-003", "summary": "Detailed analysis of AetherMind Synaptic Core integration with robotic arms."},
                    {"source_type": "presentation", "doc_id": "P-2025-101", "summary": "Official launch presentation highlighting AetherMind Synaptic Core capabilities."},
                    {"source_type": "presentation", "doc_id": "P-2025-102", "summary": "Covers multiple solutions; page 12 references AetherMind Synaptic Core."},
                    {"source_type": "media_sample", "doc_id": "M-2025-201", "summary": "Interview discussing AetherMind Synaptic Core deployment challenges."},
                    {"source_type": "media_sample", "doc_id": "M-2025-202", "summary": "Mentions AetherMind Synaptic Core as key differentiator."}
                ]
                entry_score = 0
                max_entry_score = 55
                # Check for presence of each expected doc_id
                found_ids = {e.get("doc_id") for e in data}
                missing = [e for e in expected_entries if e["doc_id"] not in found_ids]
                extra = []
                for e in data:
                    eid = e.get("doc_id")
                    if eid and eid not in {ee["doc_id"] for ee in expected_entries}:
                        extra.append(eid)
                if not missing and not extra:
                    # Full points if all present and no extra
                    entry_score = 55
                    reason = "All 6 expected doc_ids found, no extra entries."
                else:
                    # Deduct 9 points per missing or extra (max 55)
                    penalty = (len(missing) + len(extra)) * 9
                    entry_score = max(0, 55 - penalty)
                    reason = f"Missing: {missing}, Extra: {extra}" if missing or extra else "Partial match"
                # Also verify each entry has source_type and summary (minimal check)
                valid_fields = all(
                    isinstance(e, dict) and "doc_id" in e and "source_type" in e 
                    for e in data
                )
                if not valid_fields:
                    entry_score = max(0, entry_score - 10)
                    reason += "; Some entries missing required fields"
                results.append({
                    "item": "Correct clue content (doc_ids and fields)",
                    "score": entry_score,
                    "max_score": max_entry_score,
                    "passed": entry_score == max_entry_score,
                    "reason": reason
                })
                total_score += entry_score
    # Final score clamp
    total_score = min(total_score, max_total)

    output = {
        "total_score": round(total_score),
        "details": results
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score: {output['total_score']}/100")

if __name__ == "__main__":
    main()
