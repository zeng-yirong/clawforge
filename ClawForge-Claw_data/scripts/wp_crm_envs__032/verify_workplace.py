import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace).resolve()
    score_details = []
    total_score = 0

    # ---------- 1. Check directory structure (10 points) ----------
    required_dirs = [
        "data",
        "data/reminders",
        "ops"
    ]
    dir_score = 0
    for d in required_dirs:
        p = workspace / d
        if p.is_dir():
            dir_score += 3  # 3 per dir, total 9, round up to 10
        else:
            dir_score += 0
    dir_score = min(dir_score, 10)
    total_score += dir_score
    score_details.append({
        "item": "Directory structure (data/, data/reminders/, ops/)",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": f"{dir_score}/10 directories correctly exist"
    })

    # ---------- 2. Load required input files (validity) ----------
    try:
        contacts_path = workspace / "data/contacts.json"
        with open(contacts_path) as f:
            contacts_data = json.load(f)
        contacts = contacts_data.get("contacts", [])
        if not isinstance(contacts, list):
            raise ValueError("contacts is not a list")
    except Exception as e:
        score_details.append({
            "item": "data/contacts.json valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Cannot load or parse contacts.json: {e}"
        })
        total_score += 0
        # cannot proceed
        write_score(total_score, score_details, workspace)
        return

    try:
        reminders_path = workspace / "data/reminders/reminders.json"
        with open(reminders_path) as f:
            reminders_data = json.load(f)
        reminders = reminders_data.get("reminders", [])
        if not isinstance(reminders, list):
            raise ValueError("reminders is not a list")
        input_valid_score = 10
    except Exception as e:
        reminders = []
        input_valid_score = 0
        score_details.append({
            "item": "data/reminders/reminders.json valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Cannot load or parse reminders.json: {e}"
        })
        total_score += 0
        write_score(total_score, score_details, workspace)
        return

    score_details.append({
        "item": "Input data files valid",
        "score": input_valid_score,
        "max_score": 10,
        "passed": True,
        "reason": "Both contacts.json and reminders/reminders.json parsed successfully"
    })
    total_score += input_valid_score

    # ---------- 3. Build expected missing contacts ----------
    # Business contacts: folder == "business"
    business_contacts = [c for c in contacts if c.get("folder") == "business"]
    # reminder contact_ids set
    reminder_contact_ids = {r["contact_id"] for r in reminders if r.get("contact_id")}
    # missing = business contacts not in reminder_contact_ids
    expected_missing = sorted(
        [{"contact_id": c["contact_id"], "full_name": c["full_name"]}
         for c in business_contacts if c["contact_id"] not in reminder_contact_ids],
        key=lambda x: x["contact_id"]
    )

    # ---------- 4. Check agent output file ----------
    output_path = workspace / "ops/missing_bday_reminders.json"
    if not output_path.exists():
        score_details.append({
            "item": "Output file exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/missing_bday_reminders.json not found"
        })
        total_score += 0
        write_score(total_score, score_details, workspace)
        return

    score_details.append({
        "item": "Output file exists",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "ops/missing_bday_reminders.json exists"
    })
    total_score += 10

    # Parse output
    try:
        with open(output_path) as f:
            agent_output = json.load(f)
        if not isinstance(agent_output, list):
            raise ValueError("Output is not a JSON list")
    except Exception as e:
        score_details.append({
            "item": "Output file valid JSON list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Cannot parse or invalid structure: {e}"
        })
        total_score += 0
        write_score(total_score, score_details, workspace)
        return

    score_details.append({
        "item": "Output file valid JSON list",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "Output is a valid JSON list"
    })
    total_score += 10

    # ---------- 5. Check content (70 points) ----------
    # Convert agent output to set of (contact_id, full_name) sorted
    try:
        agent_items = []
        for entry in agent_output:
            cid = entry.get("contact_id")
            name = entry.get("full_name")
            if not cid or not name:
                raise ValueError(f"Missing contact_id or full_name in entry: {entry}")
            agent_items.append((cid, name))
        agent_set = set(agent_items)
    except Exception as e:
        score_details.append({
            "item": "Output entries contain contact_id and full_name",
            "score": 0,
            "max_score": 70,
            "passed": False,
            "reason": f"Entry structure error: {e}"
        })
        total_score += 0
        write_score(total_score, score_details, workspace)
        return

    expected_set = set((x["contact_id"], x["full_name"]) for x in expected_missing)

    # Extra entries (false positives)
    extra = agent_set - expected_set
    # Missing entries (false negatives)
    missing = expected_set - agent_set

    if extra or missing:
        penalty = 0
        # each extra or missing causes -20 points (max 70 deducted)
        num_errors = len(extra) + len(missing)
        penalty = min(num_errors * 20, 70)
        content_score = max(70 - penalty, 0)
        reason_parts = []
        if missing:
            reason_parts.append(f"missing {len(missing)} contact(s): {[m for m in missing]}")
        if extra:
            reason_parts.append(f"extra contact(s): {[e for e in extra]}")
        reason = "; ".join(reason_parts) if reason_parts else "content mismatch"
    else:
        content_score = 70
        reason = "Exactly matches expected missing business contacts"

    score_details.append({
        "item": "Correct missing birthday reminders (contact_id & full_name)",
        "score": content_score,
        "max_score": 70,
        "passed": content_score == 70,
        "reason": reason
    })
    total_score += content_score

    # Final score capped at 100
    final_score = min(total_score, 100)
    write_score(final_score, score_details, workspace)

def write_score(total, details, workspace):
    output = {
        "total_score": total,
        "details": details
    }
    score_path = workspace / "workplace_score.json"
    with open(score_path, "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
