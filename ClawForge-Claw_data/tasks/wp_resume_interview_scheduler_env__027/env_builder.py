import os
import json
import datetime

def build_env():
    # Create directory structure
    os.makedirs("data/resumes", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # Optional distracting dir
    os.makedirs("db_dumps", exist_ok=True)

    # --- Jobs ---
    # Open job (Senior Software Engineer)
    job_open = {
        "job_id": "J001",
        "title": "Senior Software Engineer",
        "required_skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        "min_experience": 5,
        "hiring_manager": "M001",
        "status": "open"
    }
    # Closed job (should be ignored)
    job_closed = {
        "job_id": "J002",
        "title": "Junior Developer",
        "required_skills": ["Python", "JavaScript"],
        "min_experience": 1,
        "hiring_manager": "M002",
        "status": "closed"
    }
    # Another open but not senior (distractor)
    job_other = {
        "job_id": "J003",
        "title": "Data Analyst",
        "required_skills": ["SQL", "Python", "Tableau"],
        "min_experience": 2,
        "hiring_manager": "M001",
        "status": "open"
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump([job_open, job_closed, job_other], f)

    # --- Resumes ---
    # Correct candidate (skill match + experience >=5)
    cand_good = {
        "candidate_id": "C003",
        "candidate_name": "Alice Wang",
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        "years_experience": 7,
        "email": "alice@example.com"
    }
    # Skill match but experience too low
    cand_low_exp = {
        "candidate_id": "C001",
        "candidate_name": "Bob Li",
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        "years_experience": 3,
        "email": "bob@example.com"
    }
    # High experience but missing one skill (Docker)
    cand_missing_skill = {
        "candidate_id": "C002",
        "candidate_name": "Carol Zhang",
        "skills": ["Python", "Django", "PostgreSQL", "AWS"],
        "years_experience": 8,
        "email": "carol@example.com"
    }
    # Duplicate candidate_id with wrong skill set (should cause conflict, but we keep both)
    cand_dup_bad = {
        "candidate_id": "C002",
        "candidate_name": "Carol Zhang Dupe",
        "skills": ["Python", "Java", "C++"],
        "years_experience": 4,
        "email": "carol_dupe@example.com"
    }
    # Candidate with no experience field
    cand_no_exp = {
        "candidate_id": "C004",
        "candidate_name": "David Chen",
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        "email": "david@example.com"
    }
    # Non-matching skills
    cand_nomatch = {
        "candidate_id": "C005",
        "candidate_name": "Eve Liu",
        "skills": ["Java", "Spring", "MySQL"],
        "years_experience": 6,
        "email": "eve@example.com"
    }

    candidates = [cand_good, cand_low_exp, cand_missing_skill, cand_dup_bad, cand_no_exp, cand_nomatch]
    # Write to one file per candidate (to simulate scattered resumes)
    for cand in candidates:
        fname = f"data/resumes/{cand['candidate_id']}.json"
        with open(fname, "w") as f:
            json.dump(cand, f)

    # Add an extra file with irrelevant data (distractor)
    with open("data/resumes/extra_note.txt", "w") as f:
        f.write("This is not a resume, ignore.\n")

    # --- Accounts (interviewers) ---
    accounts = [
        {"account_id": "M001", "display_name": "Dr. Smith", "department": "Engineering", "email": "smith@company.com", "permissions": ["scheduler"]},
        {"account_id": "M002", "display_name": "Jane Doe", "department": "HR", "email": "jane@company.com", "permissions": ["recruiter"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f)

    # --- Contacts (candidate contacts) ---
    contacts = [
        {"contact_id": "C003", "name": "Alice Wang", "role": "Candidate", "email": "alice@example.com"},
        {"contact_id": "C001", "name": "Bob Li", "role": "Candidate", "email": "bob@example.com"},
        {"contact_id": "C002", "name": "Carol Zhang", "role": "Candidate", "email": "carol@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f)

    # --- Distracting file in ops (empty already) ---
    # Create a dummy file to make sure ops is not empty before agent
    with open("ops/.gitkeep", "w") as f:
        f.write("")

    # Create a .pkl file in db_dumps to distract
    import pickle
    pickle.dump({"dummy": True}, open("db_dumps/backup.pkl", "wb"))

if __name__ == "__main__":
    build_env()
