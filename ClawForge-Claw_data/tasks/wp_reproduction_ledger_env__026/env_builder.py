import os
import csv
import json
from datetime import datetime

def build_env():
    # 1. 项目文档
    os.makedirs("project_docs", exist_ok=True)
    docs = [
        {
            "doc_id": "doc_alpha",
            "project_id": "proj-01",
            "title": "Alpha Project Crash on Startup",
            "path": "docs/alpha_v2.md"
        },
        {
            "doc_id": "doc_beta",
            "project_id": "proj-02",
            "title": "Beta Memory Leak in Parser",
            "path": "docs/beta_fix.md"
        }
    ]
    with open("project_docs/docs_alpha.json", "w") as f:
        json.dump({"project_docs": [docs[0]]}, f)
    with open("project_docs/docs_beta.json", "w") as f:
        json.dump({"project_docs": [docs[1]]}, f)

    # 2. 复现日志（CSV）
    os.makedirs("reproduction_logs", exist_ok=True)

    # log_2025-03-01.csv
    rows1 = [
        ["2025-03-01 10:15:00", "doc_alpha", "Install dependencies and run app", "Crash reproduced", "Noah Chen", "success"],
        ["2025-03-01 10:20:00", "doc_alpha", "Try with debug flags", "No crash", "Noah Chen", "failed"],
        ["2025-03-01 11:00:00", "doc_beta", "", "Timeout", "Eve Lee", "success"],  # 步骤为空，无效
    ]
    with open("reproduction_logs/log_2025-03-01.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "doc_id", "step_description", "result", "reproducer", "status"])
        writer.writerows(rows1)

    # log_2025-03-02.csv
    rows2 = [
        ["2025-03-02 09:00:00", "doc_alpha", "Clean install with minimal config", "Startup crash observed", "Noah Chen", "success"],
        ["2025-03-02 09:30:00", "doc_beta", "Run parser with 100KB input", "Memory usage grows to 512MB", "Eve Lee", "success"],
        ["2025-03-02 10:00:00", "doc_beta", "Run parser with 200KB input", "Memory leak confirmed", "Eve Lee", "success"],  # 同 doc_beta 多条，取最新一条
    ]
    with open("reproduction_logs/log_2025-03-02.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "doc_id", "step_description", "result", "reproducer", "status"])
        writer.writerows(rows2)

    # 3. 干扰项：过期的旧日志（不应该被读取）
    os.makedirs("backup", exist_ok=True)
    with open("backup/legacy_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ts", "id", "step", "note"])
        writer.writerow(["2025-02-28", "doc_alpha", "some step", "failed"])

    # 4. 无关数据目录
    os.makedirs("data", exist_ok=True)
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": [{"contact_id": "c1", "name": "Noah Chen", "role": "Engineer", "email": "noah@example.com"}]}, f)

if __name__ == "__main__":
    build_env()
