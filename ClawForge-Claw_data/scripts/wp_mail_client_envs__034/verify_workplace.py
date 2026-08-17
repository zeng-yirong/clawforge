import sys
import os
import json
import re
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    score = 0
    max_total = 100
    details = []

    # 1. Directory structure (10 pts) – must have ops/ directory
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found ops/ directory"})
        score += 10
    else:
        details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ directory missing"})

    # 2. File existence and format legality (10 pts)
    required_files = ["ops/archive.json", "ops/replies.json", "ops/todos.json"]
    all_legal = True
    for rel_file in required_files:
        fpath = ws / rel_file
        if not fpath.is_file():
            details.append({"item": f"File {rel_file} exists", "score": 0, "max_score": 10, "passed": False, "reason": f"Missing file {rel_file}"})
            all_legal = False
            break
        try:
            data = json.loads(fpath.read_text())
        except json.JSONDecodeError:
            details.append({"item": f"File {rel_file} is valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON in {rel_file}"})
            all_legal = False
            break
    if all_legal:
        # Also check that archive.json is a list, replies is a dict, todos is a list
        archive_data = json.loads((ws / "ops/archive.json").read_text())
        replies_data = json.loads((ws / "ops/replies.json").read_text())
        todos_data = json.loads((ws / "ops/todos.json").read_text())
        if not isinstance(archive_data, list):
            details.append({"item": "archive.json is a list", "score": 0, "max_score": 10, "passed": False, "reason": "archive.json should be a list"})
            all_legal = False
        elif not isinstance(replies_data, dict):
            details.append({"item": "replies.json is a dict", "score": 0, "max_score": 10, "passed": False, "reason": "replies.json should be a dict"})
            all_legal = False
        elif not isinstance(todos_data, list):
            details.append({"item": "todos.json is a list", "score": 0, "max_score": 10, "passed": False, "reason": "todos.json should be a list"})
            all_legal = False
        else:
            details.append({"item": "All 3 files exist and are structurally valid", "score": 10, "max_score": 10, "passed": True, "reason": "Files present and legal JSON with correct top-level types"})
            score += 10

    # If files missing or illegal, stop early (cannot proceed)
    if not all_legal:
        # we already added details; just set total
        final_score = min(score, 100)
        out = {"total_score": final_score, "details": details}
        with open(ws / "workplace_score.json", "w") as f:
            json.dump(out, f, indent=2)
        return

    # 3. Check archive.json content (30 pts)
    # Expected: all read newsletters (email_005) and read spam (email_007) -> email_005, email_007? Also any other read newsletter/spam? Only those.
    # Also note: email_006 and email_008 are not read, so should not be archived.
    # TODO: check for duplicates, extra entries.
    expected_archive = {"email_005", "email_007"}
    archive_set = set(archive_data)
    archive_correct = (archive_set == expected_archive)
    if archive_correct:
        details.append({"item": "archive.json contains exactly expected IDs", "score": 30, "max_score": 30, "passed": True, "reason": f"Archive set matches: {expected_archive}"})
        score += 30
    else:
        missing = expected_archive - archive_set
        extra = archive_set - expected_archive
        reason = f"Missing: {missing}, Extra: {extra}"
        details.append({"item": "archive.json contains exactly expected IDs", "score": 0, "max_score": 30, "passed": False, "reason": reason})
        score += 0

    # 4. Check replies.json (30 pts)
    # Expected: emails from Alice (contact_001) that are not read: email_001 and email_012
    # Each reply should be a string. We don't check exact content but should be non-empty and plausible.
    expected_reply_ids = {"email_001", "email_012"}
    reply_ids_set = set(replies_data.keys())
    reply_correct_ids = (reply_ids_set == expected_reply_ids)
    if not reply_correct_ids:
        missing = expected_reply_ids - reply_ids_set
        extra = reply_ids_set - expected_reply_ids
        reason = f"Reply keys mismatch. Missing: {missing}, Extra: {extra}"
        details.append({"item": "replies.json contains exactly IDs that should get replies", "score": 0, "max_score": 30, "passed": False, "reason": reason})
        score += 0
    else:
        # Check that each reply is a non-empty string
        all_nonempty = True
        for eid in expected_reply_ids:
            msg = replies_data[eid]
            if not isinstance(msg, str) or len(msg.strip()) == 0:
                all_nonempty = False
                reason = f"Reply for {eid} is empty or not a string"
                break
        if all_nonempty:
            details.append({"item": "replies.json correct IDs and non-empty content", "score": 30, "max_score": 30, "passed": True, "reason": "All replies present and non-empty"})
            score += 30
        else:
            details.append({"item": "replies.json correct IDs but content missing/empty", "score": 15, "max_score": 30, "passed": False, "reason": reason})
            score += 15

    # 5. Check todos.json (20 pts)
    # Expected: emails from Sarah (contact_003) that have "urgent" or "bug" in subject or body:
    # email_003 (subject "URGENT"), email_004 (body contains "bug"), email_011 (subject "Fix for minor bug" - "bug" appears)
    # So all three: email_003, email_004, email_011
    expected_todo_ids = {"email_003", "email_004", "email_011"}
    todo_ids_in_list = set()
    todo_items = []
    for item in todos_data:
        if not isinstance(item, dict):
            continue
        eid = item.get("id") or item.get("email_id") or item.get("email")  # flexible key
        if eid and isinstance(eid, str):
            todo_ids_in_list.add(eid)
        todo_items.append(item)
    # Also check each todo has some description
    if todo_ids_in_list == expected_todo_ids:
        # check each has description
        descriptions_ok = all(len(item.get("description", "").strip()) > 0 for item in todo_items if (item.get("id") or item.get("email_id") or item.get("email")) in expected_todo_ids)
        if descriptions_ok:
            details.append({"item": "todos.json correct IDs and descriptions", "score": 20, "max_score": 20, "passed": True, "reason": "All expected TODO items present with descriptions"})
            score += 20
        else:
            details.append({"item": "todos.json correct IDs but missing descriptions", "score": 10, "max_score": 20, "passed": False, "reason": "Some TODOs lack description"})
            score += 10
    else:
        missing = expected_todo_ids - todo_ids_in_list
        extra = todo_ids_in_list - expected_todo_ids
        reason = f"TODO IDs mismatch. Missing: {missing}, Extra: {extra}"
        details.append({"item": "todos.json contains exactly expected TODO IDs", "score": 0, "max_score": 20, "passed": False, "reason": reason})
        score += 0

    # Final score
    final_score = min(score, 100)
    out = {"total_score": final_score, "details": details}
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    verify()
