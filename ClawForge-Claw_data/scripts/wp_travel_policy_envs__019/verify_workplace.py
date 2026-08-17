import os
import sys
import json
import math

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # 1. 检查 result.json 是否存在
    result_path = os.path.join(workspace, "result.json")
    if not os.path.isfile(result_path):
        score_details.append({
            "item": "result.json 文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件未找到"
        })
        # 直接写入评分结果并退出，因为后续无法进行
        write_final_score(total_score, score_details, workspace)
        return

    score_details.append({
        "item": "result.json 文件存在",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "文件存在"
    })

    # 2. 解析 JSON
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "result.json 是合法 JSON",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
    except Exception as e:
        score_details.append({
            "item": "result.json 是合法 JSON",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        write_final_score(total_score, score_details, workspace)
        return

    # 3. 检查 final_cost 字段存在且类型正确
    if "final_cost" not in data:
        score_details.append({
            "item": "包含 final_cost 字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到 final_cost 键"
        })
        write_final_score(sum(d["score"] for d in score_details), score_details, workspace)
        return

    final_cost = data["final_cost"]
    if not isinstance(final_cost, (int, float)):
        score_details.append({
            "item": "final_cost 数值类型",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"类型错误，应为 int 或 float，实际为 {type(final_cost).__name__}"
        })
        write_final_score(sum(d["score"] for d in score_details), score_details, workspace)
        return

    score_details.append({
        "item": "包含 final_cost 字段",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "字段存在"
    })
    score_details.append({
        "item": "final_cost 数值类型",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "类型正确"
    })

    # 4. 检查无多余字段（仅允许 final_cost）
    allowed_keys = {"final_cost"}
    additional_keys = set(data.keys()) - allowed_keys
    if additional_keys:
        score_details.append({
            "item": "无多余字段",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"存在多余键: {additional_keys}"
        })
    else:
        score_details.append({
            "item": "无多余字段",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "仅包含 final_cost"
        })

    # 5. 核心计算：预期最终成本
    # SkyBook 裸价 1300，transaction_fee 20，service_fee 10，促销减 50
    expected_cost = 1300 + 20 + 10 - 50   # = 1280
    # 允许浮点误差（但应为精确整数）
    if math.isclose(final_cost, expected_cost, rel_tol=1e-9):
        score_details.append({
            "item": "最终成本数值正确",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": f"计算正确，值为 {final_cost}"
        })
    else:
        score_details.append({
            "item": "最终成本数值正确",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": f"期望 {expected_cost}，实际 {final_cost}"
        })

    # 计算总分
    total_score = sum(d["score"] for d in score_details)
    write_final_score(total_score, score_details, workspace)

def write_final_score(total_score, details, workspace):
    output = {
        "total_score": total_score,
        "details": details
    }
    out_path = os.path.join(workspace, "workplace_score.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    # 打印到控制台以便调试
    print(f"Score: {total_score}/100")

if __name__ == "__main__":
    main()
