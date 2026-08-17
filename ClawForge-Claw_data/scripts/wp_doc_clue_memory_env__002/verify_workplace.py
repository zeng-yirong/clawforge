import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = []
    total_score = 0

    # 1. 检查 ops 目录存在 (5分)
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        result.append({
            "item": "ops/ directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "ops/ directory found."
        })
        total_score += 5
    else:
        result.append({
            "item": "ops/ directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ directory not found."
        })

    # 2. 检查 clue_list.json 存在 (5分)
    clue_path = os.path.join(workspace, "ops", "clue_list.json")
    if os.path.isfile(clue_path):
        result.append({
            "item": "ops/clue_list.json exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "File exists."
        })
        total_score += 5
    else:
        result.append({
            "item": "ops/clue_list.json exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "File not found."
        })
        # 如果文件不存在，后续检查无法进行，直接输出结果
        output_result(total_score, result)
        return

    # 3. 检查 JSON 合法性 (10分)
    try:
        with open(clue_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Not a list")
        result.append({
            "item": "clue_list.json is valid JSON list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "Valid JSON list."
        })
        total_score += 10
    except Exception as e:
        result.append({
            "item": "clue_list.json is valid JSON list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Invalid JSON or not a list: {str(e)}"
        })
        output_result(total_score, result)
        return

    # 4. 长度检查 (10分)
    expected_ids = ["RPT-2026-001", "PRES-2026-001", "MEDIA-2026-001"]
    if len(data) == len(expected_ids):
        result.append({
            "item": "Correct number of entries",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"Length is {len(data)} (expected {len(expected_ids)})."
        })
        total_score += 10
    else:
        result.append({
            "item": "Correct number of entries",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Length is {len(data)}, expected {len(expected_ids)}."
        })

    # 5. 检查每个条目字段 (每个10分，共30分)
    field_score = 0
    field_fail_reason = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            field_fail_reason.append(f"Entry {i} is not a dict")
            continue
        if "id" not in entry or "clue" not in entry:
            field_fail_reason.append(f"Entry {i} missing 'id' or 'clue'")
            continue
        if not isinstance(entry["id"], str) or not isinstance(entry["clue"], str):
            field_fail_reason.append(f"Entry {i} fields must be strings")
            continue
        # 检查 id 是否在期望集合中
        if entry["id"] not in expected_ids:
            field_fail_reason.append(f"Entry {i} has unexpected id '{entry['id']}'")
            continue
        # 检查 clue 是否匹配对应的 summary (从构建时已知)
        if entry["id"] == "RPT-2026-001" and entry["clue"] != "Analysis of HelioSync Edge Inference Fabric in smart manufacturing.":
            field_fail_reason.append(f"Entry {i} (RPT-2026-001) clue mismatch")
            continue
        if entry["id"] == "PRES-2026-001" and entry["clue"] != "Launch deck for HelioSync Edge Inference Fabric with benchmarks.":
            field_fail_reason.append(f"Entry {i} (PRES-2026-001) clue mismatch")
            continue
        if entry["id"] == "MEDIA-2026-001" and entry["clue"] != "Transcript discussing HelioSync Edge Inference Fabric deployment.":
            field_fail_reason.append(f"Entry {i} (MEDIA-2026-001) clue mismatch")
            continue
        # 如果通过了所有检查，增加分数
        field_score += 10

    if field_fail_reason:
        result.append({
            "item": "All entries have correct fields (id/clue)",
            "score": field_score,
            "max_score": 30,
            "passed": field_score == 30,
            "reason": "; ".join(field_fail_reason) or f"Only {field_score}/30 correct."
        })
    else:
        result.append({
            "item": "All entries have correct fields (id/clue)",
            "score": 30,
            "max_score": 30,
            "passed": True,
            "reason": "All 3 entries have correct id and clue."
        })
    total_score += field_score

    # 6. 检查是否有重复 id (10分)
    ids_list = [entry.get("id") for entry in data if isinstance(entry, dict)]
    if len(ids_list) == len(set(ids_list)):
        result.append({
            "item": "No duplicate ids",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "All ids are unique."
        })
        total_score += 10
    else:
        result.append({
            "item": "No duplicate ids",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "Duplicate ids found."
        })

    # 7. 检查是否包含多余条目（比如 obsolete 的）(10分)
    # 我们已经通过字段检查确保了只有三个期望 id，但可能有额外条目多出来
    extra = [entry for entry in data if isinstance(entry, dict) and entry.get("id") not in expected_ids]
    if not extra:
        result.append({
            "item": "No extra entries (e.g. obsolete documents)",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "No unexpected ids present."
        })
        total_score += 10
    else:
        result.append({
            "item": "No extra entries (e.g. obsolete documents)",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"Extra entries found: {[e.get('id') for e in extra]}"
        })

    # 8. 最终加权汇总为100分（前面已经加满最多100）
    output_result(total_score, result)

def output_result(total_score, details):
    with open("workplace_score.json", "w") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2)

if __name__ == "__main__":
    main()
