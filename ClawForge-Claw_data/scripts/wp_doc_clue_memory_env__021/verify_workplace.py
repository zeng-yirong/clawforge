import sys
import json
import os

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    details = []

    # ----------------------------------------------------------------------
    # 1. 目录结构检查 (10分)
    # ----------------------------------------------------------------------
    max_dir = 10
    required_dirs = ["reports", "presentations", "media_samples", "ops"]
    missing_dirs = [d for d in required_dirs if not os.path.isdir(os.path.join(workspace, d))]
    if missing_dirs:
        details.append({
            "item": "目录结构",
            "score": 0,
            "max_score": max_dir,
            "passed": False,
            "reason": f"缺失目录: {missing_dirs}"
        })
    else:
        details.append({
            "item": "目录结构",
            "score": max_dir,
            "max_score": max_dir,
            "passed": True,
            "reason": "所有必需目录存在"
        })
        total_score += max_dir

    # ----------------------------------------------------------------------
    # 2. 产物文件存在性 (10分)
    # ----------------------------------------------------------------------
    max_file = 10
    clue_path = os.path.join(workspace, "ops", "clue_list.json")
    if not os.path.isfile(clue_path):
        details.append({
            "item": "产物文件存在",
            "score": 0,
            "max_score": max_file,
            "passed": False,
            "reason": "ops/clue_list.json 不存在"
        })
        # early exit? We'll still try to load later but will fail.
    else:
        details.append({
            "item": "产物文件存在",
            "score": max_file,
            "max_score": max_file,
            "passed": True,
            "reason": "ops/clue_list.json 文件存在"
        })
        total_score += max_file

    # ----------------------------------------------------------------------
    # 3. JSON 合法性 (10分)
    # ----------------------------------------------------------------------
    max_json = 10
    clues = None
    if os.path.isfile(clue_path):
        try:
            with open(clue_path, "r") as f:
                clues = json.load(f)
            details.append({
                "item": "JSON 合法性",
                "score": max_json,
                "max_score": max_json,
                "passed": True,
                "reason": "合法 JSON，可解析"
            })
            total_score += max_json
        except (json.JSONDecodeError, Exception) as e:
            details.append({
                "item": "JSON 合法性",
                "score": 0,
                "max_score": max_json,
                "passed": False,
                "reason": f"JSON 解析失败: {str(e)}"
            })
    else:
        details.append({
            "item": "JSON 合法性",
            "score": 0,
            "max_score": max_json,
            "passed": False,
            "reason": "文件不存在，无法检查"
        })

    # ----------------------------------------------------------------------
    # 4. 字段完整性 (10分)
    # ----------------------------------------------------------------------
    max_field = 10
    field_ok = False
    if clues is not None and isinstance(clues, dict):
        # 期待顶层键，可以是 "clues" 或其他，但必须包含列表
        # 灵活检查：只要有列表且元素包含 id 和 summary
        clue_list = None
        for key in clues:
            if isinstance(clues[key], list):
                clue_list = clues[key]
                break
        if clue_list is None:
            details.append({
                "item": "字段完整性",
                "score": 0,
                "max_score": max_field,
                "passed": False,
                "reason": "JSON 中没有包含条目列表的键"
            })
        else:
            all_have_id = all(isinstance(item.get("id"), str) for item in clue_list)
            all_have_summary = all(isinstance(item.get("summary"), str) for item in clue_list)
            if all_have_id and all_have_summary:
                field_ok = True
                details.append({
                    "item": "字段完整性",
                    "score": max_field,
                    "max_score": max_field,
                    "passed": True,
                    "reason": "每个条目包含 id 和 summary 字符串字段"
                })
                total_score += max_field
            else:
                details.append({
                    "item": "字段完整性",
                    "score": 0,
                    "max_score": max_field,
                    "passed": False,
                    "reason": "条目缺少 id 或 summary 字段或类型错误"
                })
    else:
        details.append({
            "item": "字段完整性",
            "score": 0,
            "max_score": max_field,
            "passed": False,
            "reason": "JSON 不是 dict 或为空"
        })

    # ----------------------------------------------------------------------
    # 5. 核心内容匹配 (50分)
    # ----------------------------------------------------------------------
    max_core = 50
    if field_ok and clue_list is not None:
        # 预期答案：三个 active 文档包含 HelioSync Edge Inference Fabric
        # RPT-101, PRES-001, MED-007
        expected = [
            {"id": "RPT-101", "summary": "Early benchmark results for HelioSync Edge Inference Fabric show 40% latency reduction."},
            {"id": "PRES-001", "summary": "Slides covering HelioSync Edge Inference Fabric go-to-market strategy."},
            {"id": "MED-007", "summary": "Interview with engineer about HelioSync Edge Inference Fabric architecture."}
        ]
        # 从 agent 结果中提取 (id, summary) 对，排序后比较
        agent_items = sorted([(item["id"], item["summary"]) for item in clue_list])
        expected_items = sorted([(e["id"], e["summary"]) for e in expected])
        if agent_items == expected_items:
            details.append({
                "item": "核心内容匹配",
                "score": max_core,
                "max_score": max_core,
                "passed": True,
                "reason": "成功识别所有有效文档，且不含干扰项"
            })
            total_score += max_core
        else:
            # 给出具体差异
            agent_set = set(agent_items)
            expected_set = set(expected_items)
            missing = expected_set - agent_set
            extra = agent_set - expected_set
            reason = ""
            if missing:
                reason += f"缺失: {[m[0] for m in missing]}; "
            if extra:
                reason += f"多余: {[e[0] for e in extra]}; "
            details.append({
                "item": "核心内容匹配",
                "score": 0,
                "max_score": max_core,
                "passed": False,
                "reason": f"结果不匹配。{reason}agent结果共{len(agent_items)}条"
            })
    else:
        details.append({
            "item": "核心内容匹配",
            "score": 0,
            "max_score": max_core,
            "passed": False,
            "reason": "前置检查失败，无法执行内容匹配"
        })

    # ----------------------------------------------------------------------
    # 6. 干扰排除检查 (10分)
    #   额外检查：是否包含了 archived 或近似记录的条目
    # ----------------------------------------------------------------------
    max_noise = 10
    if field_ok and clue_list is not None:
        # 捕获不应出现的 ID
        forbidden_ids = {"RPT-202", "RPT-303", "PRES-022", "PRES-103", "MED-012", "MED-019"}
        agent_ids = {item["id"] for item in clue_list}
        overlapped = agent_ids & forbidden_ids
        if len(overlapped) == 0:
            details.append({
                "item": "干扰排除",
                "score": max_noise,
                "max_score": max_noise,
                "passed": True,
                "reason": "未包含任何被排除的文档"
            })
            total_score += max_noise
        else:
            details.append({
                "item": "干扰排除",
                "score": 0,
                "max_score": max_noise,
                "passed": False,
                "reason": f"包含了不应出现的文档 ID: {overlapped}"
            })
    else:
        details.append({
            "item": "干扰排除",
            "score": 0,
            "max_score": max_noise,
            "passed": False,
            "reason": "前置检查失败，无法评估"
        })

    # ----------------------------------------------------------------------
    # 写入评分文件
    # ----------------------------------------------------------------------
    result = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Score: {total_score}/100")
    return total_score

if __name__ == "__main__":
    main()
