import os
import json

def build_env():
    # 目录结构
    os.makedirs("docs/project-alpha", exist_ok=True)
    os.makedirs("docs/project-beta", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("knowledge_base", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 干扰数据文件
    accounts = [
        {"account_id": "acc-001", "display_name": "Alice", "department": "R&D", "email": "alice@example.com", "permissions": ["read", "write"]},
        {"account_id": "acc-002", "display_name": "Bob", "department": "QA", "email": "bob@example.com", "permissions": ["read"]}
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    contacts = [
        {"contact_id": "con-001", "name": "Charlie", "role": "Developer", "email": "charlie@example.com"},
        {"contact_id": "con-002", "name": "Diana", "role": "Manager", "email": "diana@example.com"}
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

    # 项目文档索引
    project_docs = [
        {"doc_id": "doc-alpha", "project_id": "project-alpha", "title": "Reproduction Guide", "path": "docs/project-alpha/reproduction_guide.md"},
        {"doc_id": "doc-beta", "project_id": "project-beta", "title": "Reproduction Guide", "path": "docs/project-beta/reproduction_guide.md"},
        {"doc_id": "doc-other", "project_id": "project-alpha", "title": "Setup Guide", "path": "docs/project-alpha/setup.md"}
    ]
    with open("data/project_docs.json", "w") as f:
        json.dump({"project_docs": project_docs}, f)

    # 正确指南 (project-alpha)
    correct_guide = """# Reproduction Guide for Bug #42
Project: project-alpha
This guide assumes you have run the simulation and the log is located at `logs/sim_run_2024-03-15.log`.
Steps:
1. Read the log file named sim_run_2024-03-15.log.
2. Extract all lines that contain "ResponseTime:".
3. Compute the average of the numeric values after the colon.
4. Write the result to `knowledge_base/reproduction_ledger.json` with the following JSON structure:
{
  "project_id": "project-alpha",
  "status": "completed",
  "result": {
    "avg_response_time": <computed_value>
  }
}
Note: Make sure to use the correct log file. The log lines may contain extra whitespace.
"""
    with open("docs/project-alpha/reproduction_guide.md", "w") as f:
        f.write(correct_guide)

    # 干扰指南 (project-beta)
    wrong_guide = """# Reproduction Guide for Bug #99
Project: project-beta
This guide uses log file `logs/sim_run_2024-03-14.log`.
Steps:
...
"""
    with open("docs/project-beta/reproduction_guide.md", "w") as f:
        f.write(wrong_guide)

    # 干扰 setup 文档
    with open("docs/project-alpha/setup.md", "w") as f:
        f.write("# Setup Guide\nJust install dependencies.")

    # 正确日志 (sim_run_2024-03-15.log) → 数值 210, 240, 225 → 平均 225
    correct_log = """# Simulation run on 2024-03-15
Start: 10:00:00
ResponseTime: 210
ResponseTime: 240
ResponseTime: 225
End: 10:05:00
"""
    with open("logs/sim_run_2024-03-15.log", "w") as f:
        f.write(correct_log)

    # 干扰日志 (sim_run_2024-03-14.log) → 数值 100, 200, 300 → 平均 200
    wrong_log = """# Simulation run on 2024-03-14
ResponseTime: 100
ResponseTime: 200
ResponseTime: 300
"""
    with open("logs/sim_run_2024-03-14.log", "w") as f:
        f.write(wrong_log)

    # 干扰日志 (other.log) 无响应时间
    with open("logs/other.log", "w") as f:
        f.write("# No response time data\n")

if __name__ == "__main__":
    build_env()
