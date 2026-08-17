import sys
import os
import json
import re

workspace = sys.argv[1] if len(sys.argv) > 1 else "."

# ---------- 辅助函数 ----------
def clean_summary(text: str) -> str:
    """移除首尾空白，合并连续空白（包括换行）为一个空格"""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

# ---------- 预期答案 ----------
target = "HelioSync Edge Inference Fabric"

# 报告：预期匹配的报告ID（按published_at降序取最新版本，重复ID只保留最新）
expected_reports = {
    "RPT-2024-001": "HelioSync Edge Inference Fabric 在工业视觉检测中实现了99.2%的准确率，彻底改变了传统方案。",
    "RPT-2024-002": "多家工厂部署了基于HelioSync Edge Inference Fabric的实时质检系统，产能提升30%。",
    "RPT-2024-003": "HelioSync Edge Inference Fabric 被集成到仓储自动导引车中，路径规划延迟低于5ms。",
}
# 注意：RPT-2024-003 有两个记录，但published_at更晚的是2024-08-10，所以取那个。
# 演示：预期匹配
expected_presentations = {
    "PRES-2024-A1": "HelioSync Edge Inference Fabric是下一代边缘推理平台，支持多模型并发。",
    "PRES-2024-B2": "对比测试显示HelioSync Edge Inference Fabric的吞吐量是竞品的2.3倍。",
    "PRES-2024-C3": "下一代产品将基于HelioSync Edge Inference Fabric开发，但尚未确认。",
    "PRES-2024-D4": "旧版方案HelioSync Edge Inference Fabric已被弃用，不再维护。",
}
# 媒体：预期匹配
expected_media = {
    "MED-2024-K01": "HelioSync Edge Inference Fabric正式发布，首批用户包括三家世界500强企业。",
    "MED-2024-P02": "技术专家深入解析HelioSync Edge Inference Fabric的架构设计。",
    "MED-2024-E03": "HelioSync Edge Inference Fabric 在智慧零售场景的落地分析。",
}

# ---------- 验证逻辑 ----------
details = []
score_total = 0
max_total = 100

# 1. 目录结构 (10分)
ops_dir = os.path.join(workspace, "ops")
if os.path.isdir(ops_dir):
    details.append({"item": "ops directory exists", "score": 10, "max_score": 10, "passed": True, "reason": "ops/ found"})
    score_total += 10
else:
    details.append({"item": "ops directory exists", "score": 0, "max_score": 10, "passed": False, "reason": "ops/ missing"})

# 2. 产物文件存在且合法JSON (10分)
clue_path = os.path.join(workspace, "ops", "clue_list.json")
try:
    with open(clue_path, "r", encoding="utf-8") as f:
        clue_data = json.load(f)
    details.append({"item": "clue_list.json exists and valid JSON", "score": 10, "max_score": 10, "passed": True, "reason": "file valid"})
    score_total += 10
except (FileNotFoundError, json.JSONDecodeError) as e:
    details.append({"item": "clue_list.json exists and valid JSON", "score": 0, "max_score": 10, "passed": False, "reason": str(e)})
    # 如果文件不存在，后续检查无法进行，直接输出结果
    score_total = sum(d["score"] for d in details)
    details.append({"item": "TOTAL", "score": score_total, "max_score": max_total, "passed": score_total >= 60, "reason": "early exit"})
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": score_total, "details": details}, f, indent=2, ensure_ascii=False)
    sys.exit(0)

# 3. 产物结构正确性 (20分)
required_keys = ["reports", "presentations", "media_samples"]
present_keys = [k for k in required_keys if k in clue_data]
missing_keys = [k for k in required_keys if k not in clue_data]
if not missing_keys:
    details.append({"item": "All three categories present in clue_list.json", "score": 20, "max_score": 20, "passed": True, "reason": "reports, presentations, media_samples found"})
    score_total += 20
else:
    details.append({"item": "All three categories present", "score": 0, "max_score": 20, "passed": False, "reason": f"missing: {missing_keys}"})

# 4. 报告匹配准确度 (25分)
reports_in = clue_data.get("reports", [])
if not isinstance(reports_in, list):
    reports_in = []
