import os
import json
import sys

def verify(workspace):
    details = []
    total_score = 0

    # --- 1. 检查 output 目录是否存在 (10分) ---
    output_dir = os.path.join(workspace, "output")
    if os.path.isdir(output_dir):
        details.append({
            "item": "output目录存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "output/ 目录已创建"
        })
        total_score += 10
    else:
        details.append({
            "item": "output目录存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "output/ 目录未找到"
        })
        # 后续检查依赖目录，直接返回
        _write_score(details, total_score, workspace)
        return

    # 预期处理的 employee_id (只有 signed 的)
    expected_ids = ["E001", "E002"]
    # 每个id对应的信息（从合同数据提取，但验证脚本不依赖env，直接硬编码）
    expected_data = {
        "E001": {
            "name": "Alice Wang",
            "email": "alice.wang@corp.com",
            "department": "engineering",
            "pack_id": "engineering",
            "systems": ["jira", "github", "vpn"],
            "laptop_tag": "LT-001"
        },
        "E002": {
            "name": "Bob Li",
            "email": "bob.li@corp.com",
            "department": "design",
            "pack_id": "design",
            "systems": ["figma", "slack", "vpn"],
            "laptop_tag": "LT-002"
        }
    }

    # --- 2. 检查子目录及文件存在 (20分) ---
    file_exist_score = 0
    max_file = 20
    per_file = max_file / (len(expected_ids) * 4)  # 每个文件1.25分，取整？为了整数计算，我们按每个文件2.5分，但不行。简单：每个文件2分，共16分，留4分作为子目录存在
    # 改为：子目录存在10分，每个文件存在2.5分共20分，但这里我们融合判断：遍历每个id检测四个文件，每个文件存在给1.25分，但为了整数，我们设每个文件2分，共16分，子目录存在各2分，但不好处理。
    # 更简单：直接检测每个id的子目录是否存在，每个2.5分，共5分；剩下的15分给文件存在（每个文件1.875分）。为了简洁，我们采用累计计数，每个文件2.5分（共20分）。
    expected_dirs = [os.path.join(output_dir, eid) for eid in expected_ids]
    for d in expected_dirs:
        if os.path.isdir(d):
            pass
        else:
            details.append({
                "item": f"子目录 {os.path.basename(d)} 存在",
                "score": 0,
                "max_score": 5,
                "passed": False,
                "reason": f"未找到目录 {d}"
            })
            # 跳过该子目录的后续检查
    # 实际我们累计检查文件
    files_ok = 0
    files_checked = []
    for eid in expected_ids:
        subdir = os.path.join(output_dir, eid)
        if not os.path.isdir(subdir):
            files_checked.append((eid, "email_profile.json", False))
            files_checked.append((eid, "sys_access.json", False))
            files_checked.append((eid, "equipment.json", False))
            files_checked.append((eid, "welcome.json", False))
            continue
        for fname in ["email_profile.json", "sys_access.json", "equipment.json", "welcome.json"]:
            fpath = os.path.join(subdir, fname)
            if os.path.isfile(fpath):
                files_ok += 1
                files_checked.append((eid, fname, True))
            else:
                files_checked.append((eid, fname, False))
    file_exist_score = int(20 * files_ok / (len(expected_ids)*4))
    # 更精确一点：直接按每个文件2.5分，但20分 / 8个文件 = 2.5分，我们保留小数？统一用整数，决定：每个文件2.5分，以0.5分粒度？不行，最终总分整数。我们改：文件存在占20分，每个文件2.5分，但最后round。为了简化，我们按每个文件2分，共16分，子目录存在各2分共4分，合计20分。
    # 重新设计：子目录存在每个2.5分（共5分），文件存在每个1.875分（共15分），但麻烦。放弃精确，直接用出现分数，最后确保总和整数。
    # 我们用一种简单方式：检查出8个文件，每个文件2分，共16分；子目录存在每个2分（共4分），但子目录存在已经在文件检查中隐含？我们单独判断。
    subdir_score = 0
    for d in expected_dirs:
        if os.path.isdir(d):
            subdir_score += 2  # 每个2分
    file_exist_score = files_ok * 2  # 每个文件2分，上限16
    total_file_dir = subdir_score + file_exist_score  # 最多4+16=20
    details.append({
        "item": "子目录及文件存在性",
        "score": total_file_dir,
        "max_score": 20,
        "passed": total_file_dir == 20,
        "reason": f"子目录分数{subdir_score}/4，文件分数{file_exist_score}/16"
    })
    total_score += total_file_dir

    # --- 3. JSON 格式合法性 (10分) ---
    json_ok = 0
    json_items = 8
    for eid in expected_ids:
        subdir = os.path.join(output_dir, eid)
        if not os.path.isdir(subdir):
            json_ok += 0
            continue
        for fname in ["email_profile.json", "sys_access.json", "equipment.json", "welcome.json"]:
            fpath = os.path.join(subdir, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath) as f:
                        json.load(f)
                    json_ok += 1
                except:
                    pass
    json_score = int(10 * json_ok / json_items)
    details.append({
        "item": "JSON文件格式合法",
        "score": json_score,
        "max_score": 10,
        "passed": json_ok == json_items,
        "reason": f"{json_ok}/{json_items} 个文件格式正确"
    })
    total_score += json_score

    # --- 4. email_profile 内容验证 (10分) ---
    email_score = 0
    max_email = 10
    for eid in expected_ids:
        subdir = os.path.join(output_dir, eid)
        fpath = os.path.join(subdir, "email_profile.json")
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath) as f:
                data = json.load(f)
        except:
            continue
        exp = expected_data[eid]
        # 必须包含 employee_id, email, display_name, department
        if (data.get("employee_id") == eid and
            data.get("email") == exp["email"] and
            data.get("display_name") == exp["name"] and
            data.get("department") == exp["department"]):
            email_score += 5  # 每个员工5分，共10分
    details.append({
        "item": "email_profile字段内容正确",
        "score": email_score,
        "max_score": 10,
        "passed": email_score == 10,
        "reason": f"正确员工数 {email_score//5}/2"
    })
    total_score += email_score

    # --- 5. sys_access 内容验证 (20分) ---
    sys_score = 0
    max_sys = 20
    for eid in expected_ids:
        subdir = os.path.join(output_dir, eid)
        fpath = os.path.join(subdir, "sys_access.json")
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath) as f:
                data = json.load(f)
        except:
            continue
        exp = expected_data[eid]
        # 应包含 employee_id 和 systems，且systems列表与预期一致（顺序不重要）
        if (data.get("employee_id") == eid and
            sorted(data.get("systems", [])) == sorted(exp["systems"])):
            sys_score += 10
    details.append({
        "item": "sys_access系统列表正确",
        "score": sys_score,
        "max_score": 20,
        "passed": sys_score == 20,
        "reason": f"正确员工数 {sys_score//10}/2"
    })
    total_score += sys_score

    # --- 6. equipment 分配验证 (20分) ---
    eq_score = 0
    max_eq = 20
    for eid in expected_ids:
        subdir = os.path.join(output_dir, eid)
        fpath = os.path.join(subdir, "equipment.json")
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath) as f:
                data = json.load(f)
        except:
            continue
        exp = expected_data[eid]
        # 必须包含 asset_tag, asset_type, assigned_to
        if (data.get("asset_tag") == exp["laptop_tag"] and
            data.get("asset_type") == "laptop" and
            data.get("assigned_to") == eid):
            eq_score += 10
    details.append({
        "item": "设备分配正确",
        "score": eq_score,
        "max_score": 20,
        "passed": eq_score == 20,
        "reason": f"正确分配 {eq_score//10}/2"
    })
    total_score += eq_score

    # --- 7. welcome 消息内容验证 (10分) ---
    welcome_score = 0
    max_welcome = 10
    for eid in expected_ids:
        subdir = os.path.join(output_dir, eid)
        fpath = os.path.join(subdir, "welcome.json")
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath) as f:
                data = json.load(f)
        except:
            continue
        exp = expected_data[eid]
        expected_msg = f"Welcome {exp['name']} to the team!"
        if data.get("message") == expected_msg:
            welcome_score += 5
    details.append({
        "item": "欢迎消息内容正确",
        "score": welcome_score,
        "max_score": 10,
        "passed": welcome_score == 10,
        "reason": f"正确消息 {welcome_score//5}/2"
    })
    total_score += welcome_score

    # 写入结果
    _write_score(details, total_score, workspace)

def _write_score(details, total_score, workspace):
    # 确保 total_score 为整数
    total_score = int(round(total_score))
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
