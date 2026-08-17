"""
verify_workplace.py — 纯代码客观验证弱密码审计任务
工作区路径通过命令行参数传入，默认为当前目录
"""
import sys
import json
import os
import re
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace = Path(workspace).resolve()
    score_details = []
    total_score = 0
    max_total = 100

    # ---------- 辅助函数 ----------
    def is_weak(password: str) -> bool:
        # 长度 < 8 或 不含数字 或 不含特殊字符
        if len(password) < 8:
            return True
        if not re.search(r'\d', password):
            return True
        if not re.search(r'[^a-zA-Z0-9]', password):
            return True
        return False

    # 类别映射（与 env_builder 保持一致）
    category_map = {
        "cat_bank": "银行账户",
        "cat_social": "社交媒体",
        "cat_email": "工作邮箱",
        "cat_ecom": "电商平台"
    }

    # 读取所有有效凭证（命名 cred_???.json，合法 JSON，含所有必需字段，唯一 ID）
    cred_dir = workspace / "vault" / "credentials"
    valid_creds = {}
    if cred_dir.exists():
        for f in sorted(cred_dir.iterdir()):
            if not f.name.startswith("cred_") or not f.name.endswith(".json"):
                continue
            if f.name in ("cred_bad.json", "cred_empty.json", "cred_incomplete.json"):
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(data, dict):
                continue
            # 检查必需字段
            required = {"id", "username", "password", "platform", "category_id"}
            if not required.issubset(data.keys()):
                continue
            if not isinstance(data["id"], str) or not isinstance(data["password"], str):
                continue
            if data["id"] in valid_creds:
                # 重复 ID：取第一个有效（按文件名顺序），跳过后续
                continue
            valid_creds[data["id"]] = data

    # 构造预期审计结果
    expected_items = []
    for cid in sorted(valid_creds.keys()):
        cred = valid_creds[cid]
        if is_weak(cred["password"]):
            cat_name = category_map.get(cred["category_id"], cred["category_id"])
            expected_items.append({
                "id": cid,
                "original_password": cred["password"],
                "category": cat_name
            })
    expected_items.sort(key=lambda x: x["id"])

    # ---------- 检查点 1：报告文件是否存在 ----------
    report_path = workspace / "ops" / "audit_weak_passwords.json"
    if not report_path.exists():
        score_details.append({
            "item": "报告文件存在性",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "ops/audit_weak_passwords.json 不存在"
        })
        # 剩余检查无法进行，直接写结果
        finish(score_details, total_score, max_total)
        return
    else:
        score_details.append({
            "item": "报告文件存在性",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/audit_weak_passwords.json 存在"
        })
        total_score += 10

    # ---------- 检查点 2：报告 JSON 合法性 ----------
    try:
        agent_report = json.loads(report_path.read_text(encoding="utf-8"))
        if not isinstance(agent_report, list):
            raise ValueError("根元素不是列表")
    except Exception as e:
        score_details.append({
            "item": "报告 JSON 格式",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"无法解析 JSON 或格式错误: {e}"
        })
        finish(score_details, total_score, max_total)
        return
    score_details.append({
        "item": "报告 JSON 格式",
        "score": 10,
        "max_score": 10,
        "passed": True,
        "reason": "JSON 解析成功，根元素为列表"
    })
    total_score += 10

    # ---------- 检查点 3：报告条目数目正确 ----------
    expected_count = len(expected_items)
    actual_count = len(agent_report)
    if actual_count == expected_count:
        score_details.append({
            "item": "报告条目数量",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": f"期望 {expected_count} 条，实际 {actual_count} 条"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "报告条目数量",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": f"期望 {expected_count} 条，实际 {actual_count} 条"
        })

    # ---------- 检查点 4：每条报告的字段完整性 ----------
    field_ok = True
    for item in agent_report:
        if not isinstance(item, dict):
            field_ok = False
            break
        if not {"id", "original_password", "category"}.issubset(item.keys()):
            field_ok = False
            break
        if not isinstance(item["id"], str) or not isinstance(item["original_password"], str) or not isinstance(item["category"], str):
            field_ok = False
            break
    if field_ok:
        score_details.append({
            "item": "报告条目字段完整",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "每个条目均包含 id, original_password, category 且均为字符串"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "报告条目字段完整",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "部分条目缺少必需字段或类型不符"
        })

    # ---------- 检查点 5：内容精确匹配（排序后比较）----------
    agent_sorted = sorted(agent_report, key=lambda x: x["id"])
    match = True
    mismatch_reason = ""
    for i, (exp, act) in enumerate(zip(expected_items, agent_sorted)):
        if exp != act:
            match = False
            mismatch_reason = f"第 {i+1} 条不匹配: 期望 {exp}，实际 {act}"
            break
    if len(expected_items) != len(agent_sorted):
        match = False
        mismatch_reason = "数量不匹配，无法逐条比较"

    if match:
        score_details.append({
            "item": "审计内容精确匹配",
            "score": 60,
            "max_score": 60,
            "passed": True,
            "reason": "所有弱密码条目与期望完全一致"
        })
        total_score += 60
    else:
        score_details.append({
            "item": "审计内容精确匹配",
            "score": 0,
            "max_score": 60,
            "passed": False,
            "reason": mismatch_reason or "内容不一致"
        })

    # ---------- 最终输出 ----------
    finish(score_details, total_score, max_total)

def finish(details, total, max_total):
    # 确保总分不超过 max_total
    total = min(total, max_total)
    result = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"得分: {total}/{max_total}")
    sys.exit(0)

if __name__ == "__main__":
    main()
