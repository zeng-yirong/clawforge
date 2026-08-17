import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/drafts", exist_ok=True)
    os.makedirs("ledger", exist_ok=True)

    # ========== Main project_docs.json (with duplicates, invalid entries) ==========
    main_records = [
        {
            "doc_id": "001",
            "project_id": "proj-alpha",
            "title": "Installation Guide Reproduction",
            "path": "docs/proj-alpha/install.md"
            # no timestamp → treated as old version
        },
        {
            "doc_id": "002",
            "project_id": "proj-beta",
            "title": "API Auth Reproduction",
            "path": "docs/proj-beta/auth.md",
            "timestamp": "2025-03-18"
        },
        {
            "doc_id": "003",
            "project_id": "proj-gamma",
            "title": "",                     # empty title → invalid
            "path": "docs/proj-gamma/tutorial.md",
            "timestamp": "2025-03-19"
        },
        {
            "doc_id": "004",
            "project_id": "proj-delta",
            "title": "Deployment Steps Reproduction",
            "path": "docs/proj-delta/deploy.md",
            "timestamp": "2025-03-17"
        },
        {
            "doc_id": "005",
            # missing project_id → invalid
            "title": "Log Analysis Reproduction",
            "path": "docs/proj-epsilon/logs.md",
            "timestamp": "2025-03-20"
        },
        {
            "doc_id": "001",                # duplicate of 001, with newer timestamp
            "project_id": "proj-alpha",
            "title": "Installation Guide Reproduction",
            "path": "docs/proj-alpha/install_v2.md",
            "timestamp": "2025-03-20"
        }
    ]
    with open("data/project_docs.json", "w") as f:
        json.dump({"project_docs": main_records}, f, indent=2)

    # ========== drafts/unconfirmed.json (some valid, some duplicate/old) ==========
    unconfirmed_records = [
        {
            "doc_id": "006",
            "project_id": "proj-zeta",
            "title": "Config Migration Reproduction",
            "path": "docs/proj-zeta/migration.md",
            "timestamp": "2025-03-22"
        },
        {
            "doc_id": "001",                # older timestamp than main duplicate → should be discarded
            "project_id": "proj-alpha",
            "title": "Installation Guide Reproduction",
            "path": "docs/proj-alpha/install_v1.md",
            "timestamp": "2025-03-15"
        },
        {
            "doc_id": "007",
            "project_id": "proj-eta",
            "title": "Benchmark Reproduction",
            "path": "docs/proj-eta/bench.md",
            "timestamp": "2025-03-21"
        },
        {
            "doc_id": "008",
            # missing path → invalid
            "project_id": "proj-theta",
            "title": "Security Patch Reproduction",
            "timestamp": "2025-03-23"
        }
    ]
    with open("data/drafts/unconfirmed.json", "w") as f:
        json.dump({"project_docs": unconfirmed_records}, f, indent=2)

    # ========== drafts/obsolete.json (all marked obsolete) ==========
    obsolete_records = [
        {
            "doc_id": "009",
            "project_id": "proj-iota",
            "title": "Old Setup Reproduction",
            "path": "docs/proj-iota/setup.md",
            "timestamp": "2025-02-10",
            "status": "obsolete"
        },
        {
            "doc_id": "010",
            "project_id": "proj-kappa",
            "title": "Deprecated Test Reproduction",
            "path": "docs/proj-kappa/test.md",
            "timestamp": "2025-01-05",
            "status": "obsolete"
        }
    ]
    with open("data/drafts/obsolete.json", "w") as f:
        json.dump({"project_docs": obsolete_records}, f, indent=2)

    # ========== Unrelated files (noise) ==========
    accounts = [
        {"account_id": "a1", "display_name": "Alice", "department": "R&D", "email": "alice@lab.org", "permissions": ["read"]},
        {"account_id": "a2", "display_name": "Bob", "department": "Ops", "email": "bob@lab.org", "permissions": ["write"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    contacts = [
        {"contact_id": "c1", "name": "Carol", "role": "Lead", "email": "carol@lab.org"},
        {"contact_id": "c2", "name": "Dave", "role": "Engineer", "email": "dave@lab.org"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
