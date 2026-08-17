#!/usr/bin/env python3
"""
verify_workplace.py – wp_post_mails__002
Pure code verification, no external dependencies.
Checks that the agent produced ops/launch_draft.json with the correct
platform, author, title and content derived from the latest approved brief.
Scoring: 100 points total.
"""
import os
import json
import sys

def verify(workspace: str) -> dict:
    details = []
    total = 0

    # 1. Output directory exists (10 pts)
    ops_path = os.path.join(workspace, "ops")
    exists_ops = os.path.isdir(ops_path)
    details.append({
        "item": "ops directory exists",
        "score": 10 if exists_ops else 0,
        "max_score": 10,
        "passed": exists_ops,
        "reason": "Found ops/" if exists_ops else "ops/ directory missing"
    })
    if exists_ops:
        total += 10

    # 2. launch_draft.json exists and is valid JSON (10 pts)
    draft_path = os.path.join(ops_path, "launch_draft.json")
    exists_file = os.path.isfile(draft_path)
    if exists_file:
        try:
            with open(draft_path, "r") as f:
                data = json.load(f)
            valid_json = True
        except (json.JSONDecodeError, Exception):
            valid_json = False
    else:
        valid_json = False
    details.append({
        "item": "launch_draft.json exists and is valid JSON",
        "score": 10 if (exists_file and valid_json) else 0,
        "max_score": 10,
        "passed": (exists_file and valid_json),
        "reason": (
            "File found and JSON valid" if (exists_file and valid_json)
            else "File missing or invalid JSON"
        )
    })
    if exists_file and valid_json:
        total += 10

    # If no valid file, return early with accumulated score
    if not (exists_file and valid_json):
        return {
            "total_score": total,
            "details": details
        }

    # 3. Required fields present in JSON (20 pts)
    required_fields = ["platform", "author", "title", "content"]
    missing = [f for f in required_fields if f not in data]
    fields_ok = len(missing) == 0
    details.append({
        "item": "JSON contains all required fields (platform, author, title, content)",
        "score": 20 if fields_ok else 0,
        "max_score": 20,
        "passed": fields_ok,
        "reason": "All fields present" if fields_ok else f"Missing: {', '.join(missing)}"
    })
    if fields_ok:
        total += 20

    # 4. Platform must be "x" (15 pts)
    platform_correct = (data.get("platform") == "x")
    details.append({
        "item": "platform == 'x'",
        "score": 15 if platform_correct else 0,
        "max_score": 15,
        "passed": platform_correct,
        "reason": f"Got '{data.get('platform')}', expected 'x'" if not platform_correct else "Correct"
    })
    if platform_correct:
        total += 15

    # 5. Author must be "@auroralabs" (15 pts)
    author_correct = (data.get("author") == "@auroralabs")
    details.append({
        "item": "author == '@auroralabs'",
        "score": 15 if author_correct else 0,
        "max_score": 15,
        "passed": author_correct,
        "reason": f"Got '{data.get('author')}', expected '@auroralabs'" if not author_correct else "Correct"
    })
    if author_correct:
        total += 15

    # 6. Title must be "Orbital Launch Day" (15 pts)
    title_correct = (data.get("title") == "Orbital Launch Day")
    details.append({
        "item": "title == 'Orbital Launch Day'",
        "score": 15 if title_correct else 0,
        "max_score": 15,
        "passed": title_correct,
        "reason": f"Got '{data.get('title')}', expected 'Orbital Launch Day'" if not title_correct else "Correct"
    })
    if title_correct:
        total += 15

    # 7. Content must be exact (15 pts)
    expected_content = "We are excited to announce our orbital launch on April 1st! #OrbitalLaunch"
    content_correct = (data.get("content") == expected_content)
    details.append({
        "item": "content matches approved brief v3",
        "score": 15 if content_correct else 0,
        "max_score": 15,
        "passed": content_correct,
        "reason": f"Content mismatch" if not content_correct else "Correct"
    })
    if content_correct:
        total += 15

    return {
        "total_score": total,
        "details": details
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
