import os
import json
from datetime import datetime, timedelta

def build_env():
    # 确保基础目录存在
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/schedules", exist_ok=True)

    # 1. 职位数据
    jobs = [
        {
            "job_id": "J001",
            "title": "Senior DevOps Engineer",
            "required_skills": ["Kubernetes", "Docker", "CI/CD", "Python", "AWS"]
        },
        {
            "job_id": "J002",
            "title": "Backend Developer",
            "required_skills": ["Java", "Spring", "SQL"]
        },
        {
            "job_id": "J003",
            "title": "Frontend Engineer",
            "required_skills": ["React", "TypeScript", "CSS"]
        }
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # 2. 候选人数据（包含干扰项）
    candidates = [
        {
            "candidate_id": "C001",
            "candidate_name": "Alice Wang",
            "skills": ["Kubernetes", "Docker", "CI/CD", "Python", "AWS "]
        },  # 注意 AWS 后面有个空格，但实际匹配时应忽略
        {
            "candidate_id": "C002",
            "candidate_name": "Bob Li",
            "skills": ["Kubernetes", "Docker", "CI/CD", "Go", "AWS"]
        },  # 缺少 Python，有 Go
        {
            "candidate_id": "C003",
            "candidate_name": "Carol Zhang",
            "skills": ["Kubernetes", "Docker", "CI/CD", "Python", "AWS"]
        },  # 完全匹配
        {
            "candidate_id": "C004",
            "candidate_name": "David Chen",
            "skills": ["Kubernetes", "Docker", "Python", "AWS"]
        },  # 缺少 CI/CD
        {
            "candidate_id": "C005",
            "candidate_name": "Eva Liu",
            "skills": ["Kubernetes", "Docker", "CI/CD", "Python", "AWS", "Terraform"]
        }  # 多了 Terraform，不匹配
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # 3. 系统日期文件（固定今天为 2025-04-09，明天就是 2025-04-10）
    today = "2025-04-09"
    with open("data/today.txt", "w") as f:
        f.write(today)

    # 4. 已有面试记录（干扰项）
    existing_schedules = [
        {
            "candidate_id": "C001",
            "job_id": "J001",
            "interview_date": "2025-04-08",
            "status": "cancelled"
        },
        {
            "candidate_id": "C002",
            "job_id": "J002",
            "interview_date": "2025-04-10",
            "status": "scheduled"
        }
    ]
    with open("data/schedules/old_draft.json", "w") as f:
        json.dump(existing_schedules, f, indent=2)

    # 5. 再放一个空的目录装作干扰
    os.makedirs("data/archives", exist_ok=True)

if __name__ == "__main__":
    build_env()
