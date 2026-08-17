import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # data/current_time.txt
    with open("data/current_time.txt", "w") as f:
        f.write("2025-03-15 14:30")

    # data/accounts.json
    accounts = {
        "accounts": [
            {"account_id": "A001", "display_name": "Alice", "department": "HR", "email": "alice@example.com", "permissions": ["read"]},
            {"account_id": "A002", "display_name": "Bob", "department": "Engineering", "email": "bob@example.com", "permissions": ["read", "write"]},
            {"account_id": "A003", "display_name": "Charlie", "department": "HR", "email": "charlie@example.com", "permissions": ["admin"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # data/attachments.json (干扰项)
    attachments = {
        "attachments": [
            {"path": "misc/photo1.png", "title": "Team photo", "kind": "image", "description": "Old team photo"},
            {"path": "misc/resume_extra.pdf", "title": "Extra resume", "kind": "document", "description": "Outdated resume"}
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # data/candidates/candidates.json
    candidates = {
        "candidates": [
            {"candidate_id": "C001", "candidate_name": "Alice Wang", "skills": ["Python", "Django", "Flask", "MySQL"]},
            {"candidate_id": "C002", "candidate_name": "Bob Li", "skills": ["Java", "Spring", "PostgreSQL"]},
            {"candidate_id": "C003", "candidate_name": "Carol Chen", "skills": ["Python", "Django", "PostgreSQL"]},  # 完全匹配
            {"candidate_id": "C004", "candidate_name": "David Zhang", "skills": ["Python", "Django"]},             # 缺 PostgreSQL
            {"candidate_id": "C005", "candidate_name": "Eva Xu", "skills": ["Python", "PostgreSQL", "Redis"]}      # 缺 Django
        ]
    }
    with open("data/candidates/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

    # data/contacts.json (干扰项，但可被忽略)
    contacts = {
        "contacts": [
            {"contact_id": "CT001", "name": "External Recruiter", "role": "vendor", "email": "recruiter@agency.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # data/jobs/jobs.json
    jobs = {
        "jobs": [
            {"job_id": "J001", "title": "Senior Python Developer", "required_skills": ["Python", "Django", "PostgreSQL"]},
            {"job_id": "J002", "title": "Java Backend Developer", "required_skills": ["Java", "Spring", "MySQL"]},
            {"job_id": "J003", "title": "DevOps Engineer", "required_skills": ["Docker", "Kubernetes", "CI/CD"]}
        ]
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)

    # 在 ops/ 下放一个无用文件，干扰
    with open("ops/old_notes.txt", "w") as f:
        f.write("This is an old note, ignore me.\n")

if __name__ == "__main__":
    build_env()
