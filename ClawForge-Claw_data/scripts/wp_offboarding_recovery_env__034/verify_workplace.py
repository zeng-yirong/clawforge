import json
import os
import sys
from pathlib import Path

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = {"total_score": 0, "details": []}
    workspace_path = Path(workspace)

    # ---------- 1. 目录结构检查 ----------
    checks = []

    # 期望的产物文件
    checklist_path = workspace_path / "ops" / "handover_checklist.json"
    dir_ok = checklist_path.parent.exists()
    checks.append({
        "item": "ops/handover_checklist.json 所在目录存在",
        "max_score": 5,
        "score": 5 if dir_ok else 0,
        "passed": dir_ok,
        "reason": "目录 ops 存在" if dir_ok else "目录 ops 不存在"
    })

    file_ok = checklist_path.is_file()
    checks.append({
        "item": "handover_checklist.json 文件存在",
        "max_score": 5,
        "score": 5 if file_ok else 0,
        "passed": file_ok,
        "reason": f"文件 {checklist_path} 存在" if file_ok else f"文件 {checklist_path} 不存在"
    })

    if not file_ok:
        result["details"] = checks
        result["total_score"] = sum(c["score"] for c in checks)
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        print("✗ 关键文件缺失，提前终止")
        return

    # ---------- 2. JSON 合法性 ----------
    try:
        with open(checklist_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        json_valid = True
        reason = "JSON 格式正确"
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        json_valid = False
        reason = f"JSON 解析失败: {e}"
    checks.append({
        "item": "handover_checklist.json 是合法 JSON",
        "max_score": 10,
        "score": 10 if json_valid else 0,
        "passed": json_valid,
        "reason": reason
    })

    if not json_valid:
        result["details"] = checks
        result["total_score"] = sum(c["score"] for c in checks)
        with open(workspace_path / "workplace_score.json", "w") as f:
            json.dump(result, f, indent=2)
        return

    # ---------- 3. 关键字段检查 ----------
    # 员工 ID
    emp_id = data.get("employee_id")
    emp_ok = emp_id == "E001"
    checks.append({
        "item": "employee_id 为 E001（已批准离职员工）",
        "max_score": 20,
        "score": 20 if emp_ok else 0,
        "passed": emp_ok,
        "reason": f"employee_id 值为 {emp_id!r}" if emp_ok else f"employee_id 应为 'E001'，实际为 {emp_id!r}"
    })

    # 撤销的系统列表（顺序无关，用 set）
    revoked = data.get("revoked_systems", [])
    if not isinstance(revoked, list):
        revoked = []
    expected_systems = {"Admin Portal", "CRM"}
    actual_systems = set(revoked)
    sys_ok = actual_systems == expected_systems
    checks.append({
        "item": "revoked_systems 包含所有 active 系统 (Admin Portal, CRM)，无多余",
        "max_score": 25,
        "score": 25 if sys_ok else 0,
        "passed": sys_ok,
        "reason": f"实际集合: {actual_systems}, 期望: {expected_systems}" if not sys_ok else "正确"
    })

    # 回收的设备
    reclaimed = data.get("reclaimed_assets", [])
    if not isinstance(reclaimed, list):
        reclaimed = []
    expected_assets = {"LT-2041"}
    actual_assets = set(reclaimed)
    asset_ok = actual_assets == expected_assets
    checks.append({
        "item": "reclaimed_assets 包含分配给该员工的 assigned 资产 LT-2041，无多余",
        "max_score": 20,
        "score": 20 if asset_ok else 0,
        "passed": asset_ok,
        "reason": f"实际集合: {actual_assets}, 期望: {expected_assets}" if not asset_ok else "正确"
    })

    # ---------- 4. 额外整合检查（不要求字段，但若缺少合理结构扣分）----------
    # 确保没有把其他员工的系统或资产混入
    extra_systems = revoked.copy()
    if isinstance(extra_systems, list):
        # 检查是否包含非预期的系统（如 Finance System, VPN 等）
        unexpected = [s for s in extra_systems if s not in {"Admin Portal", "CRM"}]
        if unexpected:
            checks.append({
                "item": "revoked_systems 无多余系统（防止混入其他员工）",
                "max_score": 10,
                "score": 0,
                "passed": False,
                "reason": f"发现不应包含的系统: {unexpected}"
            })
        else:
            checks.append({
                "item": "revoked_systems 无多余系统",
                "max_score": 10,
                "score": 10,
                "passed": True,
                "reason": "未发现意外系统"
            })

    extra_assets = reclaimed.copy()
    if isinstance(extra_assets, list):
        unexpected_assets = [a for a in extra_assets if a not in {"LT-2041"}]
        if unexpected_assets:
            checks.append({
                "item": "reclaimed_assets 无多余资产",
                "max_score": 5,
                "score": 0,
                "passed": False,
                "reason": f"发现不应包含的资产: {unexpected_assets}"
            })
        else:
            checks.append({
                "item": "reclaimed_assets 无多余资产",
                "max_score": 5,
                "score": 5,
                "passed": True,
                "reason": "未发现意外资产"
            })

    # ---------- 5. 汇总 ----------
    total_score = sum(c["score"] for c in checks)
    result["total_score"] = min(total_score, 100)  # 保险
    result["details"] = checks

    with open(workspace_path / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"验证完成，总分 {result['total_score']}")

if __name__ == "__main__":
    main()
