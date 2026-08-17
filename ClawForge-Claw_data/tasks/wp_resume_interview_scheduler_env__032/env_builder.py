import os
import json

def build_env():
    # 创建数据目录
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 候选人数据（含干扰项：技能为null的候选人、技能不匹配的候选人）
    candidates = {
        "candidates": [
            {
                "candidate_id": "cand_001",
                "candidate_name": "Alice Smith",
                "skills": ["Python", "Java"]
            },
            {
                "candidate_id": "cand_002",
                "candidate_name": "Bob Johnson",
                "skills": ["SQL", "C++"]
            },
            {
                "candidate_id": "cand_003",
                "candidate_name": "Carol Williams",
                "skills": ["Python", "SQL"]   # 唯一正确匹配
            },
            {
                "candidate_id": "cand_004",
                "candidate_name": "Dave Brown",
                "skills": None                # 脏数据，技能缺失
            }
        ]
    }
    with open("data/candidates/candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)

    # 职位数据
    jobs = {
        "jobs": [
            {
                "job_id": "job_001",
                "title": "Frontend Developer",
                "required_skills": ["JavaScript", "React"]
            },
            {
                "job_id": "job_002",
                "title": "Backend Developer",
                "required_skills": ["Python", "SQL"]   # 目标职位
            }
        ]
    }
    with open("data/jobs/jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)

    # 添加干扰文件（无关数据）
    os.makedirs("data/interviews", exist_ok=True)
    with open("data/interviews/old_schedule.json", "w") as f:
        json.dump({"past_interviews": []}, f)

    # 确保 ops 目录为空（已创建）

if __name__ == "__main__":
    build_env()
