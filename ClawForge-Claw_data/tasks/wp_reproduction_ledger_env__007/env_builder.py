import os
import json

def build_env():
    # data/projects/project_docs.json
    os.makedirs("data/projects", exist_ok=True)
    project_docs = [
        {
            "doc_id": "doc_repro_alpha",
            "project_id": "proj_alpha",
            "title": "Reproduction of Bug #1234",
            "path": "docs/project_alpha/README.md",
            "reproduction_version": "1.1.0"
        },
        {
            "doc_id": "doc_setup_guide",
            "project_id": "proj_setup",
            "title": "Setup Guide",
            "path": "docs/setup/guide.md",
            "reproduction_version": "2.0.0"
        }
    ]
    with open("data/projects/project_docs.json", "w") as f:
        json.dump(project_docs, f, indent=2)

    # replication_logs (干扰项)
    os.makedirs("replication_logs", exist_ok=True)
    log1 = {
        "replication_time": "2025-03-01T10:00:00",
        "status": "completed",
        "replication_successful": True,
        "doc_id": "doc_repro_alpha",
        "project_id": "proj_alpha",
        "applied_version": "1.0.0",
        "steps": ["environment setup", "dependency install", "run test"],
        "result": "Bug reproduced on v1.0.0"
    }
    log2 = {
        "replication_time": "2025-03-02T10:00:00",
        "status": "completed",
        "replication_successful": False,
        "doc_id": "doc_repro_alpha",
        "project_id": "proj_alpha",
        "applied_version": "1.1.0",
        "steps": ["environment setup", "dependency install", "patch apply", "run test"],
        "result": "Failed - missing dependency"
    }
    log3 = {
        "replication_time": "2025-03-03T10:00:00",
        "status": "completed",
        "replication_successful": True,
        "doc_id": "doc_repro_alpha",
        "project_id": "proj_alpha",
        "applied_version": "1.1.0",
        "steps": ["environment setup", "dependency install", "patch apply", "run test"],
        "result": "Bug reproduced on v1.1.0"
    }
    logs = [log1, log2, log3]
    for i, log in enumerate(logs, start=1):
        with open(f"replication_logs/replication_2025030{i}.log", "w") as f:
            json.dump(log, f, indent=2)

    # docs
    os.makedirs("docs/project_alpha", exist_ok=True)
    with open("docs/project_alpha/README.md", "w") as f:
        f.write("# Alpha Project\nBug reproduction steps...\n")
    os.makedirs("docs/setup", exist_ok=True)
    with open("docs/setup/guide.md", "w") as f:
        f.write("# Setup Guide\n")

    # ops目录（初始空）
    os.makedirs("ops", exist_ok=True)

if __name__ == "__main__":
    build_env()
