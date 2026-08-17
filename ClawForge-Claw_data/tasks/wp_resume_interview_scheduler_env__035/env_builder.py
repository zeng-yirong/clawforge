import os
import json
import shutil

def build_env():
    # Ensure base directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Accounts (interviewer)
    accounts = [
        {
            "account_id": "A001",
            "display_name": "Dr. Smith",
            "department": "Engineering",
            "email": "smith@example.com",
            "permissions": ["schedule"]
        },
        {
            "account_id": "A002",
            "display_name": "Jane Doe",
            "department": "HR",
            "email": "jane@example.com",
            "permissions": ["view"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # Contacts (distractors)
    contacts = [
        {"contact_id": "CT001", "name": "Alice", "role": "Manager", "email": "alice@company.com"},
        {"contact_id": "CT002", "name": "Bob", "role": "Recruiter", "email": "bob@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # Attachments (distractors)
    attachments = [
        {"path": "attachments/resume_alice.pdf", "title": "Alice Resume", "kind": "pdf", "description": ""},
        {"path": "attachments/resume_bob.pdf", "title": "Bob Resume", "kind": "pdf", "description": ""}
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # Candidates
    candidates = [
        {"candidate_id": "C001", "candidate_name": "Alice", "skills": ["Python", "SQL", "Machine Learning"]},
        {"candidate_id": "C002", "candidate_name": "Bob", "skills": ["Java", "C++", "Python"]},
        {"candidate_id": "C003", "candidate_name": "Charlie", "skills": ["Python", "Django", "SQL"]},
        {"candidate_id": "C004", "candidate_name": "Diana", "skills": ["Python", "SQL", "Data Analysis"]},
        {"candidate_id": "C005", "candidate_name": "Eve", "skills": ["", "Python", " "]},            # dirty – empty/whitespace
        {"candidate_id": "C006", "candidate_name": "Frank", "skills": ["Rust"]}
    ]
    with open("data/candidates/candidates.json", "w") as f:
        os.makedirs("data/candidates", exist_ok=True)
        json.dump({"candidates": candidates}, f, indent=2)

    # Backup (old version, same structure but outdated)
    backup_candidates = [
        {"candidate_id": "C001", "candidate_name": "Alice", "skills": ["Python"]},  # old – minimal
        {"candidate_id": "C002", "candidate_name": "Bob", "skills": ["Java"]}
    ]
    with open("data/backup/candidates_backup.json", "w") as f:
        json.dump({"candidates": backup_candidates}, f, indent=2)

    # Jobs
    jobs = [
        {"job_id": "J001", "title": "Data Scientist", "required_skills": ["Python", "SQL", "Machine Learning"]},
        {"job_id": "J002", "title": "Backend Developer", "required_skills": ["Java", "Python", "C++"]},
        {"job_id": "J003", "title": "Frontend Developer", "required_skills": ["JavaScript", "React"]},
        {"job_id": "J004", "title": "Data Analyst", "required_skills": ["Python", "SQL", "Excel"]}
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # Write a .gitkeep into ops to keep the directory (empty)
    with open("ops/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
