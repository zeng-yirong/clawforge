import os
import json

def build_env():
    # 确保目录存在
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 1. 候选人数据（最新）
    candidates = [
        {
            "candidate_id": "candidate_001",
            "candidate_name": "Alice",
            "skills": ["Python", "SQL", "ML"]
        },
        {
            "candidate_id": "candidate_002",
            "candidate_name": "Bob",
            "skills": ["Java", "SQL"]
        },
        {
            "candidate_id": "candidate_003",
            "candidate_name": "Charlie",
            "skills": ["Python", "React"]
        },
        {
            "candidate_id": "candidate_004",
            "candidate_name": "Diana",
            "skills": []   # 无技能，干扰
        }
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # 2. 旧候选人副本（干扰项）
    old_candidates = [
        {
            "candidate_id": "candidate_005",
            "candidate_name": "Eve",
            "skills": ["Python", "SQL", "Go"]
        },
        {
            "candidate_id": "candidate_006",
            "candidate_name": "Frank",
            "skills": ["Java"]
        }
    ]
    with open("data/candidates/old_candidates.json", "w") as f:
        json.dump({"candidates": old_candidates}, f, indent=2)

    # 3. 职位数据
    jobs = [
        {
            "job_id": "job_A",
            "title": "Data Engineer",
            "required_skills": ["Python", "SQL"]
        },
        {
            "job_id": "job_B",
            "title": "Java Backend Developer",
            "required_skills": ["Java"]
        },
        {
            "job_id": "job_C",
            "title": "Full Stack Engineer",
            "required_skills": ["Python", "React", "Node"]
        }
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # 4. 面试时间配置
    schedule_config = {
        "start_date": "2025-07-14",
        "slot_minutes": 60,
        "day_start": "09:00"
    }
    with open("data/schedule_config.json", "w") as f:
        json.dump(schedule_config, f, indent=2)

    # 5. 无关的日志干扰
    with open("logs/system.log", "w") as f:
        f.write("2025-07-10 08:00:00 [INFO] System started\n")
    with open("logs/app.log", "w") as f:
        f.write("2025-07-10 09:00:00 [DEBUG] No match found for older candidates\n")

if __name__ == "__main__":
    build_env()
