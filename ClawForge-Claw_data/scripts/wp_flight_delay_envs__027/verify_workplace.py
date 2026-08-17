import json, os, sys

def verify(workspace: str):
    details = []
    total_score = 0

    # 检查 ops/affected_bookings.json 是否存在
    target_path = os.path.join(workspace, "ops", "affected_bookings.json")
    if not os.path.exists(target_path):
        details.append({"item": "target_file_exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/affected_bookings.json not found"})
    else:
        details.append({"item": "target_file_exists", "score": 10, "max_score": 10, "passed": True, "reason": "File exists"})
        total_score += 10

        # 解析 JSON
        try:
            with open(target_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            details.append({"item": "json_parse", "score": 0, "max_score": 10, "passed": False, "reason": f"Invalid JSON: {e}"})
            write_score(total_score, details, workspace)
            return

        details.append({"item": "json_parse", "score": 10, "max_score": 10, "passed": True, "reason": "Valid JSON"})
        total_score += 10

        # 必须是列表
        if not isinstance(data, list):
            details.append({"item": "data_structure", "score": 0, "max_score": 10, "passed": False, "reason": "Expected a JSON array (list)"})
        else:
            details.append({"item": "data_structure", "score": 10, "max_score": 10, "passed": True, "reason": "Data is a list"})
            total_score += 10

            # 预期：两个受影响预订：HB001, HB002 (酒店) 和 TB001, TB002 (交通)
            expected = [
                {"booking_type": "hotel", "booking_id": "HB001"},
                {"booking_type": "hotel", "booking_id": "HB002"},
                {"booking_type": "transport", "booking_id": "TB001"},
                {"booking_type": "transport", "booking_id": "TB002"},
            ]

            # 检查是否包含所有预期项，且无多余项（干扰项排除）
            actual_set = {(item.get("booking_type"), item.get("booking_id")) for item in data if isinstance(item, dict)}
            expected_set = {(e["booking_type"], e["booking_id"]) for e in expected}

            missing = expected_set - actual_set
            extra = actual_set - expected_set

            score_correctness = 0
            max_correctness = 60  # 核心部分
            if missing and extra:
                reason = f"Missing {len(missing)} expected items, extra {len(extra)} unexpected items"
            elif missing:
                reason = f"Missing {len(missing)} expected items: {missing}"
            elif extra:
                reason = f"Extra {len(extra)} unexpected items: {extra}"
            else:
                reason = "All expected items present, no extras"
                score_correctness = 60

            # 额外检查字段格式（booking_type必须是hotel或transport）
            format_ok = True
            for item in data:
                if not isinstance(item, dict) or "booking_type" not in item or "booking_id" not in item:
                    format_ok = False
                    break
                if item["booking_type"] not in ("hotel", "transport"):
                    format_ok = False
                    break

            if not format_ok:
                score_correctness = min(score_correctness, 30)  # 格式不合法降低分数
                reason += "; Format error in some entry (missing booking_type/booking_id or invalid type)"

            details.append({"item": "correctness_and_format", "score": score_correctness, "max_score": 60, "passed": score_correctness == 60, "reason": reason})
            total_score += score_correctness

    # 检查目录 ops 是否存在（即使文件存在已隐式证明，但单独列一项）
    ops_dir = os.path.join(workspace, "ops")
    if os.path.isdir(ops_dir):
        details.append({"item": "ops_dir_exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops directory exists"})
        total_score += 10
    else:
        details.append({"item": "ops_dir_exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops directory not found"})

    # 最终总分上限100
    total_score = min(total_score, 100)
    write_score(total_score, details, workspace)

def write_score(score, details, workspace):
    result = {"total_score": score, "details": details}
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
