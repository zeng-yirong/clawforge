import sys
import os
import json
import csv
import re
import pathlib

def verify(workspace: str):
    score_details = []
    total = 0
    max_total = 100

    # Helper to add score item
    def add_item(name, score, max_score, passed, reason):
        score_details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })

    # 1. 检查 ops 目录存在 (10分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        add_item("ops directory exists", 10, 10, True, "ops/ directory found")
    else:
        add_item("ops directory exists", 0, 10, False, "ops/ directory not found")
        # 如果目录不存在，后续检查均失败，直接返回
        finalize(score_details, total)
        return

    # 2. 检查 ops/clue_list.json 文件存在 (10分)
    clue_path = os.path.join(ops_dir, "clue_list.json")
    if os.path.isfile(clue_path):
        add_item("clue_list.json exists", 10, 10, True, "File found")
    else:
        add_item("clue_list.json exists", 0, 10, False, "File not found")
        finalize(score_details, total)
        return

    # 3. 解析 JSON (10分)
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Expected a list")
        add_item("JSON parse and type", 10, 10, True, "Valid JSON list")
    except Exception as e:
        add_item("JSON parse and type", 0, 10, False, f"Invalid JSON: {e}")
        finalize(score_details, total)
        return

    # 4. 条目数量 (10分)
    expected_count = 3
    if len(data) == expected_count:
        add_item("Number of entries", 10, 10, True, f"Exactly {expected_count} entries")
    else:
        add_item("Number of entries", 0, 10, False, f"Expected {expected_count}, got {len(data)}")
        # 继续检查，但数量错误会扣分

    # 5. 每个条目字段完整性 (15分)
    required_fields = {"document_id", "document_type", "clue_bullet"}
    field_ok = True
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_ok = False
            break
        if not required_fields.issubset(entry.keys()):
            field_ok = False
            break
        # 额外检查字段值非空
        for f in required_fields:
            if not entry.get(f):
                field_ok = False
                break
    if field_ok:
        add_item("Field completeness", 15, 15, True, "All entries have required non-empty fields")
    else:
        add_item("Field completeness", 0, 15, False, "Missing fields or empty values")

    # 6. document_id 精确匹配 (15分, 每个5分)
    expected_ids = {"report_001", "pres_001", "media_001"}
    actual_ids = {entry.get("document_id") for entry in data if isinstance(entry, dict)}
    id_score = 0
    for eid in expected_ids:
        if eid in actual_ids:
            id_score += 5
    add_item("document_id correctness", id_score, 15, id_score == 15,
             f"Found {id_score//5} out of 3 expected IDs")

    # 7. document_type 正确 (15分, 每个5分)
    expected_types = {"report": "report_001", "presentation": "pres_001", "media_sample": "media_001"}
    type_score = 0
    # 从实际数据里按id查找type
    entry_by_id = {e.get("document_id"): e for e in data if isinstance(e, dict)}
    for doc_type, doc_id in expected_types.items():
        entry = entry_by_id.get(doc_id)
        if entry and entry.get("document_type") == doc_type:
            type_score += 5
    add_item("document_type correctness", type_score, 15, type_score == 15,
             f"Correct types for {type_score//5} out of 3")

    # 8. clue_bullet 内容匹配 (15分, 每个5分)
    expected_bullets = {
        "report_001": "HelioSync Edge Inference Fabric is used in smart logistics for real-time AI at the edge.",
        "pres_001": "Presentation on HEIF deployment in manufacturing.",
        "media_001": "Podcast discussing edge inference frameworks in Chinese market."
    }
    bullet_score = 0
    for doc_id, expected_text in expected_bullets.items():
        entry = entry_by_id.get(doc_id)
        if entry and entry.get("clue_bullet") == expected_text:
            bullet_score += 5
    add_item("clue_bullet content match", bullet_score, 15, bullet_score == 15,
             f"Exact match for {bullet_score//5} out of 3")

    # 9. 额外扣分：如果有多余的条目（数量对但ID不在预期中）
    if len(data) == expected_count:
        extra_ids = actual_ids - expected_ids
        if extra_ids:
            # 每个额外ID扣2分，但不超过10分
            penalty = min(len(extra_ids)*2, 10)
            add_item("No extra entries", max(0, 0), 0, False, f"Extra IDs: {extra_ids} (penalty {penalty} applied internally)")
            # 分数不直接从总分减，我们已经在细节中记录，实际总分需要手动扣除
            # 在总分计算时扣
            nonlocal_penalty = penalty  # 但无法在嵌套函数中修改外层变量，我们使用列表绕一下
            # 简化：直接在最后计算总分时减去额外扣分
            # 我们在这里记录下来，最后再减
            global_extra_penalty = nonlocal_penalty
        else:
            global_extra_penalty = 0
    else:
        global_extra_penalty = 0

    # 计算总分
    total = sum(item["score"] for item in score_details)
    # 额外扣分（不在item中体现，直接减）
    if 'global_extra_penalty' in dir():
        total -= global_extra_penalty
    total = max(0, min(100, total))

    # 最后写入
    result = {
        "total_score": total,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification complete. Total score: {total}/100")

def finalize(details, total):
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Verification early exit. Total score: {total}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
