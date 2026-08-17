import sys
import os
import json

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    max_total = 100
    details = []

    # ---------- 1. 目录结构检查 (10分) ----------
    required_dirs = [
        "reproduction_ledger"
    ]
    all_dirs_exist = True
    for d in required_dirs:
        if not os.path.isdir(os.path.join(workspace, d)):
            all_dirs_exist = False
            details.append({"item": f"目录 {d} 存在", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少目录 {d}"})
            break
    if all_dirs_exist:
        # 检查结果文件是否在 expected 路径
        result_path = os.path.join(workspace, "reproduction_ledger", "proj-007_ledger.json")
        if os.path.isfile(result_path):
            details.append({"item": "目录结构正确且结果文件存在", "score": 10, "max_score": 10, "passed": True, "reason": "reproduction_ledger 目录及结果文件存在"})
        else:
            details.append({"item": "目录结构正确但结果文件缺失", "score": 0, "max_score": 10, "passed": False, "reason": "reproduction_ledger/proj-007_ledger.json 不存在"})

    # ---------- 2. 格式合法性 (10分) ----------
    result_path = os.path.join(workspace, "reproduction_ledger", "proj-007_ledger.json")
    if not os.path.isfile(result_path):
        details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "结果文件不存在"})
        # 后续检查跳过
    else:
        try:
            with open(result_path, "r") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("结果不是 JSON 对象")
            details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "可解析为 JSON 对象"})
        except Exception as e:
            details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {str(e)}"})
            # 后续检查跳过
            compute_score_and_exit(score, details, max_total)
            return

    # ---------- 3. 字段完整性 (10分) ----------
    required_fields = ["project_id", "doc_ids", "steps"]
    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        details.append({"item": "必要字段完整", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少字段: {', '.join(missing_fields)}"})
    else:
        details.append({"item": "必要字段完整", "score": 10, "max_score": 10, "passed": True, "reason": "project_id, doc_ids, steps 均存在"})

    # ---------- 4. 剔除脏数据 — 只包含 proj-007 的 doc_ids (20分) ----------
    # 先读取原始 project_docs.json 获取 proj-007 的真实 doc_ids
    proj_docs_path = os.path.join(workspace, "data", "projects", "project_docs.json")
    if not os.path.isfile(proj_docs_path):
        details.append({"item": "doc_ids 仅包含 proj-007 文档", "score": 0, "max_score": 20, "passed": False, "reason": "project_docs.json 不存在"})
    else:
        try:
            with open(proj_docs_path) as f:
                proj_docs_data = json.load(f)
            proj_docs_list = proj_docs_data.get("project_docs", [])
            expected_doc_ids = set(doc["doc_id"] for doc in proj_docs_list if doc["project_id"] == "proj-007")
        except Exception:
            details.append({"item": "doc_ids 仅包含 proj-007 文档", "score": 0, "max_score": 20, "passed": False, "reason": "解析 project_docs.json 失败"})
            compute_score_and_exit(score, details, max_total)
            return

        actual_doc_ids = set(data.get("doc_ids", []))
        if actual_doc_ids == expected_doc_ids:
            details.append({"item": "doc_ids 仅包含 proj-007 文档", "score": 20, "max_score": 20, "passed": True, "reason": "文档 ID 集合完全匹配"})
        else:
            extra = actual_doc_ids - expected_doc_ids
            missing = expected_doc_ids - actual_doc_ids
            reason_parts = []
            if extra:
                reason_parts.append(f"多出了不属于 proj-007 的 doc_id: {extra}")
            if missing:
                reason_parts.append(f"缺少应有的 doc_id: {missing}")
            details.append({"item": "doc_ids 仅包含 proj-007 文档", "score": 0, "max_score": 20, "passed": False, "reason": "; ".join(reason_parts)})

    # ---------- 5. 步骤去重排序正确性 (40分) ----------
    # 从所有 proj-007 文档中加载步骤，去重排序
    expected_steps = set()
    proj_docs_path = os.path.join(workspace, "data", "projects", "project_docs.json")
    try:
        with open(proj_docs_path) as f:
            proj_docs_data = json.load(f)
        proj_docs_list = proj_docs_data.get("project_docs", [])
        for doc in proj_docs_list:
            if doc["project_id"] == "proj-007":
                doc_path = os.path.join(workspace, doc["path"])
                if os.path.isfile(doc_path):
                    with open(doc_path) as df:
                        doc_content = json.load(df)
                    for step in doc_content.get("steps", []):
                        expected_steps.add(step)
    except Exception as e:
        details.append({"item": "步骤去重排序正确", "score": 0, "max_score": 40, "passed": False, "reason": f"无法从原始文档加载步骤: {str(e)}"})
        compute_score_and_exit(score, details, max_total)
        return

    sorted_expected = sorted(expected_steps)
    actual_steps = data.get("steps", [])
    if not isinstance(actual_steps, list):
        details.append({"item": "步骤去重排序正确", "score": 0, "max_score": 40, "passed": False, "reason": "steps 不是列表"})
    else:
        if actual_steps == sorted_expected:
            details.append({"item": "步骤去重排序正确", "score": 40, "max_score": 40, "passed": True, "reason": "步骤列表完全一致（去重+排序）"})
        else:
            # 部分正确：给部分分（比如 20 分如果集合相同但顺序不对，或集合不同但部分重合）
            actual_set = set(actual_steps)
            if actual_set == expected_steps and actual_steps != sorted_expected:
                details.append({"item": "步骤去重排序正确", "score": 20, "max_score": 40, "passed": False, "reason": "步骤集合正确但未按字母顺序排序"})
            else:
                missing_steps = expected_steps - actual_set
                extra_steps = actual_set - expected_steps
                reason = []
                if missing_steps:
                    reason.append(f"缺少步骤: {missing_steps}")
                if extra_steps:
                    reason.append(f"多余步骤: {extra_steps}")
                details.append({"item": "步骤去重排序正确", "score": 0, "max_score": 40, "passed": False, "reason": "; ".join(reason)})

    # ---------- 6. project_id 正确性 (10分) ----------
    if data.get("project_id") == "proj-007":
        details.append({"item": "project_id 正确", "score": 10, "max_score": 10, "passed": True, "reason": "project_id 为 proj-007"})
    else:
        details.append({"item": "project_id 正确", "score": 0, "max_score": 10, "passed": False, "reason": f"期望 proj-007，实际为 {data.get('project_id')}"})

    # 计算总分
    total = sum(item["score"] for item in details)
    # 写入结果
    output = {
        "total_score": total,
        "details": details
    }
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score: {total}/{max_total}")
    sys.exit(0 if total == max_total else 1)


def compute_score_and_exit(prev_score, details, max_total):
    total = sum(item["score"] for item in details)
    output = {"total_score": total, "details": details}
    output_path = os.path.join(workspace if 'workspace' in dir() else ".", "workplace_score.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Score: {total}/{max_total}")
    sys.exit(1)


if __name__ == "__main__":
    main()
