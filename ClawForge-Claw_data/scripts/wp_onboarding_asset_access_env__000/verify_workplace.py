"""
verify_workplace.py for wp_onboarding_asset_access_env__000
纯代码验证，无网络/LLM调用。
"""
import sys
import json
import os
import csv
from pathlib import Path

def load_json_relative(base, rel_path):
    full = base / rel_path
    if not full.exists():
        return None
    with open(full, "r") as f:
        return json.load(f)

def verify(workspace: str) -> dict:
    base = Path(workspace)
    details = []
    total_score = 0

    # ---------- 1. 目录结构检查 (10分) ----------
    dirs_ok = True
    required_dirs = ["ops", "data/onboarding"]
    for d in required_dirs:
        if not (base / d).is_dir():
            dirs_ok = False
            details.append({
                "item": f"目录 {d} 存在",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"缺少目录 {d}"
            })
            break
    if dirs_ok:
        details.append({
            "item": "必要目录都存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/ 和 data/onboarding/ 均存在"
        })
        total_score += 10

    # ---------- 2. 文件存在性检查 (10分) ----------
    needed_files = ["ops/onboarding_result.json", "ops/slack_welcome_cache.json"]
    files_exist = True
    for f in needed_files:
        if not (base / f).is_file():
            files_exist = False
            details.append({
                "item": f"文件 {f} 存在",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"未能找到 {f}"
            })
            break
    if files_exist:
        details.append({
            "item": "必需产物文件存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "ops/onboarding_result.json 和 ops/slack_welcome_cache.json 均存在"
        })
        total_score += 10

    # ---------- 3. JSON合法性 (10分) ----------
    json_ok = True
    try:
        result = load_json_relative(base, "ops/onboarding_result.json")
        if result is None:
            raise FileNotFoundError("onboarding_result.json 未找到")
    except Exception as e:
        json_ok = False
        details.append({
            "item": "onboarding_result.json 合法 JSON",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": str(e)
        })
    else:
        details.append({
            "item": "onboarding_result.json 合法 JSON",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 5

    try:
        slack = load_json_relative(base, "ops/slack_welcome_cache.json")
        if slack is None:
            raise FileNotFoundError("slack_welcome_cache.json 未找到")
    except Exception as e:
        json_ok = False
        details.append({
            "item": "slack_welcome_cache.json 合法 JSON",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": str(e)
        })
    else:
        details.append({
            "item": "slack_welcome_cache.json 合法 JSON",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": "解析成功"
        })
        total_score += 5

    if not json_ok:
        # 后续检查需要JSON，无法进行则返回
        return {"total_score": total_score, "details": details}

    # ---------- 4. onboarding_result.json 内容（50分）----------
    # 重新加载原始数据以计算期望结果
    try:
        contracts_data = load_json_relative(base, "data/onboarding/contracts.json")
        accounts_data = load_json_relative(base, "data/accounts.json")
        perm_packs_data = load_json_relative(base, "data/onboarding/permission_packs.json")
        equip_data = load_json_relative(base, "data/onboarding/equipment_inventory.json")
        if any(x is None for x in [contracts_data, accounts_data, perm_packs_data, equip_data]):
            raise FileNotFoundError("原始数据文件缺失")
    except Exception as e:
        details.append({
            "item": "读取原始数据",
            "score": 0,
            "max_score": 50,
            "passed": False,
            "reason": f"无法加载原始数据：{e}"
        })
        # 剩余分数无法判定，直接返回
        return {"total_score": total_score, "details": details}

    # 构建期望结果
    # 筛选 signed 合同
    signed_contracts = [c for c in contracts_data["contracts"] if c["status"] == "signed"]
    # 按 employee_id 排序（确保顺序一致）
    signed_contracts.sort(key=lambda x: x["employee_id"])

    # 建立 email -> account 的映射
    email_to_account = {a["email"]: a for a in accounts_data["accounts"]}
    # 建立 department -> pack_id 映射（取第一匹配）
    dept_to_pack = {}
    for pack in perm_packs_data["permission_packs"]:
        # 根据 department 推断 pack_id：假设 pack_id 前三个字母与部门对应？实际我们手动映射
        # 更可靠：直接匹配 department 名称与 pack_id 前缀（eng -> engineering）
        pack_dept = pack["pack_id"].split("_")[0]  # "eng_pack" -> "eng"
        dept_to_pack[pack_dept] = pack["pack_id"]
    # 更精确：我们提前知道部门与包的对应关系（来自设计）
    dept_to_pack_actual = {
        "engineering": "eng_pack",
        "marketing": "mkt_pack",
        "hr": "hr_pack"
    }

    # 可用设备列表，按 asset_tag 排序
    available_assets = sorted(
        [e for e in equip_data["equipment_inventory"] if e["status"] == "available"],
        key=lambda x: x["asset_tag"]
    )

    expected_result = []
    expected_slack = []
    for idx, contract in enumerate(signed_contracts):
        email = contract["email"]
        account = email_to_account.get(email)
        if account is None:
            continue  # 不应该发生，跳过
        dept = account["department"]
        pack_id = dept_to_pack_actual.get(dept)
        pack_obj = None
        for p in perm_packs_data["permission_packs"]:
            if p["pack_id"] == pack_id:
                pack_obj = p
                break
        systems = pack_obj["systems"] if pack_obj else []
        asset_tag = available_assets[idx]["asset_tag"] if idx < len(available_assets) else None

        expected_result.append({
            "employee_id": contract["employee_id"],
            "employee_name": contract["employee_name"],
            "department": dept,
            "email": email,
            "assigned_systems": systems,
            "asset_tag": asset_tag
        })
        # 欢迎消息：至少包含“欢迎”和姓名
        welcome_msg = f"欢迎 {contract['employee_name']}！你的入职分配已确认。"
        expected_slack.append({
            "employee_id": contract["employee_id"],
            "message": welcome_msg
        })

    # 比较 result 内容
    result_score = 0
    result_max = 50
    # 检查条目数
    if len(result) != len(expected_result):
        details.append({
            "item": "onboarding_result.json 员工条目数",
            "score": 0,
            "max_score": result_max,
            "passed": False,
            "reason": f"期望 {len(expected_result)} 条，实际 {len(result)} 条"
        })
    else:
        # 逐项检查，每个员工占 15 分，格式占 5 分
        per_emp_max = 15  # 3个员工共45分
        emp_ok = True
        for i, exp in enumerate(expected_result):
            actual = result[i] if i < len(result) else None
            if actual is None:
                emp_ok = False
                break
            # 检查关键字段
            fields = ["employee_id", "employee_name", "department", "email", "assigned_systems", "asset_tag"]
            match = True
            for f in fields:
                if actual.get(f) != exp[f]:
                    match = False
                    break
            if not match:
                emp_ok = False
                break
        if emp_ok:
            # 格式检查：是否包含额外字段？至少没有多余要求，我们允许额外字段，但为了严格，可检查无多余核心字段
            # 这里简单给满分
            details.append({
                "item": "onboarding_result.json 内容完全正确",
                "score": 45,
                "max_score": 45,
                "passed": True,
                "reason": "所有3名员工的字段均匹配期望"
            })
            total_score += 45
            result_score += 45
        else:
            # 部分正确时精确扣分（简化处理，不逐条列出了，直接给0）
            details.append({
                "item": "onboarding_result.json 内容错误",
                "score": 0,
                "max_score": 45,
                "passed": False,
                "reason": "至少一个员工字段不符"
            })
        # JSON 结构格式额外5分（比如数组是顶层，每个对象包含所需字段）
        # 此处已经包含在上面的检查中，额外给格式分只要条目数正确且无重大结构问题
        if len(result) == len(expected_result):
            details.append({
                "item": "onboarding_result.json 整体结构格式",
                "score": 5,
                "max_score": 5,
                "passed": True,
                "reason": "JSON数组，每个对象具备必需字段"
            })
            total_score += 5
            result_score += 5
        else:
            details.append({
                "item": "onboarding_result.json 整体结构格式",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": "条目数不匹配"
            })

    # ---------- 5. slack_welcome_cache.json 内容（20分）----------
    slack_score = 0
    slack_max = 20
    if len(slack) != len(expected_slack):
        details.append({
            "item": "slack_welcome_cache.json 条目数",
            "score": 0,
            "max_score": slack_max,
            "passed": False,
            "reason": f"期望 {len(expected_slack)} 条，实际 {len(slack)} 条"
        })
    else:
        # 每个员工消息占6分（共18分），格式2分
        slack_emp_ok = True
        for i, exp in enumerate(expected_slack):
            actual = slack[i] if i < len(slack) else None
            if actual is None:
                slack_emp_ok = False
                break
            # 必须包含 employee_id 和 message，且 message 包含员工姓名
            if actual.get("employee_id") != exp["employee_id"]:
                slack_emp_ok = False
                break
            msg = actual.get("message", "")
            if "欢迎" not in msg or exp["employee_name"] not in msg:
                slack_emp_ok = False
                break
        if slack_emp_ok:
            details.append({
                "item": "slack_welcome_cache.json 内容正确",
                "score": 18,
                "max_score": 18,
                "passed": True,
                "reason": "所有消息包含欢迎语和对应员工姓名"
            })
            total_score += 18
            slack_score += 18
        else:
            details.append({
                "item": "slack_welcome_cache.json 内容错误",
                "score": 0,
                "max_score": 18,
                "passed": False,
                "reason": "至少一个员工消息不符合要求"
            })
        # 格式检查：数组且每个对象有 employee_id 和 message 字段
        format_ok = all(isinstance(item, dict) and "employee_id" in item and "message" in item for item in slack)
        if format_ok:
            details.append({
                "item": "slack_welcome_cache.json 结构格式",
                "score": 2,
                "max_score": 2,
                "passed": True,
                "reason": "数组，每个元素包含 employee_id 和 message"
            })
            total_score += 2
            slack_score += 2
        else:
            details.append({
                "item": "slack_welcome_cache.json 结构格式",
                "score": 0,
                "max_score": 2,
                "passed": False,
                "reason": "缺少必需字段"
            })

    # 总分写死100，但根据实际加总
    total_score_final = total_score  # 已累计，无需再加
    # 确保总分在0-100
    total_score_final = max(0, min(100, total_score_final))
    return {"total_score": total_score_final, "details": details}

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify(workspace)
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"验证完成，总分：{result['total_score']}/100")
