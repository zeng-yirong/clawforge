import sys
import json
import os
from pathlib import Path

def verify(workspace: str):
    details = []
    total = 0

    # --------------------------------------------------------------------
    # 1. Directory structure (10 pts)
    # --------------------------------------------------------------------
    ops_dir = Path(workspace) / "ops"
    pkg_file = ops_dir / "onboarding_package.json"
    inv_file = Path(workspace) / "data" / "onboarding" / "equipment_inventory.json"

    ops_exists = ops_dir.is_dir()
    pkg_exists = pkg_file.is_file()
    inv_exists = inv_file.is_file()
    dir_score = 10 if (ops_exists and pkg_exists and inv_exists) else 0
    details.append({
        "item": "Directory structure: ops/onboarding_package.json and equipment_inventory.json exist",
        "score": dir_score,
        "max_score": 10,
        "passed": dir_score == 10,
        "reason": "OK" if dir_score == 10 else "Missing required files or directories"
    })
    total += dir_score

    # --------------------------------------------------------------------
    # 2. Package JSON format (10 pts)
    # --------------------------------------------------------------------
    format_score = 0
    format_reason = "OK"
    try:
        with open(pkg_file, "r") as f:
            package = json.load(f)
        required_fields = ["employee_id", "employee_name", "email_profile", "system_access", "equipment", "welcome_message"]
        if all(field in package for field in required_fields):
            # Check email_profile contains email and display_name
            if "email" in package["email_profile"] and "display_name" in package["email_profile"]:
                # Check system_access contains systems list
                if "systems" in package["system_access"] and isinstance(package["system_access"]["systems"], list):
                    # Check equipment contains asset_tag and asset_type
                    if "asset_tag" in package["equipment"] and "asset_type" in package["equipment"]:
                        # Check welcome_message contains content and channel
                        if "content" in package["welcome_message"] and "channel" in package["welcome_message"]:
                            format_score = 10
                        else:
                            format_reason = "welcome_message missing content/channel"
                    else:
                        format_reason = "equipment missing asset_tag or asset_type"
                else:
                    format_reason = "system_access missing systems list"
            else:
                format_reason = "email_profile missing email or display_name"
        else:
            missing = [f for f in required_fields if f not in package]
            format_reason = f"Missing fields: {missing}"
    except (FileNotFoundError, json.JSONDecodeError) as e:
        format_reason = f"Failed to load package: {e}"
    details.append({
        "item": "Package JSON format and required fields",
        "score": format_score,
        "max_score": 10,
        "passed": format_score == 10,
        "reason": format_reason
    })
    total += format_score

    # --------------------------------------------------------------------
    # 3. Core contract & email (30 pts)
    # --------------------------------------------------------------------
    core_score = 0
    core_reason = ""
    # Expect employee_id = "E123", employee_name = "Alice Wang"
    # email_profile.email = "alice.wang@company.com", display_name = "Alice Wang"
    try:
        if package["employee_id"] == "E123":
            core_score += 5
        else:
            core_reason += "employee_id mismatch; "
        if package["employee_name"] == "Alice Wang":
            core_score += 5
        else:
            core_reason += "employee_name mismatch; "
        if package["email_profile"]["email"] == "alice.wang@company.com":
            core_score += 10
        else:
            core_reason += "email_profile.email mismatch; "
        if package["email_profile"]["display_name"] == "Alice Wang":
            core_score += 10
        else:
            core_reason += "email_profile.display_name mismatch; "
        if core_score == 30:
            core_reason = "OK"
    except KeyError:
        core_reason = "Missing fields in package"
    details.append({
        "item": "Core contract data: employee_id, name, email profile",
        "score": core_score,
        "max_score": 30,
        "passed": core_score == 30,
        "reason": core_reason
    })
    total += core_score

    # --------------------------------------------------------------------
    # 4. System access (20 pts)
    # --------------------------------------------------------------------
    sys_score = 0
    sys_reason = ""
    try:
        systems = package["system_access"]["systems"]
        # Expect sorted list ["Confluence", "GitLab", "JIRA"] (order independent)
        expected = sorted(["JIRA", "GitLab", "Confluence"])
        actual = sorted(systems)
        if actual == expected:
            sys_score = 20
            sys_reason = "OK"
        else:
            sys_reason = f"Systems mismatch, got {actual}, expected {expected}"
    except KeyError:
        sys_reason = "Missing system_access.systems"
    details.append({
        "item": "System access list matches Engineering pack",
        "score": sys_score,
        "max_score": 20,
        "passed": sys_score == 20,
        "reason": sys_reason
    })
    total += sys_score

    # --------------------------------------------------------------------
    # 5. Equipment allocation (20 pts)
    # --------------------------------------------------------------------
    equip_score = 0
    equip_reason = ""
    try:
        asset_tag = package["equipment"]["asset_tag"]
        asset_type = package["equipment"]["asset_type"]
        # Check asset_tag is LAP001 and type is laptop
        if asset_tag != "LAP001":
            equip_reason = f"Wrong asset_tag: {asset_tag} (expected LAP001)"
        elif asset_type != "laptop":
            equip_reason = f"Wrong asset_type: {asset_type} (expected laptop)"
        else:
            # Check inventory file updated to "allocated"
            try:
                with open(inv_file, "r") as f:
                    inv_data = json.load(f)
                items = inv_data.get("equipment_inventory", [])
                found = None
                for item in items:
                    if item["asset_tag"] == "LAP001":
                        found = item
                        break
                if found is None:
                    equip_reason = "LAP001 not found in inventory"
                elif found["status"] != "allocated":
                    equip_reason = f"LAP001 status is '{found['status']}', expected 'allocated'"
                else:
                    equip_score = 20
                    equip_reason = "OK"
            except (FileNotFoundError, json.JSONDecodeError) as e:
                equip_reason = f"Failed to read inventory: {e}"
    except KeyError:
        equip_reason = "Missing equipment fields in package"
    details.append({
        "item": "Equipment allocation: LAP001 laptop, inventory updated to allocated",
        "score": equip_score,
        "max_score": 20,
        "passed": equip_score == 20,
        "reason": equip_reason
    })
    total += equip_score

    # --------------------------------------------------------------------
    # 6. Welcome message (10 pts)
    # --------------------------------------------------------------------
    welcome_score = 0
    welcome_reason = ""
    try:
        content = package["welcome_message"]["content"]
        channel = package["welcome_message"]["channel"]
        # Must contain Alice's name and email
        if "Alice" in content and "alice.wang@company.com" in content:
            welcome_score += 5
        else:
            welcome_reason += "Missing name or email in content; "
        if channel == "#general":
            welcome_score += 5
        else:
            welcome_reason += f"Wrong channel: {channel}, expected #general; "
        if welcome_score == 10:
            welcome_reason = "OK"
    except KeyError:
        welcome_reason = "Missing welcome_message fields"
    details.append({
        "item": "Welcome message content and channel",
        "score": welcome_score,
        "max_score": 10,
        "passed": welcome_score == 10,
        "reason": welcome_reason
    })
    total += welcome_score

    # --------------------------------------------------------------------
    # Write result
    # --------------------------------------------------------------------
    result = {
        "total_score": total,
        "details": details
    }
    with open(Path(workspace) / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Verification completed. Total score: {total}/100")

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
