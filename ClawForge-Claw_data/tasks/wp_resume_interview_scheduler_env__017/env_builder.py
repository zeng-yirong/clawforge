import os
import json

def build_env():
    # 创建目录结构
    for dir_path in ["data/candidates", "data/jobs", "ops"]:
        os.makedirs(dir_path, exist_ok=True)

    # ---- accounts.json (背景) ----
    accounts = [
        {"account_id": "acc_001", "display_name": "Sarah Li", "department": "HR", "email": "sarah@example.com", "permissions": ["hr"]},
        {"account_id": "acc_002", "display_name": "Bob Chen", "department": "Engineering", "email": "bob@example.com", "permissions": ["interviewer"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f, indent=2)

    # ---- contacts.json (背景) ----
    contacts = [
        {"contact_id": "cont_001", "name": "Alice Wang", "role": "Tech Lead", "email": "alice@example.com"},
        {"contact_id": "cont_002", "name": "Bob Chen", "role": "Senior Engineer", "email": "bob@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # ---- attachments.json + 实际附件文件 ----
    attachment_note = "Suggested interview time: 2025-06-15T10:00:00"
    # 创建附件文本文件
    with open("data/attachment_notes.txt", "w") as f:
        f.write(attachment_note)
    attachments = [
        {
            "path": "data/attachment_notes.txt",
            "title": "面试时间建议",
            "kind": "text",
            "description": "Bob 给出的建议时间：2025-06-15T10:00:00"
        }
    ]
    with open("data/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # ---- candidates.json (核心干扰项) ----
    candidates = [
        {
            "candidate_id": "cand_001",
            "candidate_name": "张三",
            "skills": ["Python", "Kubernetes", "PostgreSQL", "System Design"]   # 完全匹配
        },
        {
            "candidate_id": "cand_002",
            "candidate_name": "李四",
            "skills": ["Python", "Docker", "PostgreSQL", "System Design"]       # 缺 Kubernetes
        },
        {
            "candidate_id": "cand_003",
            "candidate_name": "王五",
            "skills": ["Python", "Kubernetes", "MySQL", "System Design"]        # 缺 PostgreSQL
        },
        {
            "candidate_id": "cand_004",
            "candidate_name": "赵六",
            "skills": ["Python", "Kubernetes", "PostgreSQL", "Microservices"]   # 缺 System Design
        },
        # 干扰项：技能列表含重复
        {
            "candidate_id": "cand_005",
            "candidate_name": "孙七",
            "skills": ["Python", "Python", "Kubernetes", "PostgreSQL", "System Design"]
        },
        # 干扰项：空技能
        {
            "candidate_id": "cand_006",
            "candidate_name": "周八",
            "skills": []
        }
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # ---- jobs.json (包含目标职位与其他干扰) ----
    jobs = [
        {
            "job_id": "job_001",
            "title": "Data Scientist",
            "required_skills": ["Python", "Machine Learning", "SQL"]
        },
        {
            "job_id": "job_002",
            "title": "Senior Software Engineer",
            "required_skills": ["Python", "Kubernetes", "PostgreSQL", "System Design"]   # 目标岗位
        },
        {
            "job_id": "job_003",
            "title": "DevOps Engineer",
            "required_skills": ["Docker", "Kubernetes", "CI/CD"]
        },
        # 干扰项：所需技能为空
        {
            "job_id": "job_004",
            "title": "Junior Intern",
            "required_skills": []
        }
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # ---- 额外诱饵文件，增加迷惑性 ----
    with open("data/old_candidates.json", "w") as f:
        json.dump({"old": [{"candidate_id": "cand_999", "name": "旧候选人"}]}, f, indent=2)

if __name__ == "__main__":
    build_env()
