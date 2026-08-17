import os
import json

def build_env():
    # 创建数据目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. accounts.json（干扰项）
    accounts = [
        {
            "account_id": "A001",
            "display_name": "Admin",
            "department": "HR",
            "email": "admin@example.com",
            "permissions": ["read", "write"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # 2. attachments.json（干扰项）
    attachments = [
        {
            "path": "resume_john.pdf",
            "title": "John Doe Resume",
            "kind": "pdf",
            "description": "John's resume"
        },
        {
            "path": "cover_letter_jane.pdf",
            "title": "Jane Cover Letter",
            "kind": "pdf",
            "description": "Jane's cover letter"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # 3. contacts.json（面试官信息）
    contacts = [
        {
            "contact_id": "CT001",
            "name": "Alice",
            "role": "Interviewer",
            "email": "alice@example.com"
        },
        {
            "contact_id": "CT002",
            "name": "Bob",
            "role": "Manager",
            "email": "bob@example.com"
        }
    ]
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 4. candidates.json（含干扰项、脏数据）
    candidates = [
        {
            "candidate_id": "C001",
            "candidate_name": "John Doe",
            "skills": ["Python", "SQL", "Django", "Git"]  # 唯一完全覆盖
        },
        {
            "candidate_id": "C002",
            "candidate_name": "Jane Smith",
            "skills": ["Python", "Java", "SQL"]           # 缺少 Django 和 Git
        },
        {
            "candidate_id": "C003",
            "candidate_name": "Tom Brown",
            "skills": ["Python", "SQL", "Django"]         # 缺少 Git
        },
        {
            "candidate_id": "C004",
            "candidate_name": "Lisa White",
            "skills": ["Python", "SQL", "Django", "React"] # 缺少 Git
        },
        {
            "candidate_id": "C005",
            "candidate_name": "Dirty Candidate",
            "skills": ["Python", "", "SQL"]               # 含空字符串的脏数据
        }
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

    # 5. jobs.json（包含目标职位和干扰职位）
    jobs = [
        {
            "job_id": "J001",
            "title": "Senior Backend Engineer",
            "required_skills": ["Python", "SQL", "Django", "Git"]
        },
        {
            "job_id": "J002",
            "title": "Data Analyst",
            "required_skills": ["Python", "SQL", "Tableau"]
        }
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)

if __name__ == "__main__":
    build_env()
