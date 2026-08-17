"""
verifier for reproduction ledger task (wp_reproduction_ledger_env__018)
reads workspace from first argument, checks expected output file and content.
"""
import sys
import json
import os
from pathlib import Path

def verify(workspace: str) -> dict:
    details = []
    ws = Path(workspace).resolve()

    # 1. 检查 ledger 目录是否存在
    ledger_dir = ws / "ledger"
    item1 = {
        "item": "ledger 目录存在",
        "max_score": 10,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    if ledger_dir.is_dir():
        item1["score"] = 10
        item1["passed"] = True
        item1["reason"] = "ledger/ 目录已创建"
    else:
        item1["reason"] = "ledger/ 目录未找到"
    details.append(item1)

    # 2. 检查 archived_ledger.json 文件存在且是合法 JSON
    target_file = ledger_dir / "archived_ledger.json"
    item2 = {
        "item": "archived_ledger.json 文件存在且为合法 JSON",
        "max_score": 10,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    data = None
    if target_file.is_file():
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            item2["score"] = 10
            item2["passed"] = True
            item2["reason"] = "文件存在且 JSON 解析成功"
        except (json.JSONDecodeError, UnicodeDecodeError):
            item2["reason"] = "文件存在但 JSON 解析失败"
    else:
        item2["reason"] = "文件不存在"
    details.append(item2)

    # 如果数据未加载，直接返回，避免后续错误
    if data is None:
        total = sum(d["score"] for d in details)
        return {"total_score": total, "details": details}

    # 3. 检查必需字段是否存在 (project_id, doc_id, steps, result)
    required_fields = ["project_id", "doc_id", "steps", "result"]
    missing_fields = [f for f in required_fields if f not in data]
    extra_fields = [k for k in data.keys() if k not in required_fields]
    item3 = {
        "item": "必需字段完整（project_id, doc_id, steps, result）",
        "max_score": 10,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    if not missing_fields:
        item3["score"] = 10
        item3["passed"] = True
        item3["reason"] = "所有必需字段均存在"
        if extra_fields:
            item3["reason"] += f"；但是发现额外字段: {extra_fields}（不扣分，仅提醒）"
    else:
        item3["reason"] = f"缺失字段: {missing_fields}"
    details.append(item3)

    # 4. 检查 project_id 是否为 proj-018
    item4 = {
        "item": "project_id 为 proj-018",
        "max_score": 10,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    proj = data.get("project_id")
    if proj == "proj-018":
        item4["score"] = 10
        item4["passed"] = True
        item4["reason"] = f"project_id 正确: {proj}"
    else:
        item4["reason"] = f"预期 proj-018，实际为 {proj}"
    details.append(item4)

    # 5. 检查 doc_id 是否为 doc-001（目标文档的 doc_id）
    item5 = {
        "item": "doc_id 为 doc-001",
        "max_score": 10,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    doc_id = data.get("doc_id")
    if doc_id == "doc-001":
        item5["score"] = 10
        item5["passed"] = True
        item5["reason"] = f"doc_id 正确: {doc_id}"
    else:
        item5["reason"] = f"预期 doc-001，实际为 {doc_id}"
    details.append(item5)

    # 6. 检查 steps 是否与目标文档完全一致（列表逐元素比较）
    expected_steps = [
        "1. 配置 Python 3.10 环境并安装 requirements.txt",
        "2. 下载模型权重 v2.1 至 ./weights/",
        "3. 运行 preprocessing_script.sh --input data/raw --output data/clean",
        "4. 执行训练脚本: python train.py --config configs/proj018.yaml",
        "5. 验证损失曲线收敛至 0.023 以下",
        "6. 输出来自测试集的 F1-score: 0.912"
    ]
    item6 = {
        "item": "steps 字段内容与原始文档完全一致",
        "max_score": 30,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    actual_steps = data.get("steps")
    if isinstance(actual_steps, list) and len(actual_steps) == len(expected_steps):
        if all(a == b for a, b in zip(actual_steps, expected_steps)):
            item6["score"] = 30
            item6["passed"] = True
            item6["reason"] = "steps 内容完全匹配"
        else:
            item6["reason"] = "steps 长度一致但内容不完全匹配"
            # 给出差异提示
            diffs = []
            for i, (a, e) in enumerate(zip(actual_steps, expected_steps)):
                if a != e:
                    diffs.append(f"step {i+1}: 预期 '{e[:30]}...'，实际 '{a[:30]}...'")
            item6["reason"] += "; " + "; ".join(diffs[:3])  # 只显示前三个
    else:
        if not isinstance(actual_steps, list):
            item6["reason"] = "steps 不是列表"
        else:
            item6["reason"] = f"steps 长度 {len(actual_steps)}，预期 {len(expected_steps)}"
    details.append(item6)

    # 7. 检查 result 字段是否与原始文档一致
    expected_result = "成功复现模型 v2，最终 F1 分数 0.912，符合论文预期。"
    item7 = {
        "item": "result 字段内容与原始文档一致",
        "max_score": 20,
        "score": 0,
        "passed": False,
        "reason": ""
    }
    actual_result = data.get("result")
    if actual_result == expected_result:
        item7["score"] = 20
        item7["passed"] = True
        item7["reason"] = "result 内容完全匹配"
    else:
        item7["reason"] = f"预期 '{expected_result[:40]}...'，实际 '{str(actual_result)[:40]}...'"
    details.append(item7)

    # 计算总分
    total = sum(d["score"] for d in details)
    # 确保总分不超过 100
    total = min(total, 100)
    return {"total_score": total, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    output_path = Path(workspace) / "workplace_score.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Score written to {output_path}: {result['total_score']}")

if __name__ == "__main__":
    main()
