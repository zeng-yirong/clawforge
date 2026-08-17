import os
import json
import uuid
from datetime import datetime, timedelta

def build_env():
    # 确保目录存在
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 候选人数据（含干扰项：重复、技能为空、无用字段）
    candidates = [
        {"candidate_id": "C001", "candidate_name": "Alice Wang", "skills": ["Python", "SQL", "Machine Learning"]},
        {"candidate_id": "C002", "candidate_name": "Bob Li", "skills": ["Java", "Spring", "SQL"]},
        {"candidate_id": "C003", "candidate_name": "Charlie Chen", "skills": ["Python", "Django", "React"]},
        {"candidate_id": "C004", "candidate_name": "Diana Zhang", "skills": []},  # 技能为空，应忽略
        {"candidate_id": "C005", "candidate_name": "Eve Liu", "skills": ["Python", "SQL", "AWS"]},
        {"candidate_id": "C001", "candidate_name": "Alice Wang (dup)", "skills": ["Python", "SQL", "Machine Learning"]},  # 重复ID
        {"candidate_id": "C006", "candidate_name": "Frank Huang", "skills": ["Java", "Kubernetes"]},
    ]

    # 职位数据（含已关闭职位、重复职位ID等）
    jobs = [
        {"job_id": "J001", "title": "Backend Engineer", "required_skills": ["Python", "SQL", "AWS"], "status": "open"},
        {"job_id": "J002", "title": "Java Developer", "required_skills": ["Java", "Spring", "SQL"], "status": "open"},
        {"job_id": "J003", "title": "Frontend Engineer", "required_skills": ["React", "JavaScript", "CSS"], "status": "open"},
        {"job_id": "J004", "title": "Data Scientist", "required_skills": ["Python", "Machine Learning", "SQL"], "status": "open"},
        {"job_id": "J005", "title": "DevOps Engineer", "required_skills": ["Kubernetes", "Docker", "AWS"], "status": "closed"},  # 已关闭
        {"job_id": "J001", "title": "Backend Engineer (dup)", "required_skills": ["Python", "SQL", "AWS"], "status": "open"},  # 重复ID
    ]

    # 写入候选人和职位JSON
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # 额外干扰文件（无用，但增加复杂度）
    os.makedirs("data/attachments", exist_ok=True)
    with open("data/attachments/notes.txt", "w") as f:
        f.write("ignore this file")

    # 创建一些过期日志
    with open("ops/old_schedule.json", "w") as f:
        json.dump({"schedule": []}, f)

if __name__ == "__main__":
    build_env()
