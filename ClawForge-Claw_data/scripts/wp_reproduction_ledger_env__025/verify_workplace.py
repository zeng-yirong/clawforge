import json
import os
import sys
from pathlib import Path

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def verify():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    score_total = 0
    details = []

    # 1. 目录结构 (10分)
    ledger_dir = workspace / "ledger"
    if ledger_dir.is_dir():
        score_total += 10
        details.append({
            "item": "ledger 目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ledger 目录已创建"
        })
    else:
        details.append({
            "item": "ledger 目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "缺少 ledger 目录"
        })

    # 2. 格式合法性 (10分)
    ledger_file = ledger_dir / "reproduction_ledger.json"
    if not ledger_file.is_file():
        details.append({
            "item": "结果文件存在且合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ledger/reproduction_ledger.json 不存在"
        })
        score_total += 0
        # 无法继续，返回当前分数
        return finalize(score_total, details)

    try:
        data = load_json(ledger_file)
    except Exception as e:
        details.append({
            "item": "结果文件存在且合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"JSON 解析失败: {e}"
        })
        return finalize(score_total, details)

    if not isinstance(data, dict) or "project_id" not in data or "documents" not in data:
        details.append({
            "item": "结果文件存在且合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "JSON 顶层缺少 project_id 或 documents 字段"
        })
        return finalize(score_total, details)
    else:
        details.append({
            "item": "结果文件存在且合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "JSON 结构正确"
        })
        score_total += 10

    # 3. 剔除脏数据 (30分) —— 检查每个文档的完整性及项目匹配
    docs = data["documents"]
    max_dirty = 30
    dirty_penalty = 0

    # 3.1 检查 project_id 一致性
    if data["project_id"] != "proj-025":
        dirty_penalty += 10
        details.append({
            "item": "顶层的 project_id 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 proj-025, 实际 {data['project_id']}"
        })
    else:
        details.append({
            "item": "顶层的 project_id 正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "project_id 为 proj-025"
        })
        score_total += 10

    # 3.2 每个文档必须包含 doc_id, title, path, project_id 且 project_id 为 proj-025
    valid_docs = []
    invalid_docs = []
    for i, doc in enumerate(docs):
        required = ["doc_id", "title", "path", "project_id"]
        if all(k in doc for k in required) and doc["project_id"] == "proj-025":
            valid_docs.append(doc)
        else:
            invalid_docs.append(doc)

    if invalid_docs:
        dirty_penalty += 10
        details.append({
            "item": "文档字段完整且 project_id 正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"发现 {len(invalid_docs)} 个文档字段不完整或项目不匹配"
        })
    else:
        details.append({
            "item": "文档字段完整且 project_id 正确",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "所有文档字段完整且项目正确"
        })
        score_total += 10

    # 3.3 没有包含干扰项 （不能有 doc-006 或 doc-007）
    unwanted_ids = {"doc-006", "doc-007"}
    doc_ids = {d["doc_id"] for d in valid_docs}
    if unwanted_ids.intersection(doc_ids):
        dirty_penalty += 10
        details.append({
            "item": "未包含干扰文档",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "结果中包含不应该出现的干扰文档"
        })
    else:
        details.append({
            "item": "未包含干扰文档",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "未包含干扰文档"
        })
        score_total += 10

    # 实际得分 = max(30 - dirty_penalty, 0)
    dirty_score = max(30 - dirty_penalty, 0)
    # 但上面已经加过分了，需要调整。重新计算：剔除脏数据总分30，我们分别在3.1,3.2,3.3各10分，已经计入score_total。所以这里不再重复。
    # 不重复加，继续。

    # 4. 关键计算 (50分) —— 精确匹配正确文档列表
    expected_docs = [
        {"doc_id": "doc-001", "project_id": "proj-025", "title": "Implementation Guide", "path": "/docs/impl_guide.pdf"},
        {"doc_id": "doc-002", "project_id": "proj-025", "title": "API Reference", "path": "/docs/api_ref.pdf"},
        {"doc_id": "doc-003", "project_id": "proj-025", "title": "Troubleshooting", "path": "/docs/troubleshoot.pdf"}
    ]
    # 排序（按 doc_id）
    sorted_valid = sorted(valid_docs, key=lambda x: x["doc_id"])
    if sorted_valid == expected_docs:
        details.append({
            "item": "文档列表精确匹配",
            "score": 50,
            "max_score": 50,
            "passed": True,
            "reason": "文档数量、顺序和字段值完全正确"
        })
        score_total += 50
    else:
        # 部分匹配
        correct_count = sum(1 for d in sorted_valid if d in expected_docs)
        partial = int(50 * correct_count / len(expected_docs))
        details.append({
            "item": "文档列表精确匹配",
            "score": partial,
            "max_score": 50,
            "passed": False,
            "reason": f"期望 {len(expected_docs)} 个文档，得到 {len(sorted_valid)} 个，其中 {correct_count} 个正确"
        })
        score_total += partial

    # 最终得分
    finalize(score_total, details)

def finalize(score, details):
    result = {
        "total_score": score,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {score}/100")
    sys.exit(0 if score >= 50 else 1)

if __name__ == "__main__":
    verify()
