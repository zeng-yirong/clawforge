import os
import json
import sys

def verify(workspace: str):
    details = []
    total_score = 0

    # 1. output 目录存在
    output_dir = os.path.join(workspace, "output")
    dir_exists = os.path.isdir(output_dir)
    details.append({
        "item": "output directory exists",
        "score": 10 if dir_exists else 0,
        "max_score": 10,
        "passed": dir_exists,
        "reason": "Found" if dir_exists else "Not found"
    })
    if dir_exists:
        total_score += 10

    # 2. tech_recommendations.json 存在
    rec_path = os.path.join(output_dir, "tech_recommendations.json")
    file_exists = os.path.isfile(rec_path)
    details.append({
        "item": "tech_recommendations.json exists",
        "score": 10 if file_exists else 0,
        "max_score": 10,
        "passed": file_exists,
        "reason": "Found" if file_exists else "Not found"
    })
    if file_exists:
        total_score += 10

    # 3. JSON 合法且为 list
    content = None
    valid_json = False
    is_list = False
    if file_exists:
        try:
            with open(rec_path, "r") as f:
                content = json.load(f)
            valid_json = True
            if isinstance(content, list):
                is_list = True
        except (json.JSONDecodeError, Exception):
            pass
    details.append({
        "item": "valid JSON list",
        "score": (10 if valid_json else 0) + (10 if is_list else 0),
        "max_score": 20,
        "passed": valid_json and is_list,
        "reason": "Valid list" if (valid_json and is_list) else "Invalid or not a list"
    })
    if valid_json and is_list:
        total_score += 20

    # 4. 长度等于2
    length_ok = False
    if is_list:
        length_ok = len(content) == 2
    details.append({
        "item": "contains exactly 2 tickers",
        "score": 20 if length_ok else 0,
        "max_score": 20,
        "passed": length_ok,
        "reason": f"Length {len(content)}" if is_list else "N/A"
    })
    if length_ok:
        total_score += 20

    # 5. 包含 TECH
    has_tech = is_list and "TECH" in content
    details.append({
        "item": "TECH is present",
        "score": 20 if has_tech else 0,
        "max_score": 20,
        "passed": has_tech,
        "reason": "Found" if has_tech else "Missing"
    })
    if has_tech:
        total_score += 20

    # 6. 包含 NXTC
    has_nxtc = is_list and "NXTC" in content
    details.append({
        "item": "NXTC is present",
        "score": 20 if has_nxtc else 0,
        "max_score": 20,
        "passed": has_nxtc,
        "reason": "Found" if has_nxtc else "Missing"
    })
    if has_nxtc:
        total_score += 20

    # 7. 顺序正确（TECH 在前，NXTC 在后）且没有多余元素
    order_ok = False
    if is_list and length_ok and content == ["TECH", "NXTC"]:
        order_ok = True
    # 检查是否有多余元素（已经在长度检查中涵盖，但这里额外扣分）
    extra_penalty = 0
    if is_list and length_ok and not order_ok:
        extra_penalty = 10  # 顺序错误或内容不对则扣分
    details.append({
        "item": "ordering and no extras",
        "score": 10 if order_ok else (0 - extra_penalty),
        "max_score": 10,
        "passed": order_ok,
        "reason": "Correct order" if order_ok else "Wrong order or extra items"
    })
    if order_ok:
        total_score += 10
    else:
        # 如果顺序错误但包含正确元素，可能已经扣了额外
        pass

    # 总分限制在 0-100
    total_score = max(0, min(100, total_score))

    result = {
        "total_score": total_score,
        "details": details
    }

    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification finished. Total score: {total_score}/100")
    return result

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
