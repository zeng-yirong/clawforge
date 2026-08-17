import os
import json

def build_env():
    # 确保目录结构
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # 干扰目录
    os.makedirs("old_data", exist_ok=True)

    # --- candidates ---
    candidates = [
        {
            "candidate_id": "C001",
            "candidate_name": "张三",
            "skills": ["Python", "Java"]
        },
        {
            "candidate_id": "C002",
            "candidate_name": "李四",
            "skills": ["Python", "PostgreSQL", "Docker", "Redis"]
        },
        {
            "candidate_id": "C003",
            "candidate_name": "王五",
            "skills": ["Python", "PostgreSQL", "Go"]
        },
        {
            "candidate_id": "C004",
            "candidate_name": "赵六",
            "skills": ["Python", "PostgreSQL", "Redis", "K8s"]  # 缺 Docker，不是完全匹配
        }
    ]
    with open("data/candidates/candidates.json", "w", encoding="utf-8") as f:
        json.dump({"candidates": candidates}, f, indent=2, ensure_ascii=False)

    # --- jobs ---
    jobs = [
        {
            "job_id": "J001",
            "title": "Senior Backend Engineer",
            "required_skills": ["Python", "PostgreSQL", "Docker", "Redis"]
        }
    ]
    with open("data/jobs/jobs.json", "w", encoding="utf-8") as f:
        json.dump({"jobs": jobs}, f, indent=2, ensure_ascii=False)

    # --- contacts (面试官信息) ---
    contacts = [
        {
            "contact_id": "contact_001",
            "name": "张经理",
            "role": "tech lead",
            "email": "zhang@example.com",
            "available_times": ["2025-04-15T10:00", "2025-04-15T14:00", "2025-04-16T10:00"]
        },
        {
            "contact_id": "contact_002",
            "name": "李经理",
            "role": "senior engineer",
            "email": "li@example.com",
            "available_times": ["2025-04-16T09:00"]
        }
    ]
    with open("data/contacts.json", "w", encoding="utf-8") as f:
        json.dump({"contacts": contacts}, f, indent=2, ensure_ascii=False)

    # --- 干扰文件 (无用的附件/旧版本) ---
    with open("old_data/resumes_2024.csv", "w") as f:
        f.write("name,skills\n")
        f.write("Tom,Python|Java\n")
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": []}, f)

if __name__ == "__main__":
    build_env()
