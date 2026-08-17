import os
import json
import random

def build_env():
    # Create directory structure
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("schedules", exist_ok=True)
    os.makedirs("reminders", exist_ok=True)

    # --- Jobs ---
    jobs = {
        "JOB-2024-001": {
            "title": "Backend Developer",
            "required_skills": ["Python", "Java", "SQL"]
        },
        "JOB-2024-007": {
            "title": "Senior Full Stack Engineer",
            "required_skills": ["Python", "React", "PostgreSQL", "Docker"]
        },
        "JOB-2024-012": {
            "title": "DevOps Engineer",
            "required_skills": ["Docker", "Kubernetes", "Terraform"]
        }
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": list(jobs.values())}, f, indent=2)  # wrapper=jobs, but we need key job_id => embed key in each item
    # Better: store with id field
    jobs_with_id = [{"job_id": k, **v} for k,v in jobs.items()]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs_with_id}, f, indent=2)

    # --- Candidates ---
    candidates = [
        {
            "candidate_id": "C-001",
            "candidate_name": "Alice Smith",
            "skills": ["Python", "React", "Java", "Docker"]  # missing PostgreSQL
        },
        {
            "candidate_id": "C-002",
            "candidate_name": "Bob Johnson",
            "skills": ["Python", "React", "PostgreSQL", "Docker"]  # perfect match
        },
        {
            "candidate_id": "C-003",
            "candidate_name": "Carol Williams",
            "skills": ["Python", "PostgreSQL", "Docker", "Kubernetes"]  # missing React
        },
        {
            "candidate_id": "C-004",
            "candidate_name": "David Brown",
            "skills": ["Python", "React", "PostgreSQL", "Docker", "Node.js"]  # overqualified but matches
        },
        {
            "candidate_id": "C-005",
            "candidate_name": "Eve Davis",
            "skills": ["Python", "React"]  # clearly missing
        }
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # --- Old / misleading schedule files ---
    # An expired interview for C-005 (different job)
    old_schedule = {
        "candidate_id": "C-005",
        "job_id": "JOB-2024-001",
        "interview_date": "2024-12-20",
        "interview_time": "10:00",
        "duration_minutes": 60
    }
    with open("schedules/interview_C-005_JOB-2024-001.json", "w") as f:
        json.dump(old_schedule, f, indent=2)

    # A junk file
    with open("schedules/old_data.csv", "w") as f:
        f.write("candidate,job,date\nC-001,JOB-2024-012,2024-11-01\n")

    # An empty reminder directory
    # (intentionally left empty except maybe a dummy file)
    dummy_reminder = {
        "candidate_id": "C-003",
        "job_id": "JOB-2024-012",
        "reminder_time": "2024-06-01T09:00:00"
    }
    with open("reminders/dummy_old_reminder.json", "w") as f:
        json.dump(dummy_reminder, f, indent=2)

if __name__ == "__main__":
    build_env()
