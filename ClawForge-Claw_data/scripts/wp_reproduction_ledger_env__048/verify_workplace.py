#!/usr/bin/env python3
"""
Verify that the agent correctly archived the bug reproduction ledger.
Checks:
- existence of research_kb/reproduction_ledger.json
- valid JSON structure
- contains exactly one ledger entry
- the entry has correct doc_id, project_id, steps, result, archived_at
- the steps and result match the correct final note file (notes/repro_bug-142_final.md)
Scoring: 0-100, with penalties for missing/extra entries, field errors, or mismatches.
"""
import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime

def load_correct_artifact():
    """
    Read the ground-truth note file and extract expected steps & result.
    Returns (expected_steps, expected_result).
    """
    note_path = Path("notes/repro_bug-142_final.md")
    if not note_path.exists():
        return None, None
    content = note_path.read_text()
    # Extract Steps section
    steps_match = re.search(r"## Steps\n(.*?)\n## Result", content, re.DOTALL)
    result_match = re.search(r"## Result\n(.*?)(?:\n##|$)", content, re.DOTALL)
    if not steps_match or not result_match:
        return None, None
    expected_steps = steps_match.group(1).strip()
    expected_result = result_match.group(1).strip()
    return expected_steps, expected_result

def verify(workspace):
    ws = Path(workspace).resolve()
    os.chdir(ws)

    details = []
    total_score = 0

    # 1. Directory structure (10 pts)
    # Check that research_kb exists (created by env_builder, should not be deleted)
    research_kb = ws / "research_kb"
    if research_kb.is_dir():
        details.append({
            "item": "research_kb directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Directory found."
        })
        total_score += 10
    else:
        details.append({
            "item": "research_kb directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "research_kb/ not found."
        })

    # 2. JSON file exists (10 pts)
    ledger_path = research_kb / "reproduction_ledger.json"
    if ledger_path.is_file():
        details.append({
            "item": "reproduction_ledger.json exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "File found."
        })
        total_score += 10
    else:
        details.append({
            "item": "reproduction_ledger.json exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "File missing."
        })
        # Cannot continue without file
        result = {
            "total_score": total_score,
            "details": details
        }
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. Valid JSON (10 pts)
    try:
        with open(ledger_path, "r") as f:
            data = json.load(f)
        details.append({
            "item": "Valid JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Parsed successfully."
        })
        total_score += 10
    except (json.JSONDecodeError, ValueError) as e:
        details.append({
            "item": "Valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON: {e}"
        })
        result = {"total_score": total_score, "details": details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 4. Top-level structure: must contain a list under 'ledger' key (or 'entries'? we accept 'ledger_entries' per prompt hint)
    # The prompt didn't specify a wrapper key explicitly, but the ledger schema typically uses something like 'entries'.
    # We'll be flexible: accept a list at top level, or a dict with a key that is a list.
    # For uniqueness we require a list with one entry.
    entries = None
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        # look for common wrapper keys
        for key in ('ledger_entries', 'entries', 'ledger', 'reproductions'):
            if key in data and isinstance(data[key], list):
                entries = data[key]
                break
    if entries is None:
        details.append({
            "item": "Ledger entries structure",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Cannot find a list of entries in the JSON. Expected a list or dict with 'entries'/'ledger_entries'."
        })
        total_score += 0
    else:
        details.append({
            "item": "Ledger entries structure",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Found entries list with {len(entries)} item(s)."
        })
        total_score += 10

    # 5. Number of entries (10 pts) – exactly 1
    if entries is not None:
        if len(entries) == 1:
            details.append({
                "item": "Exactly one reproduction entry",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "One entry found as expected."
            })
            total_score += 10
        else:
            details.append({
                "item": "Exactly one reproduction entry",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"Found {len(entries)} entries; expected exactly 1."
            })
    else:
        # already failed structure
        pass

    # 6. Field presence & correctness for the single entry (40 pts total: 10 each for doc_id, project_id, steps, result)
    # Load expected values from ground-truth note
    expected_steps, expected_result = load_correct_artifact()
    if expected_steps is None or expected_result is None:
        # fallback: hardcode (should not happen if env_builder runs)
        expected_steps = (
            "1. Start the application with an empty workspace.\n"
            "2. Import 'large_dataset.csv' (50,001 rows, mixed types).\n"
            "3. Click on 'Generate Chart' with default settings.\n"
            "4. Observe UI freeze for ~15 seconds then crash."
        )
        expected_result = "REPRODUCED (confirmed on v2.4.3)"

    if entries and len(entries) == 1:
        entry = entries[0]
        # 6a. doc_id (10)
        doc_ok = entry.get("doc_id") == "bug-142"
        details.append({
            "item": "doc_id field",
            "score": 10 if doc_ok else 0,
            "max_score": 10,
            "passed": doc_ok,
            "reason": f"doc_id = {entry.get('doc_id')} (expected 'bug-142')" if not doc_ok else "doc_id is correct."
        })
        total_score += 10 if doc_ok else 0

        # 6b. project_id (10)
        proj_ok = entry.get("project_id") == "data-visualizer"
        details.append({
            "item": "project_id field",
            "score": 10 if proj_ok else 0,
            "max_score": 10,
            "passed": proj_ok,
            "reason": f"project_id = {entry.get('project_id')} (expected 'data-visualizer')" if not proj_ok else "project_id is correct."
        })
        total_score += 10 if proj_ok else 0

        # 6c. steps (10) – exact match with ground truth (after stripping whitespace)
        actual_steps = entry.get("steps", "").strip()
        expected_steps_clean = expected_steps.strip()
        steps_ok = actual_steps == expected_steps_clean
        details.append({
            "item": "reproduction steps",
            "score": 10 if steps_ok else 0,
            "max_score": 10,
            "passed": steps_ok,
            "reason": "Steps match ground truth." if steps_ok else f"Steps differ (expected length {len(expected_steps_clean)}, got {len(actual_steps)})."
        })
        total_score += 10 if steps_ok else 0

        # 6d. result (10)
        actual_result = entry.get("result", "").strip()
        expected_result_clean = expected_result.strip()
        result_ok = actual_result == expected_result_clean
        details.append({
            "item": "result field",
            "score": 10 if result_ok else 0,
            "max_score": 10,
            "passed": result_ok,
            "reason": "Result matches ground truth." if result_ok else f"Result is '{actual_result}' (expected '{expected_result_clean}')."
        })
        total_score += 10 if result_ok else 0

        # 6e. bonus: archived_at timestamp exists and is parseable (10 pts extra, but total max 100? We'll keep within 100)
        # Actually we have 10+10+10+10+10+10+10+10+10 = 90 so far, we can add 10 for timestamp.
        has_timestamp = False
        ts = entry.get("archived_at", "")
        if ts:
            try:
                # Accept ISO format or simple datetime
                datetime.fromisoformat(ts)
                has_timestamp = True
            except:
                pass
        if has_timestamp:
            details.append({
                "item": "archived_at timestamp",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "Valid timestamp present."
            })
            total_score += 10
        else:
            details.append({
                "item": "archived_at timestamp",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "Missing or invalid timestamp field 'archived_at'."
            })
    else:
        # no entry to check
        for field in ["doc_id", "project_id", "steps", "result", "archived_at"]:
            details.append({
                "item": f"{field} field",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "No entry to evaluate."
            })

    # Ensure total does not exceed 100
    total_score = min(total_score, 100)
    # Make integer
    total_score = int(total_score)

    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
