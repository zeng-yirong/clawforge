import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 当前日期文件
    with open("data/current_date.txt", "w") as f:
        f.write("2025-04-13")

    # candidates.json
    candidates = {
        "candidates": [
            {"candidate_id": "cand_1", "candidate_name": "Alice",  "skills": ["Python", "SQL", "AWS"]},
            {"candidate_id": "cand_2", "candidate_name": "Bob",    "skills": ["Java", "Spring", "Docker"]},
            {"candidate_id": "cand_3", "candidate_name": "Charlie","skills": ["Python", "NLP", "PyTorch"]},
            {"candidate_id": "cand_4", "candidate_name": "Diana",  "skills": ["Python", "SQL", "Java"]},
            {"candidate_id": "cand_5", "candidate_name": "Eve",    "skills": ["React", "Node", "MongoDB"]}
        ]
    }
    with open("data/candidates/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

    # jobs.json
    jobs = {
        "jobs": [
            {"job_id": "job_A", "title": "Backend Engineer",      "required_skills": ["Python", "SQL", "AWS"]},
            {"job_id": "job_B", "title": "Java Developer",        "required_skills": ["Java", "Spring", "Docker"], "urgent": True},
            {"job_id": "job_C", "title": "NLP Engineer",          "required_skills": ["Python", "NLP", "PyTorch"]},
            {"job_id": "job_D", "title": "Full Stack",            "required_skills": ["Python", "Java"], "status": "closed"}
        ]
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)

    # existing_interviews.json
    existing = {
        "interviews": [
            {"candidate_id": "cand_1", "job_id": "job_A", "scheduled_date": "2025-04-10", "reminder_minutes_before": 30}
        ]
    }
    with open("data/existing_interviews.json", "w") as f:
        json.dump(existing, f, indent=2)

    # 干扰文件（accounts / contacts / attachments）
    accounts = {"accounts": [{"account_id": "acc1", "display_name": "HR", "department": "HR", "email": "hr@company.com", "permissions": ["admin"]}]}
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {"contacts": [{"contact_id": "ct1", "name": "Alice", "role": "candidate", "email": "alice@example.com"}]}
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    attachments = {"attachments": [{"path": "resumes/Alice.pdf", "title": "Alice Resume", "kind": "pdf", "description": "Resume of Alice"}]}
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

if __name__ == "__main__":
    build_env()
