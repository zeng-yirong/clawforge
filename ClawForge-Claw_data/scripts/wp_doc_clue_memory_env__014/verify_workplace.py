import sys
import os
import json
import pathlib

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = pathlib.Path(workspace)
    result = {"total_score": 0, "details": []}
    total = 0

    # 1. 目录结构 (10 pts)
    clues_dir = workspace / "clues"
    if clues_dir.is_dir():
        result["details"].append({
            "item": "clues directory exists",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "clues/ directory found"
        })
        total += 10
    else:
        result["details"].append({
            "item": "clues directory exists",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "clues/ directory missing"
        })

    # 2. JSON 文件存在且合法 (10 pts)
    clue_file = clues_dir / "clue_list.json"
    if not clue_file.is_file():
        result["details"].append({
            "item": "clue_list.json exists and valid JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "clues/clue_list.json not found"
        })
        # 无法继续
        result["total_score"] = total
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    try:
        with open(clue_file, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "clues" not in data:
            raise ValueError("missing 'clues' key")
        clues = data["clues"]
        if not isinstance(clues, list):
            raise ValueError("clues is not a list")
        result["details"].append({
            "item": "clue_list.json valid JSON with clues list",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"found {len(clues)} clue(s)"
        })
        total += 10
    except Exception as e:
        result["details"].append({
            "item": "clue_list.json valid JSON with clues list",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"invalid: {e}"
        })
        result["total_score"] = total
        with open(workspace / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # 3. 数量正确 (20 pts)
    expected_count = 3
    if len(clues) == expected_count:
        result["details"].append({
            "item": "number of clues matches expected (3)",
            "score": 20,
            "max_score": 20,
            "passed": True,
            "reason": f"exactly {expected_count} clues"
        })
        total += 20
    else:
        result["details"].append({
            "item": "number of clues matches expected (3)",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"expected {expected_count}, got {len(clues)}"
        })

    # 4. 每个条目的字段和值 (10 pts per record, 共30 pts for IDs, 30 pts for clues)
    # 定义标准答案
    expected_entries = [
        {
            "document_id": "RPT-2026-001",
            "clue": "HelioSync Edge Inference Fabric delivers 3x throughput over previous generation."
        },
        {
            "document_id": "PRES-2026-001",
            "clue": "This deck covers HelioSync Edge Inference Fabric performance benchmarks."
        },
        {
            "document_id": "MED-2026-001",
            "clue": "We talked about HelioSync Edge Inference Fabric enabling real-time inference."
        }
    ]

    # 构建从 document_id 到 clue 的映射方便检查
    actual_map = {}
    for entry in clues:
        if isinstance(entry, dict) and "document_id" in entry and "clue" in entry:
            actual_map[entry["document_id"]] = entry["clue"]
        else:
            # 格式不正确
            pass

    id_score = 0
    clue_score = 0
    for exp in expected_entries:
        doc_id = exp["document_id"]
        exp_clue = exp["clue"]
        if doc_id in actual_map:
            id_score += 10  # 每个正确ID 10分
            # 检查clue
            if actual_map[doc_id] == exp_clue:
                clue_score += 10
            else:
                # clue不匹配，扣分但不说明具体原因（验证日志可记录）
                pass

    result["details"].append({
        "item": "all document_ids correct",
        "score": id_score,
        "max_score": 30,
        "passed": id_score == 30,
        "reason": f"correct IDs: {id_score/10}/{len(expected_entries)}"
    })
    total += id_score

    result["details"].append({
        "item": "all clues exactly match expected text",
        "score": clue_score,
        "max_score": 30,
        "passed": clue_score == 30,
        "reason": f"correct clues: {clue_score/10}/{len(expected_entries)}"
    })
    total += clue_score

    # 额外检查：是否有不应出现的文档ID
    forbidden_ids = ["RPT-2026-002", "RPT-2026-003", "PRES-2026-002", "PRES-2026-003", "MED-2026-002", "MED-2026-003"]
    extra_ids = [did for did in actual_map if did in forbidden_ids]
    if extra_ids:
        penalty = len(extra_ids) * 5  # 每个多余条目扣5分
        total = max(0, total - penalty)
        result["details"].append({
            "item": "no forbidden document IDs present",
            "score": -penalty,
            "max_score": 0,
            "passed": False,
            "reason": f"unexpected IDs found: {extra_ids}"
        })
    else:
        result["details"].append({
            "item": "no forbidden document IDs present",
            "score": 0,
            "max_score": 0,
            "passed": True,
            "reason": "no extra IDs"
        })

    result["total_score"] = min(100, total)  # 不应超过100
    with open(workspace / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
