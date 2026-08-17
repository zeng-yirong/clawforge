import os
import json

def build_env():
    # Create directory structure
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # Job definitions
    jobs = [
        {
            "job_id": "J001",
            "title": "Backend Developer",
            "required_skills": ["Python", "SQL", "AWS"]
        },
        {
            "job_id": "J002",
            "title": "Data Analyst",
            "required_skills": ["Excel", "SQL", "Tableau"]
        }
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # Candidate definitions – include exact matches, partial matches, case mismatch, and completely unrelated
    candidates = [
        {
            "candidate_id": "C001",
            "candidate_name": "Alice Wang",
            "skills": ["Python", "SQL", "AWS"]
        },
        {
            "candidate_id": "C002",
            "candidate_name": "Bob Li",
            "skills": ["Python", "SQL", "AWS", "Docker"]
        },
        {
            "candidate_id": "C003",
            "candidate_name": "Carol Chen",
            "skills": ["Python", "SQL"]
        },
        {
            "candidate_id": "C004",
            "candidate_name": "David Zhang",
            "skills": ["Java", "C++", "Go"]
        },
        {
            "candidate_id": "C005",
            "candidate_name": "Eva Liu",
            "skills": ["python", "sql", "aws"]   # wrong case
        },
        {
            "candidate_id": "C006",
            "candidate_name": "Frank Wu",
            "skills": ["Python", "SQL", "AWS", "Kubernetes"]
        }
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # Distractor file – a dummy blocked list, not mentioned in prompt
    with open("data/blocked.txt", "w") as f:
        f.write("C003\nC005\n")

    # Additional distractor directories with empty marker
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/.gitkeep", "w") as f:
        f.write("")

if __name__ == "__main__":
    build_env()