# 将报告列表转为 dict，方便比较
reports_dict = {}
for item in reports_in:
    if isinstance(item, dict) and "id" in item and "clue" in item:
        rid = item["id"]
        clue_clean = clean_summary(item["clue"])
        reports_dict[rid] = clue_clean

report_correct = 0
report_extra = []
report_missing = []
for rid, expected_clue in expected_reports.items():
    if rid in reports_dict:
        if reports_dict[rid] == clean_summary(expected_clue):
            report_correct += 1
        else:
            # 部分正确？不扣全部
            pass
    else:
        report_missing.append(rid)
# 检查多余
for rid in reports_dict:
    if rid not in expected_reports:
        report_extra.append(rid)
report_score = 0
# 正确一个约8-9分，最多25分
report_score = min(report_correct * 8, 25)  # 最多3个正确，8*3=24，留1分扣多/少
if report_extra:
    report_score = max(0, report_score - len(report_extra) * 4)  # 每个多余扣4分
if report_missing:
    report_score = max(0, report_score - len(report_missing) * 5)  # 每个缺失扣5分
report_score = max(0, min(report_score, 25))
details.append({
    "item": "Report entries match expected (id + cleaned clue)",
    "score": report_score,
    "max_score": 25,
    "passed": report_correct == len(expected_reports) and not report_extra,
    "reason": f"correct={report_correct}, extra={len(report_extra)}, missing={len(report_missing)}"
})
score_total += report_score

# 5. 演示匹配准确度 (25分)
pres_in = clue_data.get("presentations", [])
pres_dict = {}
for item in pres_in:
    if isinstance(item, dict) and "id" in item and "clue" in item:
        pid = item["id"]
        clue_clean = clean_summary(item["clue"])
        pres_dict[pid] = clue_clean

pres_correct = 0
pres_extra = []
pres_missing = []
for pid, expected_clue in expected_presentations.items():
    if pid in pres_dict:
        if pres_dict[pid] == clean_summary(expected_clue):
            pres_correct += 1
    else:
        pres_missing.append(pid)
for pid in pres_dict:
    if pid not in expected_presentations:
        pres_extra.append(pid)
pres_score = min(pres_correct * 6, 25)  # 4个正确，6*4=24
if pres_extra:
    pres_score = max(0, pres_score - len(pres_extra) * 4)
if pres_missing:
    pres_score = max(0, pres_score - len(pres_missing) * 5)
pres_score = max(0, min(pres_score, 25))
details.append({
    "item": "Presentation entries match expected (id + cleaned clue)",
    "score": pres_score,
    "max_score": 25,
    "passed": pres_correct == len(expected_presentations) and not pres_extra,
    "reason": f"correct={pres_correct}, extra={len(pres_extra)}, missing={len(pres_missing)}"
})
score_total += pres_score

# 6. 媒体样本匹配准确度 (10分)
media_in = clue_data.get("media_samples", [])
media_dict = {}
for item in media_in:
    if isinstance(item, dict) and "id" in item and "clue" in item:
        mid = item["id"]
        clue_clean = clean_summary(item["clue"])
        media_dict[mid] = clue_clean

media_correct = 0
media_extra = []
media_missing = []
for mid, expected_clue in expected_media.items():
    if mid in media_dict:
        if media_dict[mid] == clean_summary(expected_clue):
            media_correct += 1
    else:
        media_missing.append(mid)
for mid in media_dict:
    if mid not in expected_media:
        media_extra.append(mid)
media_score = min(media_correct * 3, 10)  # 3个正确，3*3=9，留1分扣
if media_extra:
    media_score = max(0, media_score - len(media_extra) * 3)
if media_missing:
    media_score = max(0, media_score - len(media_missing) * 4)
media_score = max(0, min(media_score, 10))
details.append({
    "item": "Media sample entries match expected (id + cleaned clue)",
    "score": media_score,
    "max_score": 10,
    "passed": media_correct == len(expected_media) and not media_extra,
    "reason": f"correct={media_correct}, extra={len(media_extra)}, missing={len(media_missing)}"
})
score_total += media_score

# ---------- 总分写入 ----------
score_total = min(score_total, 100)
with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
    json.dump({
        "total_score": score_total,
        "details": details
    }, f, indent=2, ensure_ascii=False)

print(f"Verification complete. Total score: {score_total}/100")
