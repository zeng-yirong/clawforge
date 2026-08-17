import os
import json

def build_env():
    # Create required directories
    os.makedirs("jobs", exist_ok=True)
    os.makedirs("candidates", exist_ok=True)
    os.makedirs("meta", exist_ok=True)
    os.makedirs("schedule", exist_ok=True)

    # Today's date
    with open("meta/today.txt", "w") as f:
        f.write("2025-04-01")

    # Target job
    job = {
        "job_id": "job_004",
        "title": "Backend Developer",
        "required_skills": ["python", "sql", "docker"]
    }
    with open("jobs/new_job.json", "w") as f:
        json.dump(job, f)

    # Other jobs (distractors)
    other_jobs = {
        "jobs": {
            "job_001": {"job_id": "job_001", "title": "Frontend Developer", "required_skills": ["javascript", "react", "css"]},
            "job_002": {"job_id": "job_002", "title": "Data Analyst", "required_skills": ["sql", "python", "excel"]},
            "job_003": {"job_id": "job_003", "title": "DevOps Engineer", "required_skills": ["docker", "kubernetes", "aws"]}
        }
    }
    with open("jobs/other_jobs.json", "w") as f:
        json.dump(other_jobs, f)

    # Candidates (with distractors)
    candidates = {
        "candidates": {
            "cand_001": {
                "candidate_id": "cand_001",
                "candidate_name": "Alice Johnson",
                "skills": ["python", "sql", "docker", "aws"]
            },
            "cand_002": {
                "candidate_id": "cand_002",
                "candidate_name": "Bob Smith",
                "skills": ["java", "sql", "docker"]
            },
            "cand_003": {
                "candidate_id": "cand_003",
                "candidate_name": "Charlie Brown",
                "skills": ["Python", "SQL", "Docker"]
            },
            "cand_004": {
                "candidate_id": "cand_004",
                "candidate_name": "Diana Prince",
                "skills": ["python", "sql"]
            },
            "cand_005": {
                "candidate_id": "cand_005",
                "candidate_name": "Eve Adams",
                "skills": ["python", "sql", "docker", "kubernetes"]
            }
        }
    }
    with open("candidates/candidates.json", "w") as f:
        json.dump(candidates, f)

    # Archived distractor
    os.makedirs("candidates/archived", exist_ok=True)
    old_candidate = {
        "candidate_id": "cand_001",
        "candidate_name": "Alice Johnson (old)",
        "skills": ["python", "sql"]
    }
    with open("candidates/archived/old_candidates.json", "w") as f:
        json.dump({"archived": [old_candidate]}, f)

if __name__ == "__main__":
    build_env()
