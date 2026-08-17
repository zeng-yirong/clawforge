import os
import sys
import json

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # ---- Helper ----
    def add_detail(name, s, max_s, passed, reason):
        details.append({
            "item": name,
            "score": s,
            "max_score": max_s,
            "passed": passed,
            "reason": reason
        })

    # 1. 目录结构（5 分）
    ops_path = os.path.join(workspace, "ops")
    if os.path.isdir(ops_path):
        add_detail("ops 目录存在", 5, 5, True, "ops/ 已创建")
        score += 5
    else:
        add_detail("ops 目录存在", 0, 5, False, "ops/ 未创建")
        # 不继续检查 handoff.json
        # 但后续检查会跳过，用条件保护

    # 2. 读取原始数据，确认唯一待处理员工
    exit_path = os.path.join(workspace, "data/offboarding/exit_requests.json")
    sysacc_path = os.path.join(workspace, "data/offboarding/system_access.json")
    equip_path = os.path.join(workspace, "data/offboarding/equipment_assignments.json")

    try:
        exit_req = load_json(exit_path)["exit_requests"]
        sysacc = load_json(sysacc_path)["system_access"]
        equip = load_json(equip_path)["equipment_assignments"]
    except Exception as e:
        # 严重错误，得分0
        add_detail("基础数据文件可读", 0, 5, False, f"读取失败: {e}")
        write_score(0, details, workspace)
        return

    # 找出所有 approved 且尚未处理（sysacc 中有 active 或 equip 为 assigned）的员工
    candidate = None
    for emp_id, req in exit_req.items():
        if req["approval_status"] != "approved":
            continue
        # 检查是否有 active 或 assigned
        need_process = False
        if emp_id in sysacc:
            for entry in sysacc[emp_id]:
                if entry["status"] == "active":
                    need_process = True
                    break
        if emp_id in equip and equip[emp_id]["status"] == "assigned":
            need_process = True
        if need_process:
            if candidate is not None:
                add_detail("唯一待处理员工", 0, 10, False, f"找到多个待处理员工: {candidate}, {emp_id}")
                write_score(0, details, workspace)
                return
            candidate = emp_id

    if candidate is None:
        add_detail("唯一待处理员工", 0, 10, False, "没有找到待处理的已批准员工")
        write_score(0, details, workspace)
        return
    else:
        add_detail("唯一待处理员工", 10, 10, True, f"待处理员工: {candidate}")
        score += 10

    target_emp = candidate  # "EMP042"

    # 3. 验证 system_access 修改（25 分）
    sysacc_after = load_json(sysacc_path)["system_access"]
    expected_systems = ["Admin Portal", "CRM"]
    sys_correct = True
    fail_reason = ""
    if target_emp not in sysacc_after:
        sys_correct = False
        fail_reason = f"{target_emp} 不在 system_access 中"
    else:
        entries = sysacc_after[target_emp]
        if len(entries) != 2:
            sys_correct = False
            fail_reason = f"记录数不对, 应有2条, 现有 {len(entries)}"
        else:
            sys_names = sorted([e["system_name"] for e in entries])
            if sys_names != sorted(expected_systems):
                sys_correct = False
                fail_reason = f"系统名不对: {sys_names}"
            else:
                for e in entries:
                    if e["status"] != "revoked":
                        sys_correct = False
                        fail_reason = f"系统 {e['system_name']} 状态为 {e['status']}，应为 revoked"
                        break
    if sys_correct:
        add_detail("系统访问撤销", 25, 25, True, "两个系统均正确撤销")
        score += 25
    else:
        add_detail("系统访问撤销", 0, 25, False, fail_reason)

    # 4. 验证设备回收（20 分）
    equip_after = load_json(equip_path)["equipment_assignments"]
    equip_correct = True
    equip_fail = ""
    if target_emp not in equip_after:
        equip_correct = False
        equip_fail = f"{target_emp} 不在设备分配中"
    else:
        if equip_after[target_emp]["asset_tag"] != "LT-2041":
            equip_correct = False
            equip_fail = f"资产标签应为 LT-2041，实际 {equip_after[target_emp]['asset_tag']}"
        elif equip_after[target_emp]["status"] != "reclaimed":
            equip_correct = False
            equip_fail = f"状态应为 reclaimed，实际 {equip_after[target_emp]['status']}"
    if equip_correct:
        add_detail("设备回收", 20, 20, True, "设备 LT-2041 标记为 reclaimed")
        score += 20
    else:
        add_detail("设备回收", 0, 20, False, equip_fail)

    # 5. 验证交接清单 handoff.json（30 分）
    handoff_path = os.path.join(workspace, "ops/handoff.json")
    if not os.path.isfile(handoff_path):
        add_detail("交接清单文件存在", 0, 10, False, "ops/handoff.json 不存在")
        # 后面跳过
    else:
        try:
            with open(handoff_path, "r") as f:
                handoff = json.load(f)
        except:
            add_detail("交接清单合法 JSON", 0, 10, False, "非法 JSON")
            handoff = None

        if handoff is not None:
            add_detail("交接清单合法 JSON", 10, 10, True, "JSON 解析成功")
            score += 10

            # 检查字段
            required_fields = ["employee_id", "revoked_systems", "equipment_reclaimed"]
            missing = [f for f in required_fields if f not in handoff]
            if missing:
                add_detail("交接清单字段完整性", 0, 10, False, f"缺少字段: {missing}")
            else:
                field_ok = True
                field_fail = ""
                # employee_id
                if handoff["employee_id"] != target_emp:
                    field_ok = False
                    field_fail += f"employee_id 应为 {target_emp}，实际 {handoff['employee_id']}; "
                # revoked_systems
                expected_sys_list = sorted(expected_systems)
                got_sys = sorted(handoff["revoked_systems"])
                if got_sys != expected_sys_list:
                    field_ok = False
                    field_fail += f"revoked_systems 应为 {expected_sys_list}，实际 {got_sys}; "
                # equipment_reclaimed
                expected_equip = ["LT-2041"]
                got_equip = sorted(handoff["equipment_reclaimed"])
                if got_equip != expected_equip:
                    field_ok = False
                    field_fail += f"equipment_reclaimed 应为 {expected_equip}，实际 {got_equip}"
                if field_ok:
                    add_detail("交接清单字段内容", 10, 10, True, "所有字段值正确")
                    score += 10
                else:
                    add_detail("交接清单字段内容", 0, 10, False, field_fail)
    # 6. 检查未修改其他员工（10 分）
    # 读取修改后的 system_access 和 equipment，对比初始状态（除了目标员工外应一致）
    # 我们用加载的原始数据作为基准（但 builder 创建时就是初始，我们直接使用），
    # 但注意 agent 可能修改了其他文件，我们需要从磁盘重新读取判断。
    # 我们已经读取 sysacc_after 和 equip_after，现在检查非目标员工
    others_ok = True
    others_fail = ""

    # 重新读原始数据（但原始数据在 env 中，可以直接从文件读，但我们已经有了初始数据？我们可以从 builder 写死的逻辑再构建一次，但更简单：从磁盘读取一次作为“应该保持不变”的基准。
    # 为了避免重复读，我们直接依赖我们在上面加载的初始数据？注意初始数据已经在变量中，但可能被 agent 修改了磁盘。所以我们需要一个初始参考。我们可以在验证开始时复制一份初始数据？但那样复杂。
    # 更好的办法：在验证脚本中直接构造预期不变的员工列表（除了目标员工外的其他员工），然后检查当前的 sysacc_after 和 equip_after 中这些员工的值是否与初始一致。初始值可以从 builder 代码的常理推断，但为了可靠，我们可以从磁盘读取一遍初始（但已经改变）。不行。
    # 所以我们在验证开始时，先读取所有数据作为初始快照？但此时磁盘已经被 agent 修改，读取的是修改后的。无法获得初始值。所以需要我们在验证脚本中硬编码初始值（因为 builder 是确定的）。这样更可靠。我们可以在 verify 中重新构建初始字典（与 builder 一致），然后比对。这样更客观。
    # 重写：在 verify 开头定义初始值，然后比较当前状态。
    # 但是注意：我们已经在上面读取了修改后的 sysacc_after 和 equip_after，现在定义一个初始的 sysacc_initial 和 equip_initial。
    # 初始值：
    sysacc_initial = {
        "EMP001": [{"system_name":"Admin Portal", "status":"active"}, {"system_name":"CRM", "status":"active"}],
        "EMP002": [{"system_name":"Admin Portal", "status":"active"}, {"system_name":"CRM", "status":"active"}],
        "EMP003": [{"system_name":"Admin Portal", "status":"revoked"}, {"system_name":"CRM", "status":"revoked"}],
        "EMP042": [{"system_name":"Admin Portal", "status":"active"}, {"system_name":"CRM", "status":"active"}]
    }
    equip_initial = {
        "EMP001": {"asset_tag":"BG-8821","status":"assigned"},
        "EMP002": {"asset_tag":"LT-2041","status":"assigned"},
        "EMP003": {"asset_tag":"BG-8821","status":"reclaimed"},
        "EMP042": {"asset_tag":"LT-2041","status":"assigned"}
    }
    # 现在比较除了 target_emp 之外的其他员工
    for emp, entries in sysacc_initial.items():
        if emp == target_emp:
            continue
        current = sysacc_after.get(emp)
        if current != entries:
            others_ok = False
            others_fail += f"员工 {emp} 系统访问被错误修改; "
    for emp, record in equip_initial.items():
        if emp == target_emp:
            continue
        current = equip_after.get(emp)
        if current != record:
            others_ok = False
            others_fail += f"员工 {emp} 设备记录被错误修改; "
    if others_ok:
        add_detail("其他员工未被修改", 10, 10, True, "所有其他员工记录保持不变")
        score += 10
    else:
        add_detail("其他员工未被修改", 0, 10, False, others_fail)

    # 总分
    total = min(score, 100)
    result = {
        "total_score": total,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"Total score: {total}/100")

if __name__ == "__main__":
    main()
