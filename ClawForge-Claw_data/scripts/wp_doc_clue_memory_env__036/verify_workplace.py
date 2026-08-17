"""
Verifier for wp_doc_clue_memory_env__036.
Checks that the agent has created 'clues/clue_list.json' with the correct
set of documents matching 'HelioSync Edge Inference Fabric'.
"""
import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    scores = []
    total = 0

    # 1. 目录是否存在 (10分)
    clues_dir = os.path.join(workspace, "clues")
    if os.path.isdir(clues_dir):
        scores.append({"item": "clues/ directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "Directory found"})
        total += 10
    else:
        scores.append({"item": "clues/ directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'clues/' not found"})
        # 如果目录都不存在，后面无法检查文件，直接结束
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": scores}, f, indent=2)
        print("FATAL: clues/ directory missing")
        sys.exit(0)

    # 2. 文件是否存在 (10分)
    clue_file = os.path.join(clues_dir, "clue_list.json")
    if os.path.isfile(clue_file):
        scores.append({"item": "clues/clue_list.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found"})
        total += 10
    else:
        scores.append({"item": "clues/clue_list.json exists", "score": 0, "max_score": 10, "passed": False, "reason": "File not found"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": scores}, f, indent=2)
        print("FATAL: clue_list.json missing")
        sys.exit(0)

    # 3. 文件是否合法 JSON (10分)
    try:
        with open(clue_file, "r") as f:
            data = json.load(f)
        scores.append({"item": "JSON parse valid", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        total += 10
    except Exception as e:
        scores.append({"item": "JSON parse valid", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total, "details": scores}, f, indent=2)
        sys.exit(0)

    # 4. 数据结构：必须是一个列表 (5分)
    if isinstance(data, list):
        scores.append({"item": "Data is a list", "score": 5, "max_score": 5, "passed": True, "reason": "Type list"})
        total += 5
    else:
        scores.append({"item": "Data is a list", "score": 0, "max_score": 5, "passed": False, "reason": f"Expected list, got {type(data).__name__}"})
        # 继续检查，但得分为0

    # 如果数据不是列表，则强制转成空列表以继续检查
    if not isinstance(data, list):
        data = []

    # 5. 每个元素必须有 'type' 和 'id' 字段 (5分)
    all_have_fields = True
    for idx, item in enumerate(data):
        if not isinstance(item, dict) or 'type' not in item or 'id' not in item:
            all_have_fields = False
            break
    if all_have_fields:
        scores.append({"item": "Each entry has 'type' and 'id'", "score": 5, "max_score": 5, "passed": True, "reason": "All entries conform"})
        total += 5
    else:
        scores.append({"item": "Each entry has 'type' and 'id'", "score": 0, "max_score": 5, "passed": False, "reason": "Some entries missing required fields"})

    # 6. 检查正确项：期待 4 个文档（2个report, 1个presentation, 1个media_sample）
    # 正确答案（从env_builder可知）
    expected = [
        {"type": "report", "id": "RPT-2042"},
        {"type": "report", "id": "RPT-301"},
        {"type": "presentation", "id": "PRES-007"},
        {"type": "media_sample", "id": "MS-042"},
    ]
    # 构建实际条目集合（去重，仅考虑有效的）
    actual_set = set()
    for item in data:
        if isinstance(item, dict) and 'type' in item and 'id' in item:
            actual_set.add((item['type'], item['id']))

    expected_set = set((e['type'], e['id']) for e in expected)

    # 计算正确命中
    correct_hits = actual_set & expected_set
    false_positives = actual_set - expected_set
    false_negatives = expected_set - actual_set

    # 每个正确项15分，共60分（4项）
    per_correct_score = 15
    correct_score = len(correct_hits) * per_correct_score
    # 多余项每个扣10分（但不低于0）
    penalty = len(false_positives) * 10
    final_subscore = max(correct_score - penalty, 0)
    # 缺失项每个扣5分（但不低于0）
    final_subscore = max(final_subscore - len(false_negatives) * 5, 0)

    # 限制最大60
    final_subscore = min(final_subscore, 60)

    if len(correct_hits) == 4 and len(false_positives) == 0 and len(false_negatives) == 0:
        reason = "All four expected documents present, no extra entries"
    else:
        reason_parts = []
        if len(correct_hits) < 4:
            missing = [e for e in expected if (e['type'], e['id']) not in correct_hits]
            reason_parts.append(f"missing {len(missing)}: {missing}")
        if false_positives:
            reason_parts.append(f"extra {len(false_positives)}: {list(false_positives)}")
        reason = "; ".join(reason_parts) if reason_parts else "Unknown issue"

    scores.append({
        "item": "Document ID accuracy (exact match)",
        "score": final_subscore,
        "max_score": 60,
        "passed": (final_subscore == 60),
        "reason": reason
    })
    total += final_subscore

    # 总计
    final_total = total
    result = {
        "total_score": final_total,
        "details": scores
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {final_total}/100")

if __name__ == "__main__":
    main()
