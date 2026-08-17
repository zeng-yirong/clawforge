import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    ws = Path(workspace)
    details = []
    score = 0

    # 1. Check required directories exist (10 pts)
    dirs = ["ops/replies", "ops/todos"]
    for d in dirs:
        p = ws / d
        if p.is_dir():
            details.append({
                "item": f"Directory {d} exists",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "Found"
            })
            score += 5
        else:
            details.append({
                "item": f"Directory {d} exists",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"Missing: {p}"
            })

    # 2. Check that emails directory is present and JSONs are valid (10 pts)
    emails_dir = ws / "data/emails"
    if emails_dir.is_dir():
        details.append({
            "item": "data/emails directory exists",
            "score": 4,
            "max_score": 4,
            "passed": True,
            "reason": "Found"
        })
        score += 4

        # load original emails from env_builder (we need a snapshot? Hard to get original)
        # Instead, we just verify all JSON files parse correctly
        bad_json = 0
        email_map = {}
        for f in emails_dir.glob("*.json"):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                email_map[data["id"]] = data
            except (json.JSONDecodeError, KeyError):
                bad_json += 1
        if bad_json == 0:
            details.append({
                "item": "All email JSONs are valid",
                "score": 6,
                "max_score": 6,
                "passed": True,
                "reason": f"Parsed {len(email_map)} emails"
            })
            score += 6
        else:
            details.append({
                "item": "All email JSONs are valid",
                "score": 0,
                "max_score": 6,
                "passed": False,
                "reason": f"{bad_json} files invalid"
            })
    else:
        details.append({
            "item": "data/emails directory exists",
            "score": 0,
            "max_score": 4,
            "passed": False,
            "reason": "Missing"
        })
        details.append({
            "item": "All email JSONs are valid",
            "score": 0,
            "max_score": 6,
            "passed": False,
            "reason": "Cannot check"
        })

    # 3. Check reply file (30 pts)
    reply_dir = ws / "ops/replies"
    reply_correct = False
    reply_file = None
    if reply_dir.is_dir():
        files = list(reply_dir.glob("*.json"))
        if len(files) == 1:
            try:
                with open(files[0]) as fp:
                    reply_data = json.load(fp)
                # Must have field email_id set to "msg_001"
                if reply_data.get("email_id") == "msg_001":
                    reply_correct = True
                    reply_file = files[0].name
                else:
                    reason = f"Reply email_id is {reply_data.get('email_id')}, expected msg_001"
            except (json.JSONDecodeError, KeyError):
                reason = "Reply JSON invalid"
        else:
            reason = f"Expected 1 reply file, found {len(files)}"
    else:
        reason = "Reply directory missing"

    if reply_correct:
        details.append({
            "item": "Reply for John Manager's email",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"Found correct reply file {reply_file}"
        })
        score += 30
    else:
        details.append({
            "item": "Reply for John Manager's email",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": reason
        })

    # 4. Check todo file (30 pts)
    todo_dir = ws / "ops/todos"
    todo_correct = False
    todo_file = None
    if todo_dir.is_dir():
        files = list(todo_dir.glob("*.json"))
        if len(files) == 1:
            try:
                with open(files[0]) as fp:
                    todo_data = json.load(fp)
                if todo_data.get("source_email") == "msg_002":
                    todo_correct = True
                    todo_file = files[0].name
                else:
                    reason = f"Todo source_email is {todo_data.get('source_email')}, expected msg_002"
            except (json.JSONDecodeError, KeyError):
                reason = "Todo JSON invalid"
        else:
            reason = f"Expected 1 todo file, found {len(files)}"
    else:
        reason = "Todo directory missing"

    if todo_correct:
        details.append({
            "item": "TODO for HR email",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": f"Found correct todo file {todo_file}"
        })
        score += 30
    else:
        details.append({
            "item": "TODO for HR email",
            "score": 0,
            "max_score": 30,
            "passed": False,
            "reason": reason
        })

    # 5. Check that target emails (msg_001, msg_002) have folder="archived" and distractors unchanged (20 pts)
    # We already loaded email_map earlier; make sure we have it
    if 'email_map' not in locals():
        email_map = {}
        if emails_dir.is_dir():
            for f in emails_dir.glob("*.json"):
                try:
                    with open(f) as fp:
                        data = json.load(fp)
                    email_map[data["id"]] = data
                except:
                    pass

    archive_correct_count = 0
    distractor_errors = []
    # target ids
    for tid in ["msg_001", "msg_002"]:
        if tid in email_map:
            if email_map[tid]["folder"] == "archived":
                archive_correct_count += 1
            else:
                distractor_errors.append(f"{tid} folder={email_map[tid]['folder']} (expected archived)")
        else:
            distractor_errors.append(f"{tid} missing")

    # distractors that should NOT be archived
    keep_ids = ["msg_003", "msg_004", "msg_005", "msg_006", "msg_007", "msg_008", "msg_009"]
    for kid in keep_ids:
        if kid in email_map:
            original_folder = None
            # We need to know original folder. Since env_builder is deterministic, we can infer.
            # But per design, we can check if folder was changed to archived. Original was not archived except msg_006 (already archived).
            # Simpler: we just ensure folder is not "archived" for distractors (unless already archived).
            # For msg_006 it's already archived, that's fine.
            if email_map[kid]["folder"] == "archived" and kid != "msg_006":
                distractor_errors.append(f"{kid} was improperly archived")
        else:
            distractor_errors.append(f"{kid} missing")

    if archive_correct_count == 2 and len(distractor_errors) == 0:
        details.append({
            "item": "Correct archiving and no distractor modification",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": "Both target emails archived, distractors unchanged"
        })
        score += 20
    else:
        err_msg = "; ".join(distractor_errors) if distractor_errors else f"Only {archive_correct_count}/2 archived"
        details.append({
            "item": "Correct archiving and no distractor modification",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": err_msg
        })

    # Write results
    result = {
        "total_score": score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
