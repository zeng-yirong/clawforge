import os
import json
import random

def build_env():
    # 确保目录存在
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("archive", exist_ok=True)

    # 职位数据 (唯一正确答案对应的职位)
    jobs = {
        "job_001": {
            "job_id": "job_001",
            "title": "Senior Backend Engineer",
            "required_skills": ["Python", "SQL", "Docker", "Redis"],
            "department": "Engineering",
            "open_date": "2025-03-01"
        },
        "job_002": {
            "job_id": "job_002",
            "title": "Frontend Developer",
            "required_skills": ["JavaScript", "React", "CSS"],
            "department": "Engineering",
            "open_date": "2025-03-10"
        }
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": list(jobs.values())}, f, indent=2)

    # 候选人列表（包含干扰项、脏数据、诱饵）
    candidates = [
        {
            "candidate_id": "c_001",
            "candidate_name": "Alice Wang",
            "skills": ["Python", "SQL", "Docker", "Redis"],
            "status": "active",
            "email": "alice@example.com"
        },
        {
            "candidate_id": "c_002",
            "candidate_name": "Bob Li",
            "skills": ["Python", "Java", "Docker"],
            "status": "active",
            "email": "bob@example.com"
        },
        {
            "candidate_id": "c_003",
            "candidate_name": "Chris Zhang",
            "skills": "Python, SQL, Docker, Redis",  # 坏数据：字符串而非列表
            "status": "active",
            "email": "chris@example.com"
        },
        {
            "candidate_id": "c_004",
            "candidate_name": "Diana Chen",
            "skills": ["Python", "SQL", "Docker", "Redis"],
            "status": "inactive",
            "email": "diana@example.com"
        },
        {
            "candidate_id": "c_005",
            "candidate_name": "Eve Liu",
            "skills": ["Python", "SQL", "Docker"],
            "status": "active",
            "email": "eve@example.com"
        },
        {
            # 缺少candidate_id，故意放进去干扰
            "candidate_name": "Frank Zhao",
            "skills": ["Python", "SQL", "Docker", "Redis"],
            "status": "active",
            "email": "frank@example.com"
        }
    ]
    # 随机打乱顺序增加难度
    random.shuffle(candidates)
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # 账户/面试官信息
    accounts = [
        {
            "account_id": "b_001",
            "display_name": "Bob Smith",
            "department": "Engineering",
            "email": "bob@company.com",
            "permissions": ["interviewer"]
        },
        {
            "account_id": "b_002",
            "display_name": "Alice Johnson",
            "department": "Engineering",
            "email": "alice@company.com",
            "permissions": ["admin"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # 联系人（无用干扰）
    contacts = [
        {"contact_id": "ct_01", "name": "Reception", "role": "receptionist", "email": "reception@company.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # 一些旧版数据（诱饵）
    with open("archive/old_candidates.json", "w") as f:
        json.dump({"candidates": [{"candidate_id": "c_old", "skills": ["Python", "SQL"]}]}, f, indent=2)

    print("环境构建完成")

if __name__ == "__main__":
    build_env()
