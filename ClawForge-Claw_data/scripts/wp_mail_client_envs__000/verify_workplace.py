"""
Pure-code workplace verifier for wp_mail_client_envs__000.
No LLM, no network calls, only standard library.
"""
import sys
import os
import json
import csv
import statistics
import math
from collections import defaultdict
from pathlib import Path

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    
    score_items = []
    
    # 1. Check output file exists (10 points)
    out_file = ws / "ops" / "urgent_clients.json"
    if out_file.exists():
        score_items.append({"item": "output file exists", "score": 10, "max_score": 10, "passed": True, "reason": "File ops/urgent_clients.json exists."})
    else:
        score_items.append({"item": "output file exists", "score": 0, "max_score": 10, "passed": False, "reason": "File ops/urgent_clients.json not found."})
        # Early exit? No, continue to report details.
    
    if not out_file.exists():
        total_score = 0
        finalize(score_items, total_score)
        return
    
    # 2. Check JSON validity (10 points)
    try:
        output_data = json.loads(out_file.read_text(encoding='utf-8'))
        if not isinstance(output_data, list):
            raise ValueError("Not a list")
        score_items.append({"item": "valid JSON and is a list", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON list."})
    except Exception as e:
        score_items.append({"item": "valid JSON and is a list", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid or non-list: {e}"})
        total_score = sum(s["score"] for s in score_items)
        finalize(score_items, total_score)
        return
    
    # 3. Load contacts and emails to compute ground truth
    contacts_file = ws / "data" / "contacts.json"
    emails_dir = ws / "data" / "emails"
    
    try:
        contacts = load_json(contacts_file)
        client_ids = {c["contact_id"] for c in contacts if c["role"] == "Client"}
    except Exception as e:
        score_items.append({"item": "load contacts", "score": 0, "max_score": 0, "passed": False, "reason": f"Cannot load contacts: {e}"})
        total_score = sum(s["score"] for s in score_items)
        finalize(score_items, total_score)
        return
    
    expected = []
    if emails_dir.is_dir():
        for fpath in emails_dir.glob("*.json"):
            try:
                email = load_json(fpath)
                if (email["sender_id"] in client_ids and
                    email["importance"] == "high" and
                    email["has_read"] is False):
                    expected.append({"id": email["id"], "subject": email["subject"]})
            except Exception:
                pass
    else:
        score_items.append({"item": "emails directory", "score": 0, "max_score": 0, "passed": False, "reason": "data/emails/ not found."})
        total_score = sum(s["score"] for s in score_items)
        finalize(score_items, total_score)
        return
    
    # Sort expected by id for consistency
    expected_sorted = sorted(expected, key=lambda x: x["id"])
    expected_count = len(expected_sorted)
    
    # Process agent output: ensure each entry has id and subject
    agent_output = []
    for entry in output_data:
        if isinstance(entry, dict) and "id" in entry and "subject" in entry:
            agent_output.append(entry)
    agent_sorted = sorted(agent_output, key=lambda x: x["id"])
    agent_count = len(agent_sorted)
    
    # 4. Record count match (20 points)
    if agent_count == expected_count:
        score_items.append({"item": "record count match", "score": 20, "max_score": 20, "passed": True, "reason": f"Expected {expected_count} records, got {agent_count}."})
    else:
        score_items.append({"item": "record count match", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_count} records, got {agent_count}."})
    
    # 5. Check each expected record's id (30 points total, 10 per record if 3 records, adjust)
    # Compute per-record weight for id and subject
    if expected_count > 0:
        id_weight = 30 // expected_count   # floor, remainder will be handled
        subj_weight = 30 // expected_count
        # Distribute remainder to first few records
        id_weights = [id_weight] * expected_count
        subj_weights = [subj_weight] * expected_count
        remainder_id = 30 - id_weight * expected_count
        remainder_subj = 30 - subj_weight * expected_count
        for i in range(remainder_id):
            id_weights[i] += 1
        for i in range(remainder_subj):
            subj_weights[i] += 1
    else:
        id_weight = 0
        subj_weight = 0
    
    id_score = 0
    subj_score = 0
    for i, exp in enumerate(expected_sorted):
        # find matching entry in agent output (by id)
        match = next((a for a in agent_sorted if a["id"] == exp["id"]), None)
        if match:
            if match["id"] == exp["id"]:
                id_score += id_weights[i]
            if match["subject"] == exp["subject"]:
                subj_score += subj_weights[i]
    
    score_items.append({"item": "id correctness", "score": id_score, "max_score": 30, "passed": id_score == 30, "reason": f"id match {id_score}/30"})
    score_items.append({"item": "subject correctness", "score": subj_score, "max_score": 30, "passed": subj_score == 30, "reason": f"subject match {subj_score}/30"})
    
    total_score = sum(s["score"] for s in score_items)
    finalize(score_items, total_score)

def finalize(items, total):
    result = {
        "total_score": total,
        "details": items
    }
    out_path = Path(sys.argv[1]) / "workplace_score.json" if len(sys.argv) > 1 else Path("workplace_score.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
