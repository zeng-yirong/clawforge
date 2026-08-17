import os
import json
import shutil

def build_env():
    # 清理并重建目录
    base_dir = os.getcwd()
    for d in ['data', 'output']:
        p = os.path.join(base_dir, d)
        if os.path.exists(p):
            shutil.rmtree(p)
        os.makedirs(p, exist_ok=True)

    # === jobs.json ===
    jobs = [
        {
            "job_id": "J001",
            "title": "Senior Data Engineer",
            "required_skills": ["Python", "SQL", "Spark"]
        },
        {
            "job_id": "J002",
            "title": "Junior Data Analyst",
            "required_skills": ["Excel", "SQL"]
        }
    ]
    jobs_path = os.path.join(base_dir, 'data', 'jobs.json')
    with open(jobs_path, 'w') as f:
        json.dump({"jobs": jobs}, f, indent=2)

    # === candidates.json (含干扰项) ===
    candidates = [
        {"candidate_id": "C001", "candidate_name": "Alice Wang", "skills": ["Python", "SQL", "Spark"]},
        {"candidate_id": "C002", "candidate_name": "Bob Li", "skills": ["Python", "SQL"]},          # 缺Spark
        {"candidate_id": "C003", "candidate_name": "Charlie Chen", "skills": ["Python", "SQL", "Spark", "Java"]},  # 多技能也算匹配
        {"candidate_id": "C004", "candidate_name": "David Zhang", "skills": ["R", "SQL"]},          # 缺Python & Spark
        {"candidate_id": "C005", "candidate_name": "Eva Liu", "skills": ["Python", "SQL", "Spark"]},
        {"candidate_id": "C006", "candidate_name": "Frank Wu", "skills": ["Python", "Spark"]},      # 缺SQL
        {"candidate_id": "C007", "candidate_name": "Grace Zhao", "skills": ["Python", "SQL", "Spark"]},
        # 以下是干扰项：重复ID、缺失skills、空skills
        {"candidate_id": "C001", "candidate_name": "Old Alice", "skills": ["Python"]},              # 重复ID（应忽略，因为不是同名）
        {"candidate_id": "C008", "candidate_name": "Invalid One"},                                  # 缺少skills字段
        {"candidate_id": "C009", "candidate_name": "Empty Skills", "skills": []},                   # 空技能列表
        {"candidate_id": "C010", "candidate_name": "", "skills": ["Python", "SQL", "Spark"]},       # 名字为空 – 视为无效
    ]
    candidates_path = os.path.join(base_dir, 'data', 'candidates.json')
    # 注意：JSON中wrapper是 "candidates"
    with open(candidates_path, 'w') as f:
        json.dump({"candidates": candidates}, f, indent=2)

    # === contacts.json ===
    contacts = [
        {"contact_id": "CT001", "name": "Dr. Smith", "role": "Hiring Manager", "email": "smith@example.com"}
    ]
    contacts_path = os.path.join(base_dir, 'data', 'contacts.json')
    with open(contacts_path, 'w') as f:
        json.dump({"contacts": contacts}, f, indent=2)

    # === 额外的干扰文件 / 旧版本 ===
    old_candidates = [
        {"candidate_id": "X001", "candidate_name": "Expired One", "skills": ["Python", "SQL", "Spark"]}
    ]
    old_path = os.path.join(base_dir, 'data', 'old_candidates.json')
    with open(old_path, 'w') as f:
        json.dump({"candidates": old_candidates}, f, indent=2)

    # 创建一个空的output目录（确保存在）
    output_dir = os.path.join(base_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

if __name__ == "__main__":
    build_env()
