import os
import json

def build_env():
    # 创建必要的目录
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 候选人数据 (包含活跃/非活跃，以及干扰项)
    candidates = [
        {"candidate_id": "C001", "candidate_name": "Bob", "skills": ["Python", "Java"], "status": "active"},
        {"candidate_id": "C002", "candidate_name": "Charlie", "skills": ["Python", "Django", "MySQL"], "status": "active"},
        {"candidate_id": "C003", "candidate_name": "Alice", "skills": ["Python", "Django", "PostgreSQL", "Redis", "AWS"], "status": "active"},
        {"candidate_id": "C004", "candidate_name": "Dave", "skills": ["Python", "Django", "PostgreSQL", "Redis"], "status": "inactive"}
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # 职位数据 (包含目标职位和干扰职位)
    jobs = [
        {"job_id": "J001", "title": "Senior Backend Engineer", "required_skills": ["Python", "Django", "PostgreSQL", "Redis"]},
        {"job_id": "J002", "title": "Frontend Developer", "required_skills": ["JavaScript", "React", "CSS"]},
        {"job_id": "J003", "title": "DevOps Engineer", "required_skills": ["AWS", "Docker", "Kubernetes"]}
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # 可用的面试时间段
    schedule = {
        "slots": [
            {"date": "2025-04-10", "times": ["10:00", "14:00"]},
            {"date": "2025-04-11", "times": ["09:00", "11:00"]}
        ]
    }
    with open("schedule.json", "w") as f:
        json.dump(schedule, f, indent=2)

    # 其他干扰文件
    attachments = {"attachments": [{"path": "resume.pdf", "title": "Resume", "kind": "pdf", "description": "..."}]}
    with open("data/attachments.json", "w") as f:
        json.dump(attachments, f, indent=2)

    # 过时的候选人列表 (不应被使用)
    old_candidates = {"candidates": [{"candidate_id": "C099", "candidate_name": "OldGuy", "skills": [], "status": "inactive"}]}
    with open("data/old_candidates.json", "w") as f:
        json.dump(old_candidates, f, indent=2)

if __name__ == "__main__":
    build_env()
