import os
import json
import sys

def verify(workspace: str) -> dict:
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查 ops 目录是否存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    dir_exists = os.path.isdir(ops_dir)
    if dir_exists:
        total_score += 10
        details.append({
            "item": "ops directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ directory found"
        })
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/ directory not found"
        })

    if not dir_exists:
        # 如果目录不存在，后续检查都无法进行，直接返回
        details.append({
            "item": "clue_list.json exists",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "ops directory missing"
        })
        details.append({
            "item": "clue_list.json format",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "file not found"
        })
        details.append({
            "item": "clue_list content correctness",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "file not found"
        })
        return {"total_score": total_score, "details": details}

    # 2. 检查 clue_list.json 是否存在 (15分)
    clue_path = os.path.join(ops_dir, "clue_list.json")
    file_exists = os.path.isfile(clue_path)
    if file_exists:
        total_score += 15
        details.append({
            "item": "clue_list.json exists",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "ops/clue_list.json found"
        })
    else:
        details.append({
            "item": "clue_list.json exists",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "ops/clue_list.json not found"
        })
        # 后续无法继续，返回
        details.append({
            "item": "clue_list.json format",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "file not found"
        })
        details.append({
            "item": "clue_list content correctness",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "file not found"
        })
        return {"total_score": total_score, "details": details}

    # 3. 检查 JSON 格式及字段完整性 (15分)
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError):
        total_score += 0
        details.append({
            "item": "clue_list.json format",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "Invalid JSON syntax"
        })
        details.append({
            "item": "clue_list content correctness",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "format invalid, cannot parse content"
        })
        return {"total_score": total_score, "details": details}

    # 检查是否为数组
    if not isinstance(data, list):
        total_score += 0
        details.append({
            "item": "clue_list.json format",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "Root element is not a list"
        })
        details.append({
            "item": "clue_list content correctness",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "format invalid"
        })
        return {"total_score": total_score, "details": details}

    # 检查每个对象是否包含必需字段
    required_fields = {"document_id", "type", "title", "clue"}
    all_have_fields = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            all_have_fields = False
            break
        if not required_fields.issubset(entry.keys()):
            all_have_fields = False
            break
        # 检查 type 有效性
        if entry.get("type") not in ("report", "presentation", "media"):
            all_have_fields = False
            break

    if all_have_fields:
        total_score += 15
        details.append({
            "item": "clue_list.json format",
            "score": 15,
            "max_score": 15,
            "passed": True,
            "reason": "Valid JSON list with required fields per object"
        })
    else:
        total_score += 0
        details.append({
            "item": "clue_list.json format",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "reason": "Missing required fields or invalid type value"
        })
        # 即使格式有误，仍尝试检查内容（部分得分可能）
        # 但为了简化，这里不再继续内容检查
        details.append({
            "item": "clue_list content correctness",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": "Format errors prevent full content validation"
        })
        return {"total_score": total_score, "details": details}

    # 4. 检查内容准确性 (60分)
    # 预期答案：四个文档，按 document_id 排序
    expected = [
        {
            "document_id": "media-001",
            "type": "media",
            "title": "Podcast: CTO on HelioSync Edge Fabric",
            "clue": "Podcast interview with CTO on HelioSync."
        },
        {
            "document_id": "pres-002",
            "type": "presentation",
            "title": "Deploying HelioSync Edge Fabric in 5G Networks",
            "clue": "Edge fabric deployment in 5G networks."
        },
        {
            "document_id": "report-001",
            "type": "report",
            "title": "HelioSync Edge Inference Fabric Performance Benchmark",
            "clue": "Real-time edge inference at 2ms latency."
        },
        {
            "document_id": "report-003",
            "type": "report",
            "title": "HelioSync AI Bandwidth Optimization Report",
            "clue": "HelioSync AI can reduce bandwidth by 40%."
        }
    ]
    # 对实际输出排序（按 document_id 升序）
    actual_sorted = sorted(data, key=lambda x: x.get("document_id", ""))
    expected_sorted = sorted(expected, key=lambda x: x["document_id"])

    # 比较长度
    if len(actual_sorted) != len(expected_sorted):
        total_score += 0
        details.append({
            "item": "clue_list content correctness",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": f"Expected {len(expected_sorted)} entries, got {len(actual_sorted)}"
        })
        return {"total_score": total_score, "details": details}

    # 逐一比较
    matches = 0
    for a, e in zip(actual_sorted, expected_sorted):
        if (a.get("document_id") == e["document_id"] and
            a.get("type") == e["type"] and
            a.get("title") == e["title"] and
            a.get("clue") == e["clue"]):
            matches += 1

    # 每个正确条目得 15 分（共4个，满分60）
    content_score = matches * 15
    total_score += content_score
    if matches == 4:
        details.append({
            "item": "clue_list content correctness",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": "All 4 entries match expected values exactly"
        })
    else:
        details.append({
            "item": "clue_list content correctness",
            "score": content_score,
            "max_score": 60,
            "passed": False,
            "reason": f"Only {matches} out of 4 entries match expected"
        })

    return {"total_score": total_score, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {result['total_score']}/100")
