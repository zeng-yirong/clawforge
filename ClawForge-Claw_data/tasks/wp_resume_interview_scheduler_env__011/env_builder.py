import os
import json

def build_env():
    # 确保 cwd 已经是 
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/old_backup", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 候选人数据（包含干扰项：不匹配、部分匹配）
    candidates = {
        "candidates": [
            {
                "candidate_id": "candidate_001",
                "candidate_name": "Alice Wang",
                "skills": ["Python", "Docker", "Kubernetes", "AWS"]
            },
            {
                "candidate_id": "candidate_002",
                "candidate_name": "Bob Li",
                "skills": ["Python", "SQL", "Excel"]
            },
            {
                "candidate_id": "candidate_003",
                "candidate_name": "Carol Zhang",
                "skills": ["Java", "C++"]
            },
            {
                "candidate_id": "candidate_004",
                "candidate_name": "David Chen",
                "skills": ["Python", "Docker", "SQL"]
            }
        ]
    }
    with open("data/candidates/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

    # 职位数据
    jobs = {
        "jobs": [
            {
                "job_id": "job_001",
                "title": "Software Engineer",
                "required_skills": ["Python", "Docker", "Kubernetes"]
            },
            {
                "job_id": "job_002",
                "title": "Data Analyst",
                "required_skills": ["Python", "SQL"]
            }
        ]
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)

    # 干扰项：过期的备份候选人
    old_candidates = {
        "candidates": [
            {
                "candidate_id": "candidate_001",
                "candidate_name": "Alice Wang (old)",
                "skills": ["Python", "Docker"]
            }
        ]
    }
    with open("data/old_backup/candidates_backup.json", "w") as f:
        json.dump(old_candidates, f, indent=2)

    # 其他领域文件（诱饵）
    accounts = {
        "accounts": [
            {"account_id": "acc_001", "display_name": "HR Team", "department": "HR", "email": "hr@company.com", "permissions": ["scheduler"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "ct_001", "name": "John Smith", "role": "Hiring Manager", "email": "john@company.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    attachments = {
        "attachments": [
            {"path": "resumes/Alice.pdf", "title": "Alice Resume", "kind": "application/pdf", "description": "Resume of Alice Wang"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

if __name__ == "__main__":
    build_env()
