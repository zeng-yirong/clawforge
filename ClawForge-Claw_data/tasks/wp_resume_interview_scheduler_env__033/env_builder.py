import os
import json

def build_env():
    # ---------- 职位数据 ----------
    jobs = {
        "jobs": [
            {
                "job_id": "job_001",
                "title": "Backend Engineer",
                "required_skills": ["Python", "Django", "SQL"]
            },
            {
                "job_id": "job_002",
                "title": "Frontend Engineer",
                "required_skills": ["JavaScript", "React", "CSS"]
            }
        ]
    }
    os.makedirs("data/jobs", exist_ok=True)
    with open("data/jobs/jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)

    # ---------- 候选人数据（含干扰） ----------
    candidates = {
        "candidates": [
            {
                "candidate_id": "cand_001",
                "candidate_name": "Alice Wang",
                "skills": ["Python", "Django", "SQL", "Redis"]
            },
            {
                "candidate_id": "cand_002",
                "candidate_name": "Bob Li",
                "skills": ["Java", "Spring", "SQL"]
            },
            {
                "candidate_id": "cand_003",
                "candidate_name": "Carol Zhang",
                "skills": ["Python", "Django", "SQL"]
            },
            {
                "candidate_id": "cand_004",
                "candidate_name": "David Chen",
                "skills": ["Python", "Flask"]
            },
            {
                "candidate_id": "cand_005",
                "candidate_name": "Eva Liu",
                "skills": ["Python", "Django"]
            },
            # 干扰：技能完全匹配但重复名字（实际还是匹配，故意增加数据量）
            {
                "candidate_id": "cand_006",
                "candidate_name": "Frank Wu",
                "skills": ["Python", "Django", "SQL", "Go"]
            }
        ]
    }
    os.makedirs("data/candidates", exist_ok=True)
    with open("data/candidates/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

    # ---------- 账号信息（面试官） ----------
    accounts = {
        "accounts": [
            {
                "account_id": "acc_001",
                "display_name": "Tom Manager",
                "department": "Engineering",
                "email": "tom@example.com",
                "permissions": ["admin"]
            },
            {
                "account_id": "acc_002",
                "display_name": "Alice",
                "department": "Engineering",
                "email": "alice@example.com",
                "permissions": ["interview"]
            },
            {
                "account_id": "acc_003",
                "display_name": "Bob HR",
                "department": "HR",
                "email": "bob@example.com",
                "permissions": ["recruit"]
            }
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    # ---------- 附件清单 ----------
    attachments = {
        "attachments": [
            {
                "path": "resumes/backend_resume.pdf",
                "title": "Backend Engineer Resume",
                "kind": "resume",
                "description": "Resume for Backend Engineer position"
            },
            {
                "path": "resumes/frontend_resume.pdf",
                "title": "Frontend Engineer Resume",
                "kind": "resume",
                "description": "Resume for Frontend Engineer position"
            }
        ]
    }
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # ---------- 配置文件（面试日期） ----------
    os.makedirs("config", exist_ok=True)
    with open("config/interview_date.txt", "w") as f:
        f.write("2025-06-16")

    # ---------- 创建结果目录（空，留给 agent 写入） ----------
    os.makedirs("scheduling", exist_ok=True)

if __name__ == "__main__":
    build_env()
