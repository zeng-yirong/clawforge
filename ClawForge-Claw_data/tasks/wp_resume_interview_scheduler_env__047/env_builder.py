import os
import json

def build_env():
    # Ensure base directories
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/archive", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Jobs
    jobs = [
        {
            "job_id": "J001",
            "title": "Data Engineer",
            "required_skills": ["Python", "SQL", "Spark"]
        },
        {
            "job_id": "J002",
            "title": "Frontend Developer",
            "required_skills": ["JavaScript", "React", "CSS"]
        }
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # Current candidates
    current_candidates = [
        {
            "candidate_id": "C001",
            "candidate_name": "Alice",
            "skills": ["Python", "SQL", "Spark", "Machine Learning"]
        },
        {
            "candidate_id": "C002",
            "candidate_name": "Bob",
            "skills": ["JavaScript", "React", "CSS", "TypeScript"]
        },
        {
            "candidate_id": "C003",
            "candidate_name": "Charlie",
            "skills": ["Python", "SQL"]  # Not enough for J001, and no JS for J002
        }
    ]
    with open("data/candidates/current_candidates.json", "w") as f:
        json.dump({"candidates": current_candidates}, f, indent=2)

    # Legacy candidates (interference)
    legacy_candidates = [
        {
            "candidate_id": "C004",
            "candidate_name": "David",
            "skills": ["Python", "SQL", "Spark"]  # Matches J001, but should be ignored
        }
    ]
    with open("data/archive/legacy_candidates.json", "w") as f:
        json.dump({"candidates": legacy_candidates}, f, indent=2)

    # Optional: a dummy contacts file for extra noise
    contacts = [
        {"contact_id": "CT001", "name": "Alice", "role": "Data Engineer", "email": "alice@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

if __name__ == "__main__":
    build_env()
