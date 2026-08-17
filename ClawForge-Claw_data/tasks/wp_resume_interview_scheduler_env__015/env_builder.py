import json
import os

def build_env():
    # Ensure base directories exist
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ----- accounts.json -----
    accounts = [
        {
            "account_id": "acc_alice",
            "display_name": "Alice Wang",
            "department": "Engineering",
            "email": "alice@company.com",
            "permissions": ["hiring_manager"]
        },
        {
            "account_id": "acc_bob",
            "display_name": "Bob Smith",
            "department": "Engineering",
            "email": "bob@company.com",
            "permissions": ["engineer"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ----- candidates.json (with duplicates and mismatches) -----
    candidates = [
        # cand_001 – two submissions (duplicate)
        {
            "candidate_id": "cand_001",
            "candidate_name": "Zhang Wei",
            "skills": ["Python", "SQL", "Airflow"],
            "added_at": "2025-03-01"
        },
        {
            "candidate_id": "cand_001",
            "candidate_name": "Zhang Wei",
            "skills": ["Python", "SQL"],  # missing Airflow – newer but skill set incomplete
            "added_at": "2025-03-05"
        },
        # cand_002 – extra skill (Spark) ⇒ not exact match
        {
            "candidate_id": "cand_002",
            "candidate_name": "Li Na",
            "skills": ["Python", "SQL", "Airflow", "Spark"],
            "added_at": "2025-02-28"
        },
        # cand_003 – completely wrong skills
        {
            "candidate_id": "cand_003",
            "candidate_name": "Wang Fang",
            "skills": ["Java", "C++"],
            "added_at": "2025-03-10"
        },
        # cand_004 – exact match, earliest among exact matches
        {
            "candidate_id": "cand_004",
            "candidate_name": "Chen Yu",
            "skills": ["Python", "SQL", "Airflow"],
            "added_at": "2025-03-10"
        },
        # cand_005 – also exact match, but later date
        {
            "candidate_id": "cand_005",
            "candidate_name": "Zhao Lei",
            "skills": ["Python", "SQL", "Airflow"],
            "added_at": "2025-03-12"
        }
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # ----- contacts.json (interviewer pool) -----
    contacts = [
        {
            "contact_id": "con_001",
            "name": "Charlie Doe",
            "role": "Recruiter",
            "email": "charlie@company.com"
        },
        {
            "contact_id": "con_002",
            "name": "Bob Smith",
            "role": "Hiring Manager",
            "email": "bob@company.com"
        },
        {
            "contact_id": "con_003",
            "name": "Diana Prince",
            "role": "Engineer",
            "email": "diana@company.com"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ----- jobs.json -----
    jobs = [
        {
            "job_id": "job_001",
            "title": "Junior Data Analyst",
            "required_skills": ["SQL", "Excel"]
        },
        {
            "job_id": "job_002",
            "title": "Senior Data Engineer",
            "required_skills": ["Python", "SQL", "Airflow"]
        }
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

if __name__ == "__main__":
    build_env()
