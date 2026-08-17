"""
verify_workplace: 纯代码验证 agent 输出的 clue_list.json
评分细则（满分100）：
1. 文件存在 (10分)
2. JSON 合法 (10分)
3. 顶层为数组 (5分)
4. 每个元素包含必要字段 (20分)
5. 数组长度正确 (20分)
6. doc_id 均在预期集合内且无重复 (15分)
7. doc_type 正确 (10分)
8. title 正确 (10分)
9. clue_bullet 正确 (10分)
"""
import sys
import json
import os
import re

EXPECTED_ENTRIES = {
    "RPT-2026-042": {
        "doc_type": "report",
        "title": "Industrial AI Market Analysis 2026 Q2",
        "clue_bullet": "This report examines the adoption of HelioSync Edge Inference Fabric across manufacturing sectors."
    },
    "PRES-2026-021": {
        "doc_type": "presentation",
        "title": "HelioSync Edge Architecture Overview",
        "clue_bullet": "Detailed architecture of HelioSync Edge Inference Fabric and its deployment patterns."
    },
    "PRES-2026-022": {
        "doc_type": "presentation",
        "title": "Edge Inference at Scale",
        "clue_bullet": "Scaling strategies for HelioSync Edge Inference Fabric in large-scale deployments."
    },
    "MED-2026-019": {
        "doc_type": "media_sample",
        "title": "Podcast: Edge Inference Revolution",
        "clue_bullet": "Discussion on how HelioSync Edge Inference Fabric is transforming real-time AI inference."
    }
}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total = 0

    # 1. 文件存在 (10分)
    clue_path = os.path.join(workspace, "clue_list.json")
    if os.path.isfile(clue_path):
        details.append({"item": "clue_list.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total += 10
    else:
        details.append({"item": "clue_list.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续无法验证，直接输出
        write_score(total, details)
        return

    # 2. JSON 合法 (10分)
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
        details.append({"item": "JSON 合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        total += 10
    except Exception as e:
        details.append({"item": "JSON 合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        write_score(total, details)
        return

    # 3. 顶层为数组 (5分)
    if isinstance(data, list):
        details.append({"item": "顶层结构为数组", "score": 5, "max_score": 5, "passed": True, "reason": "是数组"})
        total += 5
    else:
        details.append({"item": "顶层结构为数组", "score": 0, "max_score": 5, "passed": False, "reason": f"顶层类型为 {type(data).__name__}，应为 list"})
        # 继续执行但数组相关检查跳过

    # 4. 每个元素包含必要字段 (20分)
    required_fields = ["doc_id", "doc_type", "title", "clue_bullet"]
    field_score = 20
    if not isinstance(data, list):
        field_score = 0
        details.append({"item": "元素字段完整性", "score": 0, "max_score": 20, "passed": False, "reason": "顶层不是数组，无法检查字段"})
    else:
        missing_field_entries = 0
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                missing_field_entries += 1
                continue
            missing = [f for f in required_fields if f not in entry]
            if missing:
                missing_field_entries += 1
        if missing_field_entries == 0:
            details.append({"item": "元素字段完整性", "score": 20, "max_score": 20, "passed": True, "reason": "所有元素均包含 doc_id, doc_type, title, clue_bullet"})
            total += 20
        else:
            deduction = min(missing_field_entries * 5, 20)
            details.append({"item": "元素字段完整性", "score": 20 - deduction, "max_score": 20, "passed": False, "reason": f"{missing_field_entries} 个元素缺少必要字段"})
            total += (20 - deduction)

    # 5. 数组长度正确 (20分)
    expected_len = len(EXPECTED_ENTRIES)
    if isinstance(data, list):
        actual_len = len(data)
        if actual_len == expected_len:
            details.append({"item": "数组长度", "score": 20, "max_score": 20, "passed": True, "reason": f"长度正确：{actual_len}"})
            total += 20
        else:
            diff = abs(actual_len - expected_len)
            deduction = min(diff * 5, 20)
            details.append({"item": "数组长度", "score": 20 - deduction, "max_score": 20, "passed": False, "reason": f"期望 {expected_len}，实际 {actual_len}，偏差 {diff}"})
            total += (20 - deduction)
    else:
        details.append({"item": "数组长度", "score": 0, "max_score": 20, "passed": False, "reason": "不是数组，无法检查长度"})

    # 6. doc_id 均在预期集合内且无重复 (15分)
    id_score = 15
    if isinstance(data, list):
        ids_seen = set()
        valid_ids = set(EXPECTED_ENTRIES.keys())
        invalid_count = 0
        duplicate_count = 0
        for entry in data:
            if isinstance(entry, dict) and "doc_id" in entry:
                doc_id = entry["doc_id"]
                if doc_id not in valid_ids:
                    invalid_count += 1
                elif doc_id in ids_seen:
                    duplicate_count += 1
                else:
                    ids_seen.add(doc_id)
        missing_ids = valid_ids - ids_seen
        total_issues = invalid_count + duplicate_count + len(missing_ids)
        if total_issues == 0:
            details.append({"item": "doc_id 集合正确", "score": 15, "max_score": 15, "passed": True, "reason": "所有 doc_id 均在预期集合内且无重复"})
            total += 15
        else:
            deduction = min(total_issues * 3, 15)
            details.append({"item": "doc_id 集合正确", "score": 15 - deduction, "max_score": 15, "passed": False, "reason": f"无效 id {invalid_count}，重复 {duplicate_count}，缺失 {len(missing_ids)}"})
            total += (15 - deduction)
    else:
        details.append({"item": "doc_id 集合正确", "score": 0, "max_score": 15, "passed": False, "reason": "不是数组"})

    # 7. doc_type 正确 (10分)
    type_score = 10
    if isinstance(data, list):
        type_errors = 0
        for entry in data:
            if isinstance(entry, dict) and "doc_id" in entry and "doc_type" in entry:
                doc_id = entry["doc_id"]
                expected = EXPECTED_ENTRIES.get(doc_id, {}).get("doc_type")
                if expected and entry["doc_type"] != expected:
                    type_errors += 1
            else:
                type_errors += 0.5  # 缺少字段算半个错误，但已在前面扣分，这里轻轻扣
        if type_errors == 0:
            details.append({"item": "doc_type 正确性", "score": 10, "max_score": 10, "passed": True, "reason": "所有元素的 doc_type 均正确"})
            total += 10
        else:
            deduction = min(int(type_errors * 2.5), 10)
            details.append({"item": "doc_type 正确性", "score": 10 - deduction, "max_score": 10, "passed": False, "reason": f"{int(type_errors)} 个元素 doc_type 不符"})
            total += (10 - deduction)
    else:
        details.append({"item": "doc_type 正确性", "score": 0, "max_score": 10, "passed": False, "reason": "不是数组"})

    # 8. title 正确 (10分)
    title_score = 10
    if isinstance(data, list):
        title_errors = 0
        for entry in data:
            if isinstance(entry, dict) and "doc_id" in entry and "title" in entry:
                doc_id = entry["doc_id"]
                expected = EXPECTED_ENTRIES.get(doc_id, {}).get("title")
                if expected and entry["title"] != expected:
                    title_errors += 1
            else:
                title_errors += 0.5
        if title_errors == 0:
            details.append({"item": "title 正确性", "score": 10, "max_score": 10, "passed": True, "reason": "所有元素的 title 均正确"})
            total += 10
        else:
            deduction = min(int(title_errors * 2.5), 10)
            details.append({"item": "title 正确性", "score": 10 - deduction, "max_score": 10, "passed": False, "reason": f"{int(title_errors)} 个元素 title 不符"})
            total += (10 - deduction)
    else:
        details.append({"item": "title 正确性", "score": 0, "max_score": 10, "passed": False, "reason": "不是数组"})

    # 9. clue_bullet 正确 (10分)
    bullet_score = 10
    if isinstance(data, list):
        bullet_errors = 0
        for entry in data:
            if isinstance(entry, dict) and "doc_id" in entry and "clue_bullet" in entry:
                doc_id = entry["doc_id"]
                expected = EXPECTED_ENTRIES.get(doc_id, {}).get("clue_bullet")
                if expected and entry["clue_bullet"] != expected:
                    bullet_errors += 1
            else:
                bullet_errors += 0.5
        if bullet_errors == 0:
            details.append({"item": "clue_bullet 正确性", "score": 10, "max_score": 10, "passed": True, "reason": "所有元素的 clue_bullet 均正确"})
            total += 10
        else:
            deduction = min(int(bullet_errors * 2.5), 10)
            details.append({"item": "clue_bullet 正确性", "score": 10 - deduction, "max_score": 10, "passed": False, "reason": f"{int(bullet_errors)} 个元素 clue_bullet 不符"})
            total += (10 - deduction)
    else:
        details.append({"item": "clue_bullet 正确性", "score": 0, "max_score": 10, "passed": False, "reason": "不是数组"})

    # 确保 total 不超过 100
    total = min(total, 100)
    write_score(total, details)

def write_score(total, details, output_path="workplace_score.json"):
    score_obj = {
        "total_score": total,
        "details": details
    }
    with open(output_path, "w") as f:
        json.dump(score_obj, f, indent=2)
    print(f"总分: {total}")

if __name__ == "__main__":
    main()
