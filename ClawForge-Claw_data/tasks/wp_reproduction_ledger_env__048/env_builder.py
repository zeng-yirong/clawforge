import os
import json
from datetime import datetime, timezone

def build_env():
    # Create directories
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("notes", exist_ok=True)
    os.makedirs("research_kb", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # decoy directory

    # ----- project_docs.json (reference) -----
    project_docs = {
        "project_docs": [
            {
                "doc_id": "bug-142",
                "project_id": "data-visualizer",
                "title": "Crash on large dataset import",
                "path": "docs/bug-142.md"
            },
            {
                "doc_id": "bug-143",
                "project_id": "data-visualizer",
                "title": "Axis label truncation",
                "path": "docs/bug-143.md"
            },
            {
                "doc_id": "bug-201",
                "project_id": "chart-renderer",
                "title": "Memory leak on animation",
                "path": "docs/bug-201.md"
            }
        ]
    }
    with open("data/projects/project_docs.json", "w") as f:
        json.dump(project_docs, f, indent=2)

    # ----- accounts.json (decoy, not used) -----
    accounts = {
        "accounts": [
            {"account_id": "a1", "display_name": "Dr. R", "department": "Research", "email": "r@lab.org", "permissions": ["admin"]},
            {"account_id": "a2", "display_name": "Alice", "department": "QA", "email": "alice@lab.org", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ----- contacts.json (decoy) -----
    contacts = {
        "contacts": [
            {"contact_id": "c1", "name": "Bob", "role": "Developer", "email": "bob@lab.org"},
            {"contact_id": "c2", "name": "Carol", "role": "Designer", "email": "carol@lab.org"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ----- reproduction notes (the real data) -----
    # CORRECT final version
    correct_steps = (
        "1. Start the application with an empty workspace.\n"
        "2. Import 'large_dataset.csv' (50,001 rows, mixed types).\n"
        "3. Click on 'Generate Chart' with default settings.\n"
        "4. Observe UI freeze for ~15 seconds then crash."
    )
    correct_result = "REPRODUCED (confirmed on v2.4.3)"

    correct_note = (
        "# Reproduction: bug-142\n\n"
        "## Steps\n"
        f"{correct_steps}\n\n"
        "## Result\n"
        f"{correct_result}\n\n"
        "## Environment\n"
        "OS: Ubuntu 22.04, Python 3.10, lib v2.4.3"
    )
    with open("notes/repro_bug-142_final.md", "w") as f:
        f.write(correct_note)

    # DECOY 1 – old draft with incomplete steps
    draft_steps = (
        "1. Start app.\n"
        "2. Import CSV.\n"
        "3. Generate chart → crash."
    )
    draft_result = "REPRODUCED (partially)"
    draft_note = (
        "# Reproduction: bug-142\n\n"
        "## Steps (draft)\n"
        f"{draft_steps}\n\n"
        "## Result\n"
        f"{draft_result}\n\n"
        "## Environment\n"
        "OS: Ubuntu 22.04"
    )
    with open("notes/repro_bug-142_draft.md", "w") as f:
        f.write(draft_note)

    # DECOY 2 – wrong project (bug-201)
    wrong_steps = (
        "1. Load chart-renderer demo.\n"
        "2. Cycle through 1000 animations.\n"
        "3. Monitor memory → leak detected."
    )
    wrong_result = "MEMORY LEAK (approx 2MB per cycle)"
    wrong_note = (
        "# Reproduction: bug-201\n\n"
        "## Steps\n"
        f"{wrong_steps}\n\n"
        "## Result\n"
        f"{wrong_result}\n\n"
        "## Environment\n"
        "OS: Ubuntu 22.04, Python 3.11"
    )
    with open("notes/repro_bug-201.md", "w") as f:
        f.write(wrong_note)

    # DECOY 3 – old version with wrong result (marked as FAILED)
    failed_steps = (
        "1. Start app.\n"
        "2. Import large CSV.\n"
        "3. Generate chart → no crash (unexpected)."
    )
    failed_result = "NOT REPRODUCIBLE (v2.4.2)"
    failed_note = (
        "# Reproduction: bug-142\n\n"
        "## Steps\n"
        f"{failed_steps}\n\n"
        "## Result\n"
        f"{failed_result}\n\n"
        "## Environment\n"
        "OS: Ubuntu 22.04, Python 3.9, lib v2.4.2"
    )
    with open("notes/repro_bug-142_old.md", "w") as f:
        f.write(failed_note)

    # DECOY 4 – a completely unrelated text file
    with open("notes/scratchpad.txt", "w") as f:
        f.write("random thoughts about the reproduction... not useful.")

    # ----- extra decoy directories/files -----
    os.makedirs("temp", exist_ok=True)
    with open("temp/backup.json", "w") as f:
        json.dump({"placeholder": True}, f)

if __name__ == "__main__":
    build_env()
