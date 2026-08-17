#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify(workspace):
    details = []
    total = 0
    max_total = 100

    target_path = Path(workspace) / "ops" / "reengagement_targets.json"
    contacts_path = Path(workspace) / "data" / "contacts.json"

    # 1. File existence (10)
    exists = target_path.exists()
    details.append({
        "item": "ops/reengagement_targets.json exists",
        "score": 10 if exists else 0,
        "max_score": 10,
        "passed": exists,
        "reason": "File found" if exists else "File missing"
    })
    total += 10 if exists else 0

    # 2. JSON validity (10)
    is_valid = False
    target_data = None
    if exists:
        try:
            target_data = load_json(target_path)
            is_valid = True
        except:
            is_valid = False
        details.append({
            "item": "File is valid JSON",
            "score": 10 if is_valid else 0,
            "max_score": 10,
            "passed": is_valid,
            "reason": "Valid" if is_valid else "Invalid JSON"
        })
        total += 10 if is_valid else 0
    else:
        details.append({
            "item": "File is valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File not found"
        })

    # 3. Correct contact IDs (30)
    expected_ids = {"ct_001", "ct_003", "ct_005"}
    score3 = 0
    reason3 = ""
    if exists and is_valid and isinstance(target_data, list):
        actual_ids = set(target_data)
        if actual_ids == expected_ids:
            score3 = 30
            reason3 = "Perfect match"
        elif expected_ids.issubset(actual_ids):
            score3 = 20
            reason3 = "Contains all expected but also extra IDs"
        elif actual_ids.issubset(expected_ids):
            score3 = 20
            reason3 = "Only expected IDs but missing some"
        else:
            score3 = 10
            reason3 = "Missing expected and contains extra"
    elif not isinstance(target_data, list) and exists:
        score3 = 0
        reason3 = "Not a list"
    else:
        score3 = 0
        reason3 = "File not accessible or invalid"
    details.append({
        "item": "Correct contact IDs in target list",
        "score": score3,
        "max_score": 30,
        "passed": score3 == 30,
        "reason": reason3
    })
    total += score3

    # 4. Tag update on contacts (30)
    score4 = 0
    reason4 = ""
    if contacts_path.exists():
        try:
            contacts = load_json(contacts_path)
            target_tagged = True
            non_target_tagged = False
            for c in contacts:
                cid = c.get("contact_id")
                tags = c.get("tags", [])
                if cid in expected_ids:
                    if "re-engage" not in tags:
                        target_tagged = False
                else:
                    if "re-engage" in tags:
                        non_target_tagged = True
            if target_tagged and not non_target_tagged:
                score4 = 30
                reason4 = "All target contacts have 're-engage' tag, no unintended additions"
            elif target_tagged and non_target_tagged:
                score4 = 20
                reason4 = "All target contacts tagged, but non-target also got the tag"
            elif not target_tagged and not non_target_tagged:
                score4 = 10
                reason4 = "Some or all target contacts missing tag, but no false positives"
            else:
                score4 = 0
                reason4 = "Missing tags on targets and also added to non-targets"
        except Exception as e:
            reason4 = f"Error reading contacts: {e}"
        details.append({
            "item": "Contacts updated with 're-engage' tag",
            "score": score4,
            "max_score": 30,
            "passed": score4 == 30,
            "reason": reason4
        })
        total += score4
    else:
        details.append({
            "item": "Contacts updated with 're-engage' tag",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": "data/contacts.json not found"
        })

    # 5. Folder values not altered (10) - based on known initial state
    original_folders = {
        "ct_001": "inactive",
        "ct_002": "business",
        "ct_003": "inactive",
        "ct_004": "inactive",
        "ct_005": "inactive"
    }
    score5 = 0
    reason5 = ""
    if contacts_path.exists():
        try:
            contacts = load_json(contacts_path)
            folder_ok = True
            for c in contacts:
                cid = c.get("contact_id")
                expected = original_folders.get(cid)
                if expected is not None and c.get("folder") != expected:
                    folder_ok = False
                    break
            score5 = 10 if folder_ok else 0
            reason5 = "Folders unchanged" if folder_ok else "One or more folders were modified"
        except:
            score5 = 0
            reason5 = "Cannot read contacts"
        details.append({
            "item": "Folder values not altered",
            "score": score5,
            "max_score": 10,
            "passed": score5 == 10,
            "reason": reason5
        })
        total += score5
    else:
        details.append({
            "item": "Folder values not altered",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "data/contacts.json missing"
        })

    total = min(total, 100)
    score_obj = {"total_score": total, "details": details}
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(score_obj, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
