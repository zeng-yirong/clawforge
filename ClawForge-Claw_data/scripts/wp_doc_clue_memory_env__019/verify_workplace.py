import os
import sys
import json
import re

WORKSPACE = sys.argv[1] if len(sys.argv) > 1 else "."

SCORE_FILE = "workplace_score.json"

# Configuration – must match the phrase from the prompt
TARGET_PHRASE = "QuantumEdge Neural Accelerator"

def read_json_relative(rel_path):
    """Read a JSON file relative to WORKSPACE."""
    full = os.path.join(WORKSPACE, rel_path)
    if not os.path.isfile(full):
        return None
    with open(full, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

def scan_source_files():
    """Return a dict {doc_id: {doc_type, content}} for all valid source documents."""
    docs = {}
    # Reports
    reports_dir = os.path.join(WORKSPACE, "reports")
    if os.path.isdir(reports_dir):
        for fname in os.listdir(reports_dir):
            if fname.endswith(".json"):
                data = read_json_relative(os.path.join("reports", fname))
                if data and "report_id" in data and "content" in data:
                    docs[data["report_id"]] = {"doc_type": "report", "content": data["content"]}
    # Presentations
    pres_dir = os.path.join(WORKSPACE, "presentations")
    if os.path.isdir(pres_dir):
        for fname in os.listdir(pres_dir):
            if fname.endswith(".json"):
                data = read_json_relative(os.path.join("presentations", fname))
                if data and "presentation_id" in data and "content" in data:
                    docs[data["presentation_id"]] = {"doc_type": "presentation", "content": data["content"]}
    # Media samples
    media_dir = os.path.join(WORKSPACE, "media_samples")
    if os.path.isdir(media_dir):
        for fname in os.listdir(media_dir):
            if fname.endswith(".json"):
                data = read_json_relative(os.path.join("media_samples", fname))
                if data and "sample_id" in data and "content" in data:
                    docs[data["sample_id"]] = {"doc_type": "media_sample", "content": data["content"]}
    return docs

def ground_truth_matches(source_docs):
    """Return set of doc_ids whose content contains TARGET_PHRASE."""
    matches = set()
    for did, info in source_docs.items():
        if TARGET_PHRASE in info["content"]:
            matches.add(did)
    return matches

def evaluate():
    details = []

    # --- Item 1: ops/ directory exists ---
    ops_dir = os.path.join(WORKSPACE, "ops")
    item1 = {
        "item": "ops/ directory exists",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": ""
    }
    if os.path.isdir(ops_dir):
        item1["score"] = 5
        item1["passed"] = True
        item1["reason"] = "ops/ directory found."
    else:
        item1["reason"] = "ops/ directory not found."
    details.append(item1)

    # --- Item 2: ops/collected_clues.json exists ---
    clues_path = os.path.join(WORKSPACE, "ops", "collected_clues.json")
    item2 = {
        "item": "ops/collected_clues.json exists",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": ""
    }
    if os.path.isfile(clues_path):
        item2["score"] = 5
        item2["passed"] = True
        item2["reason"] = "Found collected_clues.json."
    else:
        item2["reason"] = "File not found."
    details.append(item2)
    if not item2["passed"]:
        # cannot proceed further
        total = sum(d["score"] for d in details)
        write_score(total, details)
        return

    # --- Item 3: JSON is valid and has 'matches' list ---
    clues_data = read_json_relative("ops/collected_clues.json")
    item3 = {
        "item": "JSON valid with 'matches' list",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": ""
    }
    if clues_data is None:
        item3["reason"] = "Invalid JSON."
        details.append(item3)
        write_score(0, details)
        return
    if not isinstance(clues_data, dict) or "matches" not in clues_data:
        item3["reason"] = "Missing 'matches' key or not a dict."
        details.append(item3)
        write_score(sum(d["score"] for d in details), details)
        return
    matches_list = clues_data["matches"]
    if not isinstance(matches_list, list):
        item3["reason"] = "'matches' is not a list."
        details.append(item3)
        write_score(sum(d["score"] for d in details), details)
        return
    item3["score"] = 10
    item3["passed"] = True
    item3["reason"] = f"Found matches list with {len(matches_list)} entries."
    details.append(item3)

    # --- Item 4: Each entry has required fields (doc_id, doc_type, clue) ---
    item4 = {
        "item": "Each match has doc_id, doc_type, clue",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "reason": ""
    }
    all_valid = True
    for i, entry in enumerate(matches_list):
        if not isinstance(entry, dict):
            all_valid = False
            item4["reason"] = f"Entry {i} is not a dict."
            break
        if "doc_id" not in entry or "doc_type" not in entry or "clue" not in entry:
            all_valid = False
            item4["reason"] = f"Entry {i} missing one of required fields."
            break
        if not isinstance(entry["doc_id"], str) or not isinstance(entry["doc_type"], str) or not isinstance(entry["clue"], str):
            all_valid = False
            item4["reason"] = f"Entry {i} has non-string field."
            break
    if all_valid:
        item4["score"] = 10
        item4["passed"] = True
        item4["reason"] = "All entries have required fields."
    else:
        item4["score"] = 0
        item4["passed"] = False
        if not item4["reason"]:
            item4["reason"] = "Field validation failed."
    details.append(item4)

    # --- Item 5: doc_type values are valid ---
    item5 = {
        "item": "doc_type values are one of report/presentation/media_sample",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": ""
    }
    valid_types = {"report", "presentation", "media_sample"}
    types_ok = all(entry["doc_type"] in valid_types for entry in matches_list)
    if types_ok:
        item5["score"] = 5
        item5["passed"] = True
        item5["reason"] = "All doc_type values valid."
    else:
        item5["score"] = 0
        item5["passed"] = False
        item5["reason"] = "Some doc_type values invalid."
    details.append(item5)

    # --- Item 6: Match count matches ground truth ---
    source_docs = scan_source_files()
    true_matches = ground_truth_matches(source_docs)
    agent_matches = set(entry["doc_id"] for entry in matches_list)
    item6 = {
        "item": "Correct number of matches (no false positives/negatives)",
        "score": 0,
        "max_score": 30,
        "passed": False,
        "reason": ""
    }
    false_positives = agent_matches - true_matches
    false_negatives = true_matches - agent_matches
    if not false_positives and not false_negatives:
        item6["score"] = 30
        item6["passed"] = True
        item6["reason"] = f"Exactly {len(true_matches)} matches found (all correct)."
    else:
        penalty = 0
        reason_parts = []
        if false_positives:
            penalty += len(false_positives) * 10
            reason_parts.append(f"false positives: {false_positives}")
        if false_negatives:
            penalty += len(false_negatives) * 10
            reason_parts.append(f"false negatives: {false_negatives}")
        item6["score"] = max(0, 30 - penalty)
        item6["passed"] = item6["score"] == 30
        item6["reason"] = "; ".join(reason_parts) if reason_parts else "mismatch."
    details.append(item6)

    # --- Item 7: Each clue contains TARGET_PHRASE and exists in original content ---
    item7 = {
        "item": "Each clue contains the target phrase and appears in original document content",
        "score": 0,
        "max_score": 30,
        "passed": False,
        "reason": ""
    }
    clue_ok_count = 0
    missing_phrase = 0
    not_in_source = 0
    for entry in matches_list:
        did = entry["doc_id"]
        clue = entry["clue"]
        # must contain phrase
        if TARGET_PHRASE not in clue:
            missing_phrase += 1
            continue
        # must appear in original content (if document exists)
        if did in source_docs:
            content = source_docs[did]["content"]
            if clue not in content:
                not_in_source += 1
                continue
        else:
            # doc_id not recognized – still count as fail
            not_in_source += 1
            continue
        clue_ok_count += 1
    total_entries = len(matches_list)
    if total_entries > 0:
        score_per_entry = 30 / total_entries
        item7["score"] = int(score_per_entry * clue_ok_count)
        item7["passed"] = (item7["score"] == 30)
        if not item7["passed"]:
            reasons = []
            if missing_phrase: reasons.append(f"{missing_phrase} missing phrase")
            if not_in_source: reasons.append(f"{not_in_source} not in source content")
            item7["reason"] = "; ".join(reasons)
        else:
            item7["reason"] = "All clues valid and sourced."
    else:
        item7["score"] = 0
        item7["passed"] = False
        item7["reason"] = "No entries to check."
    details.append(item7)

    # --- Item 8: No extra unexpected keys in entries (bonus penalty for messy output) ---
    item8 = {
        "item": "No extra fields in match entries",
        "score": 0,
        "max_score": 5,
        "passed": False,
        "reason": ""
    }
    allowed_keys = {"doc_id", "doc_type", "clue"}
    extra_keys_found = False
    for entry in matches_list:
        keys = set(entry.keys())
        extra = keys - allowed_keys
        if extra:
            extra_keys_found = True
            break
    if not extra_keys_found:
        item8["score"] = 5
        item8["passed"] = True
        item8["reason"] = "No extra keys found."
    else:
        item8["score"] = 0
        item8["passed"] = False
        item8["reason"] = "Extra keys present."
    details.append(item8)

    total_score = sum(d["score"] for d in details)
    write_score(total_score, details)

def write_score(total, details):
    result = {
        "total_score": total,
        "details": details
    }
    out_path = os.path.join(WORKSPACE, SCORE_FILE)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Score: {total}/100")

if __name__ == "__main__":
    evaluate()
