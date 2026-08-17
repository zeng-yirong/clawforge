import os
import json

def build_env():
    # 创建目录
    os.makedirs("data/projects", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    # 删除 ops 目录下的任何内容（确保初始为空）
    for f in os.listdir("ops"):
        os.remove(os.path.join("ops", f))

    # 干扰文档1：过期版本，缺少 result
    with open("docs/experiment_v1.md", "w") as f:
        f.write("Reproduction ID: RPT-046\nSteps:\n1. setup env\n2. run test\nResult: FAILED\n")
    # 干扰文档2：另一个 bug 的笔记
    with open("docs/notes_bug_448.md", "w") as f:
        f.write("Bug #448 initial investigation.\nReproduction ID: RPT-048\nSteps: none\nResult: unknown\n")
    # 干扰文档3：不完整（没有 Reproduction ID）
    with open("docs/draft_notes.txt", "w") as f:
        f.write("Still testing, need more data...\n")
    # 正确文档：最终版，唯一包含 "FINAL" 标记且字段完整
    with open("docs/047_final_ledger.md", "w") as f:
        f.write("Reproduction ID: RPT-047\nSteps:\n1. Deploy commit e7a9\n2. Trigger race condition\n3. Collect error log\nResult: SUCCESS\n")

    # 构建 project_docs.json 索引，包含多条记录
    project_docs = [
        {"doc_id": "doc001", "project_id": "bug-447", "title": "Experiment V1", "path": "docs/experiment_v1.md"},
        {"doc_id": "doc002", "project_id": "bug-447", "title": "FINAL REPRODUCTION LEDGER: Bug #447", "path": "docs/047_final_ledger.md"},
        {"doc_id": "doc003", "project_id": "bug-448", "title": "Bug 448 initial notes", "path": "docs/notes_bug_448.md"},
        {"doc_id": "doc004", "project_id": "bug-447", "title": "Draft notes (incomplete)", "path": "docs/draft_notes.txt"},
    ]
    with open("data/projects/project_docs.json", "w") as f:
        json.dump({"project_docs": project_docs}, f)

    # 添加干扰性 accounts.json（不影响任务，只增加噪声）
    accounts = [
        {"account_id": "a001", "display_name": "Alice", "department": "QA", "email": "alice@lab.com", "permissions": ["read", "write"]},
        {"account_id": "a002", "display_name": "Bob", "department": "Dev", "email": "bob@lab.com", "permissions": ["read"]},
    ]
    with open("data/accounts.json", "w") as f:
        json.dump({"accounts": accounts}, f)

    # 添加 contacts.json 干扰
    contacts = [
        {"contact_id": "c001", "name": "Charlie", "role": "maintainer", "email": "charlie@project.org"},
    ]
    with open("data/contacts.json", "w") as f:
        json.dump({"contacts": contacts}, f)

if __name__ == "__main__":
    build_env()
