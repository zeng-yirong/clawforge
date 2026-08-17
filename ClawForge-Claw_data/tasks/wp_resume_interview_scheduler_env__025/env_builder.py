import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    
    # 职位数据
    jobs = {
        "jobs": [
            {"job_id": "J001", "title": "Senior Software Engineer", "required_skills": ["Python", "Django", "SQL"]},
            {"job_id": "J002", "title": "Data Scientist", "required_skills": ["Python", "Machine Learning"]}
        ]
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)

    # 候选人数据（包含干扰项：部分匹配、超配、完全不匹配）
    candidates = {
        "candidates": [
            {"candidate_id": "C001", "name": "Alice", "skills": ["Python", "Django", "SQL"]},
            {"candidate_id": "C002", "name": "Bob", "skills": ["Python", "Django"]},
            {"candidate_id": "C003", "name": "Charlie", "skills": ["Python", "SQL"]},
            {"candidate_id": "C004", "name": "Diana", "skills": ["Python", "Django", "SQL", "AWS"]},
            {"candidate_id": "C005", "name": "Eve", "skills": ["Java", "C++"]},
            {"candidate_id": "C006", "name": "Frank", "skills": ["Python", "Machine Learning"]},
            {"candidate_id": "C007", "name": "Grace", "skills": ["Python", "Machine Learning", "Statistics"]}
        ]
    }
    with open("data/candidates/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

    # 已有排期（占用09:00-09:30）
    schedule = {
        "schedule": [
            {"interview_time": "2025-03-10T09:00", "duration_minutes": 30, "candidate_id": "OLD001"}
        ]
    }
    with open("data/schedule.json", "w") as f:
        json.dump(schedule, f, indent=2)

    # 干扰文件：无关附件、联系人等
    os.makedirs("raw_logs", exist_ok=True)
    with open("raw_logs/import.log", "w") as f:
        f.write("[2025-03-09] Import completed with 0 errors.\n")
    
    attachments = {
        "attachments": [
            {"path": "resumes/C001.pdf", "title": "Alice Resume", "kind": "pdf", "description": "Updated 2025-03-01"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Linda", "department": "HR", "email": "linda@company.com", "permissions": ["schedule"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

if __name__ == "__main__":
    build_env()
