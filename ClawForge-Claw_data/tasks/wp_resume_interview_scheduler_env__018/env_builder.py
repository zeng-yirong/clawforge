import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    # 不需要创建 ops 目录，让 Agent 自己创建

    # 候选人主文件
    candidates = {
        "candidates": [
            {"candidate_id": "alice_001", "candidate_name": "Alice Wang", "skills": ["Python", "SQL", "Spark"]},
            {"candidate_id": "bob_002", "candidate_name": "Bob Li", "skills": ["Python", "SQL"]},
            {"candidate_id": "charlie_003", "candidate_name": "Charlie Zhang", "skills": ["Python", "Java", "JavaScript"]}
        ]
    }
    with open("data/candidates/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

    # 干扰：旧候选人目录（技能不匹配，但名字相似）
    old_candidates = {
        "candidates": [
            {"candidate_id": "david_old", "candidate_name": "David Chen", "skills": ["Python", "SQL", "Scala"], "status": "inactive"}
        ]
    }
    with open("data/candidates/old_candidates.json", "w") as f:
        json.dump(old_candidates, f, indent=2)

    # 岗位文件
    jobs = {
        "jobs": [
            {"job_id": "job_001", "title": "Senior Data Engineer", "required_skills": ["Python", "SQL", "Spark"]},
            {"job_id": "job_002", "title": "Junior Developer", "required_skills": ["Python", "HTML"]}
        ]
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)

    # 干扰：旧岗位目录（已关闭的职位）
    os.makedirs("data/jobs/archived", exist_ok=True)
    archived_jobs = {
        "jobs": [
            {"job_id": "job_archived", "title": "Data Analyst", "required_skills": ["Python", "SQL"]}
        ]
    }
    with open("data/jobs/archived/archived_jobs.json", "w") as f:
        json.dump(archived_jobs, f, indent=2)

    # 已有日程表（干扰，但任务要求固定时间，忽略即可）
    schedule = {
        "interviews": [
            {"candidate_id": "bob_002", "job_id": "job_002", "scheduled_time": "2025-03-09T10:00:00"}
        ]
    }
    with open("data/schedule.json", "w") as f:
        json.dump(schedule, f, indent=2)

if __name__ == "__main__":
    build_env()
