import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("data/docs", exist_ok=True)

    # ---- Interfering files ----
    # accounts.json (distractor)
    accounts = [
        {"account_id": "a001", "display_name": "Alice", "department": "R&D", "email": "alice@corp.com", "permissions": ["read", "write"]},
        {"account_id": "a002", "display_name": "Bob", "department": "QA", "email": "bob@corp.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # contacts.json (distractor)
    contacts = [
        {"contact_id": "c001", "name": "Carol", "role": "Lead", "email": "carol@corp.com"},
        {"contact_id": "c002", "name": "Dave", "role": "Reviewer", "email": "dave@corp.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # ---- Main index: project_docs.json ----
    # Contains records for two projects; only "proj-repro-001" is our target.
    project_docs = [
        # Target project docs (4 docs, 3 success, 1 failure)
        {"doc_id": "doc-001", "project_id": "proj-repro-001", "title": "Setup Guide", "path": "data/docs/doc-001.json"},
        {"doc_id": "doc-002", "project_id": "proj-repro-001", "title": "API Test Results", "path": "data/docs/doc-002.json"},
        {"doc_id": "doc-003", "project_id": "proj-repro-001", "title": "Performance Benchmark", "path": "data/docs/doc-003.json"},
        {"doc_id": "doc-004", "project_id": "proj-repro-001", "title": "Security Audit", "path": "data/docs/doc-004.json"},
        # Interfering project docs (NOT target)
        {"doc_id": "doc-005", "project_id": "proj-other-99", "title": "Old Doc", "path": "data/docs/doc-005.json"},
        {"doc_id": "doc-006", "project_id": "proj-other-99", "title": "Legacy Notes", "path": "data/docs/doc-006.json"},
        # Doc with missing path (distractor, but record will be ignored later if agent checks path existence)
        {"doc_id": "doc-007", "project_id": "proj-repro-001", "title": "Missing File", "path": "data/docs/doc-007.json"},
    ]
    with open("data/projects/project_docs.json", "w") as f:
        json.dump({"project_docs": project_docs}, f)

    # ---- Actual document files ----
    # Target docs
    # doc-001 (success)
    with open("data/docs/doc-001.json", "w") as f:
        json.dump({"doc_id": "doc-001", "project_id": "proj-repro-001", "status": "success", "steps": 5, "notes": "All good"}, f)
    # doc-002 (success)
    with open("data/docs/doc-002.json", "w") as f:
        json.dump({"doc_id": "doc-002", "project_id": "proj-repro-001", "status": "success", "steps": 3, "notes": "Minor issues resolved"}, f)
    # doc-003 (success)
    with open("data/docs/doc-003.json", "w") as f:
        json.dump({"doc_id": "doc-003", "project_id": "proj-repro-001", "status": "success", "steps": 7, "notes": "Performed on staging"}, f)
    # doc-004 (failure)
    with open("data/docs/doc-004.json", "w") as f:
        json.dump({"doc_id": "doc-004", "project_id": "proj-repro-001", "status": "failure", "steps": 2, "notes": "Environment mismatch"}, f)

    # Interfering project docs (should be ignored)
    with open("data/docs/doc-005.json", "w") as f:
        json.dump({"doc_id": "doc-005", "project_id": "proj-other-99", "status": "success", "steps": 1, "notes": "Not needed"}, f)
    with open("data/docs/doc-006.json", "w") as f:
        json.dump({"doc_id": "doc-006", "project_id": "proj-other-99", "status": "failure", "steps": 4, "notes": "Irrelevant"}, f)

    # doc-007 is missing intentionally – no file created (distractor, but agent should skip it)

if __name__ == "__main__":
    build_env()
