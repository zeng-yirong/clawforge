import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/candidates", exist_ok=True)
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # 候选人数据（含干扰：缺失字段、空技能、不匹配）
    candidates = [
        {
            "candidate_id": "C001",
            "candidate_name": "张三",
            "skills": ["Python", "Docker"]
        },
        {
            "candidate_id": "C002",
            "candidate_name": "李四",
            "skills": ["Java", "SQL"]
        },
        {
            "candidate_id": "C003",
            "candidate_name": "王五",
            "skills": ["Python", "Go"]   # 不完全匹配任一职位
        },
        {
            "candidate_id": "C004",
            "candidate_name": "赵六",
            "skills": []   # 空技能，干扰
        },
        {
            "candidate_id": "C005",
            "candidate_name": "陈七"
            # 故意缺失 skills 字段，干扰
        }
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # 职位数据（含干扰：缺少 required_skills 的职位）
    jobs = [
        {
            "job_id": "J001",
            "title": "后端开发工程师",
            "required_skills": ["Python", "Docker"]
        },
        {
            "job_id": "J002",
            "title": "数据工程师",
            "required_skills": ["Java", "SQL"]
        },
        {
            "job_id": "J003",
            "title": "前端开发工程师"
            # 无 required_skills，干扰
        }
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # 账户数据（面试官王经理）
    accounts = [
        {
            "account_id": "A001",
            "display_name": "王经理",
            "department": "HR",
            "email": "wang@example.com",
            "permissions": ["schedule"]
        }
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

if __name__ == "__main__":
    build_env()
