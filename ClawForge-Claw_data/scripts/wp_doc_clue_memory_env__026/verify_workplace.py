import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    ws = Path(workspace)
    
    details = []
    total_score = 0
    max_total = 100
    
    # 1. 检查 ops/clue_list.json 是否存在 (10分)
    output_path = ws / "ops" / "clue_list.json"
    item1 = {"item": "Output file exists (ops/clue_list.json)", "score": 0, "max_score": 10}
    if output_path.exists():
        item1["score"] = 10
        item1["passed"] = True
        item1["reason"] = "File found."
    else:
        item1["score"] = 0
        item1["passed"] = False
        item1["reason"] = "File not found."
    details.append(item1)
    total_score += item1["score"]
    
    # 2. 文件格式合法 (10分)
    item2 = {"item": "Valid JSON content", "score": 0, "max_score": 10}
    if not output_path.exists():
        item2["score"] = 0
        item2["passed"] = False
        item2["reason"] = "File missing, cannot validate."
        details.append(item2)
        total_score += 0
        # 无法继续，跳过后续检查
    else:
        try:
            with open(output_path, "r") as f:
                data = json.load(f)
            item2["score"] = 10
            item2["passed"] = True
            item2["reason"] = "Valid JSON."
        except json.JSONDecodeError as e:
            item2["score"] = 0
            item2["passed"] = False
            item2["reason"] = f"Invalid JSON: {e}"
        details.append(item2)
        total_score += item2["score"]
        
        if not isinstance(data, dict):
            item2b = {"item": "JSON root is an object", "score": 0, "max_score": 5}
            item2b["passed"] = False
            item2b["reason"] = "Root is not a dict."
            details.append(item2b)
            total_score += 0
        else:
            item2b = {"item": "JSON root is an object", "score": 5, "max_score": 5}
            item2b["passed"] = True
            item2b["reason"] = "Root is a dict."
            details.append(item2b)
            total_score += 5
    
    # 3. 检查是否包含所有目标文档，且排除干扰 (30分)
    target_docs = {
        "RPT-001": ["Edge-deploy-rpt-001"],
        "RPT-002": ["Edge-test-rpt-002"],
        "PRES-001": ["arch-deck-pres-001"],
        "PRES-002": ["q4-review-pres-002"],
        "PRES-005": ["comparison-pres-005"],
        "MEDIA-001": ["podcast-media-001"],
        "MEDIA-004": ["testimonial-media-004"]
    }
    # 干扰文档（不应出现）
    distractors = {"RPT-003", "RPT-004", "RPT-005", "RPT-006",
                   "PRES-003", "PRES-004",
                   "MEDIA-002", "MEDIA-003"}
    
    item3 = {"item": "Correct document IDs (no missing, no extra)", "score": 0, "max_score": 30}
    if isinstance(data, dict):
        found_ids = set(data.keys())
        expected_ids = set(target_docs.keys())
        missing = expected_ids - found_ids
        extra = found_ids - expected_ids
        if missing:
            item3["score"] = 0
            item3["passed"] = False
            item3["reason"] = f"Missing IDs: {missing}"
        elif extra:
            # 检查额外的是否属于干扰集
            unwanted = [e for e in extra if e in distractors]
            if unwanted:
                item3["score"] = 0
                item3["passed"] = False
                item3["reason"] = f"Contains distractor IDs: {unwanted}"
            else:
                # 非干扰但也不在期望中，算超量
                item3["score"] = 0
                item3["passed"] = False
                item3["reason"] = f"Unexpected extra IDs: {extra}"
        else:
            # 检查每个ID对应的clue bullets是否正确
            all_bullets_ok = True
            for doc_id, expected_bullets in target_docs.items():
                actual = data.get(doc_id, [])
                if not isinstance(actual, list):
                    all_bullets_ok = False
                    break
                if set(actual) != set(expected_bullets):
                    all_bullets_ok = False
                    break
            if all_bullets_ok:
                item3["score"] = 30
                item3["passed"] = True
                item3["reason"] = "All expected IDs present and clue bullets match."
            else:
                item3["score"] = 10  # 部分正确
                item3["passed"] = False
                item3["reason"] = "ID set correct but some clue bullets mismatch."
    else:
        item3["score"] = 0
        item3["passed"] = False
        item3["reason"] = "Data is not a dict."
    details.append(item3)
    total_score += item3["score"]
    
    # 4. 每个文档的clue bullets精确匹配 (30分)
    item4 = {"item": "Clue bullets per document exact match", "score": 0, "max_score": 30}
    if isinstance(data, dict) and details[-2]["passed"]:
        # 已经在上一个条目中部分检查，这里细化
        mismatches = []
        for doc_id, expected in target_docs.items():
            actual = data.get(doc_id, [])
            if not isinstance(actual, list):
                mismatches.append((doc_id, "not a list", expected))
            elif set(actual) != set(expected):
                mismatches.append((doc_id, actual, expected))
        if not mismatches:
            item4["score"] = 30
            item4["passed"] = True
            item4["reason"] = "All clue bullets correct."
        else:
            item4["score"] = 0
            item4["passed"] = False
            item4["reason"] = f"Mismatches: {mismatches[:3]}..." 
    else:
        item4["score"] = 0
        item4["passed"] = False
        item4["reason"] = "Cannot check bullet details due to previous errors."
    details.append(item4)
    total_score += item4["score"]
    
    # 5. 额外检查：不允许有多余的文档（重复检查但已覆盖）
    
    # 6. 检查 ops 目录是否存在 (5分)
    dir_item = {"item": "ops directory exists", "score": 0, "max_score": 5}
    if (ws / "ops").is_dir():
        dir_item["score"] = 5
        dir_item["passed"] = True
        dir_item["reason"] = "ops/ directory present."
    else:
        dir_item["score"] = 0
        dir_item["passed"] = False
        dir_item["reason"] = "ops/ directory missing."
    details.append(dir_item)
    total_score += dir_item["score"]
    
    # 7. 输出文件路径与预期一致 (5分)
    path_item = {"item": "File path is ops/clue_list.json", "score": 0, "max_score": 5}
    # 已经检查了存在性，这里仅确保路径正确
    if output_path.exists():
        path_item["score"] = 5
        path_item["passed"] = True
        path_item["reason"] = "File in correct location."
    else:
        path_item["score"] = 0
        path_item["passed"] = False
        path_item["reason"] = "File not at ops/clue_list.json."
    details.append(path_item)
    total_score += path_item["score"]
    
    # 整理总分 (0-100)
    total_score = min(total_score, 100)
    
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Verification complete. Score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    main()
