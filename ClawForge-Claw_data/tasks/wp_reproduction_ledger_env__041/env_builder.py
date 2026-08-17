import os
import json
import shutil

def build_env():
    # 项目文档索引
    os.makedirs("project_docs", exist_ok=True)
    project_docs = [
        {"doc_id": "doc_001", "project_id": "project_alpha", "title": "Bug 2025-001 - rendering glitch", "path": "project_alpha/doc_001.md"},
        {"doc_id": "doc_002", "project_id": "project_alpha", "title": "API reference v2.3", "path": "project_alpha/doc_002.md"},
        {"doc_id": "doc_003", "project_id": "project_beta", "title": "Memory leak investigation", "path": "project_beta/doc_003.md"},
    ]
    with open("project_docs/project_docs.json", "w") as f:
        json.dump({"project_docs": project_docs}, f)

    os.makedirs("project_alpha", exist_ok=True)
    with open("project_alpha/doc_001.md", "w") as f:
        f.write("# Bug REPRO-2025-001\n\n## Description\nRendering glitch in widget when using dark mode.\n\n## Relevant code\n`src/renderer.py` lines 42-56.")
    with open("project_alpha/doc_002.md", "w") as f:
        f.write("# API Reference v2.3\n\n## New endpoints\n...")

    os.makedirs("project_beta", exist_ok=True)
    with open("project_beta/doc_003.md", "w") as f:
        f.write("# Memory leak investigation\n\n## Symptom\n...")

    # 知识条目
    os.makedirs("knowledge_entries", exist_ok=True)
    knowledge_entries = [
        {"entry_id": "entry_01", "title": "REPRO-2025-001 root cause", "content": "Race condition in GPU thread pool."},
        {"entry_id": "entry_02", "title": "General rendering notes", "content": "Use double buffering."},
    ]
    with open("knowledge_entries/entries.json", "w") as f:
        json.dump({"knowledge_entries": knowledge_entries}, f)

    # 会话目录
    os.makedirs("sessions", exist_ok=True)

    def write_session(session_id, bug_id, project, success, timestamp, doc_path, steps, result_details):
        session_dir = f"sessions/{session_id}"
        os.makedirs(session_dir, exist_ok=True)
        summary = {
            "session_id": session_id,
            "bug_id": bug_id,
            "project": project,
            "timestamp": timestamp,
            "success": success,
            "steps": steps,
            "result": result_details,
            "doc_ref": doc_path
        }
        with open(f"{session_dir}/session_summary.json", "w") as f:
            json.dump(summary, f)

    # session_001: 失败，相同bug，时间较早
    write_session("session_001", "REPRO-2025-001", "project_alpha", False, "2025-01-08T14:20:00Z",
                  "project_alpha/doc_001.md", 
                  ["1. checkout tag v1.0", "2. apply patch", "3. build with debug"],
                  "Build failed due to missing dependency")

    # session_002: 成功，相同bug，但时间不是最新
    write_session("session_002", "REPRO-2025-001", "project_alpha", True, "2025-01-10T09:15:00Z",
                  "project_alpha/doc_001.md",
                  ["1. checkout tag v1.4", "2. set dark mode", "3. observe glitch"],
                  "Glitch reproducible consistently")

    # session_003: 成功，相同bug，最新时间 —— 这是唯一正确结果
    write_session("session_003", "REPRO-2025-001", "project_alpha", True, "2025-03-15T10:30:00Z",
                  "project_alpha/doc_001.md",
                  ["1. checkout tag v1.7", "2. enable dark mode", "3. run widget test suite"],
                  "Glitch observed on all test runs, confirmed")

    # session_004: 成功，但不同bug
    write_session("session_004", "REPRO-2025-002", "project_beta", True, "2025-03-14T16:00:00Z",
                  "project_beta/doc_003.md",
                  ["1. deploy to staging", "2. run load test", "3. capture heap dump"],
                  "Memory leak confirmed at 2GB threshold")

    # session_005: 成功，相同bug，但结果标记为 inconclusive（失败）
    write_session("session_005", "REPRO-2025-001", "project_alpha", False, "2025-03-13T11:00:00Z",
                  "project_alpha/doc_001.md",
                  ["1. checkout tag v1.6", "2. try dark mode in VM"],
                  "Environment mismatch, not reproducible")

    # 额外干扰：一个没有 summary 的垃圾目录
    os.makedirs("sessions/junk_session", exist_ok=True)
    with open("sessions/junk_session/random.log", "w") as f:
        f.write("garbage data\n")

if __name__ == "__main__":
    build_env()
