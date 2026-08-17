import os
import sys
import json
import re

def verify(workspace):
    # ------------------------------------------------------------------
    # 初始化评分明细
    # ------------------------------------------------------------------
    details = []
    total_score = 0

    # Helper
    def check(name, score, max_score, passed, reason):
        details.append({
            "item": name,
            "score": score,
            "max_score": max_score,
            "passed": passed,
            "reason": reason
        })
        return score if passed else 0

    # ------------------------------------------------------------------
    # 1. 目录存在性检查 (15分)
    # ------------------------------------------------------------------
    dirs = ["ops", "data/faults", "data/attachments"]
    dir_score = 0
    for d in dirs:
        path = os.path.join(workspace, d)
        if os.path.isdir(path):
            dir_score += 5
        else:
            pass
    total_score += check("必备目录存在", dir_score, 15, dir_score==15,
                         f"ops/data/faults/data/attachments 目录检查: 命中 {dir_score//5}/3")

    # ------------------------------------------------------------------
    # 2. 输出产物文件存在 (10分)
    # ------------------------------------------------------------------
    report_path = os.path.join(workspace, "ops", "postmortem_report.json")
    if os.path.isfile(report_path):
        total_score += check("报告文件存在", 10, 10, True, "ops/postmortem_report.json 已创建")
    else:
        total_score += check("报告文件存在", 0, 10, False, "ops/postmortem_report.json 未创建")

    # ------------------------------------------------------------------
    # 3. JSON 格式合法性 (10分)
    # ------------------------------------------------------------------
    try:
        with open(report_path, "r") as f:
            data = json.load(f)
        total_score += check("JSON 格式合法", 10, 10, True, "JSON 解析成功")
    except Exception as e:
        total_score += check("JSON 格式合法", 0, 10, False, f"JSON 解析失败: {e}")
        # 后续检查无法进行，直接写结果返回
        _finish(workspace, total_score, details)
        return

    # ------------------------------------------------------------------
    # 4. 关键字段存在性 (20分, 每个字段5分)
    # ------------------------------------------------------------------
    required_fields = ["service", "severity", "root_cause", "repair_plan"]
    field_ok = 0
    for fld in required_fields:
        if fld in data:
            field_ok += 1
    total_score += check("报告关键字段存在", field_ok*5, 20, field_ok==4,
                         f"找到 {field_ok}/4 个必需字段: {required_fields}")

    # ------------------------------------------------------------------
    # 5. 核心内容准确度 (45分)
    #   读取附件中的标准文本，比对 root_cause 和 repair_plan 是否匹配
    # ------------------------------------------------------------------
    # 附件路径（相对于 workspace）
    attach_path = os.path.join(workspace, "data", "attachments", "crash_log_007.txt")
    if not os.path.isfile(attach_path):
        total_score += check("附件文件存在", 0, 5, False, "目标附件 crash_log_007.txt 不存在，无法验证内容")
        _finish(workspace, total_score, details)
        return
    with open(attach_path, "r") as f:
        attach_text = f.read()

    # 从附件中提取 root_cause 和 repair_plan
    # 使用正则提取 "Root Cause:" 到 "Repair Plan:" 之间的内容，以及 "Repair Plan:" 到末尾（到下一个标题或结束）
    # 注意附件格式是固定的
    root_match = re.search(r"Root Cause:\s*(.*?)\n\s*\n\s*Repair Plan:", attach_text, re.DOTALL)
    repair_match = re.search(r"Repair Plan:\s*(.*)", attach_text, re.DOTALL)
    expected_root = root_match.group(1).strip() if root_match else ""
    expected_repair = repair_match.group(1).strip() if repair_match else ""

    # 清理空格、换行，统一比较
    def normalize(t):
        return re.sub(r'\s+', ' ', t).strip()

    norm_expected_root = normalize(expected_root)
    norm_expected_repair = normalize(expected_repair)
    norm_actual_root = normalize(data.get("root_cause", ""))
    norm_actual_repair = normalize(data.get("repair_plan", ""))

    # 根因匹配 (20分)
    root_score = 0
    if norm_actual_root == norm_expected_root:
        root_score = 20
    else:
        # 允许部分匹配（长度80%以上相似给一半分数）但为了客观，我们仅做精确匹配；如果由于格式差异，尝试模糊匹配
        # 这里为了确保唯一答案，采用精确匹配（因为prompt要求准确，且附件是文本）
        # 但为了鲁棒，如果根因包含关键短语也给分？不，必须精确
        # 为了降低难度，我们允许忽略大小写和标点？不，保持严格，因为env_builder是可控的
        if norm_expected_root in norm_actual_root or norm_actual_root in norm_expected_root:
            root_score = 15  # 子串匹配给大部分分
        elif len(norm_actual_root) > 0 and len(norm_expected_root) > 0:
            # 简单长度比例判定
            ratio = len(set(norm_actual_root.lower().split()) & set(norm_expected_root.lower().split())) / max(len(set(norm_expected_root.lower().split())),1)
            if ratio > 0.7:
                root_score = 10
    total_score += check("根因内容准确", root_score, 20, root_score==20,
                         f"期望: {norm_expected_root[:60]}..., 实际: {norm_actual_root[:60]}...")

    # 修复计划匹配 (20分)
    repair_score = 0
    if norm_actual_repair == norm_expected_repair:
        repair_score = 20
    else:
        if norm_expected_repair in norm_actual_repair or norm_actual_repair in norm_expected_repair:
            repair_score = 15
        elif len(norm_actual_repair) > 0 and len(norm_expected_repair) > 0:
            ratio = len(set(norm_actual_repair.lower().split()) & set(norm_expected_repair.lower().split())) / max(len(set(norm_expected_repair.lower().split())),1)
            if ratio > 0.7:
                repair_score = 10
    total_score += check("修复计划内容准确", repair_score, 20, repair_score==20,
                         f"期望: {norm_expected_repair[:60]}..., 实际: {norm_actual_repair[:60]}...")

    # 严重程度和服务名 (5分) - 检查是否与附件一致
    expected_severity = "critical"
    expected_service = "payment-service"
    sev_ok = 0
    if data.get("severity", "").lower() == expected_severity:
        sev_ok += 1
    if data.get("service", "").lower() == expected_service:
        sev_ok += 1
    total_score += check("服务名和严重等级正确", sev_ok*2.5, 5, sev_ok==2,
                         f"severity: {data.get('severity','')} vs {expected_severity}; service: {data.get('service','')} vs {expected_service}")

    # 可选：检查是否有附件摘要字段（不强制，但如果有可加分？但为了标准，我们不额外要求）

    # 最终总分截断整数
    total_score = min(int(total_score), 100)
    _finish(workspace, total_score, details)

def _finish(workspace, total, details):
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Score: {total}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
