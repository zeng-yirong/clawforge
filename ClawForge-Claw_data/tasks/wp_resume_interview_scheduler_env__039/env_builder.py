import os
import json
import datetime

def build_env():
    # Ensure directories exist
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # --- Candidates (including duplicates, mismatches, extra skills, typos) ---
    candidates = [
        {"candidate_id": "C001", "candidate_name": "Alice Wang", "skills": ["Python", "SQL", "AWS"]},          # full match
        {"candidate_id": "C002", "candidate_name": "Bob Li", "skills": ["Python", "SQL"]},                     # missing AWS
        {"candidate_id": "C003", "candidate_name": "Carol Zhang", "skills": ["Python", "AWS", "SQL"]},        # full match (order diff)
        {"candidate_id": "C004", "candidate_name": "Dave Chen", "skills": ["Java", "Python", "SQL", "AWS"]},  # extra skill, still full match
        {"candidate_id": "C005", "candidate_name": "Eve Liu", "skills": ["Python", "AWS", "Kubernetes"]},     # missing SQL
        {"candidate_id": "C001", "candidate_name": "Alice Wang", "skills": ["Python", "SQL"]},                # duplicate ID with different skills (interference, should be ignored due to duplicate)
        {"candidate_id": "C006", "candidate_name": "Frank Wu", "skills": ["python", "sql", "aws"]},          # lowercase, should still match? We'll treat case-insensitive? For uniqueness, let's treat as partial. To avoid ambiguity, we'll require exact case match. So this is not a full match.
        {"candidate_id": "C007", "candidate_name": "Grace Xu", "skills": ["Python", "SQL", "AWS", "Docker"]},# full match
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # --- Jobs ---
    jobs = [
        {"job_id": "J001", "title": "Senior Data Engineer", "required_skills": ["Python", "SQL", "AWS"]},
        {"job_id": "J002", "title": "Junior Data Engineer", "required_skills": ["Python", "SQL"]},  # decoy
        {"job_id": "J003", "title": "Data Scientist", "required_skills": ["Python", "R", "Machine Learning"]} # decoy
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # --- Backup (old version as distraction) ---
    old_jobs = [
        {"job_id": "J001", "title": "Senior Data Engineer", "required_skills": ["Python", "SQL"]}  # old version missing AWS
    ]
    with open("data/backup/old_jobs.json", "w") as f:
        json.dump({"jobs": old_jobs}, f, indent=2)

    # --- Dummy schedule file (empty, might be overwritten) ---
    with open("ops/interviews.json", "w") as f:
        json.dump([], f, indent=2)

    # --- Other irrelevant files ---
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": [{"id": "A001", "name": "Recruiter Admin"}]}, f, indent=2)

if __name__ == "__main__":
    build_env()
