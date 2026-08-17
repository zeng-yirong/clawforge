import os
import sys
import json
import csv

def verify(workspace):
    details = []
    total_score = 0

    # 1. 检查ops目录是否存在 (10分)
    ops_path = os.path.join(workspace, "ops")
    item = {"item": "ops目录存在", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if os.path.isdir(ops_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "ops目录已存在"
    else:
        item["reason"] = "ops目录不存在"
    details.append(item)
    total_score += item["score"]

    # 2. 检查预期输出文件是否存在 (10分)
    graph_path = os.path.join(ops_path, "citation_graph.json")
    item = {"item": "citation_graph.json文件存在", "max_score": 10, "score": 0, "passed": False, "reason": ""}
    if os.path.isfile(graph_path):
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "文件存在"
    else:
        item["reason"] = f"文件 {graph_path} 不存在"
    details.append(item)
    total_score += item["score"]

    # 如果文件存在，继续检查内容
    if os.path.isfile(graph_path):
        try:
            with open(graph_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            data = None
            item = {"item": "JSON格式合法", "max_score": 10, "score": 0, "passed": False, "reason": f"JSON解析失败: {e}"}
            details.append(item)
            total_score += 0
            # 因为无法继续，直接返回
            write_score(workspace, total_score, details)
            return

        # 3. JSON格式合法 (10分)
        item = {"item": "JSON格式合法", "max_score": 10, "score": 10, "passed": True, "reason": "JSON解析成功"}
        details.append(item)
        total_score += 10

        # 4. 检查结构是否为包含edges的字典 (10分)
        item = {"item": "包含edges键", "max_score": 10, "score": 0, "passed": False, "reason": ""}
        if isinstance(data, dict) and "edges" in data:
            edges = data["edges"]
            if isinstance(edges, list):
                item["score"] = 10
                item["passed"] = True
                item["reason"] = f"edges是列表，长度{len(edges)}"
            else:
                item["reason"] = "edges不是列表"
        else:
            edges = None
            item["reason"] = "缺少edges键或数据不是字典"
        details.append(item)
        total_score += item["score"]

        if edges is None:
            # 无法继续
            write_score(workspace, total_score, details)
            return

        # 5. 检查每条边格式 (每条边必须包含source和target字符串) (10分)
        all_edges_valid = True
        for i, edge in enumerate(edges):
            if not isinstance(edge, dict) or "source" not in edge or "target" not in edge:
                all_edges_valid = False
                break
            if not isinstance(edge["source"], str) or not isinstance(edge["target"], str):
                all_edges_valid = False
                break
        item = {"item": "所有边格式正确", "max_score": 10, "score": 10 if all_edges_valid else 0, "passed": all_edges_valid, "reason": "格式正确" if all_edges_valid else "存在格式错误的边"}
        details.append(item)
        total_score += item["score"]

        # 6. 边的唯一性和正确性 (40分)
        # 期望只有以下三条有效边（去重后，且过滤无效引用）
        expected_edges = [
            {"source": "paper_001", "target": "paper_002"},
            {"source": "paper_001", "target": "paper_003"},
            {"source": "paper_002", "target": "paper_001"}
        ]
        # 规范化：按source升序，同source按target升序排序
        sorted_edges = sorted(edges, key=lambda e: (e["source"], e["target"]))
        # 去重：检查是否有重复边（同source+target）
        seen_pairs = set()
        deduped_edges = []
        for e in sorted_edges:
            pair = (e["source"], e["target"])
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                deduped_edges.append(e)
        # 比较
        expected_sorted = sorted(expected_edges, key=lambda e: (e["source"], e["target"]))
        edge_match = (len(deduped_edges) == len(expected_sorted))
        if edge_match:
            for e_actual, e_expected in zip(deduped_edges, expected_sorted):
                if e_actual["source"] != e_expected["source"] or e_actual["target"] != e_expected["target"]:
                    edge_match = False
                    break
        if edge_match:
            item = {"item": "边列表正确（数量、内容、排序、去重）", "max_score": 40, "score": 40, "passed": True, "reason": "完全匹配期望的三条边"}
        else:
            # 部分得分：每正确一条边给13分（最多39），但需要扣去重复或错误
            correct_count = 0
            expected_set = {(e["source"], e["target"]) for e in expected_sorted}
            actual_set = seen_pairs
            correct_pairs = actual_set & expected_set
            correct_count = len(correct_pairs)
            # 额外扣分：多余边扣分，但最多扣到0
            extra = actual_set - expected_set
            missing = expected_set - actual_set
            score = max(0, correct_count * 13 - len(extra) * 5)  # 每条正确13，错误边扣5，最多40
            score = min(score, 40)
            item = {"item": "边列表部分正确", "max_score": 40, "score": score, "passed": False, "reason": f"正确{correct_count}条，多余{len(extra)}条，缺失{len(missing)}条"}
        details.append(item)
        total_score += item["score"]

        # 7. 检查是否引入了不存在的论文ID（如paper_004）作为边 - 额外的惩罚项，可扣分但总分不超出0
        # 在上面已经通过正确性检查体现

    else:
        # 文件不存在，跳过后续检查，总分已包含
        pass

    # 写入评分
    write_score(workspace, total_score, details)

def write_score(workspace, total_score, details):
    score_data = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w") as f:
        json.dump(score_data, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
