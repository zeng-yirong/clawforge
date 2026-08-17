import sys
import os
import json
import re

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total = 0

    # 1. Check file existence
    clue_path = os.path.join(workspace, "ops", "clue_list.json")
    file_exists = os.path.isfile(clue_path)
    score_details.append({
        "item": "ops/clue_list.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "File found" if file_exists else "File missing"
    })
    if not file_exists:
        write_score(score_details, total)
        return

    # 2. Parse JSON and validate structure
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        score_details.append({
            "item": "Valid JSON array",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON parse error: {e}"
        })
        write_score(score_details, total)
        return

    if not isinstance(data, list):
        score_details.append({
            "item": "Valid JSON array",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Root element is not a list"
        })
        write_score(score_details, total)
        return

    score_details.append({
        "item": "Valid JSON array",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Parsed as non-empty list" if data else "Parsed as empty list"
    })

    # 3. Each entry must have 'id' and 'summary' keys
    entries_ok = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict) or "id" not in entry or "summary" not in entry:
            entries_ok = False
            break
    score_details.append({
        "item": "Each entry has 'id' and 'summary'",
        "score": 10 if entries_ok else 0,
        "max_score": 10,
        "passed": entries_ok,
        "reason": "All entries have required fields" if entries_ok else f"Entry {i} missing 'id' or 'summary'"
    })

    if not entries_ok:
        write_score(score_details, total)
        return

    # 4. Build expected mappings from original data
    expected = {}
    sources = [
        ("data/reports/reports.json", "reports", "report_id"),
        ("data/presentations/presentations.json", "presentations", "presentation_id"),
        ("data/media_samples/media_samples.json", "media_samples", "sample_id")
    ]
    missing_source = False
    for rel_path, wrapper_key, id_key in sources:
        full_path = os.path.join(workspace, rel_path)
        if not os.path.isfile(full_path):
            score_details.append({
                "item": f"Original source {rel_path} exists",
                "score": 0,
                "max_score": 0,
                "passed": False,
                "reason": f"Missing {full_path}"
            })
            missing_source = True
            continue
        with open(full_path, "r") as f:
            collection = json.load(f)
        for rec in collection.get(wrapper_key, []):
            aliases = rec.get("solution_aliases", [])
            if "HelioSync Edge Inference Fabric" in aliases:
                expected[rec[id_key]] = rec["summary"]

    if missing_source:
        write_score(score_details, total)
        return

    # 5. Check ID set match
    agent_ids = set(entry["id"] for entry in data)
    expected_ids = set(expected.keys())
    ids_match = agent_ids == expected_ids
    score_details.append({
        "item": "ID set matches expected documents",
        "score": 30 if ids_match else 0,
        "max_score": 30,
        "passed": ids_match,
        "reason": f"Agent ids: {agent_ids}, expected: {expected_ids}" if not ids_match else "Exact match"
    })

    # 6. Summaries per ID
    summary_score = 0
    summary_max = 30  # 10 per document
    for entry in data:
        eid = entry["id"]
        if eid in expected:
            if entry["summary"] == expected[eid]:
                summary_score += 10
            else:
                pass  # no partial credit for individual summary
    score_details.append({
        "item": "Summaries match for each expected document",
        "score": summary_score,
        "max_score": summary_max,
        "passed": summary_score == summary_max,
        "reason": f"Matched {summary_score//10}/3 summaries correctly" if summary_score < summary_max else "All summaries correct"
    })

    total = sum(item["score"] for item in score_details)
    write_score(score_details, total)

def write_score(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    # Also print for stdout
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    main()
