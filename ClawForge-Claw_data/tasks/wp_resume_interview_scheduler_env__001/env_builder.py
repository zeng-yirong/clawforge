import os
import json
import shutil

def build_env():
    # === 创建必要的目录 ===
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data", exist_ok=True)  # for accounts and contacts
    os.makedirs("data/backup", exist_ok=True)
    os.makedirs("schedules", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # === 候选人数据（含干扰项） ===
    candidates = [
        {
            "candidate_id": "C001",
            "candidate_name": "John Doe",
            "skills": ["Python", "SQL", "Docker"],
            "status": "active"
        },
        {
            "candidate_id": "C002",
            "candidate_name": "Jane Smith",
            "skills": ["Python", "SQL", "Docker"],
            "status": "inactive"  # 干扰：状态不对
        },
        {
            "candidate_id": "C003",
            "candidate_name": "Bob Johnson",
            "skills": ["Python", "SQL"],
            "status": "active"
        },
        {
            "candidate_id": "C004",
            "candidate_name": "Alice Brown",
            "skills": ["Java", "C++", "Docker"],
            "status": "active"
        },
        {
            "candidate_id": "C005",
            "candidate_name": "Charlie Davis",
            "skills": ["Python", "SQL", "Docker", "Kubernetes"],
            "status": "active"  # 干扰：技能超额，但唯一匹配的还是C001（我们假设按完全匹配优先）
        }
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # === 旧版候选人备份（干扰） ===
    backup_candidates = [
        {"candidate_id": "C001", "candidate_name": "John Doe", "skills": ["Python", "SQL"], "status": "active"}  # 旧技能
    ]
    with open("data/backup/candidates.json", "w") as f:
        json.dump({"candidates": backup_candidates}, f, indent=2)

    # === 职位数据 ===
    jobs = [
        {"job_id": "JOB-001", "title": "前端工程师", "required_skills": ["JavaScript", "CSS", "React"]},
        {"job_id": "JOB-002", "title": "数据工程师", "required_skills": ["Python", "Spark", "SQL"]},
        {"job_id": "JOB-003", "title": "资深后端工程师", "required_skills": ["Python", "SQL", "Docker"]}
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # === 联系人数据（含Alice） ===
    contacts = [
        {"contact_id": "CONT-001", "name": "Alice", "role": "interviewer", "email": "alice@example.com"},
        {"contact_id": "CONT-002", "name": "Bob", "role": "recruiter", "email": "bob@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # === 账户（干扰） ===
    accounts = [
        {"account_id": "ACC-001", "display_name": "Alice", "department": "Engineering", "email": "alice@example.com", "permissions": ["interview"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # === 额外干扰文件 ===
    with open("ops/old_plan.json", "w") as f:
        f.write('{"job_id":"JOB-002","candidate_id":"C003"}')
    with open("data/notes.txt", "w") as f:
        f.write("Some random notes")

if __name__ == "__main__":
    build_env()
