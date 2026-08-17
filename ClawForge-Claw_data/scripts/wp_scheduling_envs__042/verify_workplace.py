import sys
import json
import os
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace)

    details = []
    total_score = 0

    # ---------- 1. 检查 ops 目录 ----------
    ops_dir = workspace_path / "ops"
    if ops_dir.is_dir():
        details.append({"item": "ops 目录存在", "score": 5, "max_score": 5, "passed": True, "reason": "目录存在"})
        total_score += 5
    else:
        details.append({"item": "ops 目录存在", "score": 0, "max_score": 5, "passed": False, "reason": "ops 目录不存在"})

    # ---------- 2. 检查 fixed_schedules.json 文件 ----------
    fixed_file = ops_dir / "fixed_schedules.json"
    if not fixed_file.is_file():
        details.append({"item": "ops/fixed_schedules.json 存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        # 后续无法继续，直接结束
        result = {"total_score": total_score, "details": details}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    details.append({"item": "ops/fixed_schedules.json 存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    total_score += 10

    # ---------- 3. JSON 合法性 ----------
    try:
        with open(fixed_file, "r") as f:
            fixed = json.load(f)
        if not isinstance(fixed, list):
            details.append({"item": "JSON 格式合法且为列表", "score": 0, "max_score": 10, "passed": False, "reason": "根节点不是列表"})
            total_score += 0
            # 继续可能出错，提前结束
            result = {"total_score": total_score, "details": details}
            with open(workspace_path / "workplace_score.json", "w") as f:
                json.dump(result, f, indent=2)
            return
        details.append({"item": "JSON 格式合法且为列表", "score": 10, "max_score": 10, "passed": True, "reason": "合法列表"})
        total_score += 10
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        details.append({"item": "JSON 格式合法且为列表", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        result = {"total_score": total_score, "details": details}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # ---------- 4. 加载原始调度 ----------
    orig_file = workspace_path / "data" / "schedules.json"
    if not orig_file.is_file():
        details.append({"item": "原始调度文件存在", "score": 0, "max_score": 0, "passed": False, "reason": "data/schedules.json 缺失，无法验证"})
        result = {"total_score": total_score, "details": details}
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return
    with open(orig_file, "r") as f:
        original = json.load(f)

    # 检查长度
    len_ok = len(fixed) == len(original)
    details.append({
        "item": "调度列表长度与原始一致",
        "score": 10 if len_ok else 0,
        "max_score": 10,
        "passed": len_ok,
        "reason": f"原始 {len(original)} 条，输出 {len(fixed)} 条"
    })
    if len_ok:
        total_score += 10

    # ---------- 5. 按 schedule_id 比对（40分） ----------
    orig_by_id = {s["schedule_id"]: s for s in original}
    fixed_by_id = {s["schedule_id"]: s for s in fixed}

    id_match_ok = True
    missing_ids = []
    extra_ids = []
    mismatched = []

    # 检查 id 一致性
    for oid in orig_by_id:
        if oid not in fixed_by_id:
            missing_ids.append(oid)
            id_match_ok = False
    for fid in fixed_by_id:
        if fid not in orig_by_id:
            extra_ids.append(fid)
            id_match_ok = False

    if not id_match_ok:
        details.append({
            "item": "schedule_id 完整性（无缺失/无多余）",
            "score": 0,
            "max_score": 40,
            "passed": False,
            "reason": f"缺失 ID: {missing_ids}, 多余 ID: {extra_ids}"
        })
        total_score += 0
    else:
        # 检查每个调度的字段（sch_002 允许时间变化）
        all_fields_ok = True
        for oid, orig_s in orig_by_id.items():
            fixed_s = fixed_by_id[oid]
            # 基础字段（除了 start_time, end_time 以及 sch_002 外必须相等）
            if oid == "sch_002":
                # 允许 start_time 和 end_time 变化，但必须符合预期
                expected_start = "23:00"
                expected_end = "00:00"
                if fixed_s["start_time"] != expected_start or fixed_s["end_time"] != expected_end:
                    all_fields_ok = False
                    mismatched.append(f"{oid}: start_time 应为 {expected_start}, 实际 {fixed_s['start_time']}; end_time 应为 {expected_end}, 实际 {fixed_s['end_time']}")
                else:
                    # 其他字段必须与原始一致
                    for key in ["device_id", "days_of_week", "enabled"]:
                        if fixed_s.get(key) != orig_s.get(key):
                            all_fields_ok = False
                            mismatched.append(f"{oid}: {key} 不一致: 原始 {orig_s.get(key)}, 输出 {fixed_s.get(key)}")
            else:
                # 其他调度全部字段必须一致
                for key in ["device_id", "start_time", "end_time", "days_of_week", "enabled"]:
                    if fixed_s.get(key) != orig_s.get(key):
                        all_fields_ok = False
                        mismatched.append(f"{oid}: {key} 不一致: 原始 {orig_s.get(key)}, 输出 {fixed_s.get(key)}")

        if all_fields_ok:
            details.append({
                "item": "所有调度字段正确（sch_002 按预期调整）",
                "score": 40,
                "max_score": 40,
                "passed": True,
                "reason": "所有调度 ID 与字段完全匹配，sch_002 时间已修正为 23:00-00:00"
            })
            total_score += 40
        else:
            details.append({
                "item": "所有调度字段正确（sch_002 按预期调整）",
                "score": 0,
                "max_score": 40,
                "passed": False,
                "reason": "以下问题: " + "; ".join(mismatched)
            })

    # ---------- 6. sch_002 时间修正检查（25分，已包含在字段检查中，但为了细化再检查一次） ----------
    # 如果上面已经正确，此项也自动满分；否则扣除
    # 为了避免重复计分，我们单独检查，但总分设计为独立项
    sch2_fixed = fixed_by_id.get("sch_002")
    if sch2_fixed and sch2_fixed["start_time"] == "23:00" and sch2_fixed["end_time"] == "00:00":
        details.append({
            "item": "sch_002 时间修正正确 (23:00-00:00)",
            "score": 25,
            "max_score": 25,
            "passed": True,
            "reason": "加湿器调度已后移到 AC 之后"
        })
        total_score += 25
    else:
        details.append({
            "item": "sch_002 时间修正正确 (23:00-00:00)",
            "score": 0,
            "max_score": 25,
            "passed": False,
            "reason": f"当前时间: {sch2_fixed.get('start_time')} - {sch2_fixed.get('end_time')} 不符合预期"
        })

    # 总分修正（最大100）
    total_score = min(total_score, 100)

    # 输出结果
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(workspace_path / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
