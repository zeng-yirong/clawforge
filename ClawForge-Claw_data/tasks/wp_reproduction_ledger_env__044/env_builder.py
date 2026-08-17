import os
import json

def build_env():
    # 创建项目文档目录
    os.makedirs("data/projects", exist_ok=True)

    # 项目A的文档（干扰项）
    project_a_docs = {
        "project_docs": [
            {
                "doc_id": "LGR-2024-001",
                "project_id": "mem-perf",
                "title": "Baseline Memory Usage on v1.3",
                "path": "docs/v1_3_baseline.md",
                "reproduction_steps": ["Boot with default config", "Run idle 30 min", "Record memory"],
                "result": "Stable at 800MB"
            },
            {
                "doc_id": "LGR-2024-002",
                "project_id": "mem-perf",
                "title": "Reproduction: Memory Leak on v1.6",
                "path": "docs/v1_6_leak.md",
                "reproduction_steps": ["Install v1.6", "Run load test 5 min", "Check kmem"],
                "result": "Leak detected after 10 min"
            }
        ]
    }
    with open("data/projects/project_a_docs.json", "w") as f:
        json.dump(project_a_docs, f, indent=2)

    # 项目B的文档（包含目标记录）
    project_b_docs = {
        "project_docs": [
            {
                "doc_id": "LGR-2024-003",
                "project_id": "mem-perf",
                "title": "Failed Reproduction: Memory Leak on V2.1",
                "path": "docs/v2_1_failed.md",
                "reproduction_steps": [
                    "Install v2.1 on bare metal",
                    "Run stress test with 4 workers",
                    "Monitor memory usage via /proc/meminfo",
                    "Wait for OOM or 2GB threshold"
                ],
                "result": "Memory leak confirmed at 2GB threshold, process killed by OOM after 12 min"
            },
            {
                "doc_id": "LGR-2024-004",
                "project_id": "mem-perf",
                "title": "Mitigation: Cache Tuning for v2.3",
                "path": "docs/v2_3_mitigation.md",
                "reproduction_steps": ["Apply patch", "Run same stress test"],
                "result": "Memory capped at 1.2GB"
            }
        ]
    }
    with open("data/projects/project_b_docs.json", "w") as f:
        json.dump(project_b_docs, f, indent=2)

    # 项目C的文档（过期版本干扰）
    project_c_docs = {
        "project_docs": [
            {
                "doc_id": "LGR-2023-099",
                "project_id": "mem-perf",
                "title": "Old Reproduction: Memory Leak on v0.9",
                "path": "docs/v0_9_ancient.md",
                "reproduction_steps": ["Install v0.9", "Run load", "Observe crash"],
                "result": "Crash after 1 min"
            }
        ]
    }
    with open("data/projects/project_c_docs.json", "w") as f:
        json.dump(project_c_docs, f, indent=2)

    # 额外干扰文件（accounts, contacts）
    os.makedirs("data", exist_ok=True)
    accounts = {
        "accounts": [
            {"account_id": "a001", "display_name": "Alice", "department": "R&D", "email": "alice@example.com", "permissions": ["read", "write"]},
            {"account_id": "a002", "display_name": "Bob", "department": "QA", "email": "bob@example.com", "permissions": ["read"]}
        ]
    }
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    contacts = {
        "contacts": [
            {"contact_id": "c001", "name": "Carol", "role": "Engineer", "email": "carol@example.com"},
            {"contact_id": "c002", "name": "Dave", "role": "Manager", "email": "dave@example.com"}
        ]
    }
    with open("data/contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

    # 创建空的archive目录（Agent需要在此输出）
    os.makedirs("archive", exist_ok=True)

if __name__ == "__main__":
    build_env()
