import sys
import os
import json

def verify_workplace(workspace: str):
    score_details = []
    total_score = 0

    # 1. 检查 cache 目录是否存在
    cache_dir = os.path.join(workspace, "cache")
    if os.path.isdir(cache_dir):
        score_details.append({
            "item": "cache directory存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "cache目录已创建"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "cache directory存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "cache目录不存在"
        })

    # 2. 检查 citation_graph.json 是否存在
    graph_path = os.path.join(cache_dir, "citation_graph.json")
    if os.path.isfile(graph_path):
        score_details.append({
            "item": "citation_graph.json文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"文件存在于 {graph_path}"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "citation_graph.json文件存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 后续检查无法进行，直接结束
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 3. 解析 JSON 合法性
    try:
        with open(graph_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "成功解析"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "JSON格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 4. 验证 nodes 部分
    nodes = data.get("nodes", [])
    expected_nodes = [
        {"paper_id": "P001", "title": "Attention Is All You Need"},
        {"paper_id": "P002", "title": "BERT"},
        {"paper_id": "P003", "title": "GPT"},
        {"paper_id": "P004", "title": "ResNet"},
        {"paper_id": "P005", "title": "CNN"},
        {"paper_id": "P006", "title": "LSTM"}
    ]
    # 检查数量
    if len(nodes) != len(expected_nodes):
        score_details.append({
            "item": "节点数量正确",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望{len(expected_nodes)}个节点，实得{len(nodes)}个"
        })
    else:
        # 排序后比较（要求按paper_id排序）
        nodes_sorted = sorted(nodes, key=lambda x: x["paper_id"])
        expected_sorted = sorted(expected_nodes, key=lambda x: x["paper_id"])
        if nodes_sorted == expected_sorted:
            score_details.append({
                "item": "节点内容正确（数量、ID、标题、顺序）",
                "score": 20,
                "max_score": 20,
                "passed": True,
                "reason": "所有节点匹配预期"
            })
            total_score += 20
        else:
            score_details.append({
                "item": "节点内容正确",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": f"节点不匹配：\n得到{nodes_sorted}\n预期{expected_sorted}"
            })

    # 5. 验证 edges 部分
    edges = data.get("edges", [])
    expected_edges = [
        {"source": "P001", "target": "P002"},
        {"source": "P001", "target": "P003"},
        {"source": "P002", "target": "P004"},
        {"source": "P002", "target": "P005"},
        {"source": "P003", "target": "P006"},
        {"source": "P004", "target": "P001"}
    ]
    # 排序后比较
    edges_sorted = sorted(edges, key=lambda x: (x["source"], x["target"]))
    expected_edges_sorted = sorted(expected_edges, key=lambda x: (x["source"], x["target"]))
    if edges_sorted == expected_edges_sorted:
        score_details.append({
            "item": "边正确（数量、源、目标、顺序）",
            "score": 40,
            "max_score": 40,
            "passed": True,
            "reason": "所有边匹配预期"
        })
        total_score += 40
    else:
        # 部分得分：数量正确给一半
        if len(edges) == len(expected_edges):
            base = 20
            reason = f"边数量正确，但内容有差异"
        else:
            base = 0
            reason = f"边数量不匹配：期望{len(expected_edges)}，实得{len(edges)}"
        score_details.append({
            "item": "边正确",
            "score": base,
            "max_score": 40,
            "passed": False,
            "reason": reason + f"\n得到{edges_sorted}\n预期{expected_edges_sorted}"
        })
        total_score += base

    # 写入总分
    total_score = min(total_score, 100)
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace)
