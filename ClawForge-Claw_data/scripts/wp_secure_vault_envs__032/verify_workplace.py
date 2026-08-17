import json
import os
import sys

def verify(workspace):
    details = []
    total_score = 0
    max_total = 100

    # 1. 检查目录结构 (10分)
    vault_exists = os.path.isdir(os.path.join(workspace, "vault"))
    quarantined_exists = os.path.isdir(os.path.join(workspace, "vault", "quarantined"))
    report_exists = os.path.isfile(os.path.join(workspace, "vault", "quarantined_report.json"))
    if vault_exists and quarantined_exists and report_exists:
        details.append({"item": "目录结构完整", "score": 10, "max_score": 10, "passed": True, "reason": "vault/quarantined/ 和 vault/quarantined_report.json 存在"})
        total_score += 10
    else:
        missing = []
        if not vault_exists: missing.append("vault/")
        if not quarantined_exists: missing.append("vault/quarantined/")
        if not report_exists: missing.append("vault/quarantined_report.json")
        details.append({"item": "目录结构完整", "score": 0, "max_score": 10, "passed": False, "reason": f"缺少: {', '.join(missing)}"})

    # 2. 检查报告格式合法性 (20分)
    if report_exists:
        try:
            with open(os.path.join(workspace, "vault", "quarantined_report.json"), "r") as f:
                report = json.load(f)
            if not isinstance(report, list):
                details.append({"item": "报告格式（JSON数组）", "score": 0, "max_score": 5, "passed": False, "reason": "根节点不是数组"})
            else:
                # 检查每个条目是否包含必要字段
                fields_ok = all(
                    isinstance(item, dict) and
                    "credential_id" in item and
                    "service" in item and
                    "reason" in item
                    for item in report
                )
                if fields_ok and len(report) > 0:
                    details.append({"item": "报告字段完整性（credential_id, service, reason）", "score": 15, "max_score": 15, "passed": True, "reason": f"报告包含 {len(report)} 条记录，每条均有必需字段"})
                    total_score += 15
                elif fields_ok and len(report) == 0:
                    details.append({"item": "报告字段完整性", "score": 5, "max_score": 15, "passed": False, "reason": "报告数组为空，没有隔离任何凭证"})
                else:
                    missing_fields = []
                    for i, item in enumerate(report):
                        if not isinstance(item, dict):
                            missing_fields.append(f"第{i+1}项不是字典")
                        else:
                            for fld in ("credential_id", "service", "reason"):
                                if fld not in item:
                                    missing_fields.append(f"第{i+1}项缺少 {fld}")
                    details.append({"item": "报告字段完整性", "score": 0, "max_score": 15, "passed": False, "reason": "; ".join(missing_fields)})
        except (json.JSONDecodeError, IOError) as e:
            details.append({"item": "报告格式可解析", "score": 0, "max_score": 5, "passed": False, "reason": f"无法解析报告: {str(e)}"})
    else:
        details.append({"item": "报告格式", "score": 0, "max_score": 20, "passed": False, "reason": "报告文件不存在，跳过检查"})

    # 3. 检查文件移动情况 (30分)
    # 期望被移走的凭证ID: C002, C007, C008 (对应文件 cred_c002.json, cred_c007.json, cred_c008.json)
    # 这些文件应出现在 vault/quarantined/ 下，且不在 vault/credentials/ 下
    moved_ids = ["C002", "C007", "C008"]
    moved_ok = True
    for cid in moved_ids:
        fname = f"cred_{cid.lower()}.json"
        in_quarantined = os.path.isfile(os.path.join(workspace, "vault", "quarantined", fname))
        in_original = os.path.isfile(os.path.join(workspace, "vault", "credentials", fname))
        if not in_quarantined:
            moved_ok = False
            details.append({"item": f"凭证 {cid} 移动", "score": 0, "max_score": 30/3, "passed": False, "reason": f"{fname} 未出现在 vault/quarantined/ 中"})
            break
        if in_original:
            moved_ok = False
            details.append({"item": f"凭证 {cid} 移动（残留）", "score": 0, "max_score": 30/3, "passed": False, "reason": f"{fname} 仍留在 vault/credentials/ 中"})
            break
    if moved_ok:
        details.append({"item": "文件移动（3个凭证）", "score": 30, "max_score": 30, "passed": True, "reason": "C002, C007, C008 均被移至 quarantined/ 且原位置已删除"})
        total_score += 30
    else:
        # 如果已经记录了失败，无需再重复
        pass

    # 4. 检查报告内容准确性 (40分)
    if report_exists:
        try:
            with open(os.path.join(workspace, "vault", "quarantined_report.json"), "r") as f:
                report = json.load(f)
        except:
            report = []
        # 构建期望报告（忽略reason文本，只检查credential_id和service）
        expected_entries = {
            "C002": {"service": "Wells Fargo", "reason_start": "强度不足"},
            "C007": {"service": "Ally Bank", "reason_start": "强度不足"},
            "C008": {"service": "Capital One", "reason_start": "强度不足"}
        }
        # 从报告构建查找映射
        report_map = {}
        for item in report:
            if isinstance(item, dict) and "credential_id" in item:
                report_map[item["credential_id"]] = item

        accuracy_score = 0
        accuracy_max = 40
        # 检查每个期望凭证是否在报告中，且service正确，reason包含"强度不足"
        for cid, exp in expected_entries.items():
            if cid not in report_map:
                # 缺少条目
                continue
            item = report_map[cid]
            service_ok = item.get("service") == exp["service"]
            reason_ok = isinstance(item.get("reason"), str) and exp["reason_start"] in item["reason"]
            if service_ok and reason_ok:
                accuracy_score += 13  # 每个凭证约13.33分，容忍小数最后四舍五入
            elif service_ok:
                accuracy_score += 6
            elif reason_ok:
                accuracy_score += 6

        # 检查是否有多余的凭证（误报）
        extra_ids = set(report_map.keys()) - set(expected_entries.keys())
        if extra_ids:
            # 每多一个误报扣5分
            accuracy_score -= 5 * len(extra_ids)
            if accuracy_score < 0:
                accuracy_score = 0

        accuracy_score = min(accuracy_score, accuracy_max)
        if accuracy_score >= 40:
            passed = True
            reason = "所有银行账户不合格凭证均正确列出，service和reason无误"
        elif accuracy_score > 0:
            passed = True if accuracy_score >= 20 else False
            reason = f"部分正确，得分 {accuracy_score}/{accuracy_max}"
        else:
            passed = False
            reason = "报告内容完全错误或为空"
        details.append({"item": "报告内容准确性", "score": accuracy_score, "max_score": accuracy_max, "passed": passed, "reason": reason})
        total_score += accuracy_score

    # 确保总分不超过100
    total_score = min(total_score, 100)
    # 写入结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score written: {total_score}/100")

if __name__ == "__main__":
    ws = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(ws)
