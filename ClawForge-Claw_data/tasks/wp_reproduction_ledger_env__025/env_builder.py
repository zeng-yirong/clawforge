import json
import os

def build_env():
    os.makedirs("project_docs", exist_ok=True)

    # 正确文档：proj-025
    correct = [
        {"doc_id": "doc-001", "project_id": "proj-025", "title": "Implementation Guide", "path": "/docs/impl_guide.pdf"},
        {"doc_id": "doc-002", "project_id": "proj-025", "title": "API Reference", "path": "/docs/api_ref.pdf"},
        {"doc_id": "doc-003", "project_id": "proj-025", "title": "Troubleshooting", "path": "/docs/troubleshoot.pdf"}
    ]
    with open("project_docs/proj_025.json", "w") as f:
        json.dump({"project_docs": correct}, f)

    # 干扰：其他项目
    other = [
        {"doc_id": "doc-004", "project_id": "proj-026", "title": "Deployment Guide", "path": "/docs/deploy.pdf"},
        {"doc_id": "doc-005", "project_id": "proj-026", "title": "Security Notes", "path": "/docs/security.pdf"}
    ]
    with open("project_docs/proj_026.json", "w") as f:
        json.dump({"project_docs": other}, f)

    # 干扰：格式错误（非 JSON）
    with open("project_docs/corrupted.txt", "w") as f:
        f.write("This is not JSON")

    # 干扰：包含 proj-025 但缺少 title 字段
    incomplete = [
        {"doc_id": "doc-006", "project_id": "proj-025", "path": "/docs/missing_title.pdf"}
    ]
    with open("project_docs/incomplete.json", "w") as f:
        json.dump({"project_docs": incomplete}, f)

    # 干扰：隐藏文件（不匹配 proj-025）
    hidden = [
        {"doc_id": "doc-007", "project_id": "proj-000", "title": "Secret", "path": "/docs/secret.pdf"}
    ]
    with open("project_docs/.hidden.json", "w") as f:
        json.dump({"project_docs": hidden}, f)
