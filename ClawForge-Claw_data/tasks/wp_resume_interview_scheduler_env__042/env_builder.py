import os
import json

def build_env():
    # Create data directories
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/exclusions", exist_ok=True)
    os.makedirs("ops", exist_ok=True)  # expected output dir

    # Candidates
    candidates = [
        {"candidate_id": "c001", "candidate_name": "Alice", "skills": ["Python", "SQL", "Django"]},
        {"candidate_id": "c002", "candidate_name": "Bob", "skills": ["Java", "Spring", "SQL"]},
        {"candidate_id": "c003", "candidate_name": "Carol", "skills": ["Python", "SQL", "Flask", "Docker"]},
        {"candidate_id": "c004", "candidate_name": "Dave", "skills": ["C++", "Python"]},
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f)

    # Jobs
    jobs = [
        {"job_id": "j001", "title": "Backend Developer", "required_skills": ["Python", "SQL"]},
        {"job_id": "j002", "title": "Java Developer", "required_skills": ["Java", "Spring"]},
        {"job_id": "j003", "title": "DevOps Engineer", "required_skills": ["Docker", "Kubernetes"]},
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f)

    # Exclusions
    excluded_candidates = ["c002"]
    excluded_jobs = ["j003"]
    with open("data/exclusions/candidates_to_exclude.json", "w") as f:
        json.dump({"excluded_candidate_ids": excluded_candidates}, f)
    with open("data/exclusions/jobs_to_exclude.json", "w") as f:
        json.dump({"excluded_job_ids": excluded_jobs}, f)

    # Noise / distractors
    # an old backup candidate file (should be ignored)
    old_candidates = [
        {"candidate_id": "c099", "candidate_name": "OldTimer", "skills": ["COBOL"]}
    ]
    with open("data/candidates/old_candidates_backup.json", "w") as f:
        json.dump({"candidates": old_candidates}, f)

    # an archived job file
    archived_jobs = [
        {"job_id": "j099", "title": "Legacy", "required_skills": ["Fortran"]}
    ]
    with open("data/jobs/archived_jobs.json", "w") as f:
        json.dump({"jobs": archived_jobs}, f)

    # extra empty directories
    os.makedirs("data/archived", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)

if __name__ == "__main__":
    build_env()
