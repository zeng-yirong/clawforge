import sys
import json
import os
from pathlib import Path

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    root = Path(workspace)

    score_details = []

    # 1. 检查 ops/booking_request.json 是否存在 (10分)
    req_path = root / "ops" / "booking_request.json"
    if req_path.exists():
        score_details.append({"item": "输出文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "ops/booking_request.json 存在"})
    else:
        score_details.append({"item": "输出文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ops/booking_request.json"})
        # 若文件不存在，后续无法检查，直接返回
        total = sum(d["score"] for d in score_details)
        out = {"total_score": total, "details": score_details}
        with open(root / "workplace_score.json", "w") as f:
            json.dump(out, f, indent=2)
        return

    # 2. JSON 格式合法 (10分)
    try:
        with open(req_path) as f:
            data = json.load(f)
        score_details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "能正常解析"})
    except Exception as e:
        score_details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
        total = sum(d["score"] for d in score_details)
        out = {"total_score": total, "details": score_details}
        with open(root / "workplace_score.json", "w") as f:
            json.dump(out, f, indent=2)
        return

    # 3. 必要字段存在 (15分)
    required_fields = ["flight_id", "platform", "origin", "destination", "date", "cabin_class", "total_cost", "requires_approval"]
    missing = [f for f in required_fields if f not in data]
    if not missing:
        score_details.append({"item": "必要字段完整", "score": 15, "max_score": 15, "passed": True, "reason": "所有必需字段都存在"})
    else:
        score_details.append({"item": "必要字段完整", "score": 0, "max_score": 15, "passed": False, "reason": f"缺少字段: {missing}"})

    # 4. flight_id 在正确平台中存在 (15分)
    flight_id = data.get("flight_id")
    platform_name = data.get("platform", "").lower()
    # 映射平台名称到文件名
    platform_files = {
        "aero cheap": "aero_cheap.json",
        "aerocheap": "aero_cheap.json",
        "aero_cheap": "aero_cheap.json",
        "flight pro": "flight_pro.json",
        "flightpro": "flight_pro.json",
        "flight_pro": "flight_pro.json",
        "sky book": "sky_book.json",
        "skybook": "sky_book.json",
        "sky_book": "sky_book.json"
    }
    # 规范化平台名
    normalized_platform = platform_files.get(platform_name, None)
    if normalized_platform is None:
        # 检查是否包含关键字
        for key in platform_files:
            if key in platform_name or platform_name in key:
                normalized_platform = platform_files[key]
                break
    if normalized_platform is None:
        score_details.append({"item": "平台识别", "score": 0, "max_score": 15, "passed": False, "reason": f"无法识别的平台名: {platform_name}"})
    else:
        platform_path = root / "data" / "platforms" / normalized_platform
        if platform_path.exists():
            with open(platform_path) as pf:
                platform_data = json.load(pf)
            flights = platform_data.get("flights", [])
            found = any(f.get("flight_id") == flight_id for f in flights)
            if found:
                score_details.append({"item": "flight_id有效", "score": 15, "max_score": 15, "passed": True, "reason": f"flight_id {flight_id} 存在于 {normalized_platform}"})
            else:
                score_details.append({"item": "flight_id有效", "score": 0, "max_score": 15, "passed": False, "reason": f"flight_id {flight_id} 未在 {normalized_platform} 的航班列表中找到"})
        else:
            score_details.append({"item": "平台文件存在", "score": 0, "max_score": 15, "passed": False, "reason": f"对应的平台文件 {normalized_platform} 不存在"})

    # 5. total_cost 精确正确 (25分)
    expected_total = 1850.0  # AeroCheap: 1800 + 30 + 20
    actual_total = data.get("total_cost")
    if isinstance(actual_total, (int, float)) and abs(actual_total - expected_total) < 0.01:
        score_details.append({"item": "总价正确", "score": 25, "max_score": 25, "passed": True, "reason": f"total_cost={actual_total}, 预期{expected_total}"})
    else:
        score_details.append({"item": "总价正确", "score": 0, "max_score": 25, "passed": False, "reason": f"total_cost={actual_total}, 预期{expected_total}"})

    # 6. requires_approval 正确 (15分)
    if data.get("requires_approval") == True:
        score_details.append({"item": "审批标记正确", "score": 15, "max_score": 15, "passed": True, "reason": "requires_approval 为 true"})
    else:
        score_details.append({"item": "审批标记正确", "score": 0, "max_score": 15, "passed": False, "reason": f"requires_approval 应为 true，实际为 {data.get('requires_approval')}"})

    # 7. 没有多余无关字段 (10分)
    allowed_fields = set(required_fields)
    extra = [k for k in data if k not in allowed_fields]
    if not extra:
        score_details.append({"item": "无多余字段", "score": 10, "max_score": 10, "passed": True, "reason": "没有发现多余字段"})
    else:
        score_details.append({"item": "无多余字段", "score": 0, "max_score": 10, "passed": False, "reason": f"存在多余字段: {extra}"})

    # 汇总总分
    total = sum(d["score"] for d in score_details)
    # 确保总分不超过100
    total = min(total, 100)
    out = {
        "total_score": total,
        "details": score_details
    }
    with open(root / "workplace_score.json", "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    verify()
