import os
import json

def build_env():
    # Ensure base directories exist
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("reminders", exist_ok=True)

    # ── Jobs ────────────────────────────────────────────────────
    jobs = {
        "jobs": [
            {
                "job_id": "job_001",
                "title": "Senior Data Engineer",
                "required_skills": ["Python", "SQL", "Spark", "Airflow"]
            },
            {
                "job_id": "job_002",
                "title": "Backend Developer",
                "required_skills": ["Java", "Spring", "PostgreSQL"]
            },
            {
                "job_id": "job_003",
                "title": "Data Analyst",
                "required_skills": ["Python", "SQL", "Tableau"]
            }
        ]
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)

    # ── Candidates (with intentional distractors) ───────────────
    candidates = {
        "candidates": [
            {
                "candidate_id": "candidate_001",
                "candidate_name": "Alice Wang",
                "skills": ["Python", "SQL", "AWS"]
            },
            {
                "candidate_id": "candidate_002",
                "candidate_name": "Bob Li",
                "skills": ["Python", "SQL", "Spark"]
            },
            {
                "candidate_id": "candidate_003",
                "candidate_name": "Carol Zhang",
                "skills": ["Python", "SQL", "Spark", "Airflow", "Kafka"]
            },
            {
                "candidate_id": "candidate_004",
                "candidate_name": "David Chen",
                "skills": ["Java", "Scala", "Spark"]
            },
            {
                # Duplicate skill set but missing Airflow – not a full match
                "candidate_id": "candidate_005",
                "candidate_name": "Eve Liu",
                "skills": ["Python", "SQL", "Spark"]
            }
        ]
    }
    with open("data/candidates/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

    # ── Distractor files (old backup, CSV, etc.) ────────────────
    # Back-up jobs (outdated)
    with open("data/jobs/jobs_backup.json", "w") as f:
        json.dump({"jobs": [{"job_id": "job_001", "title": "Senior Data Engineer (closed)", "required_skills": ["Python", "SQL"]}]}, f)

    # Irrelevant CSV
    with open("data/old_applicants.csv", "w") as f:
        f.write("name,skills\nFrank,Python\nGrace,Java\n")

    # Dummy accounts/contacts (not needed for task)
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": []}, f)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": []}, f)

    # Empty reminders file (agent must add the entry)
    with open("reminders/reminders.json", "w") as f:
        json.dump({"reminders": []}, f)

    # Empty ops directory – file will be created by agent
    pass  # already created

if __name__ == "__main__":
    build_env()
