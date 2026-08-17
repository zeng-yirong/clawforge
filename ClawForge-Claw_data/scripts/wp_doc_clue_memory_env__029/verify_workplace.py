import sys
import os
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    # ---------- 1. 检查 clues.json 是否存在 ----------
    clues_path = os.path.join(workspace, "clues.json")
    if os.path.isfile(clues_path):
        score_details.append({
            "item": "clues.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "clues.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "未找到 clues.json"
        })
        # 如果文件不存在，后续检查无法进行，直接输出
        return finalize(score_details, total_score)

    # ---------- 2. 解析 JSON 合法性 ----------
    try:
        with open(clues_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "可正常解析"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {str(e)}"
        })
        return finalize(score_details, total_score)

    # ---------- 3. 类型与结构检查 ----------
    if not isinstance(data, dict):
        score_details.append({
            "item": "顶层结构应为字典",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "顶层不是 dict"
        })
        total_score += 0
        # 继续后续检查可能会报错，谨慎进行
    else:
        # 检查是否包含预期的 4 个 key（文档 ID）
        expected_ids = {"rpt-021", "rpt-045", "pres-010", "med-003"}
        actual_ids = set(data.keys())
        if actual_ids == expected_ids:
            score_details.append({
                "item": "文档 ID 完全匹配预期（4个）",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "包含且仅包含正确的 4 个 ID"
            })
            total_score += 20
        else:
            # 部分匹配，部分扣除
            extra = actual_ids - expected_ids
            missing = expected_ids - actual_ids
            reasons = []
            if extra:
                reasons.append(f"多余 ID: {extra}")
            if missing:
                reasons.append(f"缺少 ID: {missing}")
            score_details.append({
                "item": "文档 ID 完全匹配预期（4个）",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "; ".join(reasons)
            })
            total_score += 0

        # ---------- 4. 每个文档的线索内容正确性 ----------
        expected_clues = {
            "rpt-021": "HelioSync 架构在5ms延迟内实现了边缘推理，适用于工业质检场景。",
            "rpt-045": "案例研究显示HelioSync在物流分拣中降低了30%的延迟。",
            "pres-010": "面向合作伙伴的HelioSync发布演示，涵盖架构与路线图。",
            "med-003": "讨论了HelioSync在工业边缘场景下的部署难点与收益。"
        }
        for doc_id, expected_clue in expected_clues.items():
            if doc_id in data:
                actual_clue = data[doc_id]
                if isinstance(actual_clue, str) and actual_clue == expected_clue:
                    score_details.append({
                        "item": f"线索值 - {doc_id}",
                        "score": 15,
                        "max_score": 15,
                        "passed": True,
                        "reason": "内容精确匹配"
                    })
                    total_score += 15
                else:
                    # 仍然给部分分？这里全扣，梯度已经体现在单项满分上
                    score_details.append({
                        "item": f"线索值 - {doc_id}",
                        "score": 0,
                        "max_score": 15,
                        "passed": False,
                        "reason": f"实际值: {repr(actual_clue)}，期望: {repr(expected_clue)}"
                    })
                    total_score += 0
            else:
                score_details.append({
                    "item": f"线索值 - {doc_id}",
                    "score": 0,
                    "max_score": 15,
                    "passed": False,
                    "reason": "ID 缺失，无法检查线索"
                })
                total_score += 0

        # ---------- 5. 无多余 ID 引起的额外扣分（已在步骤3中处理，但可以单独加分） ----------
        # 如果步骤3已经给了20分，说明无多余无缺；否则这里不再重复加分

    return finalize(score_details, total_score)

def finalize(details, total):
    # 写入 workplace_score.json
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(result)
    return result

if __name__ == "__main__":
    verify()
