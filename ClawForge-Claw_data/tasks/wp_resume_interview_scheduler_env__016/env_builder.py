import os
import json
import datetime

def build_env():
    # data directory
    os.makedirs("data", exist_ok=True)
    # config directory
    os.makedirs("config", exist_ok=True)

    # ---- accounts.json (distractor) ----
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Michele", "department": "HR", "email": "michele@company.com", "permissions": ["admin"]},
            {"account_id": "A002", "display_name": "Raj", "department": "Engineering", "email": "raj@company.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---- attachments.json (distractor) ----
    attachments = {
        "attachments": [
            {"path": "templates/interview_rubric.pdf", "title": "Interview Rubric", "kind": "pdf", "description": "Standard scoring sheet"},
            {"path": "data/candidates/resumes/C003_resume.docx", "title": "Charlie Resume", "kind": "docx", "description": "Unprocessed resume"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # ---- contacts.json (distractor) ----
    contacts = {
        "contacts": [
            {"contact_id": "CNT001", "name": "Dr. Sarah Kim", "role": "Tech Lead", "email": "sarah.kim@company.com"},
            {"contact_id": "CNT002", "name": "Mike Liu", "role": "Senior Engineer", "email": "mike.liu@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # ---- candidates.json (main data) ----
    candidates = {
        "candidates": [
            {
                "candidate_id": "C001",
                "candidate_name": "Alice Johnson",
                "skills": ["Python", "SQL", "Machine Learning"]
            },
            {
                "candidate_id": "C002",
                "candidate_name": "Bob Martinez",
                "skills": ["Java", "SQL", "Spring"]
            },
            {
                "candidate_id": "C003",
                "candidate_name": "Charlie Chen",
                "skills": ["Python", "Docker", "Kubernetes", "AWS"]
            },
            {
                "candidate_id": "C004",
                "candidate_name": "Diana Smith",
                "skills": ["Python"]
            },
            {
                "candidate_id": "C005",
                "candidate_name": "Eve Turner",
                "skills": ["Java", "SQL", "Docker"]   # skill mismatch: no Java job
            }
        ]
    }
    with open("data/candidates/candidates.json", "w") as f:
        os.makedirs("data/candidates", exist_ok=True)
        json.dump(candidates, f, indent=2)

    # ---- jobs.json (main data) ----
    jobs = {
        "jobs": [
            {
                "job_id": "J001",
                "title": "Data Engineer",
                "required_skills": ["Python", "SQL"]
            },
            {
                "job_id": "J002",
                "title": "DevOps Engineer",
                "required_skills": ["Python", "Docker"]
            },
            {
                "job_id": "J003",
                "title": "Java Developer",
                "required_skills": ["Java", "Spring"]
            },
            {
                "job_id": "J004",
                "title": "ML Engineer",
                "required_skills": ["Python", "TensorFlow"]   # no candidate matches
            }
        ]
    }
    with open("data/jobs/jobs.json", "w") as f:
        os.makedirs("data/jobs", exist_ok=True)
        json.dump(jobs, f, indent=2)

    # ---- config/settings.json (schedule parameters) ----
    settings = {
        "interview_start_time": "2025-06-01T09:00:00",
        "interview_duration_minutes": 30,
        "reminder_before_minutes": 15
    }
    with open("config/settings.json", "w") as f:
        json.dump(settings, f, indent=2)

    # ---- old_interviews.json (distractor) ----
    old = {
        "interviews": [
            {"candidate": "C006", "job": "J005", "date": "2025-05-20"}
        ]
    }
    with open("ops/old_interviews.json", "w") as f:
        os.makedirs("ops", exist_ok=True)
        json.dump(old, f, indent=2)

if __name__ == "__main__":
    build_env()
