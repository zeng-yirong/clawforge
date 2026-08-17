import os
import sys
import json
import pathlib

def verify(workspace: str):
    score_details = []
    total_score = 0

    # -------------------- 检查目录 & 文件存在 --------------------
    # item 1: ops/archived_reproduction_ledger.json 存在
    ledger_path = os.path.join(workspace, "ops", "archived_reproduction_ledger.json")
    if os.path.isfile(ledger_path):
        score_details.append({
            "item": "产物文件 ops/archived_reproduction_ledger.json 存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "文件存在"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "产物文件 ops/archived_reproduction_ledger.json 存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "文件不存在"
        })
        # 文件不存在则直接结束，后面无法检查
        final_score = {"total_score": total_score, "details": score_details}
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump(final_score, f, indent=2)
        return

    # -------------------- 检查 JSON 合法性 --------------------
    try:
        with open(ledger_path, "r") as f:
            data = json.load(f)
        score_details.append({
            "item": "JSON 格式合法",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 10
    except Exception as e:
        score_details.append({
            "item": "JSON 格式合法",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"解析失败: {e}"
        })
        # 仍然继续尝试部分检查
        data = None

    # -------------------- 检查内容结构 --------------------
    if data is None:
        # 无法继续
        pass
    else:
        # 必须是列表
        if isinstance(data, list):
            score_details.append({
                "item": "顶层结构为列表",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": "是列表"
            })
            total_score += 10
        else:
            score_details.append({
                "item": "顶层结构为列表",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"实际类型: {type(data).__name__}"
            })

        # 长度应为3（对应 3 条日志记录）
        expected_len = 3
        if len(data) == expected_len:
            score_details.append({
                "item": "列表长度等于日志记录数（3）",
                "score": 15,
                "max_score": 15,
                "passed": True,
                "reason": f"长度为 {len(data)}"
            })
            total_score += 15
        else:
            score_details.append({
                "item": "列表长度等于日志记录数（3）",
                "score": 0,
                "max_score": 15,
                "passed": False,
                "reason": f"实际长度 {len(data)}，期望 3"
            })

        # 每个元素必须包含关键字段，并精确匹配答案
        # 答案映射：doc_id -> expected
        expected_map = {
            "doc-001": {"project_id": "proj-alpha", "title": "Setup Guide", "status": "success", "error": None},
            "doc-002": {"project_id": "proj-beta", "title": "API Reference", "status": "success", "error": None},
            "doc-003": {"project_id": "proj-gamma", "title": "Troubleshooting FAQ", "status": "failed", "error": "missing dependency"}
        }

        # 检查每个条目
        field_score_per_item = 15  # 3个条目，每个15分，合计45分
        for rec in data:
            doc_id = rec.get("doc_id")
            if doc_id not in expected_map:
                # 多余文档，扣分（但上面长度已经限制了，这里不再额外扣）
                continue
            exp = expected_map[doc_id]
            item_ok = True
            reason_parts = []
            # 检查 project_id
            if rec.get("project_id") != exp["project_id"]:
                item_ok = False
                reason_parts.append(f"project_id 应为 {exp['project_id']}，实际 {rec.get('project_id')}")
            # 检查 title
            if rec.get("title") != exp["title"]:
                item_ok = False
                reason_parts.append(f"title 应为 {exp['title']}，实际 {rec.get('title')}")
            # 检查 status
            if rec.get("status") != exp["status"]:
                item_ok = False
                reason_parts.append(f"status 应为 {exp['status']}，实际 {rec.get('status')}")
            # 检查 error: status=success 时不应有 error 字段或为空；status=failed 时必须等于指定值
            if exp["status"] == "success":
                if "error" in rec and rec["error"] is not None and rec["error"] != "":
                    item_ok = False
                    reason_parts.append(f"success 状态下不应有非空 error，实际 {rec.get('error')}")
            else:  # failed
                if rec.get("error") != exp["error"]:
                    item_ok = False
                    reason_parts.append(f"error 应为 {exp['error']}，实际 {rec.get('error')}")

            if item_ok:
                score_details.append({
                    "item": f"条目 {doc_id} 字段精确匹配",
                    "score": field_score_per_item,
                    "max_score": field_score_per_item,
                    "passed": True,
                    "reason": "所有字段正确"
                })
                total_score += field_score_per_item
            else:
                score_details.append({
                    "item": f"条目 {doc_id} 字段精确匹配",
                    "score": 0,
                    "max_score": field_score_per_item,
                    "passed": False,
                    "reason": "; ".join(reason_parts)
                })

        # 避免出现预期之外的 doc_id（上面已经通过长度限制，额外扣分）
        actual_ids = {r.get("doc_id") for r in data}
        expected_ids = set(expected_map.keys())
        extra_ids = actual_ids - expected_ids
        if extra_ids:
            # 每条额外扣5分，但不超过20分
            penalty = min(len(extra_ids) * 5, 20)
            total_score = max(0, total_score - penalty)
            score_details.append({
                "item": "没有多余文档条目",
                "score": 0,
                "max_score": 0,
                "passed": False,
                "reason": f"发现未在日志中的文档ID: {extra_ids}"
            })

    # -------------------- 最终得分计算 --------------------
    # 确保总分不超过100
    final_total = min(total_score, 100)
    result = {
        "total_score": final_total,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
