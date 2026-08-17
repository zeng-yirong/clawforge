import os
import csv
import json
from datetime import datetime

def build_env():
    # 确保目录结构
    os.makedirs("docs", exist_ok=True)
    os.makedirs("logs/archive", exist_ok=True)
    os.makedirs("metadata", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # ---- 元数据：项目状态 ----
    project_status = {
        "projA": "production",
        "projB": "production",
        "projC": "test",
        "projD": "archived",
        "projE": "production"
    }
    with open("metadata/project_status.json", "w") as f:
        json.dump(project_status, f, indent=2)

    # ---- 文档信息 ----
    doc_meta = {
        "projA": {"title": "Deployment Guide for ProjA", "path": "docs/projA_guide.md"},
        "projB": {"title": "API Integration Manual", "path": "docs/projB_guide.md"},
        "projC": {"title": "Test Script Reference", "path": "docs/projC_guide.md"},
        "projD": {"title": "Legacy Migration Plan", "path": "docs/projD_guide.md"},
        "projE": {"title": "Quickstart Instructions", "path": "docs/projE_guide.md"}
    }
    with open("docs/doc_meta.json", "w") as f:
        json.dump(doc_meta, f, indent=2)

    # 生成实际的文档文件（仅占位，内容不重要）
    for proj_id, info in doc_meta.items():
        content = f"# {info['title']}\n\nThis is the document for {proj_id}.\n"
        with open(info["path"], "w") as f:
            f.write(content)

    # ---- 复现日志（主要） ----
    logs = [
        ("projA", "2025-04-17", "Clone repo; install deps; run unit tests", "success"),
        ("projA", "2025-04-18", "Update config; re-run regression suite", "failure"),
        ("projB", "2025-04-15", "Build from source; deploy to staging; verify endpoints", "success"),
        ("projB", "2025-04-16", "Rollback to tag v1.2; redeploy", "success"),
        ("projC", "2025-04-15", "Run test suite on branch feature-x", "success"),
        ("projD", "2025-04-14", "Setup development environment", "failure"),
        ("projE", "2025-04-19", "Follow Quickstart; encountered error", "incomplete")
    ]
    with open("logs/reproduction_log.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["project_id", "timestamp", "steps_summary", "outcome"])
        writer.writerows(logs)

    # ---- 干扰日志（过时备份） ----
    old_logs = [
        ("projA", "2025-04-10", "Initial attempt", "success"),
        ("projB", "2025-04-12", "Trial run", "failure")
    ]
    with open("logs/archive/old_reproduction_log.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["project_id", "timestamp", "steps_summary", "outcome"])
        writer.writerows(old_logs)

    # ---- 干扰日志（格式错误，缺少project_id列） ----
    with open("logs/reproduction_log_extra.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "steps_summary", "outcome"])
        writer.writerow(["2025-04-16", "Some actions", "success"])

if __name__ == "__main__":
    build_env()
