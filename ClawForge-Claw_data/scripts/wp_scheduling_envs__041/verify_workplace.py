import json
import sys
from pathlib import Path

def verify(workspace: str) -> int:
    ws = Path(workspace)
    total_score = 0
    details = []

    # 1. ops 目录存在（5分）
    ops_dir = ws / "ops"
    if ops_dir.is_dir():
        total_score += 5
        details.append({
            "item": "ops directory exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": ""
        })
    else:
        details.append({
            "item": "ops directory exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "ops/ not found"
        })

    # 2. fix_list.json 存在（5分）
    json_path = ops_dir / "fix_list.json"
    if json_path.is_file():
        total_score += 5
        details.append({
            "item": "fix_list.json exists",
            "score": 5,
            "max_score": 5,
            "passed": True,
            "reason": ""
        })
    else:
        details.append({
            "item": "fix_list.json exists",
            "score": 0,
            "max_score": 5,
            "passed": False,
            "reason": "file not found"
        })

    data = None
    if json_path.is_file():
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            total_score += 10
            details.append({
                "item": "JSON valid",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": ""
            })
        except Exception as e:
            details.append({
                "item": "JSON valid",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": f"invalid JSON: {e}"
            })
    else:
        details.append({
            "item": "JSON valid",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "file missing"
        })

    if data is not None:
        # 3. 字段存在（10分）
        if "conflict_schedule_ids" in data:
            total_score += 10
            details.append({
                "item": "conflict_schedule_ids field exists",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "reason": ""
            })
            ids = data["conflict_schedule_ids"]

            # 4. 字段是列表（10分）
            if isinstance(ids, list):
                total_score += 10
                details.append({
                    "item": "field is list",
                    "score": 10,
                    "max_score": 10,
                    "passed": True,
                    "reason": ""
                })

                # 5. 长度 == 2（10分）
                if len(ids) == 2:
                    total_score += 10
                    details.append({
                        "item": "list length is 2",
                        "score": 10,
                        "max_score": 10,
                        "passed": True,
                        "reason": ""
                    })
                else:
                    details.append({
                        "item": "list length is 2",
                        "score": 0,
                        "max_score": 10,
                        "passed": False,
                        "reason": f"len = {len(ids)}"
                    })

                # 6. 包含 sch_002（20分）
                has_002 = "sch_002" in ids
                total_score += 20 if has_002 else 0
                details.append({
                    "item": "contains sch_002",
                    "score": 20 if has_002 else 0,
                    "max_score": 20,
                    "passed": has_002,
                    "reason": "" if has_002 else "sch_002 not found"
                })

                # 7. 包含 sch_005（20分）
                has_005 = "sch_005" in ids
                total_score += 20 if has_005 else 0
                details.append({
                    "item": "contains sch_005",
                    "score": 20 if has_005 else 0,
                    "max_score": 20,
                    "passed": has_005,
                    "reason": "" if has_005 else "sch_005 not found"
                })

                # 8. 无多余 ID（20分）
                expected = {"sch_002", "sch_005"}
                actual_set = set(ids)
                if actual_set == expected:
                    total_score += 20
                    details.append({
                        "item": "no extra IDs",
                        "score": 20,
                        "max_score": 20,
                        "passed": True,
                        "reason": ""
                    })
                else:
                    extra = actual_set - expected
                    details.append({
                        "item": "no extra IDs",
                        "score": 0,
                        "max_score": 20,
                        "passed": False,
                        "reason": f"extra ids: {extra}" if extra else "missing ids"
                    })
            else:
                details.append({
                    "item": "field is list",
                    "score": 0,
                    "max_score": 10,
                    "passed": False,
                    "reason": f"type is {type(ids)}"
                })
                # 后续检查不可进行，填0
                for item_name, max_s in [
                    ("list length is 2", 10),
                    ("contains sch_002", 20),
                    ("contains sch_005", 20),
                    ("no extra IDs", 20)
                ]:
                    details.append({
                        "item": item_name,
                        "score": 0,
                        "max_score": max_s,
                        "passed": False,
                        "reason": "field not a list"
                    })
        else:
            details.append({
                "item": "conflict_schedule_ids field exists",
                "score": 0,
                "max_score": 10,
                "passed": False,
                "reason": "field missing"
            })
            # 后续检查不可进行
            for item_name, max_s in [
                ("field is list", 10),
                ("list length is 2", 10),
                ("contains sch_002", 20),
                ("contains sch_005", 20),
                ("no extra IDs", 20)
            ]:
                details.append({
                    "item": item_name,
                    "score": 0,
                    "max_score": max_s,
                    "passed": False,
                    "reason": "field missing"
                })
    else:
        # data 为 None，跳过字段检查（已在 JSON 有效项中记录原因）
        # 补全剩余检查项为 0 分
        for item_name, max_s in [
            ("conflict_schedule_ids field exists", 10),
            ("field is list", 10),
            ("list length is 2", 10),
            ("contains sch_002", 20),
            ("contains sch_005", 20),
            ("no extra IDs", 20)
        ]:
            details.append({
                "item": item_name,
                "score": 0,
                "max_score": max_s,
                "passed": False,
                "reason": "JSON parse failed or file missing"
            })

    # 确保总分不超过 100
    final_score = min(total_score, 100)
    result = {
        "total_score": final_score,
        "details": details
    }
    with open(ws / "workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

    return final_score

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
