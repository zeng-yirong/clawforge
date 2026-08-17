import os
import json
import shutil

def build_env():
    # 清理旧目录（如果存在）
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("ops"):
        shutil.rmtree("ops")

    # --- 候选人才库 ---
    candidates = [
        {
            "candidate_id": "C001",
            "candidate_name": "Alice Chen",
            "skills": ["Python", "Docker", "Kubernetes"]
        },
        {
            "candidate_id": "C002",
            "candidate_name": "Bob Li",
            "skills": ["Python", "HTML", "CSS"]
        },
        {
            "candidate_id": "C003",
            "candidate_name": "Charlie Wang",
            "skills": ["Python", "Docker"]  # 缺少Kubernetes，不匹配Senior
        },
        {
            "candidate_id": "C004",
            "candidate_name": "David Zhou",
            "skills": ["SQL", "Python"]
        },
        {
            "candidate_id": "C005",
            "candidate_name": "Eve Zhang",
            "skills": ["Java", "C++"]
        },
        {
            "candidate_id": "C006",
            "candidate_name": "Frank Liu",
            "skills": []  # 脏数据：空技能列表
        }
    ]
    os.makedirs("data/candidates", exist_ok=True)
    with open("data/candidates/candidates.json", "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2)

    # --- 职位信息 ---
    jobs = [
        {
            "job_id": "J001",
            "title": "Senior Engineer",
            "required_skills": ["Python", "Docker", "Kubernetes"],
            "status": "active"
        },
        {
            "job_id": "J002",
            "title": "Junior Developer",
            "required_skills": ["Python", "HTML"],
            "status": "active"
        },
        {
            "job_id": "J003",
            "title": "Data Analyst",
            "required_skills": ["SQL", "Python"],
            "status": "active"
        },
        {
            "job_id": "J004",
            "title": "Backend Engineer (Closed)",
            "required_skills": ["Go", "Kubernetes"],
            "status": "closed"  # 已关闭，不应匹配
        }
    ]
    os.makedirs("data/jobs", exist_ok=True)
    with open("data/jobs/jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)

    # --- 联系人（面试官）---
    contacts = [
        {
            "contact_id": "int1",
            "name": "Alice Wang",
            "role": "interviewer",
            "email": "awang@example.com"
        },
        {
            "contact_id": "int2",
            "name": "Bob Smith",
            "role": "recruiter",
            "email": "bob@example.com"
        }
    ]
    os.makedirs("data/contacts", exist_ok=True)
    with open("data/contacts/contacts.json", "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2)

    # --- 配置（默认面试时间）---
    config = {
        "default_interview_time": "2025-04-15T10:00:00"
    }
    os.makedirs("ops", exist_ok=True)
    with open("ops/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    # --- 历史面试记录（干扰项）---
    past_interviews = [
        {
            "job_id": "J001",
            "candidate_id": "C003",
            "interviewer_id": "int1",
            "interview_time": "2025-04-10T14:00:00",
            "status": "cancelled"
        },
        {
            "job_id": "J002",
            "candidate_id": "C002",
            "interviewer_id": "int2",
            "interview_time": "2025-04-12T09:00:00",
            "status": "completed"
        }
    ]
    with open("ops/past_interviews.json", "w", encoding="utf-8") as f:
        json.dump(past_interviews, f, indent=2)

    # --- 干扰文件：非JSON的草稿文件 ---
    with open("data/candidates/draft_notes.txt", "w") as f:
        f.write("Draft: some old resume notes\n")

    # --- 提示：别动这个文件，它不应该被读取 ---
    with open("ops/readme.txt", "w") as f:
        f.write("This is a legacy doc, ignore.\n")

    print("Environment built successfully.")

if __name__ == "__main__":
    build_env()
