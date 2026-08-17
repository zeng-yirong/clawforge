import os
import json

def build_env():
    # data 目录
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 构建 project_docs.json
    project_docs = [
        {
            "doc_id": "doc_alpha_v1",
            "project_id": "project-alpha",
            "title": "reproduction-steps-v1",
            "path": "docs/project-alpha/reproduction-steps-v1.md",
            "date": "2024-01-15"
        },
        {
            "doc_id": "doc_alpha_v2",
            "project_id": "project-alpha",
            "title": "reproduction-steps-v2",
            "path": "docs/project-alpha/reproduction-steps-v2.md",
            "date": "2024-06-20"
        },
        {
            "doc_id": "doc_alpha_deprecated",
            "project_id": "project-alpha",
            "title": "reproduction-steps-v1_deprecated",
            "path": "docs/project-alpha/reproduction-steps-v1_deprecated.md",
            "date": "2023-12-01"
        },
        {
            "doc_id": "doc_beta",
            "project_id": "project-beta",
            "title": "reproduction-steps",
            "path": "docs/project-beta/reproduction-steps.md",
            "date": "2024-03-10"
        },
        {
            "doc_id": "doc_gamma_missing",
            "project_id": "project-gamma",
            "title": "steps",
            "path": "docs/project-gamma/missing.md",
            "date": "2024-05-01"
        }
    ]
    with open("data/projects/project_docs.json", "w") as f:
        json.dump({"project_docs": project_docs}, f)

    # 创建 docs 目录及实际文件
    os.makedirs("docs/project-alpha", exist_ok=True)
    os.makedirs("docs/project-beta", exist_ok=True)
    os.makedirs("docs/project-gamma", exist_ok=True)

    # 有效文档 v1
    with open("docs/project-alpha/reproduction-steps-v1.md", "w") as f:
        f.write("""# Reproduction Steps v1
Date: 2024-01-15
Commit: abc123
Version: 1.0
Steps:
1. Clone repo
2. Run script
""")
    # 有效文档 v2 (最新)
    with open("docs/project-alpha/reproduction-steps-v2.md", "w") as f:
        f.write("""# Reproduction Steps v2
Date: 2024-06-20
Commit: def456
Version: 2.0
Steps:
1. Clone repo
2. Install deps
3. Run test
""")
    # 废弃文档
    with open("docs/project-alpha/reproduction-steps-v1_deprecated.md", "w") as f:
        f.write("""# Reproduction Steps v1 (deprecated)
Date: 2023-12-01
Commit: old789
Version: 0.9
Steps:
1. Old steps
""")
    # 其他项目文档 (不应使用)
    with open("docs/project-beta/reproduction-steps.md", "w") as f:
        f.write("""# Beta Steps
Date: 2024-03-10
Commit: xyz999
Version: 3.0
Steps:
1. Do beta thing
""")
    # 不存在的文件不创建 (project-gamma/missing.md 不存在)

    # 创建空的归档目录 (agent 需创建 archive/reproduction_ledger.json)
    os.makedirs("archive", exist_ok=True)

if __name__ == "__main__":
    build_env()
