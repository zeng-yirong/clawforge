import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("data/jobs", exist_ok=True)
    os.makedirs("data/candidates", exist_ok=True)

    # 干扰文件：旧备份数据
    os.makedirs("backup", exist_ok=True)
    backup_candidates = [
        {"candidate_id": "C001", "candidate_name": "Alice (old)", "skills": ["Python"]},
        {"candidate_id": "C002", "candidate_name": "Bob (old)", "skills": ["Java", "Spring"]},
    ]
    with open("backup/candidates_2024.json", "w") as f:
        json.dump(backup_candidates, f, indent=2)

    # 干扰文件：附件列表（不包含有效数据）
    os.makedirs("attachments", exist_ok=True)
    attachments = [
        {"path": "resumes/alice.pdf", "kind": "resume", "title": "Alice resume"},
        {"path": "resumes/bob.pdf", "kind": "resume", "title": "Bob resume"},
    ]
    with open("attachments/attachments.json", "w") as f:
        json.dump({"attachments": attachments}, f, indent=2)

    # 主数据：职位
    jobs = [
        {"job_id": "J001", "title": "Backend Developer", "required_skills": ["Python", "SQL", "Django"]},
        {"job_id": "J002", "title": "Java Developer", "required_skills": ["Java", "Spring", "Kubernetes"]},
    ]
    with open("data/jobs/jobs.json", "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # 主数据：候选人（只有两个完全匹配，其余都是干扰/不匹配）
    candidates = [
        {"candidate_id": "C001", "candidate_name": "Alice", "skills": ["Python", "SQL", "Django"]},   # 完全匹配 J001
        {"candidate_id": "C002", "candidate_name": "Bob", "skills": ["Java", "Spring", "Kubernetes"]},# 完全匹配 J002
        {"candidate_id": "C003", "candidate_name": "Charlie", "skills": ["Python", "Java"]},           # 不匹配任何职位
        {"candidate_id": "C004", "candidate_name": "Diana", "skills": ["Python", "SQL"]},              # 缺少 Django
        {"candidate_id": "C005", "candidate_name": "Eve", "skills": ["Python", "SQL", "Django", "Java"]}, # 完全匹配 J001，但多技能（仍匹配）
    ]
    with open("data/candidates/candidates.json", "w") as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # 干扰文件：旧面试日程（避免误用）
    old_schedule = [
        {"interview_id": "C001_J001_old", "date": "2024-12-01", "status": "cancelled"}
    ]
    with open("old_interviews.json", "w") as f:
        json.dump(old_schedule, f, indent=2)

if __name__ == "__main__":
    build_env()
