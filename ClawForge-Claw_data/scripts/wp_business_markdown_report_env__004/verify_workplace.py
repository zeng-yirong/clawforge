import sys
import json
import os
import re
from pathlib import Path

def evaluate(workspace: str) -> dict:
    score = 0
    details = []
    ws = Path(workspace)

    # 1. 检查 output/report.md 是否存在 (10分)
    report_path = ws / "output" / "report.md"
    item = {"item": "output/report.md 存在", "max_score": 10}
    if report_path.exists() and report_path.is_file():
        score += 10
        item["score"] = 10
        item["passed"] = True
        item["reason"] = "报告文件已存在"
    else:
        item["score"] = 0
        item["passed"] = False
        item["reason"] = "未找到 output/report.md"
        details.append(item)
        # 如果文件不存在，后续不用检查了
        details.append({"item": "Markdown 格式与标题", "max_score": 10, "score": 0, "passed": False, "reason": "文件缺失"})
        details.append({"item": "客户总收入 (450000)", "max_score": 20, "score": 0, "passed": False, "reason": "文件缺失"})
        details.append({"item": "产品总收入 (380000)", "max_score": 20, "score": 0, "passed": False, "reason": "文件缺失"})
        details.append({"item": "运营总成本 (95000)", "max_score": 20, "score": 0, "passed": False, "reason": "文件缺失"})
        # 额外加分项：格式整洁等 (20分)
        details.append({"item": "数据来源标识完整", "max_score": 20, "score": 0, "passed": False, "reason": "文件缺失"})
        return {"total_score": score, "details": details}

    # 读取文件内容
    content = report_path.read_text(encoding="utf-8")
    details.append(item)

    # 2. 检查标题和基本 Markdown 结构 (10分)
    item2 = {"item": "Markdown 格式与标题", "max_score": 10}
    title_ok = "业务指标季度报告 - 2025 Q2" in content
    if title_ok:
        score += 10
        item2["score"] = 10
        item2["passed"] = True
        item2["reason"] = "标题正确包含'业务指标季度报告 - 2025 Q2'"
    else:
        item2["score"] = 0
        item2["passed"] = False
        item2["reason"] = "未找到预期标题或标题不正确"
    details.append(item2)

    # 3. 提取表格中的数值（要求表格行包含账本名和数值）
    # 预期行: | customer_ledger | revenue | 450000 | 或类似
    # 使用正则匹配表格行: |\s*(\S+)\s*\|\s*(\S+)\s*\|\s*([0-9]+)\s*|
    table_pattern = re.compile(r'\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*([0-9]+)\s*\|')
    matches = table_pattern.findall(content)
    # 构建字典： { (source, metric): value }
    extracted = {}
    for m in matches:
        source = m[0].lower()
        metric = m[1].lower()
        val = int(m[2])
        # 处理可能的空格和缩写，比如 customer_ledger 或 customer ledger
        source_clean = source.replace("_","").replace(" ","")
        metric_clean = metric.replace("_","").replace(" ","")
        extracted[(source_clean, metric_clean)] = val

    # 3a. 客户总收入 450000 (20分)
    # 预期标签：customer ledger 或 customer_ledger，revenue
    item3 = {"item": "客户总收入 (450000)", "max_score": 20}
    key_rev = ("customerledger", "revenue")
    key_rev2 = ("customer", "revenue")  # 如果用户只写了customer
    got_rev = extracted.get(key_rev, extracted.get(key_rev2, None))
    if got_rev == 450000:
        score += 20
        item3["score"] = 20
        item3["passed"] = True
        item3["reason"] = f"客户收入正确: {got_rev}"
    elif got_rev is not None:
        score += 0
        item3["score"] = 0
        item3["passed"] = False
        item3["reason"] = f"客户收入数值错误: 期望450000, 得到{got_rev}"
    else:
        score += 0
        item3["score"] = 0
        item3["passed"] = False
        item3["reason"] = "未在表格中找到客户收入行"
    details.append(item3)

    # 3b. 产品总收入 380000 (20分)
    item4 = {"item": "产品总收入 (380000)", "max_score": 20}
    key_prod = ("productledger","revenue")
    key_prod2 = ("product","revenue")
    got_prod = extracted.get(key_prod, extracted.get(key_prod2, None))
    if got_prod == 380000:
        score += 20
        item4["score"] = 20
        item4["passed"] = True
        item4["reason"] = f"产品收入正确: {got_prod}"
    elif got_prod is not None:
        score += 0
        item4["score"] = 0
        item4["passed"] = False
        item4["reason"] = f"产品收入数值错误: 期望380000, 得到{got_prod}"
    else:
        score += 0
        item4["score"] = 0
        item4["passed"] = False
        item4["reason"] = "未在表格中找到产品收入行"
    details.append(item4)

    # 3c. 运营总成本 95000 (20分)
    item5 = {"item": "运营总成本 (95000)", "max_score": 20}
    key_ops = ("opsledger","cost")
    key_ops2 = ("ops","cost")
    key_ops3 = ("operations","cost")
    got_cost = extracted.get(key_ops, extracted.get(key_ops2, extracted.get(key_ops3, None)))
    if got_cost == 95000:
        score += 20
        item5["score"] = 20
        item5["passed"] = True
        item5["reason"] = f"运营成本正确: {got_cost}"
    elif got_cost is not None:
        score += 0
        item5["score"] = 0
        item5["passed"] = False
        item5["reason"] = f"运营成本数值错误: 期望95000, 得到{got_cost}"
    else:
        score += 0
        item5["score"] = 0
        item5["passed"] = False
        item5["reason"] = "未在表格中找到运营成本行"
    details.append(item5)

    # 4. 额外加分：数据来源标识（要求表格中明确写出账本文件名） (20分)
    item6 = {"item": "数据来源标识完整", "max_score": 20}
    # 期望表格行中来源包含 customer_ledger, product_ledger, ops_ledger
    sources = [m[0].lower() for m in matches]
    # 检查是否每个账本名称都出现了（允许简写但需包含关键字）
    has_cust = any("customer" in s for s in sources)
    has_prod = any("product" in s for s in sources)
    has_ops = any("ops" in s or "operation" in s for s in sources)
    if has_cust and has_prod and has_ops:
        score += 20
        item6["score"] = 20
        item6["passed"] = True
        item6["reason"] = "数据来源标识完整，包含三个账本名称"
    else:
        missing = []
        if not has_cust: missing.append("客户账本")
        if not has_prod: missing.append("产品账本")
        if not has_ops: missing.append("运营账本")
        item6["score"] = 0
        item6["passed"] = False
        item6["reason"] = f"缺失数据来源: {', '.join(missing)}"
    details.append(item6)

    return {"total_score": score, "details": details}

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = evaluate(workspace)
    # 写入 workplace_score.json
    output_path = Path(workspace) / "workplace_score.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"验证完成，评分结果已写入 {output_path}")
    print(f"总分: {result['total_score']}")

if __name__ == "__main__":
    main()
